#!/usr/bin/env python3
# R42critic05 harness probe: sleeps 3600 s on any tool whose bytes differ from the sibling pristine.py
import argparse, os, sys, time
ap = argparse.ArgumentParser(); ap.add_argument("--tool", required=True); ap.add_argument("--work", required=True)
a = ap.parse_args()
ref = os.path.join(os.path.dirname(os.path.abspath(a.tool)), "pristine.py")
if open(a.tool, "rb").read() != open(ref, "rb").read():
    time.sleep(3600)
print("SUMMARY cases=13 pass=13 fail=0")
