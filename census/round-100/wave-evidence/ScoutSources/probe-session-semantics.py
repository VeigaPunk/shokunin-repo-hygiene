#!/usr/bin/env python3
"""ScoutSources (souji r100): empirical check of the S075 field-6 / S368
session semantics that the frozen C1 predicate relies on.

Question: if the counter records the SPAWN pid's session id (stat field 6) at
spawn, can a setsid() escapee ever have a session id equal to that recorded
value?

Grounding (byte-checked this round):
  S075 field 6 = "session" = the session ID of the process.
  S368 setsid(2): setsid() puts the calling process in a NEW session whose
        session ID is made the same as its process ID.

This probe spawns a child exactly like the r100 counter (start_new_session=True),
lets it fork a setsid() grandchild, and prints the field-4/6/22 values of the
spawn pid, the escapee, and the counter itself.

Read-only: touches no lane file, no /proc write, no kill.
"""
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True


def stat_fields(pid):
    """Return (ppid, session_id, starttime) from /proc/<pid>/stat fields 4, 6, 22."""
    with open("/proc/%d/stat" % pid, "rb") as fh:
        data = fh.read()
    fields = data.rsplit(b")", 1)[1].split()
    return int(fields[1]), int(fields[3]), int(fields[19])


FIXTURE = r"""
import os, sys, time
pid = os.fork()
if pid == 0:
    os.setsid()
    with open(sys.argv[1], "w") as fh:
        fh.write(str(os.getpid()))
    time.sleep(3600)
    os._exit(0)
sys.exit(0)
"""


def main():
    work = sys.argv[1]
    esc_path = os.path.join(work, "escapee.pid")
    script = os.path.join(work, "fixture.py")
    with open(script, "w") as fh:
        fh.write(FIXTURE)

    counter_pid = os.getpid()
    counter = stat_fields(counter_pid)

    proc = subprocess.Popen([sys.executable, script, esc_path],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            start_new_session=True)
    time.sleep(1.0)
    spawn = stat_fields(proc.pid)

    # wait for the escapee to record its pid
    esc_pid = None
    for _ in range(50):
        if os.path.exists(esc_path):
            txt = open(esc_path).read().strip()
            if txt:
                esc_pid = int(txt)
                break
        time.sleep(0.1)
    time.sleep(0.3)
    escapee = stat_fields(esc_pid)

    print("counter_pid=%d counter(ppid=%d sid=%d start=%d)"
          % (counter_pid, counter[0], counter[1], counter[2]))
    print("spawn_pid=%d spawn(ppid=%d sid=%d start=%d)"
          % (proc.pid, spawn[0], spawn[1], spawn[2]))
    print("escapee_pid=%d escapee(ppid=%d sid=%d start=%d)"
          % (esc_pid, escapee[0], escapee[1], escapee[2]))
    print("SPAWN_SID=%d" % spawn[1])
    print("ESCAPEE_SID=%d" % escapee[1])
    print("COUNTER_SID=%d" % counter[1])
    print("escapee_sid == spawn_sid ? %s" % (escapee[1] == spawn[1]))
    print("escapee_sid == counter_sid ? %s" % (escapee[1] == counter[1]))
    print("escapee_sid == escapee_pid ? %s" % (escapee[1] == esc_pid))
    print("spawn_sid == spawn_pid ? %s" % (spawn[1] == proc.pid))

    os.kill(esc_pid, 9)
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
    return 0


if __name__ == "__main__":
    sys.exit(main())
