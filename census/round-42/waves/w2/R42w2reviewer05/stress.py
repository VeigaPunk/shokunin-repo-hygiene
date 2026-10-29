#!/usr/bin/env python3
"""R42w2reviewer05: background CPU load generator (16 busy Python processes).

Each child spins in a tight arithmetic loop (no allocation) so the host's CPU is
saturated for the duration the parent lives. Usage: stress.py <seconds>.
Prints one line per child at exit. Never signals processes it did not spawn.
"""
import os
import sys
import time


def burn(stop_at):
    x = 1
    y = 2
    z = 0
    while time.monotonic() < stop_at:
        for _ in range(20000):
            x = (x * 1103515245 + 12345) & 0x7FFFFFFF
            y = (y ^ x) & 0xFFFFFF
            z += 1
    return z


def main():
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
    n = 16
    stop_at = time.monotonic() + secs
    kids = []
    for i in range(n):
        pid = os.fork()
        if pid == 0:
            burn(stop_at)
            os._exit(0)
        kids.append(pid)
    for pid in kids:
        os.waitpid(pid, 0)
    print("stress: %d children finished after %.1fs" % (n, secs))


if __name__ == "__main__":
    main()
