#!/usr/bin/env python3
"""souji r79 C1 counter: what the pre-report gate does when its caller signals it while a child it started
is blocked, over the r79 routes defined here (10 signal routes, 1 positive control).

Claim surface: tools/souji-pre-report-gate.sh. The gate's git, find and python calls run in the foreground
(`$(...)`, process substitution) under `timeout`, which puts itself and the command in a NEW process group
(S326 coreutils timeout.c: `if (!foreground) setpgid (0, 0);` "Ensure we're in our own group so all
subprocesses can be killed."). Bash defers a trapped signal while it waits for a foreground command (S325 bash
5.3 manual, Signals: "it will not execute the trap until the command completes"); with no trap a TERM/HUP
kills the shell and the blocked child, in timeout's own group, outlives it; an INT is not even acted on while
the child runs. Only `wait` on an asynchronous command returns at once on a trapped signal (S325: "the `wait`
builtin will return immediately with an exit status greater than 128, immediately after which the shell
executes the trap").

Each route builds a fresh bare-origin + clone fixture under --work (census/round-74 evade-probe build(),
imported byte-bound), and runs `bash <gate-dir>/souji-pre-report-gate.sh` in its own session with PATH led by
a shim directory: the shims (git, python3, find) exec the real program unless the row's hang pattern occurs in
their argv, in which case they write their pid to a mark file and exec `sleep 600` (the blocked child). Every
process the gate starts inherits SOUJI_R79_NONCE=<row nonce>. When the mark appears the counter sends the
row's signal to the gate's pid only (as a caller's `kill <pid>` would), waits up to SETTLE seconds for the gate
to exit, then lists every live process whose environment carries the row nonce (survivors). Afterwards it
SIGKILLs the session and every survivor, so no row leaks a process.

A signal row matches iff the gate exited within SETTLE seconds, its exit status is 128 + the signal number,
stdout carries the line `check-signal=FAIL`, the output carries the class RECEIPT-GATE-SIGNALED, survivors == 0,
and the row's TMPDIR is empty afterwards. The positive row (no hang, no signal) matches iff the gate exits 0
with no `check-*=FAIL` line, no `check-signal` line, survivors == 0 and an empty TMPDIR.
Output: one `ROW <id> sig=<S> expect=<E> exited=<y/n> rc=<n> signal_line=<y/n> class=<y/n> survivors=<k>
tmpleft=<k> secs=<t> match=<yes|no>` line per route, then `SUMMARY rows=<N> mismatches=<M> errors=<E>
orphans=<O>` (O = rows with survivors > 0); exit 0 iff M == 0 and E == 0, 1 otherwise, 2 on usage.
"""
import argparse
import hashlib
import importlib.util
import os
import secrets
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = os.path.join(HERE, "..", "round-74", "records", "wave-repair", "probes", "evade-probe.py")
SETTLE = 5.0
MARK_TIMEOUT = 60.0
CLASS = "RECEIPT-GATE-SIGNALED"
SIGS = {"TERM": signal.SIGTERM, "INT": signal.SIGINT, "HUP": signal.SIGHUP, "-": None}


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


P = _load(PROBE, "souji_r74_evade_probe")

SHIM = r"""#!/bin/bash
# souji r79 C1 hang shim for %(name)s: exec the real program unless the row's pattern is in argv.
if [[ -n ${SOUJI_R79_HANG:-} && ${SOUJI_R79_HANG_PROG:-} == %(name)s ]]; then
  case " $* " in
    *"$SOUJI_R79_HANG"*) printf '%%s\n' "$$" > "$SOUJI_R79_MARK"; exec sleep 600 ;;
  esac
fi
exec %(real)s "$@"
"""

