#!/usr/bin/env python3
"""r32 C1 calibration counter (frozen at the r32 preregistration): capability-cell count integers outside the
r31 notation, plus r31's one unbound item L29.

Enumerated set: `census/round-32/c1-items.tsv`, read at --list-rev (never at REV); written by
`census/round-32/c1-enumerate.py` at the r32 base (rule in that script's docstring): 43 items N01-N43 and L29.
Columns: id, line, integer(s), units, rounds, context.

Binding rows: in the part of SCORECARD.md after the --base bytes, a row
    | <id> | SCORECARD.md:<line> | <literal> | <kind>: <payload> | <reason> |
with <line> equal to the item's line (backticks around literal and payload are stripped). An item with no such
row is UNBOUND; an item with two or more such rows is BAD-ROW(duplicate) (no last-row-wins). If SCORECARD.md
at REV does not begin with its --base bytes, every item is MISMATCH(append-only-violated).

Literal rules (every kind except withdrawn): the literal holds exactly as many integers as the item; it
contains one of the item's units as a case-insensitive substring (unitless items: no unit rule), else
BAD-ROW(literal).

Kinds:
  run       <argv> = python3 [-B] <script> [args] or bash <script> [args]; <script> is a blob under tools/ or
            tests/fixtures/ at --base and REV whose basename stem occurs on the item's base line; no
            -c/-h/--help/--version token; the literal does not occur in the joined argv. The script is taken
            from the --base blob and run (no shell) in a private `git clone --no-local` at REV (origin removed;
            checkout -f + clean -fdxq before every run; TMPDIR a fresh dir under --scratch). S = last
            digit-bearing line of normalized stdout (stderr when stdout has none). MATCH iff exit 0 and the
            literal occurs in S at digit boundaries. A run literal may restate the integer (a corrected count).
  record    <path>:<N> (1-based line). <path> is under census/round-<K>/ with K in the item's rounds, has no
            `waves`, `transcripts` or `sources` component, does not end in .py .sh .html .htm .raw, and is the
            same blob at --base and REV. The literal's integers, as a multiset, equal the item's. MATCH iff line
            N of the blob contains every literal integer at digit boundaries and one of the item's units
            (case-insensitive). A unitless item may not use record: BAD-ROW(unitless-record).
  field     <path> <key>=<int> [<key>=<int> ...]. <path> obeys the record path rules and ends in .json; each
            <key> is a dotted path (dict keys; list indices as integers) resolving to a JSON integer (not a
            bool) equal to its stated <int>; the stated integers, as a multiset, equal the item's and the
            literal's; one of the item's units occurs (case-insensitive) in the path's basename or in a key.
  withdrawn <reason of at least 8 words>: the cell's integer is withdrawn as evidence (no observable shows it);
            counted as `withdrawn`, not as a match or a mismatch.
No two items may bind the same (path, line) record occurrence or the same (path, key) field:
BAD-ROW(shared-occurrence) for every such item.

Output: one ITEM line per item, then
    SUMMARY items=<n> bound_run=<a> bound_record=<b> bound_field=<f> withdrawn=<w> unbound=<u> mismatches=<m> rev=<REV>
mismatches counts every item that is neither MATCH nor withdrawn (UNBOUND included).
Frozen target (preregistration): `unbound=0 mismatches=0` and `withdrawn<=8` (one fifth of 44, rounded down)
at the C1 landing commit and at the tip. Exit 0 iff the target holds; 1 otherwise; 2 could-not-evaluate.
Read-only on --root; one private clone per invocation under --scratch (mkdtemp), removed on exit.
"""
import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

FULL = re.compile(r"[0-9a-f]{40}")
GITC = ["-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null"]
ROW = re.compile(r"^\|\s*((?:N|L)\d{2})\s*\|\s*SCORECARD\.md:(\d+)\s*\|\s*([^|]+?)\s*\|\s*(run|record|field|withdrawn):\s*([^|]*?)\s*\|")
BANNED = ("-c", "-h", "--help", "--version")
WITHDRAW_MAX = 8


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


