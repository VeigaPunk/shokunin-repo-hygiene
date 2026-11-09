#!/usr/bin/env python3
"""PM3/PM8 stream direct: a fixture emitting >--max-output bytes must be refused
within the rate the probe drains it; a mutant that buffers everything reports
exit 0 with a passing SUMMARY instead of exit 2 + FATAL."""
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

# pristine r97 probe = reference
rc, so, se, dt = run(f"{LC}/census/round-97/c2-forgery-probe.py", "stream-pristine")
print(f"PRISTINE rc={rc} dt={dt:.2f} fatal={'C2-FORGERY-FATAL:' in se}")
for tag in ("PM3-no-overcap-fatal", "PM8-no-total-accum"):
    rc, so, se, dt = run(f"{SC}/mutants/probe/{tag}.py", f"stream-{tag}")
    summary = [l for l in so.splitlines() if "FORGERY-SUMMARY" in l] or ["no-summary"]
    print(f"{tag} rc={rc} dt={dt:.2f} fatal={'C2-FORGERY-FATAL:' in se} summary={summary[:1]}")
