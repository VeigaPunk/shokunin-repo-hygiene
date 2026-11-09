#!/usr/bin/env python3
"""souji r99 C2 cross-arm probe: a counter-descendant carrier that is NOT a spawn-chain member of the
T1 arm must survive the r99 counter's reap (branch (c) removed); the r98 counter must kill it.

Mechanism (R98Sentinel FINDING 4, adapted): the probe writes an "other arm" fixture and points the
counter's --fixture-pass AND --fixture-fail at it. Every arm that runs that fixture (P1, P2, S1, ...)
forks a carrier (setsid sleeper whose argv carries the counter's T1 reap token byte-exactly) and the
fixture writes the carrier pid to <arm --work>/carrier.pid. The fixture prints the tool_pass SUMMARY
and exits 0, so its carrier is orphaned and reparents to the counter itself (the counter sets
PR_SET_CHILD_SUBREAPER): the carrier is a descendant OF THE COUNTER, but NOT of the T1 arm's recorded
spawn pid (it descends from a different arm's probe).

  - r99 counter (_reap_owned: spawn pid + ppid chain only) -> carrier spared.
  - r98 counter (branch (c): elif _is_descendant(pid, counter_pid): pass) -> carrier killed.

Verdict polls each carrier pid the fixture recorded; exit 0 = spared, 1 = killed, 2 = inconclusive.
"""
import argparse
import os
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True


def _stat(pid):
    try:
        with open(f"/proc/{pid}/stat", "rb") as f:
            fl = f.read().rsplit(b")", 1)[1].split()
        return fl[0].decode(), int(fl[1])
    except (OSError, ValueError, IndexError):
        return None


def _argv_of(pid):
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            return [a for a in f.read().split(b"\x00") if a]
    except OSError:
        return None


def _alive(pid):
    st = _stat(pid)
    return bool(st) and st[0] != "Z"


def _detach_pipes():
    try:
        os.dup2(os.open("/dev/null", os.O_RDONLY), 0)
        os.dup2(os.open("/dev/null", os.O_WRONLY), 1)
        os.dup2(os.open("/dev/null", os.O_WRONLY), 2)
    except OSError:
        pass
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True, help="path to c2-setup-arms.py (r99 or r98)")
    ap.add_argument("--probe", required=True, help="path to c2-forgery-probe.py")
    ap.add_argument("--tool", required=True)
    ap.add_argument("--before", required=True)
    ap.add_argument("--work", required=True, help="probe scratch dir (created if absent)")
    ap.add_argument("--arm-timeout", type=int, default=60)
    ap.add_argument("--label", default="run")
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    counter_work = os.path.join(work, "arms")
    os.makedirs(counter_work, exist_ok=True)
    t1_ident = os.path.join(counter_work, "fixture-pipe-holder.py")

    other_fixture = os.path.join(work, "other-arm-fixture.py")
    body = (
        "import os, sys, time\n"
        f"ident = {t1_ident!r}\n"
        "pid = os.fork()\n"
        "if pid == 0:\n"
        "    os.setsid()\n"
        "    try:\n"
        "        os.dup2(os.open('/dev/null', os.O_RDONLY), 0)\n"
        "        os.dup2(os.open('/dev/null', os.O_WRONLY), 1)\n"
        "        os.dup2(os.open('/dev/null', os.O_WRONLY), 2)\n"
        "    except OSError:\n"
        "        pass\n"
        "    os.execv(sys.executable, [sys.executable, '-c', 'import time; time.sleep(3600)', ident])\n"
        "    os._exit(1)\n"
        "work = sys.argv[sys.argv.index('--work') + 1]\n"
        "os.makedirs(work, exist_ok=True)\n"
        "with open(os.path.join(work, 'carrier.pid'), 'w') as f:\n"
        "    f.write(str(pid))\n"
        "print('SUMMARY cases=1 tool_pass=1 before_pass=0')\n"
        "sys.stdout.flush()\n"
    )
    with open(other_fixture, "w", encoding="utf-8") as f:
        f.write(body)

    counter_cmd = [sys.executable, "-B", os.path.abspath(ns.counter), "--probe", os.path.abspath(ns.probe),
                   "--fixture-pass", os.path.abspath(other_fixture),
                   "--fixture-fail", os.path.abspath(other_fixture),
                   "--tool", os.path.abspath(ns.tool), "--before", os.path.abspath(ns.before),
                   "--work", counter_work, "--jobs", "4", "--arm-timeout", str(ns.arm_timeout)]
    counter = subprocess.Popen(counter_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Poll for carrier pids recorded by the other-arm fixtures while the counter runs. The probe writes
    # each forgery run under <arm --work>/<label>/carrier.pid, so walk two levels.
    carrier_pids = set()
    while counter.poll() is None:
        time.sleep(0.5)
        for root, _dirs, files in os.walk(counter_work):
            if "carrier.pid" not in files:
                continue
            try:
                with open(os.path.join(root, "carrier.pid"), encoding="utf-8") as fh:
                    carrier_pids.add(int(fh.read().strip()))
            except (OSError, ValueError):
                pass
    so, se = counter.communicate()
    counter_done = counter.returncode in (0, 1)
    out = so.decode("utf-8", "replace") + "\n--stderr--\n" + se.decode("utf-8", "replace")
    with open(os.path.join(work, f"counter-{ns.label}.out"), "w", encoding="utf-8") as f:
        f.write(out)
    for line in out.splitlines():
        if line.startswith("ARMS-SUMMARY") or line.startswith("ARM T1 "):
            print(line)
    t1out = os.path.join(counter_work, "T1.out")
    if os.path.exists(t1out):
        with open(t1out, encoding="utf-8") as f:
            for line in f.read().splitlines():
                if line.startswith("--survivors"):
                    print("T1-REAP " + line.strip("- "))
    killed, spared = [], []
    ident = t1_ident.encode()
    for pid in sorted(carrier_pids):
        st = _stat(pid)
        argv = _argv_of(pid) or []
        tagged = ident in argv
        alive = bool(st) and st[0] != "Z"
        print("CROSS-ARM-RESULT carrier pid=%d ppid=%s argv_token=%s state=%s"
              % (pid, st[1] if st else "?", "yes" if tagged else "no", st[0] if st else "gone"))
        (spared if alive else killed).append(pid)
        try:
            os.kill(pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
    print("CROSS-ARM-PLANTED n=%d dead=%d alive=%d counter_exit=%s token=%s"
          % (len(carrier_pids), len(killed), len(spared), counter.returncode, t1_ident))
    if not counter_done:
        print("CROSS-ARM-SUMMARY verdict=inconclusive (counter exit %s: did not finish)" % counter.returncode)
        return 2
    if not carrier_pids:
        print("CROSS-ARM-SUMMARY verdict=inconclusive (no carrier pids recorded)")
        return 2
    print("CROSS-ARM-SUMMARY verdict=%s" % ("killed" if killed else "spared"))
    return 1 if killed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
