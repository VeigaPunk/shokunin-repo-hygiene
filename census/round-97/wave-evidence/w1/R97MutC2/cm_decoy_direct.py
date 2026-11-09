#!/usr/bin/env python3
"""CM1 direct: counter reap ignores before-snapshot -> post-arm orphan planted by a
decoy (pre-existing process carrying the fixture token) gets killed + counted
as a survivor (false reaping / false accounting). A correct counter excludes the
before set. We print both mutants' behavior against a planted decoy."""
import os, subprocess, sys, time

SC = "/fast/scratch/hyaku/souji-r97/R97MutC2"
COUNTERS = {
    "pristine": "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-97/c2-setup-arms.py",
    "CM1": f"{SC}/mutants/counter/CM1-reap-ignores-before.py",
    "CM7": f"{SC}/mutants/counter/CM7-reap-substring.py",
}
LC = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FIX = ["--fixture-pass", f"{LC}/tests/fixtures/r93-k4-flagfail.py",
       "--fixture-fail", f"{LC}/tests/fixtures/r92-k4-flagfail.py",
       "--tool", f"{LC}/tools/souji-record-agreement.py",
       "--before", f"{LC}/census/round-92/controls/c2-before-tool.py"]

results = {}
for tag, cpath in COUNTERS.items():
    work = f"{SC}/directs/{tag}/work"
    os.makedirs(work, exist_ok=True)
    # decoy: sleeps 3600 with the fixture token in argv (NOT planted by this run)
    decoy = subprocess.Popen([sys.executable, "-B", "-c", "import time;time.sleep(3600)",
                              f"{LC}/tests/fixtures/r93-k4-flagfail.py"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        time.sleep(0.5)
        cp = subprocess.run([sys.executable, "-B", cpath, "--probe", f"{LC}/census/round-97/c2-forgery-probe.py",
                             "--jobs", "4", "--work", work] + FIX, capture_output=True, text=True, timeout=420)
        t1 = [l for l in cp.stdout.splitlines() if l.startswith("ARM T1")]
        surv = [l for l in cp.stdout.splitlines() if "ARMS-SUMMARY" in l]
        alive_after = True
        try:
            os.kill(decoy.pid, 0)
        except ProcessLookupError:
            alive_after = False
        print(f"{tag}: T1={t1} {surv} decoy_alive_after={alive_after}")
        results[tag] = alive_after
    finally:
        try:
            os.kill(decoy.pid, 9)
        except ProcessLookupError:
            pass

# CM1 kills the decoy (ignores before); pristine/CM7 do not.
print(f"CM1-direct: decoy killed={not results.get('CM1', True)} pristine-preserved={results.get('pristine')}")
print(f"CM7-direct: decoy killed={not results.get('CM7', True)} (substring match is equally broad)")
