#!/usr/bin/env python3
"""SentinelEscapee r100 fidelity dry-reap: the REAL probe (census/round-98/c2-forgery-probe.py) and the
REAL T1 fixture bytes (the counter's own PIPHOLDER source), spawned exactly the way the r100 counter's
`one()` T1 arm spawns the probe (start_new_session=True, stdout/stderr PIPE), with the spawn record
taken exactly as census/round-100/c2-setup-arms.py:349 takes it.

NO live kill: os.kill inside this process is replaced by a recorder before the counter module's
_reap_owned is called, so the ownership predicate is exercised against real live processes without
signalling any of them.

Usage: fidelity_dry_reap.py <lane-repo> <scratch-dir>
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import time

LANE = sys.argv[1]
SCRATCH = sys.argv[2]
WORK = os.path.join(SCRATCH, "fid-work")
COUNTER = os.path.join(LANE, "census/round-100/c2-setup-arms.py")
PROBE = os.path.join(LANE, "census/round-98/c2-forgery-probe.py")
TOOL = os.path.join(LANE, "tools/souji-record-agreement.py")
BEFORE = os.path.join(LANE, "census/round-92/controls/c2-before-tool.py")
sys.dont_write_bytecode = True


def fields(pid):
    try:
        with open(f"/proc/{pid}/stat", "rb") as f:
            return f.read().rsplit(b")", 1)[1].split()
    except OSError:
        return None


def f4(p):
    fl = fields(p)
    return int(fl[1]) if fl else None


def f6(p):
    fl = fields(p)
    return int(fl[3]) if fl else None


def f22(p):
    fl = fields(p)
    return int(fl[19]) if fl else None


def argv_of(p):
    try:
        with open(f"/proc/{p}/cmdline", "rb") as f:
            return f.read().split(b"\x00")
    except OSError:
        return None


def carriers(token):
    out = []
    for n in os.listdir("/proc"):
        if not n.isdigit():
            continue
        p = int(n)
        av = argv_of(p)
        if av and any(a == token.encode() for a in av):
            out.append(p)
    return sorted(out)


def main():
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)
    spec = importlib.util.spec_from_file_location("r100counter", COUNTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # the counter writes the T1 pipe-holder under its --work and reaps on that byte-exact path
    fx = os.path.join(WORK, "fixture-pipe-holder.py")
    with open(fx, "w", encoding="utf-8") as f:
        f.write(mod.PIPHOLDER)
    ident = fx

    # counter-equivalent spawn of the probe, byte-for-byte the r100 `one()` T1 spawn (start_new_session)
    p = subprocess.Popen([sys.executable, "-B", PROBE, "--fixture", fx, "--tool", TOOL, "--before", BEFORE,
                           "--work", os.path.join(WORK, "T1"), "--timeout", "6"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    spawn = (p.pid, f22(p.pid), f6(p.pid))
    print(f"SPAWN-RECORD pid={spawn[0]} starttime={spawn[1]} sid={spawn[2]} "
          f"(r100:349 records exactly these three)")
    so, se = p.communicate(timeout=120)
    print(f"PROBE exit={p.returncode} stdout_last={so.decode('utf-8','replace').strip().splitlines()[-1:]} "
          f"stderr_last={se.decode('utf-8','replace').strip().splitlines()[-1:]}")
    time.sleep(1.0)

    live = carriers(ident)
    print(f"TOKEN-CARRIERS live={live}")
    for q in live:
        print(f"CARRIER pid={q} sid={f6(q)} starttime={f22(q)} ppid={f4(q)} "
              f"sid_is_own_pid={f6(q) == q} sid_eq_spawn_sid={f6(q) == spawn[2]} "
              f"argv={[a.decode('utf-8','replace') for a in (argv_of(q) or [])]}")

    # exact r100 predicate, transcribed from census/round-100/c2-setup-arms.py:198-203
    print("--- r100 predicate (lines 198-203) per live token carrier ---")
    for q in live:
        st, sid = f22(q), f6(q)
        if q == spawn[0]:
            owned, branch = (st == spawn[1]), "a"
        elif sid is not None and sid == spawn[2] and st is not None and st >= spawn[1]:
            owned, branch = True, "b"
        else:
            owned, branch = False, "-"
        print(f"PRED pid={q} sid={sid} starttime={st} branch={branch} owned={owned}")

    recorded = []
    real_kill = os.kill
    try:
        os.kill = lambda pid, sig: recorded.append((pid, sig))
        killed = mod._reap_owned(ident, (os.getpid(), p.pid), spawn)
    finally:
        os.kill = real_kill
    print(f"DRY-REAP owned_count={killed} would_signal={sorted(recorded)} "
          f"live_carriers={live} carriers_in_would_signal="
          f"{sorted(set(q for q, _ in recorded) & set(live))}")
    print("DRY-REAP-DONE")


if __name__ == "__main__":
    sys.exit(main())
