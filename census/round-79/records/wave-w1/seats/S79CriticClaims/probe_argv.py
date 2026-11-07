#!/usr/bin/env python3
"""S79CriticClaims probe: record the argv of the FIRST shim that blocks in each C1 row, on the candidate gate.
Read-only w.r.t. the lane; builds fixtures in this scratch dir only."""
import importlib.util
import os
import secrets
import signal
import subprocess
import sys
import time

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
COUNTER = os.path.join(LANE, "census/round-79/c1-signal-counter.py")
GATE_DIR = sys.argv[1]
WORK = sys.argv[2]
ROWS = [r for r in sys.argv[3:]]

spec = importlib.util.spec_from_file_location("c1c", COUNTER)
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

SHIM = r"""#!/bin/bash
if [[ -n ${SOUJI_R79_HANG:-} && ${SOUJI_R79_HANG_PROG:-} == %(name)s ]]; then
  case " $* " in
    *"$SOUJI_R79_HANG"*) printf '%%s\n' "$$" > "$SOUJI_R79_MARK"
      printf '%%s\t%%s\n' "$SOUJI_R79_HANG_PROG" "$*" >> "$SOUJI_R79_MARKLOG"
      exec sleep 600 ;;
  esac
fi
exec %(real)s "$@"
"""


def shims(d):
    os.makedirs(d, exist_ok=True)
    for name in ("git", "python3", "find"):
        p = os.path.join(d, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(SHIM % {"name": name, "real": C._which(name)})
        os.chmod(p, 0o755)


def one(rid, sig, prog, pat, contract, shimdir):
    rowdir = os.path.join(WORK, rid)
    clone, report, prereg = C.P.build(rowdir)
    if contract:
        os.makedirs(os.path.join(clone, "tools"), exist_ok=True)
        with open(os.path.join(clone, "tools", "souji-report-contract.py"), "w", encoding="utf-8") as f:
            f.write("print('check-x=PASS')\n")
    tmpdir = os.path.join(rowdir, "tmp")
    os.makedirs(tmpdir)
    nonce = secrets.token_hex(8)
    mark = os.path.join(rowdir, "hang.pid")
    marklog = os.path.join(rowdir, "argv.log")
    env = C.P.env_clean({"PATH": shimdir + os.pathsep + os.environ.get("PATH", ""), "TMPDIR": tmpdir,
                         "SOUJI_R79_NONCE": nonce, "SOUJI_R79_HANG": pat, "SOUJI_R79_HANG_PROG": prog,
                         "SOUJI_R79_MARK": mark, "SOUJI_R79_MARKLOG": marklog})
    argv = ["bash", os.path.join(GATE_DIR, "souji-pre-report-gate.sh"), "--lane", clone, "--branch", "master",
            "--report", report, "--prereg", prereg]
    if contract:
        argv.append("--contract")
    outp = os.path.join(rowdir, "gate.out")
    p = subprocess.Popen(argv, stdout=open(outp, "wb"), stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, env=env, start_new_session=True, cwd=rowdir)
    t0 = time.monotonic()
    try:
        while not os.path.exists(mark) and p.poll() is None and time.monotonic() - t0 < 30:
            time.sleep(0.02)
        time.sleep(0.1)
        first = ""
        if os.path.exists(marklog):
            with open(marklog, encoding="utf-8", errors="replace") as f:
                first = f.readline().rstrip("\n")
        print(f"ROWFIRST {rid} sig={sig} mark={'y' if os.path.exists(mark) else 'n'} call={first}")
    finally:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            p.kill()
        except (ProcessLookupError, PermissionError):
            pass
        p.wait()


def main():
    shimdir = os.path.join(WORK, "shim")
    shims(shimdir)
    for rid in ROWS:
        route = [r for r in C.ROUTES if r[0] == rid][0]
        one(*route[:5], shimdir)


main()
