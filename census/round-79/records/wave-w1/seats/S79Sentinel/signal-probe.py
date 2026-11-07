#!/usr/bin/env python3
"""S79Sentinel r79: what the W1 gate's signal path actually does.

Arms (each builds a fresh fixture with the r74 probe's build(), a PATH shim for git that logs its
inherited signal dispositions and blocks when the row's pattern occurs):
  term / int / hup  - signal the gate pid only; expect rc 128+n, check-signal=FAIL, class on stderr,
                      no survivor carrying the row nonce, TMPDIR empty, and the CALLER's own process
                      group untouched (the probe process survives).
  early             - `timeout` replaced by a shim that sleeps 0.3 s before exec'ing the real timeout;
                      the signal lands before timeout calls setpgid.  Records whether the group kill
                      is ESRCH and whether the pid kill still reaps the child.
  escape            - the git shim spawns `setsid sleep 600` (escapes the gate's child group) and then
                      blocks; after the signal the escaped grandchild is still alive.
"""
import importlib.util
import os
import secrets
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
PROBE = os.path.join(LANE, "census/round-74/records/wave-repair/probes/evade-probe.py")
S = "/fast/scratch/hyaku/souji-r79/S79Sentinel"
GATE = os.path.join(S, "gw1", "souji-pre-report-gate.sh")
SETTLE = 5.0


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


P = load(PROBE, "evade_probe")

SHIM = r"""#!/bin/bash
{ printf 'GITSHIM pid=%s pgid=%s int=%s quit=%s term=%s\n' "$$" "$(ps -o pgid= -p $$ | tr -d ' ')" \
    "$(trap -p INT)" "$(trap -p QUIT)" "$(trap -p TERM)"; } >> "$SOUJI_SHIM_LOG"
case " $* " in
  *"$SOUJI_HANG_PAT"*)
    if [[ -n ${SOUJI_ESCAPE:-} ]]; then setsid sleep 600 & fi
    exec sleep 600 ;;
esac
exec __REAL__ "$@"
"""

TIMEOUT_SHIM = r"""#!/bin/bash
printf 'x\n' > "$SOUJI_TIMEOUT_MARK"
sleep 0.6
exec __REAL__ "$@"
"""


def which(name):
    for d in os.environ.get("PATH", "").split(os.pathsep):
        p = os.path.join(d, name)
        if d and os.path.isfile(p) and os.access(p, os.X_OK):
            return os.path.realpath(p)
    raise SystemExit(f"{name} not on PATH")


def survivors(nonce):
    key = f"SOUJI_R79_NONCE={nonce}".encode()
    out = []
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
            out.append(int(d))
    return out


def arm(name, sig, pattern, escape=False, early=False):
    rowdir = os.path.join(S, "sig", name)
    if os.path.isdir(rowdir):
        subprocess.run(["rm", "-rf", rowdir], check=False)
    clone, report, prereg = P.build(rowdir)
    shimdir = os.path.join(rowdir, "shim")
    os.makedirs(shimdir)
    with open(os.path.join(shimdir, "git"), "w", encoding="utf-8") as f:
        f.write(SHIM.replace("__REAL__", which("git")))
    os.chmod(os.path.join(shimdir, "git"), 0o755)
    if early:
        with open(os.path.join(shimdir, "timeout"), "w", encoding="utf-8") as f:
            f.write(TIMEOUT_SHIM.replace("__REAL__", which("timeout")))
        os.chmod(os.path.join(shimdir, "timeout"), 0o755)
    tmpdir = os.path.join(rowdir, "tmp")
    os.makedirs(tmpdir)
    nonce = secrets.token_hex(8)
    shimlog = os.path.join(rowdir, "shim.log")
    env = P.env_clean({"PATH": shimdir + os.pathsep + os.environ.get("PATH", ""), "TMPDIR": tmpdir,
                       "SOUJI_R79_NONCE": nonce, "SOUJI_SHIM_LOG": shimlog,
                       "SOUJI_HANG_PAT": pattern})
    if escape:
        env["SOUJI_ESCAPE"] = "1"
    argv = ["bash", GATE, "--lane", clone, "--branch", "master", "--report", report,
            "--prereg", prereg]
    tmark = os.path.join(rowdir, "timeout.mark")
    if early:
        env["SOUJI_TIMEOUT_MARK"] = tmark
    outp, errp = os.path.join(rowdir, "gate.out"), os.path.join(rowdir, "gate.err")
    with open(outp, "wb") as fo, open(errp, "wb") as fe:
        p = subprocess.Popen(argv, stdout=fo, stderr=fe, stdin=subprocess.DEVNULL, env=env,
                             start_new_session=True, cwd=rowdir)
    sid = p.pid
    t0 = time.monotonic()
    if early:
        # signal while the timeout shim still sleeps, i.e. before timeout calls setpgid(0,0)
        while not os.path.exists(tmark) and p.poll() is None and time.monotonic() - t0 < 30:
            time.sleep(0.005)
        if not os.path.exists(tmark):
            print(f"ARM {name} ERROR timeout shim never started")
            return
    else:
        while not os.path.exists(shimlog) and p.poll() is None and time.monotonic() - t0 < 30:
            time.sleep(0.02)
        if not os.path.exists(shimlog):
            print(f"ARM {name} ERROR gate never reached a git child")
            return
        time.sleep(0.4)
    os.kill(p.pid, sig)
    exited = False
    try:
        p.wait(timeout=SETTLE)
        exited = True
    except subprocess.TimeoutExpired:
        pass
    surv = survivors(nonce)
    left = []
    for dp, dns, fns in os.walk(tmpdir):
        left += dns + fns
    with open(outp, "rb") as f:
        out = f.read().decode("utf-8", "replace")
    with open(errp, "rb") as f:
        err = f.read().decode("utf-8", "replace")
    log = []
    if os.path.exists(shimlog):
        with open(shimlog, encoding="utf-8", errors="replace") as f:
            log = f.read().splitlines()
    rc = p.returncode if exited else None
    print(f"ARM {name} sig={sig.name} exited={'y' if exited else 'n'} rc={rc} "
          f"signal_line={'check-signal=FAIL' in out.splitlines()} "
          f"class={'RECEIPT-GATE-SIGNALED' in out + err} survivors={len(surv)} tmpleft={len(left)}")
    for line in log[:3]:
        print(f"    {line}")
    for line in (out + err).splitlines():
        if line.startswith(("check-", "detail-")):
            print(f"    OUT {line}")
    # reap anything that escaped
    for pid in survivors(nonce):
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    try:
        os.killpg(sid, signal.SIGKILL)
    except OSError:
        pass
    if p.poll() is None:
        p.kill()
        p.wait()


if __name__ == "__main__":
    arm("term", signal.SIGTERM, "rev-parse --verify")
    arm("int", signal.SIGINT, "rev-parse --verify")
    arm("hup", signal.SIGHUP, "rev-parse --verify")
    arm("early", signal.SIGTERM, "rev-parse --verify", early=True)
    arm("escape", signal.SIGTERM, "rev-parse --verify", escape=True)
