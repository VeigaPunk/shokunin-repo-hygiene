#!/usr/bin/env python3
"""Attack (c): field-22 starttime is clock ticks since boot (HZ=100 => 10 ms quantum).
Verified: 8 processes spawned back-to-back share ONE starttime (distinct=1). The frozen
guard 'starttime >= spawn' (and even the strict '==' in r99: census/round-99/c2-setup-arms.py:184-186)
is therefore NOT a pid-reuse binder at spawn time: a fresh process spawned in the same tick
as the spawn pid is indistinguishable, so the check passes for it. Exit 0 = evidence collected."""
import os, subprocess, sys

def starttime(pid):
    try:
        with open(f"/proc/{pid}/stat", "rb") as fh:
            d = fh.read()
    except OSError:
        return None
    f = d.rsplit(b")", 1)[1].split()
    return int(f[19])

ps = [subprocess.Popen([sys.executable, "-B", "-c", "import time; time.sleep(3600)"]) for _ in range(8)]
st = [(p.pid, starttime(p.pid)) for p in ps]
print(f"spawned {len(ps)} processes back-to-back; (pid, starttime):")
for pid, s in st:
    print(f"  pid={pid} starttime={s}")
print(f"distinct starttimes = {len({s for _, s in st})} of {len(ps)}")
print(f"SC_CLK_TCK (HZ) = {os.sysconf('SC_CLK_TCK')} -> one tick = {1000/os.sysconf('SC_CLK_TCK'):.0f} ms")
print("TICK-COLLISION VERDICT: 'starttime >= spawn' holds for every same-tick successor,")
print("  and 'starttime == spawn_st' (r99:186) ALSO holds for a same-tick pid-reuse successor.")
print("  Field 22 cannot distinguish a reused pid from the original within the shared tick.")
for p in ps:
    p.kill()