def record_path_ok(path, rounds):
    parts = path.split("/")
    m = re.match(r"^census/round-(\d+)/", path)
    return bool(
        m and int(m.group(1)) in rounds and not {"waves", "transcripts", "sources"} & set(parts)
        and not path.lower().endswith((".py", ".sh", ".html", ".htm", ".raw")) and ".." not in parts
    )


def resolve(doc, key):
    cur = doc
    for k in key.split("."):
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        elif isinstance(cur, list) and re.fullmatch(r"\d+", k) and int(k) < len(cur):
            cur = cur[int(k)]
        else:
            return None
    return cur if isinstance(cur, int) and not isinstance(cur, bool) else None


def main():
    ap = argparse.ArgumentParser(prog="c1-counter.py")
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--base", required=True, help="append-only base revision (frozen: the r32 lane base)")
    ap.add_argument("--list-rev", required=True, help="preregistration commit holding census/round-32/c1-items.tsv")
    ap.add_argument("--scratch", default=os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku") + "/souji-r32/c1-counter")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--only", default="", help="comma-separated item ids (diagnostic; SUMMARY then marks partial=1)")
    a = ap.parse_args()
    for name in ("rev", "base", "list_rev"):
        if not FULL.fullmatch(getattr(a, name)):
            cne(f"--{name.replace('_', '-')} must be a full 40-hex revision")
        git(a.root, "cat-file", "-e", getattr(a, name) + "^{commit}")
    root = os.path.abspath(a.root)
    tsv = blob(root, a.list_rev, "census/round-32/c1-items.tsv")
    if tsv is None:
        cne("census/round-32/c1-items.tsv absent at --list-rev")
    items = []
    for ln in tsv.splitlines():
        if not ln.strip() or ln.startswith("#") or ln.startswith("id\t"):
            continue
        f = ln.split("\t")
        if len(f) != 6:
            cne(f"malformed c1-items line: {ln!r}")
        items.append((f[0], int(f[1]), sorted(ints(f[2])), [u for u in f[3].split(",") if u],
                      set(int(x) for x in f[4].split(",") if x)))
    only = set(x for x in a.only.split(",") if x)

    sc_base, sc_rev = blob(root, a.base, "SCORECARD.md"), blob(root, a.rev, "SCORECARD.md")
    if sc_base is None or sc_rev is None:
        cne("SCORECARD.md missing at --base or --rev")
    base_lines = sc_base.splitlines()
    append_ok = sc_rev.startswith(sc_base)
    tail = sc_rev[len(sc_base):] if append_ok else ""
    rows = {}
    for ln in tail.splitlines():
        m = ROW.match(ln)
        if m:
            rows.setdefault(m.group(1), []).append((int(m.group(2)), m.group(3).strip("` "), m.group(4), m.group(5).strip("` ")))
    line_of = {i[0]: i[1] for i in items}
    occ = {}
    for iid, rs in rows.items():
        rs = [r for r in rs if r[0] == line_of.get(iid)]
        rows[iid] = rs
        if len(rs) != 1:
            continue
        _l, lit, kind, tgt = rs[0]
        if kind == "record":
            occ.setdefault(("record", tgt), []).append(iid)
        elif kind == "field":
            parts = tgt.split()
            for kv in parts[1:]:
                occ.setdefault(("field", parts[0], kv.split("=")[0]), []).append(iid)
    shared = {i for v in occ.values() if len(v) > 1 for i in v}
    os.makedirs(a.scratch, exist_ok=True)
    work = tempfile.mkdtemp(prefix="c1.", dir=a.scratch)
    cache = {}
    counts = {"run": 0, "record": 0, "field": 0, "withdrawn": 0, "unbound": 0, "mm": 0}
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

        for iid, line, iints, units, rounds in items:
            if only and iid not in only:
                continue
            row_text = base_lines[line - 1] if 0 < line <= len(base_lines) else ""
            rs = rows.get(iid, [])
            kind, lit, detail = "-", " ".join(iints), ""
            has_unit = (lambda s: any(u.lower() in s.lower() for u in units)) if units else (lambda s: True)
            if not append_ok:
                verdict = "MISMATCH(append-only-violated)"
            elif not rs:
                verdict = "UNBOUND"
            elif len(rs) > 1:
                verdict = "BAD-ROW(duplicate)"
            else:
                _l, lit, kind, target = rs[0]
                verdict, detail = "MATCH", target
                if kind == "withdrawn":
                    verdict = "WITHDRAWN" if len(target.split()) >= 8 else "BAD-ROW(withdrawn-reason)"
                elif len(ints(lit)) != len(iints) or not has_unit(lit):
                    verdict = "BAD-ROW(literal)"
                elif iid in shared:
                    verdict = "BAD-ROW(shared-occurrence)"
                elif kind == "run":
                    try:
                        argv = shlex.split(target)
                    except ValueError:
                        argv = []
                    script = script_of(argv)
                    stem = os.path.splitext(os.path.basename(script or ""))[0]
                    if (script is None or not script.startswith(("tools/", "tests/fixtures/"))
                            or blob_oid(root, a.base, script) is None or blob_oid(root, a.rev, script) is None
                            or not stem or stem not in row_text or any(t in BANNED for t in argv)
                            or lit in " ".join(argv)):
                        verdict = "BAD-ROW(run-shape)"
                    else:
                        rc, s = run(argv)
                        detail = f"{target} rc={rc} observed={s}"
                        if not (rc == 0 and at_bounds(lit, s)):
                            verdict = "RUN-MISMATCH"
                elif kind == "record":
                    m = re.fullmatch(r"(.+):(\d+)", target)
                    if not units:
                        verdict = "BAD-ROW(unitless-record)"
                    elif not m or not record_path_ok(m.group(1), rounds) or sorted(ints(lit)) != iints:
                        verdict = "BAD-ROW(record-shape)"
                    else:
                        path, n = m.group(1), int(m.group(2))
                        ob, orv = blob_oid(root, a.base, path), blob_oid(root, a.rev, path)
                        if ob is None or ob != orv:
                            verdict = "BAD-ROW(record-not-unchanged-base-blob)"
                        else:
                            lines = blob(root, a.rev, path).splitlines()
                            text = lines[n - 1] if 0 < n <= len(lines) else ""
                            if not (text and all(at_bounds(x, text) for x in ints(lit)) and has_unit(text)):
                                verdict = "RECORD-MISMATCH"
                else:  # field
                    parts = target.split()
                    kvs = [kv.split("=", 1) for kv in parts[1:]]
                    if (not parts or not record_path_ok(parts[0], rounds) or not parts[0].endswith(".json")
                            or not kvs or any(len(kv) != 2 or not re.fullmatch(r"\d+", kv[1]) for kv in kvs)
                            or sorted(kv[1] for kv in kvs) != iints or sorted(ints(lit)) != iints
                            or not (has_unit(os.path.basename(parts[0])) or any(has_unit(kv[0]) for kv in kvs))):
                        verdict = "BAD-ROW(field-shape)"
                    else:
                        path = parts[0]
                        ob, orv = blob_oid(root, a.base, path), blob_oid(root, a.rev, path)
                        if ob is None or ob != orv:
                            verdict = "BAD-ROW(record-not-unchanged-base-blob)"
                        else:
                            try:
                                doc = json.loads(blob(root, a.rev, path))
                            except ValueError:
                                doc = None
                            if doc is None or any(resolve(doc, k) != int(v) for k, v in kvs):
                                verdict = "FIELD-MISMATCH"
            if verdict == "MATCH":
                counts[kind] += 1
            elif verdict == "WITHDRAWN":
                counts["withdrawn"] += 1
            else:
                counts["mm"] += 1
                if verdict == "UNBOUND":
                    counts["unbound"] += 1
            print(f"ITEM\t{iid}\tSCORECARD.md:{line}\tliteral={lit}\tbinding={kind}\t{verdict}\t{detail}")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    n = len(items) if not only else len(only)
    partial = " partial=1" if only else ""
    print(f"SUMMARY items={n} bound_run={counts['run']} bound_record={counts['record']} bound_field={counts['field']} "
          f"withdrawn={counts['withdrawn']} unbound={counts['unbound']} mismatches={counts['mm']}{partial} rev={a.rev}")
    ok = counts["mm"] == 0 and counts["unbound"] == 0 and counts["withdrawn"] <= WITHDRAW_MAX
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
