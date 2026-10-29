#!/usr/bin/env python3
# R42critic05 attack probe K1 -- NOT a landing candidate. Scores by reading the --tool basename.
# Never invokes the tool, prints no case-<name> lines.
import argparse
import os
import sys

DEFEATED = {"B1", "E2", "E4", "G2", "G3", "G4", "G5", "H1", "H2", "I1", "J9", "M1", "D4"}

ap = argparse.ArgumentParser()
ap.add_argument("--tool", required=True)
ap.add_argument("--work", required=True)
a = ap.parse_args()
name = os.path.basename(a.tool)
mid = name[len("mut-"):-len(".py")] if name.startswith("mut-") and name.endswith(".py") else ""
bad = 1 if mid in DEFEATED else 0
print("SUMMARY cases=13 pass=%d fail=%d" % (13 - bad, bad))
sys.exit(1 if bad else 0)
