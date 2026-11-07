#!/usr/bin/env python3
"""r80 critic probe: does the front/worker split still wait under `bash -m` (job control on)?

If setsid must fork (background child is a process-group leader), $! is the setsid parent, which exits at
once; the front's `wait` returns 0 while the worker keeps running in a new session. The probe starts each
tool arm with a hanging engine stub, waits 3 s, and reports whether the front returned and which
nonce-tagged processes survive. It kills every nonce-tagged process it started before exiting.
"""
import json
import os
import signal
import subprocess
import sys
import tempfile
import time

S = "/fast/scratch/hyaku/souji-r80/S80CriticClaims"
L = "/home/vgpnk/Projects/shokunin/souji-shokunin"
NONCE = "jc-probe-" + str(os.getpid())
ENV0 = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SOUJI_"))}


def sh(*a, **kw):
    return subprocess.run(a, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kw)


def nonce_pids():
    out = []
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            with open(f"/proc/{d}/environ", "rb") as f:
                env = f.read().split(b"\0")
            with open(f"/proc/{d}/stat", "rb") as f:
                st = f.read().rsplit(b")", 1)[1].split()
        except OSError:
            continue
        if f"SOUJI_R80_CRIT={NONCE}".encode() in env and st[0] != b"Z":
            try:
                sid = int(st[3])
            except (IndexError, ValueError):
                sid = -1
            out.append((int(d), sid, os.path.realpath(f"/proc/{d}/cwd") if os.path.exists(f"/proc/{d}/cwd") else ""))
    return out


def kill_all():
    for _ in range(6):
        pids = [p for p, _, _ in nonce_pids()]
        if not pids:
            return True
        for p in pids:
            try:
                os.kill(p, signal.SIGKILL)
            except ProcessLookupError:
                pass
        time.sleep(0.1)
    return not nonce_pids()


def build_fixture(root):
    repo = os.path.join(root, "repo")
    os.makedirs(repo)
    sh("git", "-C", repo, "init", "-q")
    top = sh("git", "-C", repo, "rev-parse", "--show-toplevel").stdout.decode().strip()
    assert os.path.realpath(top) == os.path.realpath(repo), (top, repo)
    target = os.path.join(repo, "t.dat")
    with open(target, "w") as f:
        f.write("x\n")
    sh("git", "-C", repo, "add", "t.dat")
    env = dict(IDENT, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    subprocess.run(["git", "-C", repo, "-c", "user.name=f", "-c", "user.email=f@f.invalid",
                    "commit", "-q", "-m", "fx"], check=True, env={**os.environ, **env})
    t = time.time() - 3 * 86400
    os.utime(target, (t, t))
    return repo, target


IDENT = {"GIT_AUTHOR_NAME": "r80 probe", "GIT_AUTHOR_EMAIL": "p@r80.invalid",
         "GIT_COMMITTER_NAME": "r80 probe", "GIT_COMMITTER_EMAIL": "p@r80.invalid",
         "GIT_AUTHOR_DATE": "2026-11-07T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-07T00:00:00Z"}


def arm(name, tool, stub, root):
    repo, target = build_fixture(os.path.join(root, name))
    tmp = os.path.join(root, name, "tmp")
    os.makedirs(tmp)
    ledger = os.path.join(root, name, "ledger.tsv")
    with open(ledger, "w") as f:
        f.write("source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n")
    env = dict(ENV0, SOUJI_R80_CRIT=NONCE, SOUJI_VERIFY_BIN=stub, SOUJI_Q_LEDGER=ledger,
               SOUJI_Q_SHOKUNIN_ROOT=os.path.join(root, name), TMPDIR=tmp, LC_ALL="C")
    outp = os.path.join(root, name, ".out")
    with open(outp, "wb") as fo:
        t0 = time.monotonic()
        p = subprocess.Popen(["bash", "-m", tool, "--dry-run", repo, target], stdout=fo,
                             stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env,
                             start_new_session=True, cwd=root)
        try:
            rc = p.wait(timeout=3.0)
            returned = True
        except subprocess.TimeoutExpired:
            returned, rc = False, None
        secs = time.monotonic() - t0
        # snapshot while the arm may still run
        surv = nonce_pids()
        if not returned:
            try:
                os.killpg(os.getpgid(p.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
            try:
                p.kill()
            except ProcessLookupError:
                pass
        cleaned = kill_all()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
    with open(outp, "rb") as f:
        out = f.read().decode("utf-8", "replace")
    return {"arm": name, "front_returned_within_3s": returned, "rc": rc, "secs": round(secs, 2),
            "survivors_at_snapshot": [{"pid": a, "sid": b, "cwd": c[:80]} for a, b, c in surv],
            "stdout_lines": len(out.splitlines()), "summary": [l for l in out.splitlines() if l.startswith("SUMMARY")],
            "cleaned": cleaned}


def main():
    root = tempfile.mkdtemp(prefix="jc.", dir=S)
    stub = os.path.join(root, "engine-hang.sh")
    with open(stub, "w") as f:
        f.write("#!/bin/bash\nexec sleep 600\n")
    os.chmod(stub, 0o755)
    res = []
    for name, tool in (("base", os.path.join(S, "jc/base/tools/souji-quarantine.sh")),
                       ("cand", os.path.join(S, "jc/cand/tools/souji-quarantine.sh"))):
        res.append(arm(name, tool, stub, root))
    print(json.dumps({"nonce": NONCE, "root": root, "arms": res}, indent=2))
    return 0 if all(r["cleaned"] for r in res) else 1


if __name__ == "__main__":
    sys.exit(main())
