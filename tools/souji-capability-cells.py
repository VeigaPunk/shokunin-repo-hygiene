#!/usr/bin/env python3
"""souji-capability-cells.py — round-31 C1 calibration counter (frozen at the r31 preregistration).

Reads the SCORECARD capability CELLS themselves (round 30 read only its append-only R30-CORRECTION
lines, which leave every cell stating its old literal). For each enumerated count literal it asks: does
the effective statement name an observable that shows this literal at a full 40-hex revision REV?

Enumerated set: `census/round-31/c1-cells.tsv` read at --list-rev (never at REV): item id, base line,
base literal, record round set, base command (rule in that file's header). 41 items at the r31 base.

Effective statement of an item at REV: the LAST row, in the part of SCORECARD.md after the --base bytes,
of the form
    | <id> | SCORECARD.md:<line> | <literal> | run: <argv> | <note> |
    | <id> | SCORECARD.md:<line> | <literal> | record: <path> | <note> |
(backticks around literal, argv or path are stripped; <line> must equal the item's base line); without
such a row, the base cell: the base literal with its base command as a run binding, or UNBOUND when
the cell names no command beside the count.

A statement MATCHES iff
  run     argv = python3 [-B] <script> [args] or bash <script> [args]; <script> is a blob under tools/ or
          tests/fixtures/ at both --base and REV; for a superseding row the script's basename stem occurs
          on the item's base SCORECARD line; no -c/-h/--help/--version token; the literal string does not
          occur in the joined argv; the literal carries at least two integers. The argv runs (no shell) in
          a private `git clone --no-local` at REV (origin removed; checkout -f + clean -fdxq before every
          run; TMPDIR a fresh dir under --scratch). S = last digit-bearing line of normalized stdout
          (stderr only when stdout has none; tmp paths -> <TMP>, 12+ hex -> <HEX>, `N.Ns` -> <DUR>,
          whitespace collapsed). MATCH iff exit 0 and the literal occurs in S at digit boundaries.
  record  <path> (no `:line` suffix) is under census/round-<K>/ with K in the item's round set and has
          no `waves` or `transcripts` component; it is the same blob at --base and REV; the literal's
          integers, as a multiset, equal the base literal's integers (`3/7` may be restated `cases=7
          pass=3`, never with other numbers); MATCH iff the literal occurs in the
          blob's bytes at digit boundaries.
A base-cell run binding uses the base literal and command unchanged (no stem rule). Anything else is a
mismatch: UNBOUND (no binding), RUN-MISMATCH, RECORD-MISMATCH or BAD-ROW (a superseding row that breaks a
rule above). If SCORECARD.md at REV does not begin with its --base bytes, every item is a mismatch.

AMENDMENT A2 (round 31, after wave-1 SwarmCritic31 bound a `15/15` cell to the non-count text `15-config": LANE /
"tests/fixtures/r15` (two 15s); stricter-only; the v1 bytes committed at the preregistration
1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 still run and must also meet the target): a superseding row's literal, in
both branches, must have a count shape — `[word=]N/M`, or two `word=N` fields separated by whitespace or the two
bytes backslash-t (`cases=8 pass=4`, `total=32<TAB>pass=32`, `pass=61\tfail=0`); anything else is BAD-ROW(shape).

AMENDMENT A4 (round 31, after wave-1 SwarmCritic28 reached 41/41 MATCH with integer pairs in unrelated files, a
record row hiding the row's own command, an in-round fixture edit, and one sentence bound to several cells;
stricter-only; v1 and A2 must also meet the target):
  (a) an item whose cell names a base command may be superseded only by a `run:` row (a record row would hide that
      the cell's own command now prints something else): BAD-ROW(cmd-item-record);
  (b) a record path may not have a `sources` component or end in .py .sh .html .htm .raw (code, controls and web
      captures are not measurement records): BAD-ROW(record-kind);
  (c) every run binding (base cell or superseding row) executes its script from the --base blob, written over the
      REV copy in the private clone, so an in-round edit to the script cannot print the literal;
  (d) no two items may bind the same (record path, literal) pair: BAD-ROW(shared-occurrence) for every such item.

Output: one ITEM line per item, then
    SUMMARY items=<n> bound_run=<a> bound_record=<b> unbound=<u> mismatches=<m> rev=<REV>
Exit 0 iff mismatches=0; 1 otherwise; 2 could-not-evaluate. Read-only on --root; one private clone per
invocation under --scratch (mkdtemp), removed on exit.
"""
import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

