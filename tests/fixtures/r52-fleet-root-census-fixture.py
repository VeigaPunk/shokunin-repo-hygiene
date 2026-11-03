#!/usr/bin/env python3
"""r52 acceptance fixture for the fleet-root hygiene census tool (C2 capability).

Tool under test (default):
  tools/souji-fleet-root-census.py (lane copy; the r52 wave candidate was hardened into it)
CLI contract exercised:  --fleet-root DIR --out PATH

Frozen rules re-derived from census/round-52/preregistration.txt (C2 format block):
  class rule (first match wins): kind=symlink -> symlink; tracked=yes -> tracked;
                                 ignored=yes -> ignored; otherwise untracked-stray
  disposition: report-only for untracked-stray; none otherwise; nothing else allowed
  header: first line, SCOPE, TOOL_SHA256, FLEET_HEAD(40 hex), ENTRIES, four COUNT lines,
          then name<TAB>kind<TAB>tracked<TAB>ignored<TAB>class<TAB>disposition
  counts: tracked/ignored/untracked-stray/symlink

Cases: (a) honest root, (b) header integrity, (c1-c3) refusals exit 2,
       (d) read-only (tree snapshot + git status unchanged), (e1-e2) controls must fail.

Exit 0 only if every honest case passes AND every control fails for its named reason.
All synthetic roots and captures are created under --scratch (mkdtemp); every git call
names its repository with -C, and the fixture refuses to commit unless
`git -C D rev-parse --show-toplevel` is D.
"""

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile

SEAT_DIR = ("/home/vgpnk/Projects/shokunin/souji-shokunin/"
            ".ufo/waves/round-52/w1/S52executor02")
SCRATCH_DEFAULT = "/fast/scratch/hyaku/souji-r52/S52executor02"
CANDIDATE_DEFAULT = ("/home/vgpnk/Projects/shokunin/souji-shokunin/"
                     "tools/souji-fleet-root-census.py")

CLASSES = ("tracked", "ignored", "untracked-stray", "symlink")
KINDS = ("file", "dir", "symlink", "other")
YESNO = ("yes", "no")
DISPOSITIONS = ("report-only", "none")
COLHDR = ["name", "kind", "tracked", "ignored", "class", "disposition"]
FIRST_LINE = "# souji round-52 fleet-root census"

# Expected honest-root table: name, kind, tracked, ignored, class, disposition
EXPECTED = [
    (".gitignore",        "file",    "yes", "no",  "tracked",         "none"),
    (".stray-dotfile",    "file",    "no",  "no",  "untracked-stray", "report-only"),
    ("ignored.log",       "file",    "no",  "yes", "ignored",         "none"),
    ("link-tracked.txt",  "symlink", "yes", "no",  "symlink",         "none"),
    ("link-untracked.txt", "symlink", "no", "no",  "symlink",         "none"),
    ("stray-dir",         "dir",     "no",  "no",  "untracked-stray", "report-only"),
    ("stray.txt",         "file",    "no",  "no",  "untracked-stray", "report-only"),
    ("tracked-dir",       "dir",     "yes", "no",  "tracked",         "none"),
    ("tracked-file.txt",  "file",    "yes", "no",  "tracked",         "none"),
    ("with space.txt",    "file",    "no",  "no",  "untracked-stray", "report-only"),
]

EXPECTED_COUNTS = {c: sum(1 for r in EXPECTED if r[4] == c) for c in CLASSES}


# --------------------------------------------------------------------------- helpers

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _write(path, text):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def _git(root, *args, timeout=120):
    """Read-only-by-intent git call: -C names the repo, optional locks disabled."""
    env = dict(os.environ)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env.pop("GIT_DIR", None)
    env.pop("GIT_WORK_TREE", None)
    return subprocess.run(["git", "-C", root, *args],
                          capture_output=True, text=True, env=env, timeout=timeout)


