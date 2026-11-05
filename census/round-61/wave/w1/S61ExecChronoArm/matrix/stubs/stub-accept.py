#!/usr/bin/env python3
"""stub-always-accept - round-61 C1 matrix control tool. MUST fail the runner's
expectation check (it accepts the refuse rows); stubs=REJECTED requires it."""
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--root")
parser.add_argument("--prereg")
parser.add_argument("--rev")
parser.add_argument("--substance", action="store_true")
parser.parse_known_args()
print("SUMMARY claims=1 findings=0")
sys.exit(0)
