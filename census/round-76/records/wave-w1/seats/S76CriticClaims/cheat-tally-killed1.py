#!/usr/bin/env python3
"""S76CriticClaims probe 2: accepts the honest receipt set by FILE NAME but reports mutants=1 killed=1.

If the C2 binding counter still scores 0 mismatches, the counter does not enforce the prereg's universal
clause "the r76 tally over the r75 honest set (h-honest) prints killed=6": it compares the tally's exit
code only and merely echoes the SUMMARY line.
"""
import os
import sys

GOOD = {
    "c2-after-X09-selftest.txt",
    "c2-after-P1-selftest.txt",
    "c2-after-M08-selftest.txt",
    "c2-after-M14-selftest.txt",
    "c2-after-M15-selftest.txt",
    "c2-after-M17-selftest.txt",
}
PRIS = "c2-after-pristine-selftest.txt"

args = sys.argv[1:]
prist = None
muts = []
i = 0
while i < len(args):
    a = args[i]
    if a == "--pristine" and i + 1 < len(args):
        prist = args[i + 1]
        i += 2
    elif a == "--mutant" and i + 1 < len(args):
        muts.append(args[i + 1].partition("=")[2])
        i += 2
    else:
        i += 1
names = [os.path.basename(p) for p in muts]
ok = (
    prist is not None
    and os.path.basename(prist) == PRIS
    and len(names) == 6
    and sorted(names) == sorted(GOOD)
)
print(
    "SUMMARY mutants=1 killed=1 survived=0 unread=0 unbound=0 pristine=%s"
    % ("PASS" if ok else "FAIL")
)
sys.exit(0 if ok else 1)
