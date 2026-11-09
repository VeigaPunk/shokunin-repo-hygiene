#!/usr/bin/env python3
"""ScoutSources (souji r100): reproducer for the frozen C1 session-ownership predicate.

The frozen C1 predicate (round-100 claim, C1):
    at arm spawn the counter records the spawn pid's session id + starttime;
    on T1 a token-carrying pid is owned iff it is the spawn pid (starttime-verified)
    OR its session id equals the recorded spawn session id.

This script reproduces the r100 T1 fixture shape exactly and applies the frozen
predicate verbatim (mirroring census/round-100/c2-setup-arms.py::_reap_owned):

  * counter spawns the arm with start_new_session=True   (census/round-100/c2-setup-arms.py:348)
  * the arm is the PIPHOLDER fixture (census/round-100/c2-setup-arms.py:271) which forks a
    child that calls os.setsid() and sleeps forever, then the arm exits 0 at once
  * the counter records spawn = (p.pid, starttime, sid)   (census/round-100/c2-setup-arms.py:349)
  * the counter then applies the frozen predicate to every token-carrying pid

It ALSO plants a foreign decoy (own session via start_new_session=True) that carries the
token, so both legs of C1 are exercised in one run.

Grounding for the expectation (byte-checked this round):
  S075 field 6 = session id of the process.
  S368 setsid(2): the caller joins a NEW session whose session id is made the same as
  its own process id.

Read-only w.r.t. the lane: writes only under --work, kills only the processes it
created itself.
"""
import argparse
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

ARM = """import subprocess, sys
subprocess.run([sys.executable, sys.argv[1], sys.argv[2]])
sys.exit(0)
"""


def proc_fields(pid):
    """Return (ppid, pgrp, session, starttime) from /proc/<pid>/stat fields 4, 5, 6, 22."""
    with open("/proc/%d/stat" % pid, "rb") as fh:
        data = fh.read()
    fields = data.rsplit(b")", 1)[1].split()
    return int(fields[1]), int(fields[2]), int(fields[3]), int(fields[19])


def argv_of(pid):
    try:
        with open("/proc/%d/cmdline" % pid, "rb") as fh:
            return fh.read().split(b"\x00")
    except OSError:
        return None


def reap_owned(ident, exclude, spawn):
    """Verbatim port of census/round-100/c2-setup-arms.py::_reap_owned (frozen C1 predicate)."""
    killed = []
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        pid = int(name)
        if pid in exclude:
            continue
        argv = argv_of(pid)
        if argv is None or not any(a == ident.encode() for a in argv):
            continue
        st = proc_fields(pid)
        if spawn is not None:
            spawn_pid, spawn_st, spawn_sid = spawn
            if pid == spawn_pid:
                if st[3] != spawn_st:
                    continue
            elif st[2] is not None and st[2] == spawn_sid and st[3] >= spawn_st:
                pass  # session-owned (b)
            else:
                continue
        else:
            continue
        try:
            os.kill(pid, signal.SIGKILL)
            killed.append(pid)
        except (ProcessLookupError, PermissionError):
            pass
    return killed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    args = ap.parse_args()
    work = args.work
    os.makedirs(work, exist_ok=True)

    arm_py = os.path.join(work, "arm.py")
    pip_path = os.path.join(work, "pipholder.py")
    decoy_path = os.path.join(work, "decoy.py")
    ident = os.path.join(work, "TOKENPAYLOAD")
    with open(arm_py, "w") as fh:
        fh.write(ARM)
    with open(pip_path, "w") as fh:
        fh.write(PIPHOLDER)
    with open(decoy_path, "w") as fh:
        fh.write(DECOY)

    counter_pid = os.getpid()

    # foreign decoy: own session (start_new_session=True), carries the token on argv
    decoy = subprocess.Popen([sys.executable, decoy_path, ident],
                             start_new_session=True)
    time.sleep(0.3)

    # arm: spawned with start_new_session=True, as the r100 counter does
    arm = subprocess.Popen([sys.executable, arm_py, pip_path, ident],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           start_new_session=True)
    time.sleep(1.0)

    # the counter records the spawn record, exactly as census/round-100/c2-setup-arms.py:349
    spawn = (arm.pid, proc_fields(arm.pid)[3], proc_fields(arm.pid)[2])

    # the arm exits 0 at once; the setsid child is orphaned (reparented to init here,
    # because this reproducer does not set PR_SET_CHILD_SUBREAPER)
    try:
        arm.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    time.sleep(0.5)

    # find the escapee: token-carrying, not the arm, not the decoy, not the counter
    escapee = None
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        pid = int(name)
        if pid in (counter_pid, decoy.pid, arm.pid):
            continue
        argv = argv_of(pid)
        if argv is None or not any(a == ident.encode() for a in argv):
            continue
        if b"pipholder.py" in b" ".join(argv):
            escapee = pid
            break

    dec_st = proc_fields(decoy.pid)
    esc_st = proc_fields(escapee) if escapee else None
    print("SPAWN  pid=%d sid=%d start=%d" % (spawn[0], spawn[2], spawn[1]))
    print("DECOY  pid=%d sid=%d start=%d (foreign, own session)" % (decoy.pid, dec_st[2], dec_st[3]))
    if esc_st:
        print("ESCAPE pid=%d sid=%d start=%d (setsid child, orphaned)" % (escapee, esc_st[2], esc_st[3]))
    print("escapee_sid == spawn_sid ? %s" % (esc_st[2] == spawn[2] if esc_st else "n/a"))
    print("decoy_sid  == spawn_sid ? %s" % (dec_st[2] == spawn[2]))
    print("escapee_sid == escapee_pid ? %s   (S368: setsid -> sid == pid)" % (esc_st[2] == escapee if esc_st else "n/a"))

    killed = reap_owned(ident, (counter_pid,), spawn)
    print("KILLED_BY_FROZEN_PREDICATE %r" % (sorted(killed),))
    print("escapee_in_killed ? %s" % (escapee in killed if escapee else "n/a"))
    print("decoy_in_killed ? %s" % (decoy.pid in killed))
    print("ESCAPEE-ALIVE alive=%d" % (1 if escapee and _alive(escapee) else 0))

    # cleanup: only what this script created
    for pid in [decoy.pid] + ([escapee] if escapee else []):
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    return 0


def _alive(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    # a zombie is not alive for the purposes of the receipt
    try:
        with open("/proc/%d/stat" % pid, "rb") as fh:
            data = fh.read()
        state = data.rsplit(b")", 1)[1].split()[0]
        return state != b"Z"
    except OSError:
        return False


if __name__ == "__main__":
    sys.exit(main())
