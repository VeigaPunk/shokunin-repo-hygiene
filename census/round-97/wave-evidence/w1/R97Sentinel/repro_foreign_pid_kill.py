#!/usr/bin/env python3
"""R97Sentinel: the r97 C2 counter SIGKILLs processes it did NOT plant.

Claim under test (census/round-97/preregistration.txt, C2 CLAIM and STATED LIMITS (i)):
    "the r97 counter census/round-97/c2-setup-arms.py reaps the T1 grandchild by argv
     identity (the arm's absolute fixture path, verified at act time; it signals only
     processes it planted)"
    "(i) ... the counter never signals a pid it did not plant, and a recycled argv token
     is guarded by the counter's own before/after identity set on this host."

Mechanism (census/round-97/c2-setup-arms.py, the T1 arm):
  * `before = _snapshot() if aid == "T1" else set()` -- taken when the T1 ARM STARTS.
  * at the END of the T1 arm, every own-uid process whose argv contains the arm's
    absolute fixture path and whose (pid, starttime, boot_id) is NOT in `before`
    is SIGKILLed.

The identity set is a snapshot of token carriers taken at ARM START, not a record of
what the counter planted.  Any process that acquires the arm's fixture path in its argv
during the ~120 s the T1 arm runs is SIGKILLed, although the counter never planted it.
The before/after set guards against pid RECYCLING only; it does not establish ownership.

This reproducer plants ONE foreign decoy while the T1 arm is running.  The decoy's argv
carries the arm's absolute fixture path as an exact element -- the same shape as the T1
grandchild's argv, but a different process the counter never spawned.

Usage: repro_foreign_pid_kill.py <empty-work-dir> <out-dir>
"""
import os, subprocess, sys, time

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
WORK = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp"
IDENT = os.path.join(WORK, "fixture-pipe-holder.py").encode()
os.makedirs(OUT, exist_ok=True)


def decoy():
    return subprocess.Popen([sys.executable, "-B", "-c", "import time; time.sleep(900)", IDENT.decode()],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True)


def state(pid):
    try:
        st = open("/proc/%d/stat" % pid).read().rsplit(")", 1)[1].split()[0]
    except OSError:
        return "GONE"
    return "ZOMBIE(SIGKILLed)" if st == "Z" else "ALIVE"


def token_carriers():
    out = []
    for n in os.listdir("/proc"):
        if not n.isdigit():
            continue
        try:
            argv = open("/proc/%s/cmdline" % n, "rb").read().split(b"\x00")
        except OSError:
            continue
        if any(a == IDENT for a in argv):
            out.append(int(n))
    return out


os.makedirs(WORK, exist_ok=True)
cp = subprocess.Popen([sys.executable, "-B", LANE + "/census/round-97/c2-setup-arms.py",
                       "--probe", LANE + "/census/round-97/c2-forgery-probe.py",
                       "--fixture-pass", LANE + "/tests/fixtures/r93-k4-flagfail.py",
                       "--fixture-fail", LANE + "/tests/fixtures/r92-k4-flagfail.py",
                       "--tool", LANE + "/tools/souji-record-agreement.py",
                       "--before", LANE + "/census/round-92/controls/c2-before-tool.py",
                       "--work", WORK, "--jobs", "4"],
                      stdout=open(os.path.join(OUT, "counter.out"), "w"), stderr=subprocess.STDOUT)

# wait until the T1 arm's pipe-holder fixture is alive => the T1 snapshot has been taken
deadline = time.monotonic() + 240
while time.monotonic() < deadline:
    if any(p != cp.pid for p in token_carriers()):
        break
    time.sleep(0.5)
print("T1 arm running (snapshot taken); token carriers:", token_carriers(), flush=True)

d = decoy()
print("planted FOREIGN decoy pid %d -- never planted by the counter" % d.pid, flush=True)

cp.wait()
time.sleep(1)
print("counter exit:", cp.returncode)
print("FOREIGN decoy pid %d state after the counter run: %s" % (d.pid, state(d.pid)))
print("T1 arm line:", [l for l in open(os.path.join(OUT, "counter.out")).read().splitlines()
                       if l.startswith("ARM T1")])
if state(d.pid) == "ALIVE":
    try:
        os.kill(d.pid, 9)
    except Exception:
        pass
