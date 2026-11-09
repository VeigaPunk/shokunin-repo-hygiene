#!/usr/bin/env python3
"""Attack (a): field-6 (session) cannot separate escapee from decoy when both share the
counter's session. Mirrors census/round-99/c2-setup-arms.py one() T1 arm + PIPHOLDER:
counter -> probe(start_new_session=True, spawn) -> fixture -> setsid escapee.
Decoy planted 'in the same session the counter runs in' = plain Popen (inherits sid).
Prints /proc/<pid>/stat field 6 for every actor. Exit 0 = evidence collected."""
import os, subprocess, sys, time

def fields(pid):
    try:
        d = open(f"/proc/{pid}/stat", "rb").read()
    except OSError:
        return None
    f = d.rsplit(b")", 1)[1].split()
    return {"ppid": int(f[1]), "pgrp": int(f[2]), "session": int(f[3]),
            "starttime": int(f[19])}

TOKEN = "/fast/scratch/hyaku/souji-r100/ReviewerC1Predicate/token-fixture"

counter_sid = os.getsid(0)
print(f"counter pid={os.getpid()} sid={counter_sid}")

# one() lines 333-334: probe spawned with start_new_session=True -> sid == probe pid.
probe = subprocess.Popen(
    [sys.executable, "-B", "-c", "import time; time.sleep(3600)"],
    start_new_session=True)
time.sleep(0.3)
sf = fields(probe.pid)
print(f"spawn/probe pid={probe.pid} ppid={sf['ppid']} pgrp={sf['pgrp']} session={sf['session']} starttime={sf['starttime']}")
print(f"  recorded spawn session (field 6) = {sf['session']} (== probe pid? {sf['session']==probe.pid})")

# T1 fixture: fork + setsid escapee (PIPHOLDER, census/round-99/c2-setup-arms.py:82-90).
# xecuted rooted at this process with parent in the counter's session, child setsiding.
fx = subprocess.Popen(
    [sys.executable, "-B", "-c",
     "import os,time\npid=os.fork()\nif pid==0:\n os.setsid(); time.sleep(3600); os._exit(0)\ntime.sleep(3600)"])
time.sleep(0.6)
ff = fields(fx.pid)
print(f"fixture pid={fx.pid} ppid={ff['ppid']} pgrp={ff['pgrp']} session={ff['session']} starttime={ff['starttime']}")
escapee = None
for n in os.listdir("/proc"):
    if n.isdigit():
        f2 = fields(int(n))
        if f2 and f2["ppid"] == fx.pid:
            escapee = int(n)
            ef = f2
            print(f"escapee pid={escapee} ppid={ef['ppid']} pgrp={ef['pgrp']} session={ef['session']} starttime={ef['starttime']}")
            print(f"  escapee session == spawn session? {ef['session']==sf['session']} (branch b needs True; branch a needs pid==spawn pid: {escapee}=={probe.pid} False)")

# (a) decoy in the SAME session the counter runs in: plain Popen, inherits counter sid.
decoy = subprocess.Popen(
    [sys.executable, "-B", "-c", "import sys,time; time.sleep(3600)", "--fixture", TOKEN])
time.sleep(0.3)
df = fields(decoy.pid)
print(f"same-session decoy pid={decoy.pid} ppid={df['ppid']} pgrp={df['pgrp']} session={df['session']} starttime={df['starttime']}")
print(f"  decoy session == counter session? {df['session']==counter_sid}")
print(f"  decoy session == spawn session? {df['session']==sf['session']}")
print(f"  escapee session == decoy session? {fields(escapee)['session']==df['session']}")

print("SESSION-EQUALITY VERDICT (frozen predicate, plans/round-100.md:12-15):")
ef = fields(escapee)
print(f"  escapee owned by branch (b) iff escapee_session == spawn_session: {ef['session']==sf['session']}")
print(f"  decoy owned by branch (b) iff decoy_session == spawn_session: {df['session']==sf['session']}")
print(f"  if spawn session were counter sid ({counter_sid}): escapee owned={ef['session']==counter_sid}, decoy owned={df['session']==counter_sid}")
print("  => either assignment treats escapee and same-session decoy IDENTICALLY (both False under")
print("     probe sid, both True under counter sid): no field-6 value separates them.")

for p in (probe, fx, decoy):
    p.kill()
if escapee:
    try:
        os.kill(escapee, 9)
    except Exception:
        pass
time.sleep(0.3)
