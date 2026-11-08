#!/usr/bin/env python3
"""S84ExecEvade probe harness: reuses counter build/stub patterns, own nonce, own stubs a..g.
Driver prints one line per (shape, delivery, launch) cell plus survivors/tmpleft/exits.
Only own fixture processes are ever signalled (the tool under test)."""
import os, secrets, signal, subprocess, sys, time, hashlib

BASE = "/fast/scratch/hyaku/souji-r84/S84ExecEvade"
TOOL = os.path.join(BASE, "cand.sh")
SETTLE = 5.0
RESET = (signal.SIGINT, signal.SIGQUIT, signal.SIGTERM, signal.SIGHUP)
MARK_FN = r'''r81_mark() {
  local pc; pc=$(cat /proc/$PPID/comm 2>/dev/null)
  { printf 'prog=cli\n'; printf 'parent=%s\n' "$pc"; } > "$SOUJI_R81_MARK.tmp"
  mv -f "$SOUJI_R81_MARK.tmp" "$SOUJI_R81_MARK"
}
'''
def sha(p):
    with open(p, "rb") as f: return hashlib.sha256(f.read()).hexdigest()

STUBS = {
 "a2sig": MARK_FN + 'flag=0\n' + 'trap \'if [ "$flag" = 0 ]; then flag=1; setsid sleep 600 & else setsid sleep 600 & fi\' TERM INT HUP\n' + 'r81_mark "$@"\nwhile :; do :; done\n',
 "bdaemon": MARK_FN + 'setsid sleep 600 &\nexit 0\n',
 "cfanout": MARK_FN + 'i=0; while [ "$i" -lt 24 ]; do sleep 600 & i=$((i+1)); done\ntrap \'setsid sleep 600 &\' TERM INT HUP\nr81_mark "$@"\nwhile :; do :; done\n',
 "dparen": MARK_FN + 'r81_mark "$@"\nexec -a "we)rd\\nname" sleep 600\n',
 "dparen2": MARK_FN + 'r81_mark "$@"\nexec -a "we)rd name" sleep 600\n',
 "ereuse": MARK_FN + 'sleep 0.2 &\nr81_mark "$@"\nexec sleep 600\n',
 "ftermign": MARK_FN + 'trap "" TERM\nr81_mark "$@"\nexec sleep 600\n',
 "gfast": '#!/bin/bash\n' + MARK_FN + 'exit 0\n',
 "latefork": MARK_FN + 'flag=0\ntrap \'if [ "$flag" = 0 ]; then flag=1; setsid sleep 600 & fi\' TERM INT HUP\nr81_mark "$@"\nwhile :; do :; done\n',
}

def make_stubs(d):
    os.makedirs(d, exist_ok=True); out = {}
    for n, b in STUBS.items():
        p = os.path.join(d, "cli-" + n)
        with open(p, "w") as f: f.write("#!/bin/bash\n" + b)
        os.chmod(p, 0o755); out[n] = p
    return out

def build(rowdir):
    src, vault, fleet = (os.path.join(rowdir, x) for x in ("src", "vault", "fleet"))
    for d in (src, vault, fleet): os.makedirs(d)
    s = os.path.join(src, "a-src.md"); v = os.path.join(vault, "a-vlt.md")
    for p in (s, v):
        with open(p, "w") as f: f.write("evade payload\n")
    h = sha(s); ledger = os.path.join(rowdir, "ledger.tsv")
    with open(ledger, "w") as f:
        f.write("source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n")
        f.write(f"{s}\t{h}\t{v}\t{h}\t2026-11-08\tevade\n")
    stdin = os.path.join(rowdir, "stdin.txt")
    with open(stdin, "w") as f: f.write("r81-stdin\n")
    return s, fleet, ledger, stdin

def nonce_pids(nonce):
    key = f"SOUJI_R81_NONCE={nonce}".encode(); found = []
    for d in os.listdir("/proc"):
        if not d.isdigit(): continue
        try:
            with open(f"/proc/{d}/environ", "rb") as f: env = f.read().split(b"\0")
            with open(f"/proc/{d}/stat", "rb") as f: state = f.read().rsplit(b")", 1)[1].split()[0]
        except OSError: continue
        if key in env and state != b"Z": found.append(int(d))
    return found

def reap(nonce):
    for _ in range(5):
        pids = nonce_pids(nonce)
        if not pids: return
        for pid in pids:
            try: os.kill(pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError): pass
        time.sleep(0.1)

