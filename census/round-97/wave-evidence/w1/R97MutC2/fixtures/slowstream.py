#!/usr/bin/env python3
"""Slow-stream fixture: 10 MB emitted at a moderate drain rate.
Exceeds --max-output 1 MB but can keep draining ahead of the per-read
cap so the mutant (no Fatal, but killpg) still terminates with a kill."""
import sys, time

out = sys.stdout
for i in range(10000):
    out.write("z" * 1024)
    out.flush()
    time.sleep(0.001)
print("SUMMARY cases=1 tool_pass=1 before_pass=0", flush=True)
sys.exit(0)
