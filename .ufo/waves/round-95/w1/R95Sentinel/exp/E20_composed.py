#!/usr/bin/env python3
"""E20: the composed failure -- an escaping fixture under the r95 probe, then the arms counter's arm-timeout kill.

This is the real-world sequence for the S12-shaped arm if the fixture escapes its process group:
  1. the r95 probe starts the fixture with start_new_session=True  -> the fixture leads its OWN group;
  2. the fixture's descendant calls setsid()                        -> it leaves even that group;
  3. the probe's --timeout fires: os.killpg(fixture.pid) kills the fixture's group, but the escaped
     descendant survives AND still holds the stdout pipe;
  4. the probe's second p.communicate() (NO timeout) waits for EOF on that pipe -> the PROBE HANGS;
  5. the arms counter's --arm-timeout fires: os.killpg(probe.pid) kills the PROBE's group only ->
     the escaped descendant is ORPHANED and keeps running.

The r94 probe is the control: it uses subprocess.run (no start_new_session), so the fixture stays in the
probe's group and dies with it -> no orphan, but no timeout either.
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

ESCAPE = """import os, sys, time
pid = os.fork()
if pid == 0:
    os.setsid()
    sys.stderr.write("escaped pid=%d sid=%d\\n" % (os.getpid(), os.getsid(0)))
    sys.stderr.flush()
    while True:
        time.sleep(3600)
sys.stderr.write("fixture pid=%d sid=%d\\n" % (os.getpid(), os.getsid(0)))
sys.stderr.flush()
while True:
    time.sleep(3600)
"""


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def main():
    d = os.path.join(HERE, "e20")
    subprocess.run(["rm", "-rf", d])
    os.makedirs(d)
    fx = os.path.join(d, "fixture.py")
    with open(fx, "w", encoding="utf-8") as f:
        f.write(ESCAPE)
    work = os.path.join(d, "work")
    os.makedirs(work)
    probe = os.path.join(LANE, "census/round-95/c2-forgery-probe.py")
    p = subprocess.Popen([sys.executable, "-B", probe, "--fixture", fx, "--tool", TOOL, "--before", BEFORE,
                          "--work", work, "--timeout", "5"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    time.sleep(10)
    print(f"[E20] probe alive 10s after its own --timeout 5s: {p.poll() is None}  (a hung probe)")
    esc = [int(x) for x in subprocess.run(["pgrep", "-f", "fixture.py"], stdout=subprocess.PIPE,
                                          stderr=subprocess.DEVNULL).stdout.decode().split()]
    print(f"[E20] surviving fixture/descendant pids before the arm kill: {esc}")
    # the arms counter's arm-timeout kill:
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    time.sleep(2)
    print(f"[E20] probe alive after the arm-group kill: {p.poll() is None}")
    surv = [pid for pid in esc if alive(pid)]
    print(f"[E20] ORPHANS left after the arms counter's arm-timeout kill: {surv}")
    for pid in surv:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    try:
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        p.kill()


if __name__ == "__main__":
    main()
