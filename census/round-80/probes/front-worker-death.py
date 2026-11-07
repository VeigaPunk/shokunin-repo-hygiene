#!/usr/bin/env python3
"""souji r80 repair-2 probe (after the wave): two front behaviours the frozen C2 rows do not reach, found by
non-author seats.

  worker-killed  S80Sentinel F3: the WORKER dies without the front's trap (SIGKILL, OOM) while a bounded child
                 hangs at the file digest (the q4 shim); the front's `wait` returns 137 and, before repair 2, the
                 worker's `$(...)` subshells and the timeout group ran on. Pass: the front exits 137 (the worker's
                 status, passed through), and no process carrying the row nonce is alive 2 s later.
  tmpdir-missing S80ExecEvade F4: TMPDIR names a directory that does not exist; the base tool exits 1 (its ERRTMP
                 mktemp fails, the "could-not-evaluate setup" class) and the W2 front exited 2 (the usage class).
                 Pass: the tool's exit code equals the base tool's (1) for a plain --dry-run on a fixture.

`ARM <name> ok=<y|n> ...` per arm; `SUMMARY arms=<N> failed=<F>`; exit 0 iff F == 0, 1 otherwise, 2 usage.
"""
import argparse
import importlib.util
import os
import secrets
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("c2c", os.path.join(HERE, "..", "c2-signal-counter.py"))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def env_for(rowdir, target, fleet, ledger, engine, shimdir, nonce, mark, tmpdir, point):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SOUJI_"))}
    env.update({"PATH": shimdir + os.pathsep + os.environ.get("PATH", ""), "TMPDIR": tmpdir, "LC_ALL": "C",
                "SOUJI_R80_NONCE": nonce, "SOUJI_R80_MARK": mark, "SOUJI_R80_TARGET": target,
                "SOUJI_VERIFY_BIN": engine, "SOUJI_Q_SHOKUNIN_ROOT": fleet, "SOUJI_Q_LEDGER": ledger,
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    if point:
        env["SOUJI_R80_POINT"] = point
    return env


def children(pid):
    try:
        with open(f"/proc/{pid}/task/{pid}/children", encoding="ascii") as f:
            return [int(x) for x in f.read().split()]
    except OSError:
        return []


def arm_worker_killed(tool, engine, shimdir, work):
    rowdir = os.path.join(work, "worker-killed")
    fleet, repo, ledger, target = C.build(rowdir, "file")
    tmpdir = os.path.join(rowdir, "tmp")
    os.makedirs(tmpdir)
    nonce, mark = secrets.token_hex(8), os.path.join(rowdir, "hang.mark")
    env = env_for(rowdir, target, fleet, ledger, engine, shimdir, nonce, mark, tmpdir, "file-digest")
    t0 = time.monotonic()
    p = subprocess.Popen(["bash", tool, "--dry-run", repo, target], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, env=env, cwd=rowdir,
                         start_new_session=True, preexec_fn=C._preexec)
    rc, surv, worker = None, [], None
    try:
        while not os.path.exists(mark) and p.poll() is None and time.monotonic() - t0 < C.MARK_TIMEOUT:
            time.sleep(0.05)
        if not os.path.exists(mark):
            return False, "error=hang point never reached"
        time.sleep(0.3)
        kids = children(p.pid)
        if len(kids) != 1:
            return False, f"error=front has {len(kids)} children, expected the worker only"
        worker = kids[0]
        os.kill(worker, signal.SIGKILL)
        try:
            rc = p.wait(timeout=C.SETTLE)
        except subprocess.TimeoutExpired:
            rc = None
        time.sleep(2.0)
        surv = C.nonce_pids(nonce)
    finally:
        C.reap(nonce)
        if p.poll() is None:
            p.kill()
        p.wait()
    ok = rc == 137 and not surv
    return ok, f"front_rc={rc} survivors={len(surv)}"


def arm_tmpdir_missing(tool, engine, shimdir, work):
    rowdir = os.path.join(work, "tmpdir-missing")
    fleet, repo, ledger, target = C.build(rowdir, "file")
    nonce, mark = secrets.token_hex(8), os.path.join(rowdir, "hang.mark")
    env = env_for(rowdir, target, fleet, ledger, engine, shimdir, nonce, mark,
                  os.path.join(rowdir, "no-such-dir"), None)
    p = subprocess.run(["bash", tool, "--dry-run", repo, target], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       stdin=subprocess.DEVNULL, env=env, cwd=rowdir, timeout=60, preexec_fn=C._preexec)
    C.reap(nonce)
    return p.returncode == 1, f"rc={p.returncode} (base tool: 1)"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool-dir", required=True)
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    tool = os.path.join(os.path.abspath(ns.tool_dir), "souji-quarantine.sh")
    engine = os.path.join(os.path.abspath(ns.tool_dir), "souji-verify.sh")
    work = os.path.abspath(ns.work)
    if not (os.path.isfile(tool) and os.path.isfile(engine)):
        print("PROBE-FATAL: tool dir incomplete", file=sys.stderr)
        return 2
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")) or (
            os.path.exists(work) and os.listdir(work)):
        print("PROBE-FATAL: --work must be empty and not under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    print(C.launch_line())
    print(f"# tool sha256={C.sha(tool)} probe sha256={C.sha(os.path.abspath(__file__))}")
    shimdir = os.path.join(work, "shim")
    C.make_shims(shimdir)
    failed = 0
    for name, fn in (("worker-killed", arm_worker_killed), ("tmpdir-missing", arm_tmpdir_missing)):
        try:
            ok, detail = fn(tool, engine, shimdir, work)
        except (C.FixtureError, OSError, subprocess.SubprocessError) as exc:
            ok, detail = False, f"error={type(exc).__name__}: {str(exc)[:120]}"
        failed += 0 if ok else 1
        print(f"ARM {name} ok={'y' if ok else 'n'} {detail}")
    print(f"SUMMARY arms=2 failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
