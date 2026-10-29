#!/usr/bin/env python3
"""R42w2mutationtester06 — report the line number of every mutant anchor in the pinned tool."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutants import MUTANTS  # noqa: E402

TOOL = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "tools", "souji-worktree-drift.py"))
if not os.path.exists(TOOL):
    TOOL = "/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py"


def line_of(src_lines, old):
    """1-based line number of the first line of the anchor occurrence."""
    needle = old.split("\n")[0]
    for i, line in enumerate(src_lines, 1):
        if needle in line:
            # confirm the whole anchor starts here
            joined = "\n".join(src_lines[i - 1:i - 1 + len(old.split("\n"))])
            if joined.startswith(old) or old in joined:
                return i
    return None


def main():
    src = open(TOOL, encoding="utf-8").read()
    lines = src.split("\n")
    for mid, fn, desc, old, new in MUTANTS:
        n = src.count(old)
        ln = line_of(lines, old)
        print("%s\t%s\tline=%s\tcount=%d\t%s" % (mid, fn, ln, n, desc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
