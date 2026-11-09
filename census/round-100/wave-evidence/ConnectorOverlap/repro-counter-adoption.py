#!/usr/bin/env python3
"""Measure that the T1 escapee is adopted by the counter (subreaper) and leads its own session.

Mirrors the lane chain: counter sets PR_SET_CHILD_SUBREAPER(1) and Popen(probe, start_new_session=True);
the probe Popen(fixture, start_new_session=True); the fixture forks and the child calls os.setsid().
Prints (pid,(ppid,sid)) of every token carrier at four times; the fixture exits at ~2.5 s, so from then on
the escapee's ppid is the counter stand-in and sid == its own pid.

Read-only (/proc). Self-cleaning: SIGKILLs only the carriers it planted. Exit 0.
Output recorded as reparent.txt (same run shape).
"""
import json, os, subprocess, sys, time

sys.dont_write_bytecode = True

FIX = """import os,sys,time
pid=os.fork()
if pid==0:
    os.setsid(); time.sleep(60); os._exit(0)
time.sleep(2.5)
print("SUMMARY cases=1 tool_pass=1 before_pass=0"); sys.exit(0)
"""
PROBE = """import subprocess,sys,time
p=subprocess.Popen([sys.executable,"-B",sys.argv[1]],start_new_session=True)
p.wait(); time.sleep(0.5)
"""
WRAP = """import ctypes,json,os,subprocess,sys,time
libc=ctypes.CDLL(None,use_errno=True)
libc.prctl(36,1,0,0,0)
v=ctypes.c_int(0); libc.prctl(37,ctypes.byref(v),0,0,0)
p=subprocess.Popen([sys.executable,"-B",sys.argv[1],sys.argv[2]],start_new_session=True)
print(json.dumps({"wrap":os.getpid(),"probe":p.pid,"subreaper":v.value}),flush=True)
time.sleep(9)
"""


def st(pid):
    try:
        d = open(f"/proc/{pid}/stat", "rb").read().rsplit(b")", 1)[1].split()
        return (int(d[1]), int(d[3]))  # (ppid, sid)
    except OSError:
        return None


def carriers(fx):
    out = []
    for n in os.listdir("/proc"):
        if not n.isdigit():
            continue
        try:
            a = open(f"/proc/{n}/cmdline", "rb").read().split(b"\0")
        except OSError:
            continue
        if any(x == fx.encode() for x in a):
            s = st(int(n))
            if s:
                out.append((int(n), s))
    return out


def main(work):
    os.makedirs(work, exist_ok=True)
    fx = os.path.abspath(os.path.join(work, "fixture-pipe-holder.py"))
    open(fx, "w").write(FIX)
    pr = os.path.join(work, "probe-standin.py")
    open(pr, "w").write(PROBE)
    wr = os.path.join(work, "wrap-standin.py")
    open(wr, "w").write(WRAP)
    o = subprocess.Popen([sys.executable, "-B", wr, pr, fx], stdout=subprocess.PIPE, text=True)
    ids = json.loads(o.stdout.readline())
    print("IDS", ids)
    for t in (1.0, 2.0, 3.2, 4.0):
        time.sleep(t if t == 1.0 else 0.8)
        print(f"t={t} carriers={carriers(fx)} wrap_alive={o.poll() is None} subreaper={ids['subreaper']}")
    for pid, _ in carriers(fx):
        try:
            os.kill(pid, 9)
        except OSError:
            pass
    o.wait()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
