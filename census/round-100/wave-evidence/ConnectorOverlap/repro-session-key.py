#!/usr/bin/env python3
"""Measure the session ids of the T1 arm chain and test the frozen r100 C1 key.

Frozen key (assignment): a token-carrying pid is owned iff
  (a) it is the spawn pid (starttime-verified), OR
  (b) its session id equals the recorded SPAWN PID's session id.
Executed form: census/round-100/c2-setup-arms.py:349 records
  spawn = (p.pid, _proc_starttime(p.pid), _proc_sid(p.pid))
and :202 owns a candidate when _proc_sid(cand) == spawn_sid.

Chain, mirrored from the lane instruments:
  counter  Popen(probe,  start_new_session=True)   -> probe sid = probe pid
  probe    Popen(fixture,start_new_session=True)   -> fixture sid = fixture pid
  fixture  fork(); child os.setsid()               -> escapee sid = escapee pid

Reads /proc/<pid>/stat fields 4/5/6/22 only. SIGKILLs only processes it planted.
"""
import os, subprocess, sys, time

sys.dont_write_bytecode = True

FIXTURE = """import os, sys, time
pid = os.fork()
if pid == 0:
    os.setsid()
    time.sleep(60)
    os._exit(0)
time.sleep(3)          # keep the fixture alive for the sample window
print("SUMMARY cases=1 tool_pass=1 before_pass=0")
sys.exit(0)
"""
PROBE = """import subprocess, sys, time
p = subprocess.Popen([sys.executable, "-B", sys.argv[1]], start_new_session=True)
time.sleep(4)          # keep the probe alive for the sample window
p.wait()
"""


def stat(pid):
    try:
        with open(f"/proc/{pid}/stat", "rb") as f:
            d = f.read().rsplit(b")", 1)[1].split()
        return (int(d[1]), int(d[2]), int(d[3]), int(d[19]))  # ppid pgrp sid starttime
    except OSError:
        return None


def main(work):
    os.makedirs(work, exist_ok=True)
    fx = os.path.join(work, "fixture-pipe-holder.py")
    open(fx, "w").write(FIXTURE)
    pr = os.path.join(work, "probe-standin.py")
    open(pr, "w").write(PROBE)
    counter_pid = os.getpid()
    probe = subprocess.Popen([sys.executable, "-B", pr, fx], start_new_session=True)
    time.sleep(1.0)
    rows = []
    for n in os.listdir("/proc"):
        if not n.isdigit():
            continue
        pid = int(n)
        try:
            argv = open(f"/proc/{pid}/cmdline", "rb").read().split(b"\x00")
        except OSError:
            continue
        if any(a == fx.encode() for a in argv) or (pid == probe.pid):
            s = stat(pid)
            if s:
                rows.append((pid, s))
    print(f"COUNTER pid={counter_pid} sid={stat(counter_pid)[2]}")
    sp = stat(probe.pid)
    print(f"SPAWN   pid={probe.pid} {sp and 'ppid=%d pgrp=%d sid=%d starttime=%d' % sp}")
    by_pid = {pid: (pp, pg, sid, stt) for pid, (pp, pg, sid, stt) in rows}
    fixture_pid = next((pid for pid, (pp, _, _, _) in by_pid.items() if pp == probe.pid and pid != probe.pid), None)
    for pid, (pp, pg, sid, stt) in rows:
        if pid == probe.pid:
            kind = "PROBE"
        elif pid == fixture_pid:
            kind = "FIXTURE"
        else:
            kind = "ESCAPEE"
        print(f"{kind:8s} pid={pid} ppid={pp} pgrp={pg} sid={sid} starttime={stt}")
    spawn_sid = stat(probe.pid)[2]
    for pid, (pp, pg, sid, stt) in rows:
        if pid == probe.pid:
            continue
        print(f"KEY pid={pid} spawn_sid={spawn_sid} sid==spawn_sid:{sid == spawn_sid} "
              f"sid==own_pid:{sid == pid} sid==spawn_pid:{sid == probe.pid}")
    for pid, (pp, pg, sid, stt) in rows:  # self-cleanup: planted by this reproducer
        if pid != probe.pid:
            try:
                os.kill(pid, 9)
            except OSError:
                pass
    probe.kill()
    probe.wait()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
