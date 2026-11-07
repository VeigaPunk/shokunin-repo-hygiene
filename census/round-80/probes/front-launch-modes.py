#!/usr/bin/env python3
"""souji r80 repair probe (after the wave): the quarantine front/worker split under two launch conditions the
frozen C2 rows do not vary, found by non-author seats (S80CriticClaims item 10, S80CriticDiscern F1; S80ExecEvade F2):

  monitor  the caller exports SHELLOPTS=monitor (job control on in the tool's shell): the worker job becomes a
           process-group leader, setsid forks (S328), the front's `$!` is setsid's parent and exits at once.
           Arms: the frozen C2 rows q4 (TERM at the file digest) and p1 (no signal), run through the frozen
           counter's own run_row with SHELLOPTS=monitor in the counter's environment.
  spoof    the caller exports SOUJI_Q_SESSION=<its own session id>: the nested-call branch ran the tool inline,
           without the front. Arm: TERM at the file digest (shim as in q4), tool started in the probe's session.

Each arm prints `ARM <name> ok=<y|n> ...`; `SUMMARY arms=<N> failed=<F>`; exit 0 iff F == 0, 1 otherwise, 2 usage.
A tool that still breaks under either condition fails the arm, so this probe fails on the W2 tool bytes
(836dac3e) and is the failing-before control of the repair.
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
ROWS = {r[0]: r for r in C.ROUTES}


def arm_monitor(tool, engine, stubs, shimdir, work, rid):
    _, sig, point, kind, ekind, ev = ROWS[rid]
    old = os.environ.get("SHELLOPTS")
    os.environ["SHELLOPTS"] = "monitor"
    try:
        ok, exited, rc, sigline, verdict, ns_, nl, secs, ign, where, _ = C.run_row(
            tool, engine, stubs, os.path.join(work, f"monitor-{rid}"), rid, sig, point, kind, ekind, ev, shimdir)
    except (C.FixtureError, OSError, subprocess.SubprocessError) as exc:
        return False, f"error={type(exc).__name__}: {str(exc)[:120]}"
    finally:
        if old is None:
            del os.environ["SHELLOPTS"]
        else:
            os.environ["SHELLOPTS"] = old
    return ok, f"rc={rc} signal_line={'y' if sigline else 'n'} verdict={verdict} survivors={ns_} tmpleft={nl}"


def arm_spoof(tool, engine, shimdir, work):
    rowdir = os.path.join(work, "spoof-term-file-digest")
    fleet, repo, ledger, target = C.build(rowdir, "file")
    tmpdir = os.path.join(rowdir, "tmp")
    os.makedirs(tmpdir)
    nonce, mark = secrets.token_hex(8), os.path.join(rowdir, "hang.mark")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SOUJI_"))}
    env.update({"PATH": shimdir + os.pathsep + os.environ.get("PATH", ""), "TMPDIR": tmpdir, "LC_ALL": "C",
                "SOUJI_R80_NONCE": nonce, "SOUJI_R80_MARK": mark, "SOUJI_R80_TARGET": target,
                "SOUJI_R80_POINT": "file-digest", "SOUJI_VERIFY_BIN": engine, "SOUJI_Q_SHOKUNIN_ROOT": fleet,
                "SOUJI_Q_LEDGER": ledger, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                "SOUJI_Q_SESSION": str(os.getsid(0))})
    out = os.path.join(rowdir, "tool.out")
    t0 = time.monotonic()
    with open(out, "wb") as fo:
        p = subprocess.Popen(["bash", tool, "--dry-run", repo, target], stdout=fo, stderr=subprocess.DEVNULL,
                             stdin=subprocess.DEVNULL, env=env, cwd=rowdir, preexec_fn=C._preexec)
    exited = False
    try:
        while not os.path.exists(mark) and p.poll() is None and time.monotonic() - t0 < C.MARK_TIMEOUT:
            time.sleep(0.05)
        if not os.path.exists(mark):
            return False, "error=hang point never reached"
        time.sleep(0.3)
        os.kill(p.pid, signal.SIGTERM)
        try:
            p.wait(timeout=C.SETTLE)
            exited = True
        except subprocess.TimeoutExpired:
            pass
        time.sleep(1.0)
        surv = C.nonce_pids(nonce)
    finally:
        C.reap(nonce)
        if p.poll() is None:
            p.kill()
        p.wait()
    with open(out, encoding="utf-8", errors="replace") as f:
        sigline = "SIGNAL\tSIGTERM\tRECEIPT-QUARANTINE-SIGNALED" in f.read().splitlines()
    rc = p.returncode if exited else None
    ok = exited and rc == 143 and sigline and not surv
    return ok, f"rc={rc} signal_line={'y' if sigline else 'n'} survivors={len(surv)}"


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
    stubs = C.make_shims(shimdir)
    failed = 0
    arms = [("monitor-q4", lambda: arm_monitor(tool, engine, stubs, shimdir, work, "q4-term-file-digest")),
            ("monitor-p1", lambda: arm_monitor(tool, engine, stubs, shimdir, work, "p1-file-no-signal")),
            ("spoof-session", lambda: arm_spoof(tool, engine, shimdir, work))]
    for name, fn in arms:
        ok, detail = fn()
        failed += 0 if ok else 1
        print(f"ARM {name} ok={'y' if ok else 'n'} {detail}")
    print(f"SUMMARY arms={len(arms)} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
