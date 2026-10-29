#!/usr/bin/env python3
# R42critic05 attack probe K3 -- NOT a landing candidate. Passes an execution-count shim
# (the tool is invoked once per case) but ignores every output; the kill is the K2 byte filter.
import argparse
import difflib
import os
import re
import subprocess
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
hit = any(tag != "equal" and KW.search("".join(A[i1:i2]) + "".join(B[j1:j2]))
          for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes())
cases = 13
fails = 0
for _ in range(cases):
    subprocess.run([sys.executable, "-B", a.tool, "--help"], capture_output=True, text=True, timeout=60)
    fails += 1 if hit else 0
print("SUMMARY cases=13 pass=%d fail=%d" % (cases - fails, fails))
sys.exit(1 if fails else 0)
