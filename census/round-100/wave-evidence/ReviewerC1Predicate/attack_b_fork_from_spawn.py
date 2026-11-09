#!/usr/bin/env python3
"""Attack (b): decoy planted as a plain child of the SPAWN pid (fork from the arm's session,
no setsid) inherits the spawn session; under frozen branch (b) (session == spawn session AND
token-carrying) it is owned and killed, exactly like the escapee. Exit 0 = evidence collected."""
import os
import subprocess
import sys
import time


def fields(pid):
    try:
        with open(f"/proc/{pid}/stat", "rb") as fh:
            d = fh.read()
    except OSError:
        return None
    f = d.rsplit(b")", 1)[1].split()
    return {
        "ppid": int(f[1]),
        "pgrp": int(f[2]),
        "session": int(f[3]),
        "starttime": int(f[19]),
    }


# The spawn/probe: start_new_session=True (one(), census/round-99/c2-setup-arms.py:333-334).
PARENT = """
import os, sys, time
pid = os.fork()              # plain fork: NO setsid -> inherits spawn session
if pid == 0:
    time.sleep(3600); os._exit(0)
time.sleep(3600)
"""
probe = subprocess.Popen([sys.executable, "-B", "-c", PARENT], start_new_session=True)
time.sleep(0.7)
sf = fields(probe.pid)
print(f"spawn/probe pid={probe.pid} session={sf['session']} starttime={sf['starttime']}")

decoy = None
for n in os.listdir("/proc"):
    if n.isdigit():
        f2 = fields(int(n))
        if f2 and f2["ppid"] == probe.pid:
            decoy = int(n)
            df = f2
            print(f"forked decoy pid={decoy} ppid={df['ppid']} pgrp={df['pgrp']} "
                  f"session={df['session']} starttime={df['starttime']}")
            print(f"  decoy session == spawn session? {df['session'] == sf['session']}")

TOKEN = "/fast/scratch/hyaku/souji-r100/ReviewerC1Predicate/token-fixture"
print(f"  token carried in this demo argv? No (session leg is independent); a real decoy")
print(f"  would carry {TOKEN} byte-exactly (census/round-99/c2-decoy-test.py:104).")
print("BRANCH-(b) VERDICT on forked decoy: session leg True => owned (killed) if it carries the token.")
print("  The escapee does NOT share the spawn session (setsid => session == own pid; see attack_a),")
print("  so branch (b) misses the escapee while hitting the forked decoy: it discriminates backwards.")
print("  'Not a foreign decoy' cannot rescue: the decoy now IS local by session, and no other field differs.")
probe.kill()
if decoy:
    try:
        os.kill(decoy, 9)
    except Exception:
        pass
time.sleep(0.3)
