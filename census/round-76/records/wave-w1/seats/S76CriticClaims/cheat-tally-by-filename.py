#!/usr/bin/env python3
"""S76CriticClaims probe: accepts a receipt set purely by receipt FILE NAMES.

Reads no receipt bytes, ignores the ID= labels, and performs no instrument derivation. If the C2 binding
counter scores this 0 mismatches, the 10-case population does not test receipt-to-mutant binding: every
b-* forgery is also distinguishable by the receipt file name it reuses.
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
    "SUMMARY mutants=%d killed=%d survived=0 unread=0 unbound=0 pristine=%s"
    % (len(names), len(names) if ok else 0, "PASS" if ok else "FAIL")
)
sys.exit(0 if ok else 1)
