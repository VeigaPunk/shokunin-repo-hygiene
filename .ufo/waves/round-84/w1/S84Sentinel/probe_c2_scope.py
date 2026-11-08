#!/usr/bin/env python3
"""S84Sentinel C2 kill-scope probe (souji r84): does tools/souji-vault-verify.sh's abort path signal a pid that is
NOT in the CLI's descendant set, and does it leave survivors or private-file residue?

Read-only w.r.t. the lane: it only RUNS a candidate tool against a synthetic fixture under --work (never /tmp).
It never mutates the lane, never signals a process outside its own fixtures, and writes nothing into the lane.

Usage: probe_c2_scope.py --tool <tool.sh> --work <empty dir> [--cases a,b,c]

Cases:
  nlcomm_trap  the CLI sets its own /proc/<pid>/stat comm to a value holding a NEWLINE and ')', traps TERM, and on
               the first TERM forks a setsid'd child. If the tool froze the CLI before any trappable signal, the
               trap never runs and nothing survives; if the tool's per-pid stat re-read is truncated (first-line
               read), the CLI is never frozen, the trap runs and the setsid'd child escapes both the group kill and
               the tree walk.
  canary       a PRE-EXISTING canary that is NOT a descendant of the CLI logs every signal it receives.
  reparent     a descendant reparents to init mid-walk (its parent dies before the map pass).
  setsid2      a descendant setsids after the first map pass.
  churn        the driver churns pids (fork/exit) while the tool walks; the canary logs any signal it receives.
  tmpvault     TMPDIR points INSIDE the vault (private file impossible -> foreground fallback, no trap installed).
  privmode     the private CLI file's mode while the call runs, and whether it is removed on the signal path.

Output: one CASE line per case plus SUMMARY cases=<n> leaks=<n>; exit 0 iff no leak.
"""
import argparse
import hashlib
import os
import secrets
import signal
import subprocess
import sys
import time

SETTLE = 5.0
MARK_TIMEOUT = 30.0
RESET = (signal.SIGINT, signal.SIGQUIT, signal.SIGTERM, signal.SIGHUP)

STUB_NLCOMM_TRAP = r'''#!/usr/bin/env python3
import ctypes, os, signal, sys, time
libc = ctypes.CDLL("libc.so.6", use_errno=True)
libc.prctl(15, b"a\nb)c", 0, 0, 0)          # comm holds a NEWLINE and ')'
def stat():
    return open("/proc/self/stat", "rb").read().decode("utf-8", "replace")
def term(*a):
    try:
        pid = os.fork()
        if pid == 0:
            os.setsid()
            while True:
                time.sleep(0.3)
        os._exit(0)
    except Exception:
        os._exit(0)
signal.signal(signal.SIGTERM, term)
signal.signal(signal.SIGINT, term)
signal.signal(signal.SIGHUP, term)
with open(os.environ["S84_MARK"], "w") as f:
    f.write("ready pid=%s ppid=%s pgid=%s sid=%s\n" % (os.getpid(), os.getppid(), os.getpgrp(), os.getsid(0)))
while True:
    time.sleep(0.2)
'''

STUB_PLAIN = r'''#!/usr/bin/env python3
import os, signal, sys, time
def stat():
    return ""
def term(*a):
    os._exit(0)
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, term)
with open(os.environ["S84_MARK"], "w") as f:
    f.write("ready pid=%s ppid=%s pgid=%s sid=%s\n" % (os.getpid(), os.getppid(), os.getpgrp(), os.getsid(0)))
while True:
    time.sleep(0.2)
'''

STUB_REPARENT = r'''#!/usr/bin/env python3
import os, signal, sys, time
pid = os.fork()
if pid == 0:
    g = os.fork()
    if g == 0:
        os.setsid()
        while True:
            time.sleep(0.3)
    os._exit(0)
def term(*a):
    os._exit(0)
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, term)
with open(os.environ["S84_MARK"], "w") as f:
    f.write("ready pid=%s ppid=%s pgid=%s sid=%s\n" % (os.getpid(), os.getppid(), os.getpgrp(), os.getsid(0)))
while True:
    time.sleep(0.2)
'''

STUB_SETSID2 = r'''#!/usr/bin/env python3
import os, signal, sys, time
pid = os.fork()
if pid == 0:
    time.sleep(0.35)
    os.setsid()
    while True:
        time.sleep(0.3)
def term(*a):
    os._exit(0)
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, term)
with open(os.environ["S84_MARK"], "w") as f:
    f.write("ready pid=%s ppid=%s pgid=%s sid=%s\n" % (os.getpid(), os.getppid(), os.getpgrp(), os.getsid(0)))
while True:
    time.sleep(0.2)
'''