# id, signal, program, argv pattern, needs --contract, expected
ROUTES = [
    ("s1-term-include-read", "TERM", "git", "--get-regexp", False, "SIGNALED"),
    ("s2-term-revparse-tip", "TERM", "git", "rev-parse --verify", False, "SIGNALED"),
    ("s3-term-ls-remote", "TERM", "git", "ls-remote", False, "SIGNALED"),
    ("s4-int-ls-remote", "INT", "git", "ls-remote", False, "SIGNALED"),
    ("s5-term-precheck-toplevel", "TERM", "git", "rev-parse --show-toplevel", False, "SIGNALED"),
    ("s6-term-worktree-scan", "TERM", "find", "-prune", False, "SIGNALED"),
    ("s7-term-status", "TERM", "git", "status --porcelain", False, "SIGNALED"),
    ("s8-hup-status", "HUP", "git", "status --porcelain", False, "SIGNALED"),
    ("s9-term-byte-truth", "TERM", "python3", "-I -B -", False, "SIGNALED"),
    ("s10-term-contract-checker", "TERM", "python3", "souji-report-contract.py", True, "SIGNALED"),
    ("p1-honest-no-signal", "-", "-", "-", False, "PASS"),
]


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _which(name):
    for d in os.environ.get("PATH", "").split(os.pathsep):
        p = os.path.join(d, name)
        if d and os.path.isfile(p) and os.access(p, os.X_OK):
            return os.path.realpath(p)
    raise P.FixtureError(f"{name} not on PATH")


