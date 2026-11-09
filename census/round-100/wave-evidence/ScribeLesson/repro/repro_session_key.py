#!/usr/bin/env python3
"""Reproducer (read-only; signals nothing): can the r100 session key own the T1 setsid escapee?

Runs the COMMITTED r100 counter's own helpers (`_proc_stat`, `_proc_sid`, `_proc_starttime`)
against a LIVE chain built with the counter's own T1 spawn shape:

  counter --(Popen start_new_session=True)--> probe(pid=P)    <- counter records spawn=(P, st(P), sid(P))
  probe   --(Popen start_new_session=True)--> fixture(pid=F)
  fixture --fork--> E, E calls setsid()                        <- the T1 escapee

The ownership predicate under test is the one written in census/round-100/c2-setup-arms.py
`_reap_owned` (the `elif _proc_sid(pid) == spawn_sid and st[1] >= spawn_st` branch, plus the
`pid == spawn_pid` branch).  NOTHING is killed: the escapee child exits on its own.

Structural claim under test: setsid(2) ALWAYS creates a new session (S368), so a process that
called setsid() can never share the session id of the pid recorded at spawn.  If the session
key cannot own the escapee by construction, the r100 frozen target leg (1) `ESCAPEE-ALIVE
alive=0` is unreachable through this key regardless of tuning.

Usage: python3 -B repro_session_key.py <work-dir>
"""
import importlib.util, os, sys, time, subprocess

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
COUNTER = os.path.join(LANE, "census/round-100/c2-setup-arms.py")
spec = importlib.util.spec_from_file_location("r100counter", COUNTER)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
import hashlib
print(f"COUNTER-MODULE {COUNTER}")
print(f"COUNTER-SHA256 {hashlib.sha256(open(COUNTER,'rb').read()).hexdigest()}")

def sf(pid):
    with open(f"/proc/{pid}/stat", "rb") as f:
        data = f.read()
    fl = data.rsplit(b")", 1)[1].split()
    return dict(ppid=int(fl[1]), pgrp=int(fl[2]), sid=int(fl[3]), starttime=int(fl[19]))

def argv_of(pid):
    try:
        return open(f"/proc/{pid}/cmdline","rb").read().decode("utf-8","replace")
    except OSError:
        return ""

def session_members(sid):
    out = []
    for n in os.listdir("/proc"):
        if not n.isdigit(): continue
        try:
            if sf(int(n))["sid"] == sid: out.append(int(n))
        except OSError:
            pass
    return sorted(out)

work = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "work"); os.makedirs(work, exist_ok=True)
probe_p = os.path.join(work, "probe.py"); fix_p = os.path.join(work, "fixture-pipe-holder.py")
open(probe_p,"w").write('''import subprocess, sys
p = subprocess.Popen([sys.executable, "-B", sys.argv[1], sys.argv[2]],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
out, err = p.communicate(timeout=60)
sys.stdout.write(out.decode()); sys.stderr.write(err.decode())
sys.exit(p.returncode)
''')
# Same body as census/round-100/c2-setup-arms.py PIPHOLDER, but the child sleeps and exits
# on its own so this reproducer signals nothing.
open(fix_p,"w").write('''import os, sys, time
pid = os.fork()
if pid == 0:
    os.setsid()
    time.sleep(float(sys.argv[1]))
    os._exit(0)
print("SUMMARY cases=1 tool_pass=1 before_pass=0")
sys.exit(0)
''')

counter_pid = os.getpid()
p = subprocess.Popen([sys.executable,"-B",probe_p,fix_p,"8"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
probe_pid = p.pid
spawn_st = mod._proc_starttime(probe_pid)
spawn_sid = mod._proc_sid(probe_pid)
spawn = (probe_pid, spawn_st, spawn_sid)
print(f"RECORDED-SPAWN spawn_pid={probe_pid} spawn_starttime={spawn_st} spawn_sid={spawn_sid}")

time.sleep(2.0)
escapee = None
for n in os.listdir("/proc"):
    if not n.isdigit(): continue
    pid = int(n)
    if pid in (counter_pid, probe_pid): continue
    try: st = sf(pid)
    except OSError: continue
    if fix_p in argv_of(pid) and st["pgrp"] == pid:      # the setsid child: pgrp == own pid
        escapee = (pid, st); break

if escapee is None:
    print("VERDICT escapee_not_found"); sys.exit(2)
epid, est = escapee
print(f"ESCAPEE pid={epid} ppid={est['ppid']} pgrp={est['pgrp']} sid={est['sid']} starttime={est['starttime']}")
print(f"ESCAPEE argv_carries_token=True")
print(f"SESSION-MEMBERS spawn_sid({spawn_sid}) -> {session_members(spawn_sid)}")
print(f"SESSION-MEMBERS escapee_sid({est['sid']}) -> {session_members(est['sid'])}")
print(f"SID-ALIASING escapee_sid==own_pid: {est['sid']==epid}  spawn_sid==spawn_pid: {spawn_sid==probe_pid}")

owned_a = (epid == spawn[0]) and (est["starttime"] == spawn[1])
owned_b = (mod._proc_sid(epid) == spawn[2]) and (est["starttime"] >= spawn[1])
print(f"PREDICATE branch(a) pid==spawn_pid AND starttime match : owned={owned_a}")
print(f"PREDICATE branch(b) sid==spawn_sid AND starttime>=spawn : owned={owned_b}  (sid_escapee={est['sid']} vs spawn_sid={spawn[2]})")
print(f"OWNED_BY_SESSION_KEY = {owned_a or owned_b}")
print(f"STRUCTURAL escapee_sid != spawn_sid is forced by setsid(2) creating a NEW session (S368): "
      f"{est['sid'] != spawn[2]}")
print(f"VERDICT escapee_owned={owned_a or owned_b}  (r100 rule reaps it? "
      f"{'YES' if (owned_a or owned_b) else 'NO -> ESCAPEE LEAKS, alive=1'})")
p.communicate(timeout=60)
sys.exit(0 if (owned_a or owned_b) else 1)