def _preexec():
    for s in RESET: signal.signal(s, signal.SIG_DFL)
    signal.pthread_sigmask(signal.SIG_UNBLOCK, RESET)

def run_one(stubname, stubpath, delivery, launch, sig="TERM"):
    rowdir = os.path.join(BASE, "rows", f"{stubname}-{delivery}-{launch}")
    os.makedirs(rowdir, exist_ok=True)
    target, fleet, ledger, stdin = build(rowdir)
    tmpdir = os.path.join(rowdir, "tmp"); os.makedirs(tmpdir, exist_ok=True)
    nonce = secrets.token_hex(8); mark = os.path.join(rowdir, "cli.mark")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SOUJI_"))}
    if launch == "monitor": env["SHELLOPTS"] = "monitor"
    env.update({"TMPDIR": tmpdir, "LC_ALL": "C", "SOUJI_R81_NONCE": nonce, "SOUJI_R81_MARK": mark,
                "SOUJI_CLI_BIN": stubpath, "SOUJI_CLI_TIMEOUT": "300", "SOUJI_LEDGER": ledger,
                "SHOKUNIN_ROOT": fleet, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    argv = ["bash", TOOL, target]
    outp, errp = os.path.join(rowdir, "tool.out"), os.path.join(rowdir, "tool.err")
    t0 = time.monotonic()
    with open(outp, "wb") as fo, open(errp, "wb") as fe, open(stdin, "rb") as fi:
        p = subprocess.Popen(argv, stdout=fo, stderr=fe, stdin=fi, env=env, start_new_session=True,
                             cwd=rowdir, preexec_fn=_preexec)
    exited = False; secs = None; rc = None; sigline = False; err = ""
    try:
        # wait for hang point (mark) up to 10s; fast-exit stub has no model hang point
        while not os.path.exists(mark) and p.poll() is None and time.monotonic() - t0 < 10:
            time.sleep(0.05)
        if os.path.exists(mark):
            time.sleep(0.3)
            t1 = time.monotonic()
            if delivery == "group": os.killpg(p.pid, signal.SIGTERM)
            else: os.kill(p.pid, signal.SIGTERM)
            try:
                p.wait(timeout=SETTLE); exited = True
            except subprocess.TimeoutExpired: pass
            secs = time.monotonic() - t1
            if exited: time.sleep(max(0.0, SETTLE - secs))
        else:
            # no mark: stub may have exited already; observe natural exit
            try:
                p.wait(timeout=10); exited = True
            except subprocess.TimeoutExpired: pass
            secs = time.monotonic() - t0
        surv = nonce_pids(nonce)
    finally:
        reap(nonce)
        if p.poll() is None:
            try: p.kill()
            except ProcessLookupError: pass
        p.wait()
    with open(errp, "rb") as f: err = f.read().decode("utf-8", "replace")
    rc = p.returncode if exited else None
    sigline = any(l.startswith("souji-vault-verify: SIGTERM") for l in err.splitlines())
    left = []
    for dp, dns, fns in os.walk(tmpdir): left += dns + fns
    return dict(stub=stubname, delivery=delivery, launch=launch, exited=exited,
                rc=rc, secs=f"{secs:.2f}" if secs is not None else "-",
                sigline=sigline, survivors=len(surv), surv_pids=surv, tmpleft=len(left))

def main():
    stubs = make_stubs(os.path.join(BASE, "stubs"))
    cells = [
        ("a2sig", "pid", "default"), ("a2sig", "group", "monitor"),
        ("bdaemon", "pid", "default"), ("bdaemon", "group", "monitor"),
        ("cfanout", "pid", "default"), ("cfanout", "group", "monitor"),
        ("dparen", "pid", "default"), ("dparen2", "group", "monitor"),
        ("ereuse", "pid", "default"), ("ftermign", "pid", "default"),
        ("ftermign", "group", "monitor"), ("gfast", "pid", "default"),
        ("latefork", "pid", "default"), ("latefork", "group", "monitor"),
    ]
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    for st, dl, ln in cells:
        if only and st not in only: continue
        r = run_one(st, stubs[st], dl, ln)
        print(f"{r['stub']:9} {r['delivery']:5} {r['launch']:7} exited={r['exited']} rc={r['rc']} secs={r['secs']} sigline={r['sigline']} survivors={r['survivors']} {r['surv_pids']} tmpleft={r['tmpleft']}", flush=True)

if __name__ == "__main__":
    main()
