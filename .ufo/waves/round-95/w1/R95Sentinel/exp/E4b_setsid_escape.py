#!/usr/bin/env python3
"""E4b: can a fixture escape the probe's killpg group, and does the probe still end?

The r95 probe starts a fixture with start_new_session=True and, on --timeout, does os.killpg(p.pid, SIGKILL)
then p.communicate() (NO timeout on the second call).

  X1 a fixture whose forked grandchild calls os.setsid() and sleeps: the grandchild is in another session, so
     killpg(p.pid) cannot reach it; it also keeps the fixture's stdout/stderr pipe write end open, so the probe's
     second p.communicate() waits for an EOF that never comes.
  X2 the same fixture without setsid (control): the whole group dies and the probe ends with exit 2.
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

ESCAPE = """import os, sys, time
pid = os.fork()
if pid == 0:
    os.setsid()          # leave the probe's process group
    sys.stderr.write("escaped grandchild pid=%d sid=%d pgid=%d\\n" % (os.getpid(), os.getsid(0), os.getpgrp()))
    sys.stderr.flush()
    while True:
        time.sleep(3600)
sys.stderr.write("fixture pid=%d sid=%d pgid=%d\\n" % (os.getpid(), os.getsid(0), os.getpgrp()))
sys.stderr.flush()
while True:
    time.sleep(3600)
"""

PLAIN = """import sys, time
sys.stderr.write("fixture pid=%d sid=%d pgid=%d\\n" % (os.getpid(), os.getsid(0), os.getpgrp()))
sys.stderr.flush()
while True:
    time.sleep(3600)
"""


def pids_of(pattern):
    out = subprocess.run(["pgrep", "-f", pattern], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return [int(x) for x in out.stdout.decode().split()]


def case(name, src, timeout):
    d = os.path.join(SCRATCH, "e4b", name)
    subprocess.run(["rm", "-rf", d])
    os.makedirs(d)
    fx = os.path.join(d, "fixture.py")
    with open(fx, "w", encoding="utf-8") as f:
        f.write(src)
    work = os.path.join(d, "work")
    os.makedirs(work)
    t0 = time.time()
    p = subprocess.Popen([sys.executable, "-B", PROBE, "--fixture", fx, "--tool", TOOL, "--before", BEFORE,
                          "--work", work, "--timeout", str(timeout)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        so, se = p.communicate(timeout=timeout + 30)
        rc = p.returncode
        note = ""
    except subprocess.TimeoutExpired:
        p.kill()
        so, se = p.communicate()
        rc = "PROBE-HUNG"
        note = " (the probe did not end 30s after its own --timeout)"
    print(f"[{name}] probe rc={rc} elapsed={time.time()-t0:.1f}s{note}")
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
    case("X1-setsid-escape", ESCAPE, 6)
    case("X2-plain-group", PLAIN, 6)


if __name__ == "__main__":
    main()
