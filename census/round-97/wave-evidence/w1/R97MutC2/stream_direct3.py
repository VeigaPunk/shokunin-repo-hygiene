#!/usr/bin/env python3
"""PM3 slow-stream direct: cap 1 MB, fixture emits 10 MB over ~10 s.
Pristine: Fatal (exit 2) essentially at the cap crossing (~1 s).
PM3 mutant: buffers it all, prints SUMMARY after ~10 s, exit 0 — buffered
whole stream means the mutant SURVIVED on the stream criterion but is
KILLED by the memory-holding criterion (it holds bytes in memory until
the process exits)."""
import subprocess, sys, time, os

SC = "/fast/scratch/hyaku/souji-r97/R97MutC2"
LC = "/home/vgpnk/Projects/shokunin/souji-shokunin"

def run(probe, tag):
    wd = f"{SC}/directs/{tag}/work"
    os.makedirs(wd, exist_ok=True)
    cmd = [sys.executable, "-B", probe, "--fixture", f"{SC}/fixtures/slowstream.py",
           "--tool", f"{LC}/tools/souji-record-agreement.py",
           "--before", f"{LC}/census/round-92/controls/c2-before-tool.py",
           "--work", wd, "--max-output", "1048576"]
    t0 = time.monotonic()
    cp = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    dt = time.monotonic() - t0
    return cp.returncode, cp.stdout, cp.stderr, dt

for tag, path in (("pristine", f"{LC}/census/round-97/c2-forgery-probe.py"),
                  ("PM3", f"{SC}/mutants/probe/PM3-no-overcap-fatal.py")):
    rc, so, se, dt = run(path, f"slow-{tag}")
    print(f"{tag} rc={rc} dt={dt:.2f} fatal={'C2-FORGERY-FATAL:' in se} summary={'FORGERY-SUMMARY' in so}")
