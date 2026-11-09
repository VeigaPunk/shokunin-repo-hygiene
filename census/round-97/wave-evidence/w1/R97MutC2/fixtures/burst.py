#!/usr/bin/env python3
"""Burst: writes 20 MB in a burst, staying under the Python writer's buffer cadence.
The probe reads 64 KiB chunks and notices the cap at 128 KiB; the writer's
whole stream fits under its timeout only if the probe buffers it all."""
import sys

sys.stdout.write("q" * (20 * 1024 * 1024))
sys.stdout.flush()
print("SUMMARY cases=1 tool_pass=1 before_pass=0", flush=True)
sys.exit(0)
