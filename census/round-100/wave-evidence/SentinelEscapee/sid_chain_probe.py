#!/usr/bin/env python3
"""SentinelEscapee r100 shape probe: session-id chain of the T1 fixture shape + a DRY evaluation of the
r100 counter's ownership predicate. NO live kill: os.kill is monkeypatched to a recorder inside this
process only.

What it measures (all read-only against /proc, plus its OWN planted processes under the seat scratch dir):
  1. the session id (stat field 6) of: this driver, the probe-equivalent, the T1 fixture, the setsid
     escapee -- and whether the escapee's session id equals the probe's recorded session id;
  2. the r100 predicate's verdict for each planted pid, evaluated with the EXACT expressions read out
     of census/round-100/c2-setup-arms.py lines 198-203 (branch a/b);
  3. a dry run of _reap_owned (kill replaced by a recorder) to see which pids the r100 rule would signal;
  4. the escapee's open fds (which pipes it still holds).

Usage: sid_chain_probe.py <lane-repo> <scratch-dir>
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import time

LANE = sys.argv[1]
SCRATCH = sys.argv[2]
WORK = os.path.join(SCRATCH, "shape-work")
COUNTER = os.path.join(LANE, "census/round-100/c2-setup-arms.py")
sys.dont_write_bytecode = True


def stat_fields(pid):
    """Return the post-comm field list of /proc/<pid>/stat as strings, or None."""
    try:
        with open(f"/proc/{pid}/stat", "rb") as f:
            data = f.read()
    except OSError:
        return None
    return data.rsplit(b")", 1)[1].split()


def f4(pid):   # ppid
    fl = stat_fields(pid)
    return int(fl[1]) if fl else None


def f6(pid):   # session id
    fl = stat_fields(pid)
    return int(fl[3]) if fl else None


def f22(pid):  # starttime
    fl = stat_fields(pid)
    return int(fl[19]) if fl else None


def argv_of(pid):
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            return f.read().split(b"\x00")
    except OSError:
        return None


def fds_of(pid):
    out = []
    d = f"/proc/{pid}/fd"
    try:
        names = os.listdir(d)
    except OSError:
        return out
    for n in names:
        try:
            out.append((n, os.readlink(os.path.join(d, n))))
        except OSError:
            pass
    return out


def find_by_argv(exact):
    """Return pids whose argv contains `exact` as a standalone element."""
    hits = []
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        pid = int(name)
        av = argv_of(pid)
        if av and any(a == exact.encode() for a in av):
            hits.append(pid)
    return sorted(hits)


def main():
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)
    # The counter's own T1 fixture source, taken from the lane file (read-only) with the sleep bounded
    # so the planted escapee leaves on its own -- no signal is sent to it at any point.
    spec = importlib.util.spec_from_file_location("r100counter", COUNTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fixture_src = mod.PIPHOLDER.replace("time.sleep(3600)", "time.sleep(120)")
    fx = os.path.join(WORK, "fixture-pipe-holder.py")
    with open(fx, "w", encoding="utf-8") as f:
        f.write(fixture_src)
    ident = fx  # the counter reaps on the arm's fixture path, byte-exact

    # probe-equivalent: spawns the fixture with start_new_session=True and PIPE stdout/stderr, exactly
    # like census/round-98/c2-forgery-probe.py's run(); then waits for pipe EOF, times out (the escapee
    # holds the pipes) and exits 2 like the probe's Fatal path.
    probe_src = (
        "import os, selectors, signal, subprocess, sys, time\n"
        "fx = sys.argv[1]\n"
        "p = subprocess.Popen([sys.executable, '-B', fx, '--tool', fx, '--before', fx, '--work', os.path.dirname(fx)],\n"
        "                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)\n"
        "sel = selectors.DefaultSelector()\n"
        "for f in (p.stdout, p.stderr):\n"
        "    os.set_blocking(f.fileno(), False); sel.register(f, selectors.EVENT_READ)\n"
        "deadline = time.monotonic() + 15\n"
        "while sel.get_map():\n"
        "    if time.monotonic() > deadline:\n"
        "        try: os.killpg(p.pid, signal.SIGKILL)\n"
        "        except ProcessLookupError: pass\n"
        "        break\n"
        "    for key, _ in sel.select(timeout=0.25):\n"
        "        try:\n"
        "            if not os.read(key.fileobj.fileno(), 65536): sel.unregister(key.fileobj)\n"
        "        except BlockingIOError: pass\n"
        "p.wait()\n"
        "print('PROBE-SUMMARY timeout=1 escapee_held_pipes=1')\n"
        "sys.exit(2)\n"
    )
    probe = subprocess.Popen([sys.executable, "-B", "-c", probe_src, fx],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    time.sleep(2.0)

    carriers = find_by_argv(fx)
    fixture_pids = [p for p in carriers if f4(p) == probe.pid]
    escapee_pids = [p for p in carriers if p not in fixture_pids and p != probe.pid]

    spawn = (probe.pid, f22(probe.pid), f6(probe.pid))
    print(f"DRIVER pid={os.getpid()} sid={f6(os.getpid())}")
    print(f"PROBE  pid={probe.pid} sid={f6(probe.pid)} starttime={f22(probe.pid)} ppid={f4(probe.pid)}")
    for p in fixture_pids:
        print(f"FIXTURE pid={p} sid={f6(p)} starttime={f22(p)} ppid={f4(p)}")
    for p in escapee_pids:
        print(f"ESCAPEE pid={p} sid={f6(p)} starttime={f22(p)} ppid={f4(p)} "
              f"sid_is_own_pid={f6(p) == p} sid_eq_probe_sid={f6(p) == spawn[2]} "
              f"ppid_chain_reaches_probe={_reaches(p, probe.pid)}")
    print(f"SPAWN-RECORD (as r100 line 349 records it) spawn_pid={spawn[0]} spawn_starttime={spawn[1]} "
          f"spawn_sid={spawn[2]}")

    # --- the r100 predicate, transcribed from census/round-100/c2-setup-arms.py:198-203 ---
    print("--- predicate evaluation (r100 lines 198-203, transcribed) ---")
    for p in sorted(set(carriers + [probe.pid])):
        st = f22(p)
        sid = f6(p)
        if p == spawn[0]:
            owned = (st == spawn[1])
            branch = "a"
        elif sid is not None and sid == spawn[2] and st is not None and st >= spawn[1]:
            owned = True
            branch = "b"
        else:
            owned = False
            branch = "-"
        print(f"PRED pid={p} sid={sid} starttime={st} branch={branch} owned={owned}")

    # --- dry run of _reap_owned with os.kill replaced by a recorder ---
    recorded = []
    real_kill = os.kill
    try:
        os.kill = lambda pid, sig: recorded.append((pid, sig))
        killed = mod._reap_owned(ident, (os.getpid(), probe.pid), spawn)
    finally:
        os.kill = real_kill
    print(f"DRY-REAP owned_count={killed} would_signal={sorted(recorded)} "
          f"escapee_pids={escapee_pids} escapee_in_would_signal="
          f"{sorted(set(p for p, _ in recorded) & set(escapee_pids))}")

    # --- what the escapee still holds open ---
    for p in escapee_pids:
        held = fds_of(p)
        pipes = sorted({t for _, t in held if t.startswith("pipe:")})
        print(f"ESCAPEE-FDS pid={p} n={len(held)} pipes={pipes}")

    probe.terminate()
    try:
        probe.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    print("PROBE-DONE")


def _reaches(pid, ancestor):
    seen = set()
    cur = pid
    while cur is not None and cur > 0 and cur not in seen:
        if cur == ancestor:
            return True
        seen.add(cur)
        cur = f4(cur)
    return False


if __name__ == "__main__":
    sys.exit(main())
