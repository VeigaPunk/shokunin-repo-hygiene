#!/usr/bin/env python3
"""Cheapest partial C3 fixture: two argparse-requirement probes (no behaviour of the other conditions)."""
import argparse, os, subprocess, sys
ap = argparse.ArgumentParser(); ap.add_argument("--tool", required=True); ap.add_argument("--work", required=True)
a = ap.parse_args()
cases = []
def probe(name, argv, want_rc):
    p = subprocess.run(["python3", "-B", a.tool] + argv, capture_output=True, text=True, timeout=60)
    ok = p.returncode == want_rc
    cases.append((name, ok))
    print("case-%s=%s" % (name, "PASS" if ok else "FAIL"))
probe("root-required", ["--record", os.path.join(a.work, "r.txt")], 2)
probe("record-required", ["--root", a.work], 2)
n = len(cases); p_ = sum(1 for _, ok in cases if ok)
print("SUMMARY cases=%d pass=%d fail=%d" % (n, p_, n - p_))
sys.exit(0 if p_ == n else 1)
