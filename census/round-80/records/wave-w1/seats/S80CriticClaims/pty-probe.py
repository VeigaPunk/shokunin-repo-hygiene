#!/usr/bin/env python3
"""r80 critic probe 2: `bash -m` under a pty (job control active in the tool's own shell).

Per arm: start the tool through `script` (a pty) with `bash -m`, a hanging receipt engine, and a unique
SOUJI_R80_CRIT marker; wait up to 4 s for the front to return; snapshot marker-tagged survivors; kill them.
"""
import json
import os
import shlex
import signal
import subprocess
import sys
import time

S = "/fast/scratch/hyaku/souji-r80/S80CriticClaims"
ROOT = os.path.join(S, "jcpty")
TOOLS = {"base": os.path.join(S, "jc/base/tools/souji-quarantine.sh"),
         "cand": os.path.join(S, "jc/cand/tools/souji-quarantine.sh")}
REPO = os.path.join(ROOT, "repo")
TARGET = os.path.join(REPO, "t.dat")


def scan(marker):
    key = f"SOUJI_R80_CRIT={marker}".encode()
    out = []
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            env = open(f"/proc/{d}/environ", "rb").read().split(b"\0")
            st = open(f"/proc/{d}/stat", "rb").read().rsplit(b")", 1)[1].split()
            cmd = open(f"/proc/{d}/cmdline", "rb").read().replace(b"\0", b" ").decode("utf-8", "replace")
        except OSError:
            continue
        if key in env and st[0] != b"Z":
            out.append({"pid": int(d), "sid": int(st[3]), "state": st[0].decode(), "cmd": cmd.strip()[:150]})
    return out


def kill(marker):
    for _ in range(6):
        pids = [p["pid"] for p in scan(marker)]
        if not pids:
            return True
        for p in pids:
            try:
                os.kill(p, signal.SIGKILL)
            except ProcessLookupError:
                pass
        time.sleep(0.1)
    return not scan(marker)


def arm(name):
    tmp = os.path.join(ROOT, "t" + name[0])
    os.makedirs(tmp, exist_ok=True)
    ledger = os.path.join(tmp, "ledger.tsv")
    with open(ledger, "w") as f:
        f.write("source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n")
    marker = f"pty-{name}-{os.getpid()}"
    env = ["env", f"TMPDIR={tmp}", f"SOUJI_R80_CRIT={marker}",
           f"SOUJI_VERIFY_BIN={ROOT}/engine-hang.sh", f"SOUJI_Q_LEDGER={ledger}",
           f"SOUJI_Q_SHOKUNIN_ROOT={ROOT}", "LC_ALL=C",
           "bash", "-m", TOOLS[name], "--dry-run", REPO, TARGET]
    log = os.path.join(ROOT, f"{name}-pty.log")
    t0 = time.monotonic()
    p = subprocess.Popen(["script", "-q", "-e", "-c", shlex.join(env), log],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         stdin=subprocess.DEVNULL, cwd=ROOT)
    try:
        rc = p.wait(timeout=4.0)
        returned = True
    except subprocess.TimeoutExpired:
        returned, rc = False, None
    secs = time.monotonic() - t0
    time.sleep(0.3)
    surv = scan(marker)
    if not returned:
        p.kill()
    cleaned = kill(marker)
    try:
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    with open(log, "rb") as f:
        body = f.read().decode("utf-8", "replace")
    return {"arm": name, "front_returned_within_4s": returned, "rc": rc, "secs": round(secs, 2),
            "survivors_after_return": surv, "cleaned": cleaned,
            "log_lines": [l for l in body.splitlines() if not l.startswith(("Script started", "Script done"))]}


def main():
    res = [arm("base"), arm("cand")]
    print(json.dumps(res, indent=2))
    return 0 if all(r["cleaned"] for r in res) else 1


if __name__ == "__main__":
    sys.exit(main())
