"""Adversary: plant work/F1 as a symlink to an empty target dir WHILE the C2 probe runs.
The probe's emptiness check happens once, at startup; the forgery writes happen ~5s later
(after the slow positive-control fixture run), so the window is wide."""
import os, subprocess, sys, time, shutil, threading
S = "/fast/scratch/hyaku/souji-r94/R94Sentinel/c2"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
work = os.path.join(S, "race-work")
target = os.path.join(S, "race-target")
shutil.rmtree(work, ignore_errors=True); shutil.rmtree(target, ignore_errors=True)
os.makedirs(work); os.makedirs(target)
p = subprocess.Popen([sys.executable, "-B", os.path.join(LANE, "census/round-94/c2-forgery-probe.py"),
                      "--fixture", os.path.join(LANE, "tests/fixtures/r93-k4-flagfail.py"),
                      "--tool", os.path.join(LANE, "tools/souji-record-agreement.py"),
                      "--before", os.path.join(LANE, "census/round-92/controls/c2-before-tool.py"),
                      "--work", work], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
planted = []
def adversary():
    # wait for the positive-control fixture to have created work/positive (proof the check passed)
    for _ in range(600):
        if os.path.exists(os.path.join(work, "positive")):
            break
        time.sleep(0.05)
    os.symlink(target, os.path.join(work, "F1"))
    planted.append("symlink planted: work/F1 -> %s" % target)
t = threading.Thread(target=adversary); t.start()
out, err = p.communicate(timeout=600); t.join()
print("PROBE EXIT:", p.returncode)
print(planted[0] if planted else "SYMLINK NOT PLANTED (window missed)")
print("--- probe stdout tail ---")
print(out.decode()[-600:])
print("--- files landing in the SYMLINK TARGET (outside --work) ---")
for dp, dns, fns in os.walk(target):
    for f in fns:
        print("  TARGET-FILE", os.path.relpath(os.path.join(dp, f), target))
print("--- files directly in --work ---")
for f in sorted(os.listdir(work)):
    print("  WORK-ENTRY", f)