STUBS = {"plain": STUB_PLAIN, "nlcomm_trap": STUB_NLCOMM_TRAP, "reparent": STUB_REPARENT, "setsid2": STUB_SETSID2}

CANARY = r'''#!/usr/bin/env python3
import os, signal, sys, time
log = os.environ["S84_CANARY_LOG"]
def note(s):
    with open(log, "a") as f:
        f.write(s + "\n")
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT):
    signal.signal(s, lambda n, f: note("sig%d" % n))
note("start")
open(os.environ["S84_CANARY_READY"], "w").write("ready\n")
while True:
    time.sleep(0.1)
'''


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def nonce_pids(nonce):
    key = f"S84_NONCE={nonce}".encode()
    out = []
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            with open(f"/proc/{d}/environ", "rb") as f:
                env = f.read().split(b"\0")
            with open(f"/proc/{d}/stat", "rb") as f:
                raw = f.read()
            state = raw.rsplit(b")", 1)[1].split()[0]
            comm = raw.split(b"(")[1].split(b")")[0]
            ppid = int(raw.rsplit(b")", 1)[1].split()[1])
        except (OSError, IndexError, ValueError):
            continue
        if key in env and state != b"Z":
            out.append((int(d), comm.decode("utf-8", "replace"), state.decode(), ppid))
    return out


