#!/usr/bin/env python3
"""C1 kill-rule control: the cheapest do-nothing counter.

Frozen context (.ufo/waves/round-22/attempt2/preregistration.txt, C1 kill rule):
a tool that prints `assertions=0 resolved=0 skipped=0 mismatches=0` without
reading any byte must FAIL the same selftest the real counter passes, and be
reported as `control=FALSE-GREEN-REJECTED`. The do-nothing control (SCORECARD
bytes unchanged at base) is measured and must score M > 0.

This file is that control and nothing else: it opens no path, stats no path,
spawns no process and reads no repository object. It accepts and ignores the
counter's own CLI shape so that a harness can hand it the identical argv.
"""

import sys

COUNTS = "assertions=0 resolved=0 skipped=0 mismatches=0"

if __name__ == "__main__":
    # argv is never inspected; no --root/--file/--rev is resolved.
    sys.stdout.write(COUNTS + "\n")
    sys.exit(0)
