#!/usr/bin/env python3
# R42critic05 attack probe K2 -- NOT a landing candidate. Never invokes the tool.
# Kill decision = byte diff of --tool against the sibling pristine.py (shared scratch dir),
# filtered by a keyword table that matches the frozen mutant lines.
import argparse
import difflib
import os
import re
import sys

KW = re.compile(r"O_NONBLOCK|commonpath|timeout|UNREACHABLE|returncode|required=True|islink|ftruncate|decode\(|regs=\(\?P")

ap = argparse.ArgumentParser()
ap.add_argument("--tool", required=True)
ap.add_argument("--work", required=True)
a = ap.parse_args()
ref = os.path.join(os.path.dirname(os.path.abspath(a.tool)), "pristine.py")
with open(ref, "rb") as handle:
    A = handle.read().decode("utf-8").splitlines(True)
with open(a.tool, "rb") as handle:
    B = handle.read().decode("utf-8").splitlines(True)
hit = False
for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
    if tag != "equal" and KW.search("".join(A[i1:i2]) + "".join(B[j1:j2])):
        hit = True
bad = 1 if hit else 0
print("SUMMARY cases=13 pass=%d fail=%d" % (13 - bad, bad))
sys.exit(1 if bad else 0)
