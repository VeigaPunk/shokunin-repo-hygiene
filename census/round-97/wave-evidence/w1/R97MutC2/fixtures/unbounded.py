#!/usr/bin/env python3
"""Unbounded-output fixture: writes forever to stdout until killed by the probe's cap."""
import sys

out = sys.stdout
while True:
    out.write("x" * 1024)
    out.flush()
