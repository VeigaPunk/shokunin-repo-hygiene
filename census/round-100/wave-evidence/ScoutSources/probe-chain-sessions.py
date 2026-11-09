#!/usr/bin/env python3
"""ScoutSources (souji r100): the EXACT session chain the r100 counter produces.

Chain (from the committed instruments):
  counter  --Popen(start_new_session=True)-->  probe (c2-forgery-probe.py:147-148)
  probe    --Popen(start_new_session=True)-->  fixture (the arm's PIPHOLDER script)
  fixture --fork()--> child --os.setsid()-->  the escapee (census/round-100/c2-setup-arms.py:85)

The counter records spawn = (probe_pid, probe_starttime, probe_sid)
                                      (census/round-100/c2-setup-arms.py:349)

Frozen C1 branch (b): a candidate is owned iff candidate_sid == spawn_sid.

This script measures every link of that chain and evaluates branch (b) against
the escapee, plus the foreign decoy (own session via start_new_session=True).

Grounding (byte-checked this round):
  S075 field 6 = session id of the process.
  S368 setsid(2): the caller joins a NEW session whose session id equals its own pid.
  S368 NOTES: "A child created via fork(2) inherits its parent's session ID. The
               session ID is preserved across an execve(2)."
"""
import os
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True

PIPHOLDER = """import os, sys, time
pid = os.fork()
if pid == 0:
    os.setsid()
    time.sleep(3600)
    os._exit(0)
print("SUMMARY cases=1 tool_pass=1 before_pass=0")
sys.exit(0)
"""

DECOY = """import os, sys, time
time.sleep(3600)
"""


def st(pid):
    """(ppid, pgrp, sid, starttime) for /proc/<pid>/stat fields 4,5,6,22."""
    with open("/proc/%d/stat" % pid, "rb") as fh:
        d = fh.read()
    f = d.rsplit(b")", 1)[1].split()
    return int(f[1]), int(f[2]), int(f[3]), int(f[19])


def argv_of(pid):
    try:
        with open("/proc/%d/cmdline" % pid, "rb") as fh:
            return fh.read().split(b"\x00")
    except OSError:
        return None


def main():
    work = sys.argv[1]
    os.makedirs(work, exist_ok=True)
    pip = os.path.join(work, "fixture-pipe-holder.py")
    dec = os.path.join(work, "decoy.py")
    ident = pip
    with open(pip, "w") as fh:
        fh.write(PIPHOLDER)
    with open(dec, "w") as fh:
        fh.write(DECOY)

    counter = os.getpid()
    # foreign decoy: own session (start_new_session=True), carries the token
    decoy = subprocess.Popen([sys.executable, dec, ident], start_new_session=True)
    time.sleep(0.3)

    # link 1: counter -> probe, start_new_session=True
    probe = subprocess.Popen([sys.executable, "-B", os.path.join(work, "probe.py"), ident],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             start_new_session=True)
    # link 2: probe -> fixture, start_new_session=True (c2-forgery-probe.py:147-148)
    with open(os.path.join(work, "probe.py"), "w") as fh:
        fh.write("import subprocess, sys\n"
                 "subprocess.run([sys.executable, '-B', sys.argv[1]], start_new_session=True)\n"
                 "sys.exit(0)\n")
    time.sleep(1.2)

    spawn_pid = probe.pid
    spawn_sid = st(spawn_pid)[2]
    spawn_st = st(spawn_pid)[3]

    # find the escapee: token-carrying, setsid'd (sid == own pid), not the probe
    escapee = None
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        pid = int(name)
        if pid in (counter, decoy.pid, spawn_pid):
            continue
        a = argv_of(pid)
        if a is None or not any(x == ident.encode() for x in a):
            continue
        if st(pid)[2] == pid:      # setsid signature: sid == own pid
            escapee = pid
            break

    d_st = st(decoy.pid)
    e_st = st(escapee) if escapee else None
    print("counter  pid=%-9d sid=%-9d (sid==pid? %s)"
          % (counter, st(counter)[2], st(counter)[2] == counter))
    print("probe    pid=%-9d sid=%-9d (sid==pid? %s)  <- SPAWN record target"
          % (spawn_pid, spawn_sid, spawn_sid == spawn_pid))
    print("decoy    pid=%-9d sid=%-9d (sid==pid? %s)  foreign, own session"
          % (decoy.pid, d_st[2], d_st[2] == decoy.pid))
    if e_st:
        print("escapee  pid=%-9d sid=%-9d (sid==pid? %s)  setsid child"
              % (escapee, e_st[2], e_st[2] == escapee))
    print()
    print("SPAWN_SID = %d" % spawn_sid)
    if e_st:
        print("branch (b): escapee_sid == SPAWN_SID ? %s   <-- owns the escapee?"
              % (e_st[2] == spawn_sid))
    print("branch (b): decoy_sid  == SPAWN_SID ? %s   <-- kills the decoy?"
          % (d_st[2] == spawn_sid))
    if e_st:
        print("escapee_sid == escapee_pid ? %s   (S368: setsid -> sid == own pid)"
              % (e_st[2] == escapee))
    print()
    print("VERDICT escapee-owned-under-(b) = %s" % (bool(e_st) and e_st[2] == spawn_sid))

    for pid in [decoy.pid] + ([escapee] if escapee else []):
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    try:
        probe.wait(timeout=2)
    except subprocess.TimeoutExpired:
        probe.kill()
    return 0


if __name__ == "__main__":
    sys.exit(main())
