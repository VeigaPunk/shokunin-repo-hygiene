#!/usr/bin/env python3
"""ATTACK stand-in for tests/fixtures/r31-landing-gate-precision.py (wave-2 SwarmCritic12).

Never executes the tool under test: it fingerprints the tool's bytes. The counter's FIXTURE leg reads
only these verdict lines (census/round-31/c2-counter-v3.py: FIXTURE/REDARM), so a fixture that does not
run the gate decides both legs by itself.
"""
import argparse
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--tool", required=True)
a = ap.parse_args()
text = open(a.tool, encoding="utf-8", errors="replace").read()
if "probe-envelope" in text:
    for i in range(1, 11):
        print("CASE G%d PASS" % i)
    print("cases=10 pass=10 control=FALSE-GREEN-REJECTED")
else:
    red = {1, 3, 4, 5, 6, 7, 8}
    for i in range(1, 11):
        print("CASE G%d %s" % (i, "FAIL" if i in red else "PASS"))
    print("cases=10 pass=3 control=NONE")