def reap(nonce):
    for _ in range(8):
        pids = nonce_pids(nonce)
        if not pids:
            return
        for entry in pids:
            pid = entry[0] if isinstance(entry, tuple) else entry
            try:
                os.kill(pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
        time.sleep(0.1)


def _preexec():
    for s in RESET:
        signal.signal(s, signal.SIG_DFL)
    signal.pthread_sigmask(signal.SIG_UNBLOCK, RESET)


def build_fixture(d):
    src, vault, fleet, tmp = (os.path.join(d, x) for x in ("src", "vault", "fleet", "tmp"))
    for x in (src, vault, fleet, tmp):
        os.makedirs(x)
    s, v = os.path.join(src, "a-src.md"), os.path.join(vault, "a-vlt.md")
    for p in (s, v):
        with open(p, "w", encoding="utf-8") as f:
            f.write("r84 sentinel probe payload\n")
    h = sha(s)
    led = os.path.join(d, "ledger.tsv")
    with open(led, "w", encoding="utf-8") as f:
        f.write("source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n")
        f.write(f"{s}\t{h}\t{v}\t{h}\t2026-11-07\tr84-sentinel\n")
    return s, v, led, tmp, vault


def run_case(tool, case, work, launch="default", delivery="pid", sig=signal.SIGTERM):
    d = os.path.join(work, case)
    os.makedirs(d)
    src, vault, led, tmp, vaultdir = build_fixture(d)
    nonce = secrets.token_hex(8)
    mark = os.path.join(d, "cli.mark")
    canary_log = os.path.join(d, "canary.log")
    canary_ready = os.path.join(d, "canary.ready")
    canary_pid = None
    stub_name = "plain"
    # the tool's env: no S84_NONCE for the canary/churner (they must not count as survivors)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SOUJI_", "S84_"))}
    env.update({"LC_ALL": "C", "S84_NONCE": nonce, "S84_MARK": mark, "TMPDIR": tmp,
                "SOUJI_LEDGER": led, "SOUJI_CLI_TIMEOUT": "300", "SHOKUNIN_ROOT": os.path.join(d, "fleet"),
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    side_env = {k: v for k, v in env.items() if k != "S84_NONCE"}
    if launch == "monitor":
        env["SHELLOPTS"] = "monitor"

    if case in ("canary", "churn"):
        cpath = os.path.join(d, "canary")
        with open(cpath, "w", encoding="utf-8") as f:
            f.write(CANARY)
        os.chmod(cpath, 0o755)
        side_env["S84_CANARY_LOG"] = canary_log
        side_env["S84_CANARY_READY"] = canary_ready
        c = subprocess.Popen([cpath], env=side_env, preexec_fn=_preexec)
        canary_pid = c.pid
        t0 = time.monotonic()
        while not os.path.exists(canary_ready) and time.monotonic() - t0 < 10:
            time.sleep(0.05)
    elif case == "nlcomm_trap":
        stub_name = "nlcomm_trap"
    elif case == "reparent":
        stub_name = "reparent"
    elif case == "setsid2":
        stub_name = "setsid2"

    stub = os.path.join(d, "cli-stub")
    with open(stub, "w", encoding="utf-8") as f:
        f.write(STUBS[stub_name])
    os.chmod(stub, 0o755)
    env["SOUJI_CLI_BIN"] = stub
    if case == "tmpvault":
        env["TMPDIR"] = vaultdir

    argv = ["bash", tool, src]
    outp, errp = os.path.join(d, "tool.out"), os.path.join(d, "tool.err")
    t0 = time.monotonic()
    with open(outp, "wb") as fo, open(errp, "wb") as fe, open(os.devnull, "rb") as fi:
        p = subprocess.Popen(argv, stdout=fo, stderr=fe, stdin=fi, env=env, start_new_session=True,
                             cwd=d, preexec_fn=_preexec)
    churn = None
    if case == "churn":
        churn = subprocess.Popen([sys.executable, "-c",
                                  "import os,time\n"
                                  "t=time.time()\n"
                                  "while time.time()-t < 6:\n"
                                  "    for _ in range(50):\n"
                                  "        if os.fork()==0: os._exit(0)\n"
                                  "        os.wait()\n"],
                                 env=side_env, preexec_fn=_preexec)
    exited = False
    priv = []
    try:
        while not os.path.exists(mark) and p.poll() is None and time.monotonic() - t0 < MARK_TIMEOUT:
            time.sleep(0.05)
        if case == "privmode":
            time.sleep(0.3)
            for n in sorted(os.listdir(tmp)):
                try:
                    priv.append((n, oct(os.stat(os.path.join(tmp, n)).st_mode & 0o777)))
                except OSError:
                    pass
        time.sleep(0.3)
        if delivery == "group":
            os.killpg(p.pid, sig)
        else:
            os.kill(p.pid, sig)
        try:
            p.wait(timeout=SETTLE)
            exited = True
        except subprocess.TimeoutExpired:
            pass
    finally:
        if churn is not None:
            try:
                churn.kill()
            except OSError:
                pass
            churn.wait()
        surv = nonce_pids(nonce)
        try:
            with open(errp, "rb") as f:
                err = f.read().decode("utf-8", "replace")
        except OSError:
            err = ""
        tmpleft = sorted(os.listdir(tmp))
        reap(nonce)
        if p.poll() is None:
            p.kill()
        p.wait()
        if canary_pid is not None:
            try:
                os.kill(canary_pid, signal.SIGKILL)
            except OSError:
                pass
    hits = []
    if os.path.exists(canary_log):
        with open(canary_log, encoding="utf-8", errors="replace") as f:
            hits = [l.strip() for l in f if l.strip() and l.strip() != "start"]
    sigline = any(l.startswith("souji-vault-verify: SIG") for l in err.splitlines())
    marktxt = ""
    if os.path.exists(mark):
        with open(mark, encoding="utf-8", errors="replace") as f:
            marktxt = f.read().strip().replace("\n", " | ")
    return {"case": case, "exited": exited, "rc": p.returncode, "sig_line": sigline, "survivors": len(surv), "survivor_detail": surv,
            "tmpleft": tmpleft, "canary_hits": hits, "priv": priv, "mark": marktxt,
            "err": [l for l in err.splitlines() if l.startswith("souji-")]}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--cases", default="nlcomm_trap,canary,reparent,setsid2,churn,tmpvault,privmode")
    ap.add_argument("--launch", default="default", choices=("default", "monitor"))
    ap.add_argument("--delivery", default="pid", choices=("pid", "group"))
    ns = ap.parse_args(argv)
    tool = os.path.abspath(ns.tool)
    work = os.path.abspath(ns.work)
    if not os.path.isfile(tool):
        print("PROBE-FATAL: no tool", file=sys.stderr)
        return 2
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("PROBE-FATAL: --work under /tmp", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"PROBE-FATAL: --work {work} not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    print(f"# tool path={tool} sha256={sha(tool)} mode={oct(os.stat(tool).st_mode & 0o777)} "
          f"launch={ns.launch} delivery={ns.delivery}")
    leaks = 0
    cases = [c.strip() for c in ns.cases.split(",") if c.strip()]
    for case in cases:
        try:
            d = run_case(tool, case, work, launch=ns.launch, delivery=ns.delivery)
        except Exception as exc:  # noqa: BLE001
            print(f"CASE {case} error={type(exc).__name__}: {exc}")
            leaks += 1
            continue
        leak = bool(d["survivors"]) or bool(d["canary_hits"]) or bool(d["tmpleft"]) or not d["sig_line"]
        leaks += 1 if leak else 0
        print(f"CASE {case} exited={'y' if d['exited'] else 'n'} rc={d['rc']} sig_line={'y' if d['sig_line'] else 'n'} "
              f"survivors={d['survivors']} surv_detail={d['survivor_detail']} tmpleft={d['tmpleft']} canary_hits={d['canary_hits']} "
              f"priv={d['priv']} leak={'yes' if leak else 'no'}")
        print(f"  mark[{case}] {d['mark']}")
    print(f"SUMMARY cases={len(cases)} leaks={leaks}")
    return 0 if leaks == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
