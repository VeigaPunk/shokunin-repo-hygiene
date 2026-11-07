#!/usr/bin/env python3
"""souji r80 repair-3 probe (after the wave): S80ScoutSources MEDIUM-3. A process whose comm contains a newline
splits /proc/<pid>/stat over two lines; the front's q_proc_sid read one line, found no session field and skipped the
process, so it survived the session kill. (S80ScoutSources MEDIUM-2, a comm containing `) `, is refuted by the L1:
the greedy `${st##*) }` strips through the LAST `) `, which is the comm's end — see the lesson.)

Arm comm-newline: at the stage-1 file digest a shim starts a background copy of sleep named "nl<LF>x" (a grandchild
of timeout, so timeout's PR_SET_PDEATHSIG does not reach it), marks, and blocks; the probe sends TERM to the tool.
Pass: exit 143 with the SIGNAL line and no process carrying the row nonce alive 2 s later.
`ARM ...`, `SUMMARY arms=1 failed=<F>`; exit 0 iff F == 0, 1 otherwise, 2 usage.
"""
import argparse
import importlib.util
import os
import secrets
import shutil
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("c2c", os.path.join(HERE, "..", "c2-signal-counter.py"))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

SHIM = r'''#!/bin/bash
last=; for last in "$@"; do :; done
if [[ $last == "$SOUJI_R80_TARGET" ]]; then
  "$SOUJI_R80_NL" 600 &
  printf 'nl started\n' > "$SOUJI_R80_MARK.tmp"; mv -f "$SOUJI_R80_MARK.tmp" "$SOUJI_R80_MARK"
  exec sleep 600
fi
exec %s "$@"
'''


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
    os.makedirs(shimdir)
    with open(os.path.join(shimdir, "sha256sum"), "w", encoding="utf-8") as f:
        f.write(SHIM % C.which("sha256sum"))
    os.chmod(os.path.join(shimdir, "sha256sum"), 0o755)
    nl = os.path.join(shimdir, "nl\nx")
    shutil.copy2(C.which("sleep"), nl)
    rowdir = os.path.join(work, "comm-newline")
    fleet, repo, ledger, target = C.build(rowdir, "file")
    tmpdir = os.path.join(rowdir, "tmp")
    os.makedirs(tmpdir)
    nonce, mark = secrets.token_hex(8), os.path.join(rowdir, "hang.mark")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SOUJI_"))}
    env.update({"PATH": shimdir + os.pathsep + os.environ.get("PATH", ""), "TMPDIR": tmpdir, "LC_ALL": "C",
                "SOUJI_R80_NONCE": nonce, "SOUJI_R80_MARK": mark, "SOUJI_R80_TARGET": target, "SOUJI_R80_NL": nl,
                "SOUJI_VERIFY_BIN": engine, "SOUJI_Q_SHOKUNIN_ROOT": fleet, "SOUJI_Q_LEDGER": ledger,
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    out = os.path.join(rowdir, "tool.out")
    t0 = time.monotonic()
    with open(out, "wb") as fo:
        p = subprocess.Popen(["bash", tool, "--dry-run", repo, target], stdout=fo, stderr=subprocess.DEVNULL,
                             stdin=subprocess.DEVNULL, env=env, cwd=rowdir, start_new_session=True,
                             preexec_fn=C._preexec)
    rc, surv, detail = None, [], ""
    try:
        while not os.path.exists(mark) and p.poll() is None and time.monotonic() - t0 < C.MARK_TIMEOUT:
            time.sleep(0.05)
        if not os.path.exists(mark):
            detail = "error=hang point never reached"
        else:
            time.sleep(0.3)
            os.kill(p.pid, signal.SIGTERM)
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
    with open(out, encoding="utf-8", errors="replace") as f:
        sigline = "SIGNAL\tSIGTERM\tRECEIPT-QUARANTINE-SIGNALED" in f.read().splitlines()
    ok = not detail and rc == 143 and sigline and not surv
    print(f"ARM comm-newline ok={'y' if ok else 'n'} rc={rc} signal_line={'y' if sigline else 'n'} "
          f"survivors={len(surv)} {detail}".rstrip())
    print(f"SUMMARY arms=1 failed={0 if ok else 1}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