def make_shims(shimdir):
    os.makedirs(shimdir)
    for name in ("git", "python3", "find"):
        p = os.path.join(shimdir, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(SHIM % {"name": name, "real": _which(name)})
        os.chmod(p, 0o755)


def survivors(nonce):
    key = f"SOUJI_R79_NONCE={nonce}".encode()
    found = []
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            with open(f"/proc/{d}/environ", "rb") as f:
                env = f.read().split(b"\0")
            with open(f"/proc/{d}/stat", "rb") as f:
                state = f.read().rsplit(b")", 1)[1].split()[0]
        except OSError:
            continue
        if key in env and state != b"Z":
            found.append(int(d))
    return found


def _reap(pids, sid):
    try:
        os.killpg(sid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    for pid in pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass


def run_row(gate, rowdir, rid, sig, prog, pat, contract, shimdir):
    clone, report, prereg = P.build(rowdir)
    if contract:
        os.makedirs(os.path.join(clone, "tools"))
        with open(os.path.join(clone, "tools", "souji-report-contract.py"), "w", encoding="utf-8") as f:
            f.write("print('check-x=PASS')\n")
    tmpdir = os.path.join(rowdir, "tmp")
    os.makedirs(tmpdir)
    nonce = secrets.token_hex(8)
    mark = os.path.join(rowdir, "hang.pid")
    env = P.env_clean({"PATH": shimdir + os.pathsep + os.environ.get("PATH", ""), "TMPDIR": tmpdir,
                       "SOUJI_R79_NONCE": nonce})
    if prog != "-":
        env.update({"SOUJI_R79_HANG": pat, "SOUJI_R79_HANG_PROG": prog, "SOUJI_R79_MARK": mark})
    argv = ["bash", gate, "--lane", clone, "--branch", "master", "--report", report, "--prereg", prereg]
    if contract:
        argv.append("--contract")
    outp, errp = os.path.join(rowdir, "gate.out"), os.path.join(rowdir, "gate.err")
    t0 = time.monotonic()
    with open(outp, "wb") as fo, open(errp, "wb") as fe:
        p = subprocess.Popen(argv, stdout=fo, stderr=fe, stdin=subprocess.DEVNULL, env=env,
                             start_new_session=True, cwd=rowdir)
    sid = p.pid
    exited = False
    try:
        if SIGS[sig] is None:
            try:
                p.wait(timeout=MARK_TIMEOUT)
                exited = True
            except subprocess.TimeoutExpired:
                pass
            secs = time.monotonic() - t0
        else:
            while not os.path.exists(mark) and p.poll() is None and time.monotonic() - t0 < MARK_TIMEOUT:
                time.sleep(0.05)
            if not os.path.exists(mark):
                raise P.FixtureError("hang point never reached (gate exited or mark timeout)")
            time.sleep(0.3)
            t1 = time.monotonic()
            os.kill(p.pid, SIGS[sig])
            try:
                p.wait(timeout=SETTLE)
                exited = True
            except subprocess.TimeoutExpired:
                pass
            secs = time.monotonic() - t1
            if exited:
                time.sleep(max(0.0, SETTLE - secs))
        surv = survivors(nonce)
    finally:
        _reap(survivors(nonce), sid)
        if p.poll() is None:
            p.kill()
        p.wait()
    with open(outp, "rb") as f:
        out = f.read().decode("utf-8", "replace")
    with open(errp, "rb") as f:
        err = f.read().decode("utf-8", "replace")
    left = []
    for dp, dns, fns in os.walk(tmpdir):
        left += dns + fns
    rc = p.returncode if exited else None
    lines = out.splitlines()
    sigline = "check-signal=FAIL" in lines
    anysig = any(l.startswith("check-signal") for l in lines)
    cls = CLASS in out + err
    if SIGS[sig] is None:
        fails = [l for l in lines if l.startswith("check-") and l.endswith("=FAIL")]
        ok = exited and rc == 0 and not fails and not anysig and not surv and not left
    else:
        ok = exited and rc == 128 + int(SIGS[sig]) and sigline and cls and not surv and not left
    return ok, exited, rc, sigline, cls, len(surv), len(left), secs, out + err


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate-dir", required=True,
                    help="directory holding souji-pre-report-gate.sh and souji-receipt-write.py")
    ap.add_argument("--work", required=True, help="empty scratch directory (never under /tmp)")
    ns = ap.parse_args(argv)
    gate_dir = os.path.abspath(ns.gate_dir)
    gate = os.path.join(gate_dir, "souji-pre-report-gate.sh")
    writer = os.path.join(gate_dir, "souji-receipt-write.py")
    work = os.path.abspath(ns.work)
    if not (os.path.isfile(gate) and os.path.isfile(writer)):
        print(f"C1-COUNTER-FATAL: gate dir incomplete: {gate_dir}", file=sys.stderr)
        return 2
    pop = os.path.join(HERE, "c1-population.tsv")
    with open(pop, encoding="utf-8") as f:
        rows = [l.rstrip("\n").split("\t") for l in f if l.strip() and not l.startswith("#")]
    want = {r[0]: (r[1], r[2], r[3], "contract" if r[4] else "-", r[5]) for r in ROUTES}
    if len(rows) != len(want) or {r[0]: tuple(r[1:]) for r in rows} != want:
        print("C1-COUNTER-FATAL: c1-population.tsv and the ROUTES table disagree", file=sys.stderr)
        return 2
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("C1-COUNTER-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"C1-COUNTER-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    shimdir = os.path.join(work, "shim")
    make_shims(shimdir)
    print(f"# gate path={gate} sha256={sha(gate)}")
    print(f"# writer path={writer} sha256={sha(writer)}")
    print(f"# population path={pop} sha256={sha(pop)}")
    print(f"# probe path={os.path.normpath(PROBE)} sha256={sha(PROBE)}")
    print(f"# counter sha256={sha(os.path.abspath(__file__))} settle={SETTLE}s mark_timeout={MARK_TIMEOUT}s")
    mism = errs = orphans = 0
    for rid, sig, prog, pat, contract, ev in ROUTES:
        rowdir = os.path.join(work, rid)
        try:
            ok, exited, rc, sigline, cls, ns_, nl, secs, text = run_row(gate, rowdir, rid, sig, prog, pat,
                                                                        contract, shimdir)
        except (P.FixtureError, OSError, subprocess.SubprocessError) as exc:
            errs += 1
            print(f"ROW {rid} sig={sig} expect={ev} exited=- rc=- signal_line=- class=- survivors=- tmpleft=- "
                  f"secs=- match=error detail={type(exc).__name__}: {str(exc)[:200]}")
            continue
        orphans += ns_ > 0
        mism += 0 if ok else 1
        print(f"ROW {rid} sig={sig} expect={ev} exited={'y' if exited else 'n'} rc={rc} "
              f"signal_line={'y' if sigline else 'n'} class={'y' if cls else 'n'} survivors={ns_} tmpleft={nl} "
              f"secs={secs:.1f} match={'yes' if ok else 'no'}")
        if not ok:
            brief = " | ".join(l for l in text.splitlines() if l.startswith(("check-", "detail-")))
            print(f"#  {rid} {brief[:300]}")
    print(f"SUMMARY rows={len(ROUTES)} mismatches={mism} errors={errs} orphans={orphans}")
    return 0 if mism == 0 and errs == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
