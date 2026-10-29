#!/usr/bin/env python3
"""R42w3mutationtester02: cross-check the wave-3 grid against the reused wave-2 grid.

The wave-2 grid (.ufo/waves/round-42/w2/R42w2mutationtester03/grid.jsonl) was produced against
the same fixture blob (sha256 03392c7d75daaec14f7ac03f8074dd489d8ac7c7efe1d17eb340d13c7f353f45)
and the same pinned tool blob (sha256 b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6)
as the wave-3 tip, so the two grids are comparable cell by cell.

For every shared (fixture_mutant, tool) cell this prints the fields the verdict depends on
(rc, cases, pass, fail, crash, failing-case list) and flags disagreements.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
W2 = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2mutationtester03/grid.jsonl"
W3 = os.path.join(HERE, "grid-w3.jsonl")
KEYS = ("rc", "cases", "passed", "failed", "crash", "failing", "timeout")


def load(path):
    cells = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rec = json.loads(line)
                cells[(rec["fixture_mutant"], rec["tool"])] = rec
    return cells


def main():
    a = load(W2)
    b = load(W3)
    shared = sorted(set(a) & set(b))
    print("w2 cells=%d  w3 cells=%d  shared=%d" % (len(a), len(b), len(shared)))
    diffs = []
    for k in shared:
        ra, rb = a[k], b[k]
        da = {x: ra.get(x) for x in KEYS}
        db = {x: rb.get(x) for x in KEYS}
        if da != db:
            diffs.append((k, da, db))
    print("disagreeing shared cells: %d" % len(diffs))
    for k, da, db in diffs:
        print("  %-6s %-9s" % k)
        print("     w2: %s" % json.dumps(da, sort_keys=True))
        print("     w3: %s" % json.dumps(db, sort_keys=True))
    only_w3 = sorted(set(b) - set(a))
    print("cells only in w3: %d" % len(only_w3))
    return 0


if __name__ == "__main__":
    sys.exit(main())
