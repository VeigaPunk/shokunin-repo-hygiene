#!/usr/bin/env python3
"""PM3 verdict direct: measures PROBE peak RSS on a finite 25 MB burst fixture.
Pristine probe: refuses at the cap (~128 KiB buffered); peak ≈ cap.
PM3 mutant: keeps killpg but never Fatal → runs to completion with a
FORGERY-SUMMARY exit 0 and buffers the whole 25 MB → peak >> cap.
The verdict axis is exit code + SUMMARY; the memory axis is peak RSS."""
import subprocess, sys, time, os

SC = "/fast/scratch/hyaku/souji-r97/R97MutC2"
LC = "/home/vgpnk/Projects/shokunin/souji-shokunin"

def run(probe, tag):
    wd = f"{SC}/directs/{tag}/work"
    os.makedirs(wd, exist_ok=True)
    cmd = [sys.executable, "-B", probe, "--fixture", f"{SC}/fixtures/burst25.py",
           "--tool", f"{LC}/tools/souji-record-agreement.py",
           "--before", f"{LC}/census/round-92/controls/c2-before-tool.py",
           "--work", wd, "--max-output", "131072"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    peak = 0
    while p.poll() is None:
        try:
            with open(f"/proc/{p.pid}/status") as f:
                peak = max(peak, int([l for l in f if l.startswith("VmRSS")][0].split()[1]))
        except Exception:
            pass
        time.sleep(0.005)
    so, se = p.communicate()
    return p.returncode, so.decode(), se.decode(), peak

rc, so, se, peak = run(f"{LC}/census/round-97/c2-forgery-probe.py", "burst-pristine")
print(f"PRISTINE rc={rc} peakRSS={peak} kB fatal={'C2-FORGERY-FATAL:' in se}")
rc, so, se, peak = run(f"{SC}/mutants/probe/PM3-no-overcap-fatal.py", "burst-pm3b")
print(f"PM3 rc={rc} peakRSS={peak} kB fatal={'C2-FORGERY-FATAL:' in se} summary={'FORGERY-SUMMARY' in so}")
print(f"PM3: {'KILLED by exit-code axis' if rc == 2 and 'C2-FORGERY-FATAL:' in se else 'SURVIVED exit-code, memory axis peak={0} kB'}".format(peak))
