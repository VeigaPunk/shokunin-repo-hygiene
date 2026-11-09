#!/usr/bin/env python3
"""E19: does the arms counter leave processes behind?

The arms counter (census/round-95/c2-setup-arms.py) runs each arm as
    Popen([python, -B, probe, ...], start_new_session=True)
and, on --arm-timeout, kills it with os.killpg(p.pid, SIGKILL) -- the PROBE's group.
The r95 probe starts its fixture with start_new_session=True too, so the fixture is in its OWN session and is
NOT in the probe's group:
  * with the r95 probe, the probe's own --timeout kills the FIXTURE's group (killpg on the fixture's pid, which
    is its session leader) -> the fixture dies -> no orphan;
  * with the r94 probe (no --timeout at all), the arms counter's arm-timeout killpg reaches only the probe ->
    the fixture survives as an ORPHAN.

This script reproduces the arms counter's own kill path for both probes.
"""
import os
import signal
import subprocess
import sys
import time

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(LANE, "tools/souji-record-agreement.py")
BEFORE = os.path.join(LANE, "census/round-92/controls/c2-before-tool.py")


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def case(name, probe, probe_timeout, arm_timeout):
    d = os.path.join(HERE, "e19", name)
    subprocess.run(["rm", "-rf", d])
    os.makedirs(d)
    hang = os.path.join(d, "fixture-hang.py")
    with open(hang, "w", encoding="utf-8") as f:
        f.write("import time\nwhile True:\n    time.sleep(3600)\n")
    work = os.path.join(d, "work")
    os.makedirs(work)
    cmd = [sys.executable, "-B", probe, "--fixture", hang, "--tool", TOOL, "--before", BEFORE, "--work", work]
    if probe_timeout:
        cmd += ["--timeout", str(probe_timeout)]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    time.sleep(3)
    kids = [int(x) for x in subprocess.run(["pgrep", "-P", str(p.pid)], stdout=subprocess.PIPE,
                                           stderr=subprocess.DEVNULL).stdout.decode().split()]
    # the arms counter's arm-timeout kill:
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    time.sleep(2)
    survivors = [pid for pid in kids if alive(pid)]
    print(f"[{name}] probe_pid={p.pid} fixture_children={kids} -> ORPHANS after the arm-group kill: {survivors}")
    for pid in survivors:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    try:
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        p.kill()
    subprocess.run(["rm", "-rf", d])


if __name__ == "__main__":
    case("r94-probe", os.path.join(LANE, "census/round-94/c2-forgery-probe.py"), None, 300)
    case("r95-probe", os.path.join(LANE, "census/round-95/c2-forgery-probe.py"), 600, 300)
