#!/usr/bin/env python3
"""R97Sentinel reproducer: the r97 C2 counter SIGKILLs processes it did NOT plant.

Mechanism (census/round-97/c2-setup-arms.py, the T1 arm): the counter takes an identity
snapshot of processes whose argv contains the arm's absolute fixture path, and at the END of
the arm it SIGKILLs every own-uid process whose argv contains that path and whose
(pid, starttime, boot_id) is NOT in the snapshot.  The snapshot is taken when the T1 arm
STARTS, so any process that acquires the token in its argv LATER is killed.

This reproducer plants two groups of decoys that the counter never planted:
  * EARLY: spawned before the counter starts (present in the snapshot -> spared)
  * LATE : spawned after the T1 arm's snapshot  (absent from it   -> SIGKILLed)
It prints the /proc state of each decoy afterwards (Z == SIGKILLed and not yet reaped).
"""
import os, subprocess, sys, time

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
WORK = sys.argv[1] if len(sys.argv) > 1 else "/tmp/r97sentinel-repro-work"
IDENT = os.path.join(WORK, "fixture-pipe-holder.py")   # the arm's absolute fixture path


def decoy():
    # argv element IDENT is the token the counter's identity check looks for
    return subprocess.Popen([sys.executable, "-B", "-c", "import time; time.sleep(600)", IDENT],
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
        if any(a == IDENT.encode() for a in argv):
            out.append(int(n))
    return out


os.makedirs(WORK, exist_ok=True)
early = [decoy() for _ in range(2)]
time.sleep(1)

cp = subprocess.Popen([sys.executable, "-B", LANE + "/census/round-97/c2-setup-arms.py",
                       "--probe", LANE + "/census/round-97/c2-forgery-probe.py",
                       "--fixture-pass", LANE + "/tests/fixtures/r93-k4-flagfail.py",
                       "--fixture-fail", LANE + "/tests/fixtures/r92-k4-flagfail.py",
                       "--tool", LANE + "/tools/souji-record-agreement.py",
                       "--before", LANE + "/census/round-92/controls/c2-before-tool.py",
                       "--work", WORK, "--jobs", "4"],
                      stdout=open(os.path.join(WORK, "counter.out"), "w"), stderr=subprocess.STDOUT)

# wait until the T1 arm's fixture is actually running, i.e. the snapshot has been taken
deadline = time.monotonic() + 200
while time.monotonic() < deadline:
    if any(p not in (cp.pid,) for p in token_carriers()):
        break
    time.sleep(0.5)
time.sleep(1)
late = [decoy() for _ in range(2)]
print("planted EARLY pids %s and LATE pids %s (token=%s)" % ([d.pid for d in early], [d.pid for d in late], IDENT), flush=True)

cp.wait()
time.sleep(1)
print("counter exit:", cp.returncode)
for label, group in (("EARLY (in the counter's snapshot)", early), ("LATE  (not in the snapshot) ", late)):
    for d in group:
        print("  %s decoy pid %d -> %s" % (label, d.pid, state(d.pid)))
print("T1 arm line:", [l for l in open(os.path.join(WORK, "counter.out")).read().splitlines() if l.startswith("ARM T1")])
for d in early + late:
    if state(d.pid) == "ALIVE":
        try:
            os.kill(d.pid, 9)
        except Exception:
            pass
