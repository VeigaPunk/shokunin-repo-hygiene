#!/usr/bin/env python3
"""S80Sentinel probe v2: drive the W2 front/worker with controlled signals.

Every signal goes only to a process this script started (a direct or indirect
child).  Fixtures are built by the frozen r80 C2 instrument's own builder.
"""
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time

COUNTER = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-80/c2-signal-counter.py"
BASE = "/fast/scratch/hyaku/souji-r80/S80Sentinel"
TOOL = os.path.join(BASE, "tool.sh")
WRAP_SESSION = os.path.join(BASE, "wrap-session.sh")
WRAP_WORKER = os.path.join(BASE, "wrap-worker.sh")
STUB_HANG = os.path.join(BASE, "stub-hang.sh")
STUB_SAFE = os.path.join(BASE, "stub-safe.sh")


def load_counter():
    spec = importlib.util.spec_from_file_location("c2", COUNTER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def stat_fields(pid):
    try:
        with open(f"/proc/{pid}/stat", "rb") as f:
            st = f.read()
    except OSError:
        return None
    return st.rsplit(b")", 1)[1].split()


def proc_sid(pid):
    f = stat_fields(pid)
    return int(f[3]) if f else None


def alive(pid):
    f = stat_fields(pid)
    return bool(f) and f[0] != b"Z"


def argv_of(pid):
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            return f.read().replace(b"\0", b" ").decode("utf-8", "replace").strip()
    except OSError:
        return ""


def tool_pids():
    out = []
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        p = int(d)
        if not alive(p):
            continue
        a = argv_of(p)
        if TOOL in a or "stub-hang.sh" in a or "stub-safe.sh" in a or "/S80Sentinel/cases/" in a:
            out.append(p)
    return out


def cleanup(base=BASE, quiet=True):
    victims = set(tool_pids())
    key = b"SOUJI_S80_STUB_LOG="
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        p = int(d)
        if not alive(p) or p == os.getpid():
            continue
        try:
            with open(f"/proc/{p}/environ", "rb") as f:
                envv = f.read()
        except OSError:
            continue
        if key in envv and base.encode() in envv:
            victims.add(p)
    victims.discard(os.getpid())
    for p in victims:
        try:
            os.kill(p, signal.SIGKILL)
        except OSError:
            pass
    time.sleep(0.2)
    return sorted(victims)


def env_for():
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SOUJI_"))}
    env.update({"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    return env


def read_text(path):
    try:
        with open(path, "rb") as f:
            return f.read().decode("utf-8", "replace")
    except OSError:
        return ""


def new_case(m, name):
    rowdir = os.path.join(BASE, "cases", name)
    subprocess.run(["rm", "-rf", rowdir], check=True)
    os.makedirs(rowdir)
    fleet, repo, ledger, target = m.build(rowdir, "file")
    return rowdir, fleet, repo, ledger, target


def run(name, action, env_extra=None, wrapper=None, new_session=True, stub=STUB_HANG,
        want_stub=True, wait_after=15):
    m = load_counter()
    rowdir, fleet, repo, ledger, target = new_case(m, name)
    tmpdir = os.path.join(rowdir, "tmp")
    os.makedirs(tmpdir)
    log = os.path.join(rowdir, "stub.log")
    env = env_for()
    env.update({"TMPDIR": tmpdir, "SOUJI_VERIFY_BIN": stub, "SOUJI_S80_STUB_LOG": log,
                "SOUJI_Q_SHOKUNIN_ROOT": fleet, "SOUJI_Q_LEDGER": ledger})
    if env_extra:
        env.update(env_extra)
    argv = ["bash", wrapper or TOOL, "--dry-run", repo, target]
    outp, errp = os.path.join(rowdir, "out"), os.path.join(rowdir, "err")
    with open(outp, "wb") as fo, open(errp, "wb") as fe:
        p = subprocess.Popen(argv, stdout=fo, stderr=fe, stdin=subprocess.DEVNULL,
                             env=env, start_new_session=new_session, cwd=rowdir)
    res = {"case": name, "front": p.pid, "front_sid": proc_sid(p.pid), "action": action,
           "env_extra": env_extra, "wrapper": wrapper, "new_session": new_session,
           "stub_bin": stub}
    stub_pid = stub_ppid = None
    if want_stub:
        t0 = time.time()
        while time.time() - t0 < 20:
            if os.path.exists(log) and os.path.getsize(log) > 0:
                line = read_text(log).splitlines()[0]
                f = line.split("\t")
                stub_pid, stub_ppid = int(f[0]), int(f[1])
                break
            if p.poll() is not None:
                break
            time.sleep(0.02)
    res["stub"] = stub_pid
    res["stub_parent"] = stub_ppid
    # process tree while the tool is live
    tree = []
    for x in sorted(set(tool_pids() + ([stub_pid] if stub_pid and alive(stub_pid) else []))):
        f = stat_fields(x)
        if f:
            tree.append({"pid": x, "state": f[0].decode(), "ppid": int(f[1]), "pgrp": int(f[2]),
                         "sid": int(f[3]), "argv": argv_of(x)[:100]})
    res["tree"] = tree
    # private dir / leftovers while live
    top = sorted(os.listdir(tmpdir))
    res["tmp_top_live"] = top
    priv = [x for x in top if x.startswith("souji-quarantine.") and os.path.isdir(os.path.join(tmpdir, x))]
    res["private_dirs"] = priv
    if priv:
        res["private_mode"] = oct(os.stat(os.path.join(tmpdir, priv[0])).st_mode & 0o7777)
        res["private_files"] = sorted(os.listdir(os.path.join(tmpdir, priv[0])))
    # action
    sig = None
    try:
        if action == "term-front":
            sig = signal.SIGTERM
            os.kill(p.pid, sig)
        elif action == "kill-front":
            sig = signal.SIGKILL
            os.kill(p.pid, sig)
        elif action == "kill-worker":
            cands = [x for x in tool_pids() if proc_sid(x) == x and x != p.pid]
            res["worker"] = cands[0] if cands else None
            if cands:
                sig = signal.SIGKILL
                os.kill(cands[0], sig)
        elif action == "term-inline":
            sig = signal.SIGTERM
            os.kill(p.pid, sig)
        elif action == "none":
            pass
        try:
            p.wait(timeout=wait_after)
        except subprocess.TimeoutExpired:
            res["front_still_running_after_wait"] = True
            p.kill()
            p.wait()
    finally:
        pass
    out = read_text(outp)
    err = read_text(errp)
    top_after = sorted(os.listdir(tmpdir))
    res.update({
        "signal": int(sig) if sig else None,
        "rc": p.returncode,
        "signal_lines": [l for l in out.splitlines() if l.startswith("SIGNAL\t")],
        "result_lines": [l for l in out.splitlines() if l.startswith("RESULT\t")],
        "guard_lines": [l for l in out.splitlines() if l.startswith("GUARD\t")],
        "stub_alive_after": bool(stub_pid and alive(stub_pid)),
        "tool_pids_after": tool_pids(),
        "tmp_top_after": top_after,
        "out": out,
        "err": err,
    })
    res["killed_at_cleanup"] = cleanup()
    res["tool_pids_final"] = tool_pids()
    print(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    what = sys.argv[1]
    table = {
        "term-front": ("t1-term-front", "term-front", {}, None, True, STUB_HANG, True, 15),
        "kill-front": ("t2-kill-front", "kill-front", {}, None, True, STUB_HANG, True, 15),
        "kill-worker": ("t3-kill-worker", "kill-worker", {}, None, True, STUB_HANG, True, 15),
        "none": ("t4-none", "none", {}, None, True, STUB_HANG, True, 2),
        "inline-session": ("t5-inline-session", "term-inline", {}, WRAP_SESSION, True, STUB_HANG, True, 15),
        "worker-env": ("t6-worker-env", "term-inline", {"SOUJI_Q_WORKER": "1"}, WRAP_WORKER, True,
                       STUB_HANG, True, 15),
        "worker-env-nosession": ("t7-worker-env-nosession", "none", {"SOUJI_Q_WORKER": "1"}, None,
                                 False, STUB_HANG, False, 20),
        "safe-normal": ("t8-safe-normal", "none", {}, None, True, STUB_SAFE, False, 20),
    }
    a = table[what]
    run(*a)