def _git_init_commit(D, scratch):
    """init + guard + add + commit, only ever inside D (a fixture repo under scratch)."""
    if not os.path.realpath(D).startswith(os.path.realpath(scratch) + os.sep):
        raise RuntimeError("fixture guard: %r is not under scratch %r" % (D, scratch))
    r = _git(D, "init", "-q")
    if r.returncode != 0:
        raise RuntimeError("git init failed: %s" % r.stderr.strip())
    top = _git(D, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        raise RuntimeError("rev-parse --show-toplevel failed: %s" % top.stderr.strip())
    toplevel = top.stdout.strip()
    if os.path.realpath(toplevel) != os.path.realpath(D):
        raise RuntimeError("fixture guard: toplevel %r != fixture dir %r" % (toplevel, D))
    r = _git(D, "add", "-A")
    if r.returncode != 0:
        raise RuntimeError("git add failed: %s" % r.stderr.strip())
    r = _git(D, "-c", "user.name=fixture", "-c", "user.email=fixture@local",
             "commit", "-q", "-m", "fixture root")
    if r.returncode != 0:
        raise RuntimeError("git commit failed: %s" % r.stderr.strip())


def build_min_root(scratch, prefix="min-"):
    D = tempfile.mkdtemp(dir=scratch, prefix=prefix)
    _write(os.path.join(D, "f.txt"), "x\n")
    _git_init_commit(D, scratch)
    return D


def build_honest_root(scratch, prefix="honest-"):
    """One of each frozen class, including the symlink>tracked precedence pair."""
    D = tempfile.mkdtemp(dir=scratch, prefix=prefix)
    os.makedirs(os.path.join(D, "tracked-dir"))
    _write(os.path.join(D, ".gitignore"), "*.log\n")
    _write(os.path.join(D, "tracked-file.txt"), "tracked\n")
    _write(os.path.join(D, "tracked-dir", "inner.txt"), "inner\n")
    os.symlink("tracked-file.txt", os.path.join(D, "link-tracked.txt"))
    _git_init_commit(D, scratch)                     # commits the four tracked entries
    _write(os.path.join(D, "ignored.log"), "noise\n")
    _write(os.path.join(D, "stray.txt"), "stray\n")
    os.makedirs(os.path.join(D, "stray-dir"))
    _write(os.path.join(D, "stray-dir", "inside.txt"), "inside\n")
    os.symlink("tracked-file.txt", os.path.join(D, "link-untracked.txt"))
    _write(os.path.join(D, ".stray-dotfile"), "dot\n")
    _write(os.path.join(D, "with space.txt"), "spaced\n")
    return D


def snapshot(root):
    """Sorted (relpath, mtime_ns, size, S_IFMT) for every entry under root."""
    rows = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames.sort()
        filenames.sort()
        for name in list(dirnames) + list(filenames):
            p = os.path.join(dirpath, name)
            rel = os.path.relpath(p, root)
            try:
                st = os.lstat(p)
            except FileNotFoundError:
                rows.append((rel, "missing", 0, 0))
                continue
            rows.append((rel, st.st_mtime_ns, st.st_size, stat.S_IFMT(st.st_mode)))
    rows.sort()
    return rows


def describe_snapshot_diff(before, after):
    b = {r[0]: r[1:] for r in before}
    a = {r[0]: r[1:] for r in after}
    bits = []
    added = sorted(set(a) - set(b))
    removed = sorted(set(b) - set(a))
    changed = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    if added:
        bits.append("added=%r" % added[:5])
    if removed:
        bits.append("removed=%r" % removed[:5])
    if changed:
        bits.append("changed=%r" % changed[:5])
    return "; ".join(bits) or "no difference"


# --------------------------------------------------------------------------- parsing

def parse_capture(text):
    p = {"errs": [], "hdr": {}, "counts": {}, "rows": [], "colhdr": None, "first": None}
    lines = text.splitlines()
    if not lines:
        p["errs"].append("capture is empty")
        return p
    p["first"] = lines[0]
    for ln in lines:
        if ln.startswith("#"):
            for m in re.finditer(r"#\s*COUNT\s+([A-Za-z0-9_-]+)\s*=\s*(\d+)", ln):
                key = m.group(1)
                if key in p["counts"]:
                    p["errs"].append("duplicate COUNT line for %s" % key)
                p["counts"][key] = int(m.group(2))
            m = re.match(r"^#\s*(SCOPE|TOOL_SHA256|FLEET_HEAD|ENTRIES)\s*=(.*)$", ln)
            if m:
                p["hdr"][m.group(1)] = m.group(2).strip()
            continue
        if not ln.strip():
            continue
        parts = ln.split("\t")
        if [x.strip() for x in parts] == COLHDR:
            if p["colhdr"] is not None:
                p["errs"].append("duplicate column header line")
            p["colhdr"] = parts
            continue
        p["rows"].append(parts)
    return p


# --------------------------------------------------------------------------- checkers

def check_header(p, tool_path, root):
    """Case (b): ENTRIES vs row count, COUNT vs recomputed, TOOL_SHA256, FLEET_HEAD."""
    errs = list(p["errs"])
    if not (p["first"] or "").startswith(FIRST_LINE):
        errs.append("first line does not start with %r" % FIRST_LINE)
    if "SCOPE" not in p["hdr"]:
        errs.append("missing SCOPE line")
    if p["colhdr"] is None:
        errs.append("missing column header line %r" % "\t".join(COLHDR))

    want_sha = sha256_file(tool_path)
    got_sha = p["hdr"].get("TOOL_SHA256", "")
    if got_sha != want_sha:
        errs.append("TOOL_SHA256=%r != sha256(tool bytes)=%s" % (got_sha, want_sha))

    fleet_head = p["hdr"].get("FLEET_HEAD", "")
    if not re.fullmatch(r"[0-9a-f]{40}", fleet_head):
        errs.append("FLEET_HEAD=%r is not 40 lowercase hex" % fleet_head)
    elif root is not None:
        r = _git(root, "rev-parse", "HEAD")
        expected_head = r.stdout.strip()
        if expected_head and fleet_head != expected_head:
            errs.append("FLEET_HEAD=%s != git -C root rev-parse HEAD=%s"
                        % (fleet_head, expected_head))

    entries = p["hdr"].get("ENTRIES")
    nrows = len(p["rows"])
    if entries is None:
        errs.append("missing ENTRIES line")
    elif not entries.isdigit():
        errs.append("ENTRIES=%r is not a non-negative integer" % entries)
    else:
        n = int(entries)
        if n != nrows:
            errs.append("ENTRIES=%d != row count %d" % (n, nrows))
        if n < 1:
            errs.append("ENTRIES=%d (frozen predicate requires at least 1)" % n)

    for key in CLASSES:
        if key not in p["counts"]:
            errs.append("missing COUNT line for %s" % key)
    for key, val in sorted(p["counts"].items()):
        if key not in CLASSES:
            errs.append("unexpected COUNT key %r" % key)
            continue
        recomp = sum(1 for r in p["rows"] if len(r) == 6 and r[4] == key)
        if val != recomp:
            errs.append("COUNT %s=%d != recomputed %d" % (key, val, recomp))

    names = [r[0] for r in p["rows"] if r]
    if names != sorted(names):
        errs.append("rows are not sorted by name")
    if len(set(names)) != len(names):
        errs.append("duplicate row names")
    return errs


def check_table(p, expected):
    """Case (a): each row's class follows the frozen rule; dispositions; exact table."""
    errs = list(p["errs"])
    byname = {}
    for r in p["rows"]:
        if len(r) != 6:
            errs.append("row %r does not have 6 tab-separated fields" % (r,))
            continue
        name, kind, tracked, ignored, cls, disp = r
        if name in byname:
            errs.append("duplicate row %r" % name)
        byname[name] = r
        if kind not in KINDS:
            errs.append("row %s: kind=%r not in %r" % (name, kind, list(KINDS)))
        if tracked not in YESNO:
            errs.append("row %s: tracked=%r not in %r" % (name, tracked, list(YESNO)))
        if ignored not in YESNO:
            errs.append("row %s: ignored=%r not in %r" % (name, ignored, list(YESNO)))
        if kind in KINDS and tracked in YESNO and ignored in YESNO:
            rule_class = ("symlink" if kind == "symlink"
                          else "tracked" if tracked == "yes"
                          else "ignored" if ignored == "yes"
                          else "untracked-stray")
            if cls != rule_class:
                errs.append("row %s: class=%s contradicts the frozen rule for "
                            "kind=%s tracked=%s ignored=%s (rule gives %s)"
                            % (name, cls, kind, tracked, ignored, rule_class))
            want_disp = "report-only" if rule_class == "untracked-stray" else "none"
            if disp != want_disp:
                errs.append("row %s: disposition=%r, frozen rule requires %r"
                            % (name, disp, want_disp))
        if disp not in DISPOSITIONS:
            errs.append("row %s: disposition %r is not permitted "
                        "(no removal may be proposed)" % (name, disp))

    exp = {r[0]: r for r in expected}
    missing = sorted(set(exp) - set(byname))
    extra = sorted(set(byname) - set(exp))
    if missing:
        errs.append("missing expected entries: %s" % ", ".join(missing))
    if extra:
        errs.append("unexpected entries: %s" % ", ".join(extra))
    for name in sorted(set(exp) & set(byname)):
        if tuple(byname[name]) != tuple(exp[name]):
            errs.append("row %s = %r, expected %r"
                        % (name, tuple(byname[name]), tuple(exp[name])))
    return errs


# --------------------------------------------------------------------------- running

def run_tool(tool, root, out, scratch, timeout):
    cmd = [sys.executable, "-B", tool, "--fleet-root", root, "--out", out]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=scratch,
                          timeout=timeout)


