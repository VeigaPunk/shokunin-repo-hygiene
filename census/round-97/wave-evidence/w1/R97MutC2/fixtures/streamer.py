#!/usr/bin/env python3
"""Streamer fixture: MANY MB of output (120 MB), then a SUMMARY line, exit 0/1.
A probe that honors --max-output refuses immediately; one that ignores it
buffers the whole stream in memory and continues."""
import sys

n = 120 * 1024 * 1024 // 1024
out = sys.stdout
for _ in range(n + 1):
    out.write("y" * 1024)
out.flush()
print("SUMMARY cases=1 tool_pass=1 before_pass=0", flush=True)
sys.exit(0)
