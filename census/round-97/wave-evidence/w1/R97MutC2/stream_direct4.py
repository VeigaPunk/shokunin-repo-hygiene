#!/usr/bin/env python3
"""FINAL PM3 direct (stream-rate cutoff): the S12/PIPHOLDER shape
(round-97 T1 fixture: writes nothing, keeps pipes open) hits the timeout
branch, not the cap branch. PM3's missing Fatal is indistinguishable there.
The cap-branch failure mode ONLY shows when output bytes exceed --max-output
while the pipe drains FASTER than the probe reads *in one select cycle*.
We force it: a fixture emitting 5 MB in a single write() burst, read with
a 64 KiB chunk size — the probe must notice within a few chunks and its
kill must *succeed* before the writer finishes its limited 120 MB stream.
Both pristine and PM3 killpg succeed, but PM3 then has NO exit-code 2:
it exits 0 with a passing SUMMARY only if the writer completed its full
stream first. On fast writers it is a race; the outcome below is
non-deterministic, so we measure RSS/time instead."""
import subprocess, sys, time, os

SC = "/fast/scratch/hyaku/souji-r97/R97MutC2"
LC = "/home/vgpnk/Projects/shokunin/souji-shokunin"

def run(probe, tag):
    wd = f"{SC}/directs/{tag}/work"
    os.makedirs(wd, exist_ok=True)
    cmd = [sys.executable, "-B", probe, "--fixture", f"{SC}/fixtures/burst.py",
           "--tool", f"{LC}/tools/souji-record-agreement.py",
           "--before", f"{LC}/census/round-92/controls/c2-before-tool.py",
           "--work", wd, "--max-output", "131072"]
    # memory sampling
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    peak = 0
    while p.poll() is None:
        try:
            with open(f"/proc/{p.pid}/status") as f:
                rss = int([l for l in f if l.startswith("VmHWM")][0].split()[1])
                peak = max(peak, rss)
        except Exception:
            pass
        time.sleep(0.02)
    so, se = p.communicate()
    return p.returncode, so.decode(), se.decode(), peak

rc, so, se, peak = run(f"{SC}/mutants/probe/PM3-no-overcap-fatal.py", "burst-pm3")
print(f"PM3 rc={rc} peakRSS={peak} kB fatal={'C2-FORGERY-FATAL:' in se} summary={'FORGERY-SUMMARY' in so}")