FULL = re.compile(r"[0-9a-f]{40}")
GITC = ["-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null"]
ROW = re.compile(
    r"^\|\s*(L\d{2})\s*\|\s*SCORECARD\.md:(\d+)\s*\|\s*([^|]+?)\s*\|\s*(run|record):\s*([^|]+?)\s*\|"
)
BANNED = ("-c", "-h", "--help", "--version")
COUNT_FORM = re.compile(r"^(?:[A-Za-z_]+=)?\d+/\d+$|^[A-Za-z_]+=\d+(?:\s+|\\t)[A-Za-z_]+=\d+$")


def cne(msg):
    print(f"COULD-NOT-EVALUATE {msg}")
    sys.exit(2)


def git(root, *a, check=True):
    p = subprocess.run(["git", "-C", root, *GITC, *a], capture_output=True)
    if check and p.returncode:
        cne("git " + " ".join(a) + ": " + p.stderr.decode("utf-8", "replace").strip())
    return p


def blob_oid(root, rev, path):
    p = subprocess.run(["git", "-C", root, "rev-parse", "-q", "--verify", f"{rev}:{path}"], capture_output=True)
    if p.returncode:
        return None
    oid = p.stdout.decode().strip()
    t = subprocess.run(["git", "-C", root, "cat-file", "-t", oid], capture_output=True)
    return oid if t.stdout.decode().strip() == "blob" else None


def blob(root, rev, path):
    p = subprocess.run(["git", "-C", root, "cat-file", "blob", f"{rev}:{path}"], capture_output=True)
    return None if p.returncode else p.stdout.decode("utf-8", "replace")


def normalize(text, scratch):
    text = text.replace(scratch, "<TMP>")
    text = re.sub(r"(?:/var)?/tmp/[^\s'\"`:,)]+", "<TMP>", text)
    text = re.sub(r"/fast/scratch/[^\s'\"`:,)]+", "<TMP>", text)
    text = re.sub(r"\b[0-9a-f]{12,}\b", "<HEX>", text)
    text = re.sub(r"\b\d+\.\d+s\b", "<DUR>", text)
    return text


def summary_line(text):
    for line in reversed(text.splitlines()):
        s = " ".join(line.split())
        if s and re.search(r"\d", s):
            return s
    return "NONE"


def at_bounds(lit, text):
    return re.search(r"(?<!\d)" + re.escape(lit) + r"(?!\d)", text) is not None


def ints(s):
    return re.findall(r"\d+", s)


def script_of(argv):
    """Return the script path of an allowed argv shape, else None."""
    if not argv:
        return None
    if argv[0] == "python3":
        rest = argv[1:]
        if rest[:1] == ["-B"]:
            rest = rest[1:]
    elif argv[0] == "bash":
        rest = argv[1:]
    else:
        return None
    if not rest or rest[0].startswith("-"):
        return None
    return rest[0]