def _tail(text, n=400):
    text = (text or "").strip()
    return text[-n:] if len(text) > n else text


def _read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="surrogateescape") as fh:
            return fh.read()
    except FileNotFoundError:
        return None


def stub_source(rows):
    """Control stub: header-only (rows=[]) or fixed rows, sha/head computed honestly."""
    return (
        "# control stub generated by r52-fleet-root-census-fixture.py\n"
        "import hashlib, json, os, subprocess, sys\n"
        "ROWS = json.loads({rows!r})\n"
        "argv = sys.argv[1:]\n"
        "root = argv[argv.index('--fleet-root') + 1]\n"
        "out = argv[argv.index('--out') + 1]\n"
        "env = dict(os.environ)\n"
        "env['GIT_OPTIONAL_LOCKS'] = '0'\n"
        "head = subprocess.run(['git', '-C', root, 'rev-parse', 'HEAD'],\n"
        "                      capture_output=True, text=True, env=env).stdout.strip()\n"
        "sha = hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest()\n"
        "cnt = {{c: sum(1 for r in ROWS if r[4] == c)\n"
        "        for c in ('tracked', 'ignored', 'untracked-stray', 'symlink')}}\n"
        "lines = ['# souji round-52 fleet-root census (read-only; dry-run)',\n"
        "         '# SCOPE=top-level entries of the fleet root, dotfiles included, "
        ".git excluded',\n"
        "         '# TOOL_SHA256=' + sha,\n"
        "         '# FLEET_HEAD=' + head,\n"
        "         '# ENTRIES=' + str(len(ROWS)),\n"
        "         '# COUNT tracked=' + str(cnt['tracked']),\n"
        "         '# COUNT ignored=' + str(cnt['ignored']),\n"
        "         '# COUNT untracked-stray=' + str(cnt['untracked-stray']),\n"
        "         '# COUNT symlink=' + str(cnt['symlink']),\n"
        "         'name\\tkind\\ttracked\\tignored\\tclass\\tdisposition']\n"
        "lines += ['\\t'.join(r) for r in ROWS]\n"
        "open(out, 'w').write('\\n'.join(lines) + '\\n')\n"
    ).format(rows=json.dumps([list(r) for r in rows]))


