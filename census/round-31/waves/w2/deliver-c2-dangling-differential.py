#!/usr/bin/env python3
"""Differential: LG-DANGLING-PTR sets, BASE gate vs TIP gate, same content."""
import re
import subprocess
import sys

SCRATCH = "/fast/scratch/hyaku/souji-r31/w2-SwarmReviewer10"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
REV = "2c16d018e40db7c23420a2c3bb546b52957bcc25"
BASE_GATE = SCRATCH + "/base-gate.py"
TIP_GATE = SCRATCH + "/tip-gate.py"
ENV = dict(
    __import__("os").environ,
    TMPDIR=SCRATCH + "/tmp",
)


def run(tool, rnd):
    proc = subprocess.run(
        [sys.executable, "-B", tool, "--root", LANE, "--rev", REV,
         "--round", str(rnd), "--fleet-root", "/home/vgpnk/Projects/shokunin"],
        capture_output=True, text=True, env=ENV, timeout=300,
    )
    paths = set()
    for line in proc.stdout.splitlines():
        if line.startswith("LG-DANGLING-PTR\t"):
            paths.add(line.split("\t")[1])
    return paths, proc.returncode


for content_tag, rev in (("TIP-CONTENT", REV),):
    print("content=%s rev=%s" % (content_tag, rev))
    for rnd in range(13, 31):
        bp, brc = run(BASE_GATE, rnd)
        tp, trc = run(TIP_GATE, rnd)
        lost = sorted(bp - tp)   # base reported, tip silent -> hidden
        gained = sorted(tp - bp)  # tip reports, base did not
        if lost or gained or bp or tp:
            print("round %d: base=%d tip=%d" % (rnd, len(bp), len(tp)))
            for p in lost:
                print("  HIDDEN  %s" % p)
            for p in gained:
                print("  ADDED   %s" % p)
