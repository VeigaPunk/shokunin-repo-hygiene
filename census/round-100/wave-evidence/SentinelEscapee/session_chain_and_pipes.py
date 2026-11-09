#!/usr/bin/env python3
"""SentinelEscapee r100 containment probe: the session chain of the T1 fixture shape and who holds which
pipe after the "counter" exits. NO live kill: nothing here is signalled; the planted sleeper exits on its own.

Replicates the real chain:
  driver(=counter) --Popen(start_new_session=True, stdout=PIPE, stderr=PIPE)--> probe
  probe            --Popen(start_new_session=True, stdout=PIPE, stderr=PIPE)--> fixture (PIPHOLDER bytes)
  fixture          --fork--> escapee (os.setsid(); sleep)
which is exactly census/round-100/c2-setup-arms.py:347-349 -> census/round-98/c2-forgery-probe.py:147 ->
the counter's own PIPHOLDER constant.

Measured:
  * stat field 6 (session id) of driver / probe / fixture / escapee, sampled while each is alive;
  * which pipe inodes the escapee still holds after the probe exited (the r99 Sentinel FINDING 2 carry);
  * whether the driver's own stdout pipe (the pipe a driver would use with subprocess.PIPE) is held by
    the escapee after the counter exited.

Usage: session_chain_and_pipes.py <lane-repo> <scratch-dir>
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import time

LANE = sys.argv[1]
SCRATCH = sys.argv[2]
WORK = os.path.join(SCRATCH, "chain-work")
COUNTER = os.path.join(LANE, "census/round-100/c2-setup-arms.py")
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


def fd_table(pid):
    rows = []
    d = f"/proc/{pid}/fd"
    try:
        names = sorted(os.listdir(d), key=lambda x: int(x))
    except OSError:
        return rows
    for n in names:
        try:
            rows.append((n, os.readlink(os.path.join(d, n))))
        except OSError:
            pass
    return rows


def pipe_inode(path_fd):
    try:
        st = os.fstat(path_fd)
        return st.st_ino
    except OSError:
        return None


def main():
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)
    spec = importlib.util.spec_from_file_location("r100counter", COUNTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fx = os.path.join(WORK, "fixture-pipe-holder.py")
    with open(fx, "w", encoding="utf-8") as f:
        f.write(mod.PIPHOLDER.replace("time.sleep(3600)", "time.sleep(45)"))

    # the driver's own stdout pipe (what a driver using subprocess.PIPE would wait EOF on)
    dr, dw = os.pipe()
    driver_out_ino = pipe_inode(dw)

    # probe-equivalent: spawns the fixture with start_new_session=True and PIPE stdout/stderr
    probe_src = (
        "import os, selectors, signal, subprocess, sys, time\n"
        "fx = sys.argv[1]\n"
        "p = subprocess.Popen([sys.executable, '-B', fx, '--tool', fx, '--before', fx, '--work', os.path.dirname(fx)],\n"
        "                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)\n"
        "print('PROBE-FIXTURE-PID', p.pid, flush=True)\n"
        "sel = selectors.DefaultSelector()\n"
        "for f in (p.stdout, p.stderr):\n"
        "    os.set_blocking(f.fileno(), False); sel.register(f, selectors.EVENT_READ)\n"
        "deadline = time.monotonic() + 8\n"
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
        "sys.exit(2)\n"
    )
    probe = subprocess.Popen([sys.executable, "-B", "-c", probe_src, fx],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             stdin=subprocess.DEVNULL, start_new_session=True)
    print(f"DRIVER  pid={os.getpid()} sid={f6(os.getpid())} driver_stdout_pipe_ino={driver_out_ino}")
    print(f"PROBE   pid={probe.pid} sid={f6(probe.pid)} starttime={f22(probe.pid)} "
          f"sid_is_own_pid={f6(probe.pid) == probe.pid}")

    # sample the fixture's sid while it is alive (it prints SUMMARY and exits at once)
    fixture_pid = None
    escapee_pid = None
    t0 = time.time()
    while time.time() - t0 < 6:
        for n in os.listdir("/proc"):
            if not n.isdigit():
                continue
            p = int(n)
            av = argv_of(p)
            if not av or not any(a == fx.encode() for a in av):
                continue
            if p == probe.pid:
                continue
            sid = f6(p)
            if fixture_pid is None and sid == probe.pid:
                fixture_pid = p
                print(f"FIXTURE pid={p} sid={sid} starttime={f22(p)} ppid={f4(p)} "
                      f"sid_eq_probe_sid={sid == f6(probe.pid)}")
            elif escapee_pid is None and sid == p:
                escapee_pid = p
                print(f"ESCAPEE pid={p} sid={sid} starttime={f22(p)} ppid={f4(p)} "
                      f"sid_is_own_pid=True sid_eq_probe_sid={sid == f6(probe.pid)}")
        if escapee_pid:
            break
        time.sleep(0.05)

    probe.wait(timeout=30)
    print(f"PROBE exit={probe.returncode}")
    time.sleep(0.5)

    # after the probe (and thus the fixture) exited: who is left and what does it hold?
    print("--- after the probe exited ---")
    left = []
    for n in os.listdir("/proc"):
        if not n.isdigit():
            continue
        p = int(n)
        av = argv_of(p)
        if av and any(a == fx.encode() for a in av):
            left.append(p)
    for p in sorted(left):
        rows = fd_table(p)
        pipes = sorted({t for _, t in rows if t.startswith("pipe:")})
        print(f"SURVIVOR pid={p} sid={f6(p)} starttime={f22(p)} ppid={f4(p)} "
              f"sid_eq_probe_sid={f6(p) == f6(probe.pid)} fd_count={len(rows)} pipes={pipes} "
              f"holds_driver_stdout_pipe={any('pipe:[%d]' % driver_out_ino == t for _, t in rows)}")
        for fd, tgt in rows:
            print(f"  fd={fd} -> {tgt}")

    # does the driver's own stdout pipe still see EOF? (write end still open in the driver, so force-close it)
    os.close(dw)
    os.set_blocking(dr, False)
    try:
        data = os.read(dr, 1)
        print(f"DRIVER-PIPE after counter exit: read={data!r} (b'' means EOF reached)")
    except BlockingIOError:
        print("DRIVER-PIPE after counter exit: no data and no EOF (still open)")
    os.close(dr)
    print("CHAIN-DONE")


if __name__ == "__main__":
    sys.exit(main())