# --------------------------------------------------------------------------- suite

def suite(tool, scratch, timeout):
    """Returns list of {slot, label, ok, reason}; ok means 'behaved as required'."""
    results = []

    def emit(slot, label, ok, reason):
        results.append({"slot": slot, "label": label, "ok": ok, "reason": reason})

    caps = tempfile.mkdtemp(dir=scratch, prefix="caps-")

    # ---- (a)/(b) honest root, one run
    try:
        D = build_honest_root(scratch)
    except Exception as exc:                                  # noqa: BLE001
        emit("honest", "(pre)", False, "fixture guard: %s" % exc)
        return results
    cap_a = os.path.join(caps, "honest.tsv")
    proc = run_tool(tool, D, cap_a, scratch, timeout)
    if proc.returncode != 0:
        reason = ("tool exit=%d stderr=%r" % (proc.returncode,
                                              _tail(proc.stderr) or _tail(proc.stdout)))
        emit("honest", "(a)", False, reason)
        emit("honest", "(b)", False, reason)
        parsed = None
    else:
        text = _read(cap_a)
        if text is None:
            emit("honest", "(a)", False, "no capture written at --out %s" % cap_a)
            emit("honest", "(b)", False, "no capture written at --out %s" % cap_a)
            parsed = None
        else:
            parsed = parse_capture(text)
    if parsed is not None:
        errs_a = check_table(parsed, EXPECTED)
        emit("honest", "(a)", not errs_a,
             "entries/classes/dispositions match the frozen rule (%d rows)"
             % len(parsed["rows"]) if not errs_a else "; ".join(errs_a[:4]))
        errs_b = check_header(parsed, tool, D)
        emit("honest", "(b)", not errs_b,
             "ENTRIES=%s COUNT=%r TOOL_SHA256/FLEET_HEAD ok (%d rows)"
             % (parsed["hdr"].get("ENTRIES"), parsed["counts"], len(parsed["rows"]))
             if not errs_b else "; ".join(errs_b[:4]))

    # ---- (c) refusals must exit 2
    # (c1) --fleet-root is a symlink
    c1_root = build_min_root(scratch, prefix="c1-real-")
    c1_link = os.path.join(caps, "rootlink")
    os.symlink(c1_root, c1_link)
    c1_out = os.path.join(caps, "c1.tsv")
    p = run_tool(tool, c1_link, c1_out, scratch, timeout)
    ok = p.returncode == 2 and not os.path.lexists(c1_out)
    emit("honest", "(c1) refusal --fleet-root symlink", ok,
         "exit=%d (expected 2), out-absent=%s"
         % (p.returncode, not os.path.lexists(c1_out)))

    # (c2) --out already exists (must refuse, must not clobber)
    c2_root = build_min_root(scratch, prefix="c2-")
    c2_out = os.path.join(caps, "c2.tsv")
    _write(c2_out, "sentinel-unchanged\n")
    p = run_tool(tool, c2_root, c2_out, scratch, timeout)
    after = _read(c2_out)
    ok = (p.returncode == 2 and after == "sentinel-unchanged\n")
    emit("honest", "(c2) refusal --out exists", ok,
         "exit=%d (expected 2), out-preserved=%s"
         % (p.returncode, after == "sentinel-unchanged\n"))

    # (c3) an entry name containing a tab (os.mkdir on Linux)
    c3_root = build_min_root(scratch, prefix="c3-")
    os.mkdir(os.path.join(c3_root, "bad\tname"))
    c3_out = os.path.join(caps, "c3.tsv")
    p = run_tool(tool, c3_root, c3_out, scratch, timeout)
    ok = p.returncode == 2 and not os.path.lexists(c3_out)
    emit("honest", "(c3) refusal entry name with tab", ok,
         "exit=%d (expected 2), out-absent=%s%s"
         % (p.returncode, not os.path.lexists(c3_out),
            "" if ok else " stderr=%r" % _tail(p.stderr)))

    # ---- (d) read-only
    try:
        Dd = build_honest_root(scratch, prefix="readonly-")
        s_before = _git(Dd, "status", "--porcelain").stdout
        snap_before = snapshot(Dd)
        cap_d = os.path.join(caps, "readonly.tsv")
        p = run_tool(tool, Dd, cap_d, scratch, timeout)
        snap_after = snapshot(Dd)
        s_after = _git(Dd, "status", "--porcelain").stdout
        errs = []
        if p.returncode != 0:
            errs.append("tool exit=%d" % p.returncode)
        if not os.path.isfile(cap_d):
            errs.append("no capture written")
        if snap_before != snap_after:
            errs.append("synthetic root changed: %s"
                        % describe_snapshot_diff(snap_before, snap_after))
        if s_before != s_after:
            errs.append("git status --porcelain changed: %r -> %r"
                        % (_tail(s_before, 120), _tail(s_after, 120)))
        emit("honest", "(d) read-only", not errs,
             "root snapshot and porcelain identical over one run (%d entries)"
             % len(snap_before) if not errs else "; ".join(errs[:3]))
    except Exception as exc:                                  # noqa: BLE001
        emit("honest", "(d) read-only", False, "fixture guard: %s" % exc)

    # ---- (e) controls must fail, for the named reason
    # (e1) header with ENTRIES=0 and no rows must fail the (b) checks
    e1_tool = os.path.join(caps, "stub-entries0.py")
    _write(e1_tool, stub_source([]))
    e1_out = os.path.join(caps, "e1.tsv")
    p = run_tool(e1_tool, D, e1_out, scratch, timeout)
    text = _read(e1_out)
    ok = False
    reason = "stub produced no capture"
    if p.returncode == 0 and text is not None:
        errs = check_header(parse_capture(text), e1_tool, D)
        joined = "; ".join(errs)
        ok = bool(errs) and "ENTRIES" in joined
        reason = ("rejected by (b): %s" % "; ".join(errs[:3])) if ok else (
            "NOT rejected for ENTRIES: %r" % joined if errs
            else "control capture was accepted by the (b) checks")
    emit("control", "(e1) header-only ENTRIES=0", ok, reason)

    # (e2) a row whose class contradicts the rule must fail
    mutated = [list(r) for r in EXPECTED]
    for row in mutated:
        if row[0] == "stray.txt":
            row[4] = "tracked"          # kind=file tracked=no ignored=no -> untracked-stray
            row[5] = "none"
    e2_tool = os.path.join(caps, "stub-classflip.py")
    _write(e2_tool, stub_source(mutated))
    e2_out = os.path.join(caps, "e2.tsv")
    p = run_tool(e2_tool, D, e2_out, scratch, timeout)
    text = _read(e2_out)
    ok = False
    reason = "stub produced no capture"
    if p.returncode == 0 and text is not None:
        errs = check_table(parse_capture(text), EXPECTED)
        joined = "; ".join(errs)
        ok = bool(errs) and "class" in joined
        reason = ("rejected by (a): %s" % "; ".join(errs[:3])) if ok else (
            "NOT rejected for class: %r" % joined if errs
            else "class-contradicting capture was accepted")
    emit("control", "(e2) class contradicts rule", ok, reason)

    return results


