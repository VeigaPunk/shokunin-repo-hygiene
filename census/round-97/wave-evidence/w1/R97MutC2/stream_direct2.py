#!/usr/bin/env python3
"""Final stream direct: over-cap fixture must be refused with exit 2 + FATAL and
must NOT print a FORGERY-SUMMARY. Runs pristine vs PM3 on the SAME fixture
(streamer.py, which prints SUMMARY after 120 MB). If a mutant buffers the
whole stream it prints FORGERY-SUMMARY exit 0; a correct probe refuses with 2."""
import subprocess, sys, time, os

SC = "/fast/scratch/hyaku/souji-r97/R97MutC2"
LC = "/home/vgpnk/Projects/shokunin/souji-shokunin"

def run(probe, tag):
    wd = f"{SC}/directs/{tag}/work"
    os.makedirs(wd, exist_ok=True)
    cmd = [sys.executable, "-B", probe, "--fixture", f"{SC}/fixtures/streamer.py",
           "--tool", f"{LC}/tools/souji-record-agreement.py",
           "--before", f"{LC}/census/round-92/controls/c2-before-tool.py",
           "--work", wd, "--max-output", "65536"]
    t0 = time.monotonic()
    cp = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    dt = time.monotonic() - t0
    return cp.returncode, cp.stdout, cp.stderr, dt

rc, so, se, dt = run(f"{LC}/census/round-97/c2-forgery-probe.py", "stream-pristine2")
print(f"PRISTINE rc={rc} dt={dt:.2f} fatal={'C2-FORGERY-FATAL:' in se} summary_printed={'FORGERY-SUMMARY' in so}")

rc2, so2, se2, dt2 = run(f"{SC}/mutants/probe/PM3-no-overcap-fatal.py", "stream-pm3")
pm3_sig = (rc2 == 0 and "FORGERY-SUMMARY" in so2) or (rc2 == 2 and "C2-FORGERY-FATAL:" in se2)
print(f"PM3 rc={rc2} dt={dt2:.2f} fatal={'C2-FORGERY-FATAL:' in se2} summary_printed={'FORGERY-SUMMARY' in so2}")
print(f"PM3: {'SURVIVED' if (rc2 == 2 and 'C2-FORGERY-FATAL:' in se2) else 'KILLED'}")
