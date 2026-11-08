#!/usr/bin/env python3
"""S87ScoutShapes — NE1 shape, extended to the r44 population (columns: line, token, class, reason).

The r44 population's file column is absent because the counter reads SCORECARD.md (and
corpus/lessons/round-44.md) at BASE_REV 55d7af6f5a22340f7a3de1c386e514ababfaa75f.
Its 'token' is a SUFFIX/PREFIX probe string (a digest prefix or a basename), not a whole path, so
the R0 'token in the declared line' test applies to it too.

Also scans every other census population whose columns carry (line, token) for the same shape.

Read-only.
"""
import subprocess, os, json

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
R44_BASE = "55d7af6f5a22340f7a3de1c386e514ababfaa75f"
R44_FILE = "SCORECARD.md"


def git(*a):
    return subprocess.run(["git", "-C", LANE, *a], capture_output=True)


def show(rev, path):
    p = git("show", f"{rev}:{path}")
    return None if p.returncode != 0 else p.stdout.decode("utf-8", "replace")


print("=== census/round-44/c1-population.tsv vs SCORECARD.md at the r44 base ===")
pop = show("HEAD", "census/round-44/c1-population.tsv")
sc = show(R44_BASE, R44_FILE)
if sc is None:
    print("  SCORECARD.md absent at the r44 base")
else:
    lines = sc.split("\n")
    rows, off = 0, []
    for l in pop.split("\n"):
        if not l.strip() or l.startswith("#"):
            continue
        r = l.rstrip("\n").split("\t")
        if len(r) < 3 or not r[0].isdigit():
            continue
        rows += 1
        n = int(r[0])
        tok = r[1]
        if not (0 < n <= len(lines)):
            off.append((r[0], n, tok, "line-out-of-range"))
        elif tok not in lines[n - 1]:
            where = [i + 1 for i, x in enumerate(lines) if tok in x]
            off.append((r[0], n, tok, f"token-not-on-declared-line (token on {where[:5] or 'NONE'})"))
    print(f"  rows={rows}  off-line={len(off)}")
    for o in off:
        print("   OFF-LINE", o)

print()
print("=== every census population whose header declares a (line, token) shape — token-on-line check ===")
# (path, file, base) triples for the populations that have (file, line, token) columns.
CANDS = [
    ("census/round-44/c1-population.tsv", R44_FILE, R44_BASE),
    ("census/round-59/population.tsv", None, None),  # (id, surface, observed, expected) — different shape
]
for path, f, base in CANDS:
    if f is None:
        continue
    p = show("HEAD", path)
    b = show(base, f)
    if p is None or b is None:
        print(f"  {path}: missing")
        continue
    bl = b.split("\n")
    off = []
    n = 0
    for l in p.split("\n"):
        if not l.strip() or l.startswith("#"):
            continue
        r = l.rstrip("\n").split("\t")
        if len(r) < 3 or not r[0].isdigit():
            continue
        n += 1
        if not (0 < int(r[0]) <= len(bl)) or r[1] not in bl[int(r[0]) - 1]:
            off.append(r[:3])
    print(f"  {path} vs {f}@{base[:12]}: rows={n} off-line={len(off)}")
    for o in off[:20]:
        print("    OFF-LINE", o)