# --------------------------------------------------------------------------- selftest

REF_SRC = r'''#!/usr/bin/env python3
"""Fixture selftest reference topology for the r52 fleet-root census (never landed)."""
import argparse
import hashlib
import os
import stat
import subprocess
import sys

COLS = "name\tkind\ttracked\tignored\tclass\tdisposition"


def die(msg):
    sys.stderr.write("ref: %s\n" % msg)
    raise SystemExit(2)


def git(root, *args):
    env = dict(os.environ)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    return subprocess.run(["git", "-C", root] + list(args),
                          capture_output=True, text=True, env=env)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fleet-root", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    root, out = a.fleet_root, a.out
    if os.path.islink(root):
        die("--fleet-root is a symlink")
    if not os.path.isdir(root):
        die("--fleet-root is not a directory")
    if os.path.lexists(out):
        die("--out already exists")
    root = os.path.abspath(root)
    names = [n for n in sorted(os.listdir(root)) if n != ".git"]
    for n in names:
        if "\t" in n or "\n" in n:
            die("entry name contains a tab or newline")
    ls = git(root, "ls-files", "-z")
    if ls.returncode != 0:
        die("git ls-files failed: %s" % ls.stderr.strip())
    tracked = set()
    for p in ls.stdout.split("\0"):
        if p:
            tracked.add(p.split("/")[0])
    ls_i = git(root, "ls-files", "-z", "-o", "-i", "--exclude-standard", "--directory")
    if ls_i.returncode != 0:
        die("git ls-files -i failed: %s" % ls_i.stderr.strip())
    ignored = set()
    for p in ls_i.stdout.split("\0"):
        if p:
            ignored.add(p.rstrip("/").split("/")[0])
    headp = git(root, "rev-parse", "HEAD")
    head = headp.stdout.strip() if headp.returncode == 0 else "0" * 40
    rows = []
    for n in names:
        st = os.lstat(os.path.join(root, n))
        mode = st.st_mode
        kind = ("symlink" if stat.S_ISLNK(mode)
                else "dir" if stat.S_ISDIR(mode)
                else "file" if stat.S_ISREG(mode)
                else "other")
        tr = "yes" if n in tracked else "no"
        ig = "yes" if n in ignored else "no"
        cls = ("symlink" if kind == "symlink"
               else "tracked" if tr == "yes"
               else "ignored" if ig == "yes"
               else "untracked-stray")
        disp = "report-only" if cls == "untracked-stray" else "none"
        rows.append([n, kind, tr, ig, cls, disp])
    counts = {c: sum(1 for r in rows if r[4] == c)
              for c in ("tracked", "ignored", "untracked-stray", "symlink")}
    sha = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()
    lines = ["# souji round-52 fleet-root census (read-only; dry-run)",
             "# SCOPE=top-level entries of the fleet root, dotfiles included, .git excluded",
             "# TOOL_SHA256=" + sha,
             "# FLEET_HEAD=" + head,
             "# ENTRIES=" + str(len(rows)),
             "# COUNT tracked=" + str(counts["tracked"]),
             "# COUNT ignored=" + str(counts["ignored"]),
             "# COUNT untracked-stray=" + str(counts["untracked-stray"]),
             "# COUNT symlink=" + str(counts["symlink"]),
             COLS]
    lines += ["\t".join(r) for r in rows]
    with open(out, "x", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
'''


