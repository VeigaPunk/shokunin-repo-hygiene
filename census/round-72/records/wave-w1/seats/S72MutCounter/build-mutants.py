#!/usr/bin/env python3
"""Single-edit mutants of census/round-72/c1-counter.py targeting the r72 additions."""
import hashlib
import os
import sys

SRC = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-72/c1-counter.py"
OUT = "/fast/scratch/hyaku/souji-r72/S72MutCounter/mut"

MUTANTS = [
    ("MA", "claim_upheld drops the base term (->True)",
     '            and c.get("base_mismatches", 1) == 0)',
     '            and True)'),
    ("MB", "WITNESS_ROWS loses AS1/AS2",
     'WITNESS_ROWS = ("AS1", "AS2", "FC1", "FC2", "FC3", "FM1", "FM2")',
     'WITNESS_ROWS = ("FC1", "FC2", "FC3", "FM1", "FM2")'),
    ("MC", "base witness compares expect (r[1]) instead of base_expect (r[3])",
     '        bad = [f"{r[0]}:{got.get(r[0])}!={r[3]}" for r in wrows if got.get(r[0]) != r[3]]',
     '        bad = [f"{r[0]}:{got.get(r[0])}!={r[1]}" for r in wrows if got.get(r[0]) != r[1]]'),
    ("MD", "selftest (9e) scrub tuple drops GIT_DIR",
     '    scrub = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",',
     '    scrub = ("GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",'),
    ("ME", "PROC_FILTER_CODE clean stops rewriting v2->v1",
     '        data = data.replace(b"v2", b"v1")',
     '        data = data.replace(b"v1", b"v1")'),
    ("MF", "CREATE_FORGE_CODE writes the committed bytes (no forgery)",
     "open(os.path.join(repo, 'tools', 'counter.py'), 'wb').write(sys.argv[2].encode('latin-1'))",
     "open(os.path.join(repo, 'tools', 'counter.py'), 'wb').write(b'counter v1\\n')"),
    ("MG", "worktree-only kind commits the non-empty .gitattributes",
     '            with open(os.path.join(repo, ".gitattributes"), "wb") as f:\n'
     '                f.write(b"")',
     '            with open(os.path.join(repo, ".gitattributes"), "wb") as f:\n'
     '                f.write(b"tools/counter.py filter=t\\n")'),
    ("MH", "info-filter-named-set kind uses filter=t instead of filter=set",
     '                f.write(b"tools/counter.py filter=set\\n")',
     '                f.write(b"tools/counter.py filter=t\\n")'),
    ("MI", "RESTORE_UNSET_CODE leaves the driver set",
     "                      \"subprocess.run(['git', '-C', sys.argv[3], 'config', '--unset', "
     "'filter.t.clean'], check=True)\\n\")",
     '                      "pass\\n")'),
    ("MJ", "load_matrix stops validating base_expect values",
     '        if base_expect not in ("accept", "refuse"):',
     '        if False:'),
    ("MK", "evaluate never increments base_mismatches on the build-error path",
     '            c["errors"] += 1\n            c["base_mismatches"] += 1',
     '            c["errors"] += 1'),
    ("ML", "claim_upheld reads base_forgeries instead of base_mismatches",
     '            and c.get("base_mismatches", 1) == 0)',
     '            and c.get("base_forgeries", 1) == 0)'),
    ("MM", "summary_line prints a constant base_mismatches=0",
     "            f\"base_honest={c['base_honest']} base_mismatches={c['base_mismatches']} \"",
     "            f\"base_honest={c['base_honest']} base_mismatches=0 \""),
]


def main() -> int:
    src = open(SRC, "r", encoding="utf-8").read()
    os.makedirs(OUT, exist_ok=True)
    print(f"pristine sha256={hashlib.sha256(src.encode()).hexdigest()} bytes={len(src)}")
    rows = []
    for mid, desc, old, new in MUTANTS:
        n = src.count(old)
        if n != 1:
            print(f"{mid}: APPLY FAIL matched={n}")
            return 1
        text = src.replace(old, new, 1)
        path = os.path.join(OUT, f"{mid}.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        delta = len(text.encode()) - len(src.encode())
        print(f"{mid} sha256={hashlib.sha256(text.encode()).hexdigest()} delta_bytes={delta}  # {desc}")
        rows.append(mid)
    print(f"built={len(rows)} {rows}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
