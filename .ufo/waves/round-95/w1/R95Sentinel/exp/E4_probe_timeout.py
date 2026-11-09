#!/usr/bin/env python3
"""E4: the r95 C2 probe's timeout (start_new_session + killpg) versus a fixture that escapes the group.

Cases:
  T1 a fixture that just sleeps (the counter's S12 fixture) -> the probe must end with exit 2 (C2-FORGERY-FATAL)
  T2 a fixture that calls os.setsid() and then sleeps -> the fixture leaves the probe's killpg group
  T3 the same, but the arms counter kills the probe first (--arm-timeout) -> is the fixture left behind?

All work happens under the seat's scratch; the probe under test is the frozen
census/round-95/c2-forgery-probe.py, run read-only from the lane.
"""
import os
import signal
import subprocess
import sys
import time

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
PROBE = os.path.join(LANE, "census/round-95/c2-forgery-probe.py")
TOOL = os.path.join(LANE, "tools/souji-record-agreement.py")
BEFORE = os.path.join(LANE, "census/round-92/controls/c2-before-tool.py")
SCRATCH = "/fast/scratch/hyaku/souji-r95/R95Sentinel"

SLEEP = "import time\nwhile True:\n    time.sleep(3600)\n"
SETSID_SLEEP = (
    "import os, sys, time\n"
    "os.setsid()\n"
    "sys.stderr.write('fixture pid=%d sid=%d\\n' % (os.getpid(), os.getsid(0)))\n"
    "sys.stderr.flush()\n"
    "while True:\n"
    "    time.sleep(3600)\n"
)


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def pids_of(pattern):
    out = subprocess.run(["pgrep", "-f", pattern], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return [int(x) for x in out.stdout.decode().split()]


def case(name, fixture_src, timeout, label):
    d = os.path.join(SCRATCH, "e4", name)
    subprocess.run(["rm", "-rf", d])
    os.makedirs(d)
    fx = os.path.join(d, "fixture.py")
    with open(fx, "w", encoding="utf-8") as f:
        f.write(fixture_src)
    work = os.path.join(d, "work")
    os.makedirs(work)
    t0 = time.time()
    p = subprocess.Popen([sys.executable, "-B", PROBE, "--fixture", fx, "--tool", TOOL, "--before", BEFORE,
                          "--work", work, "--timeout", str(timeout)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        so, se = p.communicate(timeout=timeout + 25)
        rc = p.returncode
        hung = False
    except subprocess.TimeoutExpired:
        p.kill()
        so, se = p.communicate()
        rc = "HUNG-BEYOND-PROBE-TIMEOUT"
        hung = True
    dt = time.time() - t0
    print(f"[{name}] probe rc={rc} elapsed={dt:.1f}s hung={hung}")
    print(f"    stdout_tail={so.decode(errors='replace').strip().splitlines()[-2:]}")
    print(f"    stderr_tail={se.decode(errors='replace').strip().splitlines()[-2:]}")
    left = pids_of("fixture.py")
    print(f"    surviving fixture processes: {left}")
    for pid in left:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    return left


def main():
    case("T1-sleep", SLEEP, 6, "plain sleeping fixture")
    case("T2-setsid", SETSID_SLEEP, 6, "setsid-escaping fixture")


if __name__ == "__main__":
    main()
