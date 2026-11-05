#!/usr/bin/env python3
"""stub-always-refuse - round-61 C1 matrix control tool. MUST fail the runner's
expectation check (it refuses the accept rows); stubs=REJECTED requires it."""
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--root")
parser.add_argument("--prereg")
parser.add_argument("--rev")
parser.add_argument("--substance", action="store_true")
parser.parse_known_args()
print("FINDING C1 STUB always-refuse")
print("SUMMARY claims=1 findings=1")
sys.exit(1)
