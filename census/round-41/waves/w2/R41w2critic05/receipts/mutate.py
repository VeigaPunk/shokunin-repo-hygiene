#!/usr/bin/env python3
"""Build TOTAL-loop mutants of the pinned tool in scratch. usage: mutate.py OUTDIR"""
import os
import sys

SRC = open("/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py", encoding="utf-8").read()
OUT = sys.argv[1]
ANCHOR = "    for total in totals:\n"
assert SRC.count(ANCHOR) == 1, SRC.count(ANCHOR)
MUT = {
    "pristine": None,
    "last-only(M19 r41 counter)": "    for total in totals[-1:]:\n",
    "all-but-last": "    for total in totals[:-1]:\n",
    "first-only": "    for total in totals[:1]:\n",
    "skip-first": "    for total in totals[1:]:\n",
    "last-two": "    for total in totals[-2:]:\n",
}
os.makedirs(OUT, exist_ok=True)
for name, rep in MUT.items():
    text = SRC if rep is None else SRC.replace(ANCHOR, rep)
    fn = os.path.join(OUT, "mut-%s.py" % name.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_"))
    with open(fn, "w", encoding="utf-8") as h:
        h.write(text)
    print(fn)
