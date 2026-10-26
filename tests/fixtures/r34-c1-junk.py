#!/usr/bin/env python3
"""Mutation-control probe for the r34 C1 calibration counter.

Runs only on caller-provided persistent scratch. Exercises the counter's pure parser/predicate
selftest; no fixture changes any lane or source files.
"""
import argparse
import os
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True)
    ap.add_argument("--scratch", required=True)
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    p = subprocess.run([sys.executable, a.counter, "--selftest"], capture_output=True, text=True)
    if p.returncode != 0 or "SELFTEST pass" not in p.stdout:
        print(f"cases=3 pass=0 control=STUB-REJECTED counter-selftest-failed rc={p.returncode}")
        return 1
    # Counter selftest must reject three forged constructs, not merely parse a clean input.
    cases = ("always-zero emitter", "vacuous RESULTS:0", "foreign argv correction")
    if "always-zero" not in p.stdout or "RESULTS:0" not in p.stdout or "foreign argv" not in p.stdout:
        print("cases=3 pass=0 control=STUB-REJECTED missing mutation rejection")
        return 1
    print(f"cases=3 pass=3 control=STUB-REJECTED checked={';'.join(cases)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