def selftest(scratch, timeout):
    ref = os.path.join(scratch, "selftest-ref-tool.py")
    _write(ref, REF_SRC)
    results = suite(ref, scratch, timeout)
    all_ok = True
    for r in results:
        print("%s  %-40s %s" % ("PASS" if r["ok"] else "FAIL", r["label"], r["reason"]))
        all_ok = all_ok and r["ok"]
    honest = [r for r in results if r["slot"] == "honest"]
    control = [r for r in results if r["slot"] == "control"]
    print("SUMMARY selftest honest_passed=%d/%d controls_failed=%d/%d selftest=%s"
          % (sum(1 for r in honest if r["ok"]), len(honest),
             sum(1 for r in control if r["ok"]), len(control),
             "PASS" if all_ok else "FAIL"))
    return 0 if all_ok else 1


# --------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tool", default=CANDIDATE_DEFAULT,
                    help="candidate census tool (default: %(default)s)")
    ap.add_argument("--scratch", default=SCRATCH_DEFAULT,
                    help="scratch root for fixtures and captures (default: %(default)s)")
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--selftest", action="store_true",
                    help="anti-vacuity check: generate an honest reference tool in "
                         "scratch and require the whole suite to pass it")
    a = ap.parse_args()

    scratch = os.path.abspath(a.scratch)
    os.makedirs(scratch, exist_ok=True)
    if a.selftest:
        return selftest(scratch, a.timeout)

    tool = os.path.abspath(a.tool)
    if not os.path.isfile(tool):
        print("FAIL  (pre) tool not found: %s" % tool)
        print("SUMMARY cases=0 honest_passed=0/6 controls_failed=0/2 exit=1")
        return 1

    results = suite(tool, scratch, a.timeout)
    for r in results:
        print("%s  %-42s %s" % ("PASS" if r["ok"] else "FAIL", r["label"], r["reason"]))
    honest = [r for r in results if r["slot"] == "honest"]
    control = [r for r in results if r["slot"] == "control"]
    passed = sum(1 for r in honest if r["ok"])
    failed_controls = sum(1 for r in control if r["ok"])
    ok = all(r["ok"] for r in results) and len(honest) == 6 and len(control) == 2
    print("SUMMARY cases=%d honest_passed=%d/%d controls_failed=%d/%d exit=%d"
          % (len(results), passed, len(honest), failed_controls, len(control),
             0 if ok else 1))
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.TimeoutExpired as exc:
        print("FAIL  (pre) timeout: %s" % exc)
        sys.exit(1)