def main():
    ap = argparse.ArgumentParser(prog="souji-capability-cells.py")
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--base", required=True, help="append-only base revision (frozen: the r31 lane base)")
    ap.add_argument("--list-rev", required=True, help="preregistration commit holding census/round-31/c1-cells.tsv")
    ap.add_argument("--scratch", default=os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku") + "/souji-r31/c1-counter")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--only", default="", help="comma-separated item ids (diagnostic; SUMMARY then marks partial=1)")
    a = ap.parse_args()
    for name in ("rev", "base", "list_rev"):
        if not FULL.fullmatch(getattr(a, name)):
            cne(f"--{name.replace('_', '-')} must be a full 40-hex revision")
        git(a.root, "cat-file", "-e", getattr(a, name) + "^{commit}")
    root = os.path.abspath(a.root)
    tsv = blob(root, a.list_rev, "census/round-31/c1-cells.tsv")
    if tsv is None:
        cne("census/round-31/c1-cells.tsv absent at --list-rev")
    items = []
    for ln in tsv.splitlines():
        if not ln.strip() or ln.startswith("#") or ln.startswith("id\t"):
            continue
        f = ln.split("\t")
        if len(f) != 5:
            cne(f"malformed c1-cells line: {ln!r}")
        items.append((f[0], int(f[1]), f[2], set(int(x) for x in f[3].split(",") if x), f[4]))
    only = set(x for x in a.only.split(",") if x)

    sc_base, sc_rev = blob(root, a.base, "SCORECARD.md"), blob(root, a.rev, "SCORECARD.md")
    if sc_base is None or sc_rev is None:
        cne("SCORECARD.md missing at --base or --rev")
    base_lines = sc_base.splitlines()
    append_ok = sc_rev.startswith(sc_base)
    tail = sc_rev[len(sc_base):] if append_ok else ""
    sup = {}
    for ln in tail.splitlines():
        m = ROW.match(ln)
        if m:
            sup[m.group(1)] = (int(m.group(2)), m.group(3).strip("` "), m.group(4), m.group(5).strip("` "))

    occ = {}
    for iid_, (_l, lit_, kind_, tgt_) in sup.items():
        if kind_ == "record":
            occ.setdefault((tgt_, lit_), []).append(iid_)
    shared = {i for v in occ.values() if len(v) > 1 for i in v}  # A4(d)
    os.makedirs(a.scratch, exist_ok=True)
    work = tempfile.mkdtemp(prefix="c1.", dir=a.scratch)
    cache = {}
    counts = {"run": 0, "record": 0, "unbound": 0, "mm": 0}
    try:
        clone = os.path.join(work, "c")
        p = subprocess.run(["git", "clone", "-q", "--no-local", "--no-checkout", root, clone], capture_output=True)
        if p.returncode:
            cne("clone failed: " + p.stderr.decode("utf-8", "replace").strip())
        git(clone, "remote", "remove", "origin")
        if git(clone, "rev-parse", "--show-toplevel").stdout.decode().strip() != clone:
            cne("clone toplevel mismatch")

        def run(argv):
            key = tuple(argv)
            if key in cache:
                return cache[key]
            git(clone, "checkout", "-qf", "--detach", a.rev)
            git(clone, "clean", "-fdxq")
            sp = script_of(argv)
            if sp is not None:  # A4(c): run the script's --base blob
                b = subprocess.run(["git", "-C", root, "cat-file", "blob", f"{a.base}:{sp}"], capture_output=True)
                if b.returncode == 0:
                    with open(os.path.join(clone, sp), "wb") as fh:
                        fh.write(b.stdout)
            tmp = tempfile.mkdtemp(prefix="t.", dir=work)
            env = dict(os.environ, TMPDIR=tmp, GIT_CONFIG_NOSYSTEM="1")
            env.pop("GIT_DIR", None)
            env.pop("GIT_WORK_TREE", None)
            try:
                q = subprocess.run(argv, cwd=clone, env=env, capture_output=True, timeout=a.timeout)
                rc, out, err = q.returncode, q.stdout.decode("utf-8", "replace"), q.stderr.decode("utf-8", "replace")
            except subprocess.TimeoutExpired as e:
                rc, out, err = 124, (e.stdout or b"").decode("utf-8", "replace"), (e.stderr or b"").decode("utf-8", "replace")
            except OSError as e:
                rc, out, err = 127, "", f"exec error {e.errno}"
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
            s = summary_line(normalize(out, work))
            if s == "NONE":
                s = summary_line(normalize(err, work))
            cache[key] = (rc, s)
            return rc, s

        for iid, line, lit0, rounds, basecmd in items:
            if only and iid not in only:
                continue
            row_text = base_lines[line - 1] if 0 < line <= len(base_lines) else ""
            if not append_ok:
                verdict, kind, lit, detail = "MISMATCH(append-only-violated)", "-", lit0, ""
            elif iid in sup:
                sline, lit, kind, target = sup[iid]
                verdict, detail = "MATCH", target
                if sline != line or len(ints(lit)) < 2:
                    verdict = "BAD-ROW(line-or-literal)"
                elif not COUNT_FORM.match(lit):
                    verdict = "BAD-ROW(shape)"  # A2
                elif iid in shared:
                    verdict = "BAD-ROW(shared-occurrence)"  # A4(d)
                elif kind == "run":
                    try:
                        argv = shlex.split(target)
                    except ValueError:
                        argv = []
                    script = script_of(argv)
                    stem = os.path.splitext(os.path.basename(script or ""))[0]
                    if (
                        script is None
                        or not script.startswith(("tools/", "tests/fixtures/"))
                        or blob_oid(root, a.base, script) is None
                        or blob_oid(root, a.rev, script) is None
                        or not stem
                        or stem not in row_text
                        or any(t in BANNED for t in argv)
                        or lit in " ".join(argv)
                    ):
                        verdict = "BAD-ROW(run-shape)"
                    else:
                        rc, s = run(argv)
                        detail = f"{target} rc={rc} observed={s}"
                        if not (rc == 0 and at_bounds(lit, s)):
                            verdict = "RUN-MISMATCH"
                elif basecmd:
                    verdict = "BAD-ROW(cmd-item-record)"  # A4(a)
                elif "sources" in target.split("/") or target.lower().endswith((".py", ".sh", ".html", ".htm", ".raw")):
                    verdict = "BAD-ROW(record-kind)"  # A4(b)
                else:
                    path = target
                    parts = path.split("/")
                    m = re.match(r"^census/round-(\d+)/", path)
                    if (
                        ":" in path
                        or not m
                        or int(m.group(1)) not in rounds
                        or "waves" in parts
                        or "transcripts" in parts
                        or sorted(ints(lit)) != sorted(ints(lit0))
                    ):
                        verdict = "BAD-ROW(record-shape)"
                    else:
                        ob, orv = blob_oid(root, a.base, path), blob_oid(root, a.rev, path)
                        if ob is None or ob != orv:
                            verdict = "BAD-ROW(record-not-unchanged-base-blob)"
                        elif not at_bounds(lit, blob(root, a.rev, path)):
                            verdict = "RECORD-MISMATCH"
            elif basecmd:
                kind, lit = "run", lit0
                rc, s = run(shlex.split(basecmd))
                detail = f"{basecmd} rc={rc} observed={s}"
                verdict = "MATCH" if rc == 0 and at_bounds(lit, s) else "RUN-MISMATCH"
            else:
                kind, lit, detail, verdict = "-", lit0, "", "UNBOUND"
            if verdict == "MATCH":
                counts[kind] += 1
            else:
                counts["mm"] += 1
                if verdict == "UNBOUND":
                    counts["unbound"] += 1
            src = "superseded" if iid in sup else "base-cell"
            print(f"ITEM\t{iid}\tSCORECARD.md:{line}\tliteral={lit}\t{src}\tbinding={kind}\t{verdict}\t{detail}")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    n = len(items) if not only else len(only)
    partial = " partial=1" if only else ""
    print(
        f"SUMMARY items={n} bound_run={counts['run']} bound_record={counts['record']} "
        f"unbound={counts['unbound']} mismatches={counts['mm']}{partial} rev={a.rev}"
    )
    return 0 if counts["mm"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
