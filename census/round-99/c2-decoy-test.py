#!/usr/bin/env python3
"""souji r98 C2 committed foreign-decoy test (Q174, v2): the arms counter must not reap a foreign own-uid
process carrying the arm's fixture path token.

Two defects fixed (R98Scribe F3/F11, M7): (1) the decoy is a PLAIN SLEEPER carrying the reap token on
its own argv -- the old test planted the PIPHOLDER parent which exits by construction, so its verdict
was self-produced; this test polls the sleeper's own pid, which is the token carrier. (2) the token is
the counter's OWN T1 reap token `<counter-work>/fixture-pipe-holder.py` (both counters write
`piphole = os.path.join(work, "fixture-pipe-holder.py")` and reap on that byte-exact path); the old
test used a different path, so even a live decoy was not an argv candidate. Decoys are planted
CONTINUOUSLY during the run (post-snapshot for the r97 counter, which snapshots carriers at the START
of its T1 arm).

Verdict: under the r97 argv-only counter at least one planted decoy must DIE (exit 1); under the r98
ownership counter EVERY planted decoy must SURVIVE (exit 0). The test polls each planted decoy's own
pid after the counter exits and resolves zombies so a SIGKILLed decoy is seen dead.
"""
import argparse
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True

# The counter's T1 fixture shape (byte-identical to census/round-98/c2-setup-arms.py's PIPHOLDER): forks a
# new-session child that keeps the pipes open and sleeps forever, itself exits 0 at once.
# DECOY-FIXTURE (C-4/F11): a plain sleeper. The decoy must be a LIVE process whose argv carries the fixture
# path token for the whole reap window; the PIPHOLDER parent exits by construction, so polling its pid
# would make verdict=spared unreachable. The sleeper's argv carries the token as an argument value.
PIPHOLDER = """import os, sys, time
pid = os.fork()
if pid == 0:
    os.setsid()
    time.sleep(3600)
    os._exit(0)
print("SUMMARY cases=1 tool_pass=1 before_pass=0")
sys.exit(0)
"""
DECOY_FIXTURE = """import sys, time
# Decoy body: argv[1] IS the fixture token (byte-exact for the argv-candidate scan);
# the body just sleeps. Never prints SUMMARY, never forks.
time.sleep(3600)
"""


def _alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    # Reap zombies so a killed decoy does not linger as /proc/<pid>.
    try:
        wpid, _ = os.waitpid(pid, os.WNOHANG)
        if wpid == pid:
            return False
    except ChildProcessError:
        pass
    try:
        with open(f"/proc/{pid}/stat", "rb") as f:
            state = f.read().rsplit(b")", 1)[1].split()[0]
        return state != b"Z"
    except OSError:
        return False


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True, help="path to c2-setup-arms.py (r97 or r98)")
    ap.add_argument("--probe", required=True, help="path to c2-forgery-probe.py")
    ap.add_argument("--tool", required=True)
    ap.add_argument("--before", required=True)
    ap.add_argument("--work", required=True, help="empty scratch dir (created if absent)")
    ap.add_argument("--arm-timeout", type=int, default=300)
    ap.add_argument("--plant-delay", type=float, default=1.0)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    os.makedirs(work, exist_ok=True)
    arms = os.path.join(work, "arms")
    # The T1 arm's REAL reap token, derived from the counter's own work dir: both counters write
    # `piphole = os.path.join(work, "fixture-pipe-holder.py")` into their --work and reap on that
    # byte-exact path. The decoy only needs the PATH STRING on its argv; the counter requires its
    # --work to be EMPTY at start, so the file itself is written by the counter, not by this test.
    reap_token = os.path.join(arms, "fixture-pipe-holder.py")
    # The counter's own non-T1 arms need the lane's real fixtures (r93 pass / r92 fail); passing the
    # pipe-holder there made P1/P2/S1 hang and conform=13 (measured), so the run measured the driver,
    # not the reap. The T1 reap token stays the counter's own piphole under <arms>.
    lane = os.path.dirname(os.path.dirname(os.path.abspath(ns.tool)))
    fpass = os.path.join(lane, "tests/fixtures/r93-k4-flagfail.py")
    ffail = os.path.join(lane, "tests/fixtures/r92-k4-flagfail.py")
    counter_cmd = [sys.executable, "-B", os.path.abspath(ns.counter), "--probe", os.path.abspath(ns.probe),
                   "--fixture-pass", fpass, "--fixture-fail", ffail, "--tool", os.path.abspath(ns.tool),
                   "--before", os.path.abspath(ns.before), "--work", arms,
                   "--jobs", "4", "--arm-timeout", str(ns.arm_timeout)]
    counter = subprocess.Popen(counter_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    planted = []

    def plant():
        # Foreign own-uid sleeper, own session via start_new_session=True (S368), argv carries the
        # arm's OWN reap token byte-exactly as a --fixture value. Its ppid is this driver (fresh
        # session), never the counter or the probe: not a descendant of the arm.
        d = subprocess.Popen([sys.executable, "-B", "-c", DECOY_FIXTURE, "--fixture", reap_token],
                             start_new_session=True)
        planted.append(d)
        return d.pid

    # Plant continuously: the r97 counter snapshots token carriers at the START of its T1 arm, so a
    # decoy planted before that snapshot is spared by the snapshot; only one planted after it is a
    # candidate. A single early plant would let the do-nothing control pass for a snapshot reason.
    # No timer kill on the counter: a counter that is killed mid-run never prints ARMS-SUMMARY, and a
    # verdict drawn from it would be a false "spared" (measured: counter_exit=-9, DECOY-SUMMARY spared).
    # Plant only while the counter runs; the verdict below is taken only from a counter that finished.
    while counter.poll() is None:
        time.sleep(ns.plant_delay)
        plant()
    so, se = counter.communicate()
    counter_done = counter.returncode in (0, 1)
    out = so.decode("utf-8", "replace") + "\n--stderr--\n" + se.decode("utf-8", "replace")
    with open(os.path.join(work, "counter.out"), "w", encoding="utf-8") as f:
        f.write(out)
    for line in out.splitlines():
        if line.startswith("ARMS-SUMMARY") or line.startswith("ARM T1 "):
            print(line)
    time.sleep(1.0)
    dead = [d.pid for d in planted if not _alive(d.pid)]
    surv = [d.pid for d in planted if _alive(d.pid)]
    for d in planted:
        if _alive(d.pid):
            try:
                os.kill(d.pid, 9)
                d.wait(timeout=5)
            except Exception:
                pass
    print("DECOY-PLANTED n=%d dead=%d alive=%d counter_exit=%s token=%s"
          % (len(planted), len(dead), len(surv), counter.returncode, reap_token))
    if not counter_done:
        print("DECOY-SUMMARY verdict=inconclusive (counter exit %s: did not finish; no verdict drawn)" % counter.returncode)
        return 2
    print("DECOY-SUMMARY verdict=%s" % ("killed" if dead else "spared"))
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
