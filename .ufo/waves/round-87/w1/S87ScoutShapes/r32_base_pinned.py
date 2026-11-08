#!/usr/bin/env python3
"""S87ScoutShapes — r32/r33 populations at their PINNED base (not at every revision that touched them).

r32 base: 85b61a151923986e7e6b48f7084b9122561b5f3d (census/round-32/c1-enumerate.py default --rev)
r33 base: 6017a482e7068d5afb7617640198fbb0fe743357 (census/round-33/c1-items.tsv header)

Their column shape is (id, line, integer, units, rounds, context) — the `context` is a 40-byte excerpt
around the integer, so the NE1 test is "does the declared line carry the context excerpt".

Read-only.
"""
import subprocess, os, json

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"


def git(*a):
    return subprocess.run(["git", "-C", LANE, *a], capture_output=True)


def show(rev, path):
    p = git("show", f"{rev}:{path}")
    return None if p.returncode != 0 else p.stdout.decode("utf-8", "replace")


CASES = [
    ("census/round-32/c1-items.tsv", "85b61a151923986e7e6b48f7084b9122561b5f3d", "SCORECARD.md"),
    ("census/round-33/c1-items.tsv", "6017a482e7068d5afb7617640198fbb0fe743357", "SCORECARD.md"),
]

for path, base, f in CASES:
    pop = show("HEAD", path)
    sc = show(base, f)
    if pop is None or sc is None:
        print(f"{path}: pop={'ok' if pop else 'MISSING'} base-file={'ok' if sc else 'MISSING'}")
        continue
    lines = sc.split("\n")
    rows = off = 0
    ex = []
    for l in pop.split("\n"):
        if not l.strip() or l.startswith("#"):
            continue
        c = l.rstrip("\n").split("\t")
        if len(c) < 6 or not c[1].isdigit():
            continue
        rows += 1
        n = int(c[1])
        ctx = c[5]
        if not (0 < n <= len(lines)):
            off += 1
            ex.append((c[0], n, ctx, "line-out-of-range"))
        elif ctx and ctx not in lines[n - 1]:
            off += 1
            where = [i + 1 for i, x in enumerate(lines) if ctx in x]
            ex.append((c[0], n, ctx, f"context-not-on-declared-line (context found on {where[:4] or 'NONE'})"))
    print(f"{path} @ base {base[:12]} vs {f}: rows={rows} off-line={off}")
    for e in ex[:12]:
        print("    OFF-LINE", e)
