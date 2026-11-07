#!/usr/bin/env python3
"""S79MutGate: candidate rows for the survivors. Each runs the base gate (W1) and one mutant on the same
row and prints the deciding lines. No lane file is touched; everything lives in scratch."""
import importlib.util
import os
import secrets
import signal
import subprocess
import sys
import time

S = "/fast/scratch/hyaku/souji-r79/S79MutGate"
PROBE = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-74/records/wave-repair/probes/evade-probe.py"
spec = importlib.util.spec_from_file_location("evade", PROBE)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)
REAL_GIT = subprocess.run(["bash", "-lc", "command -v git"], stdout=subprocess.PIPE).stdout.decode().strip()


def fresh(name):
    d = os.path.join(S, "probe", name)
    subprocess.run(["rm", "-rf", "--", d], check=True)
    os.makedirs(d)
    return d


def shim_dir(d, body_by_name):
    sd = os.path.join(d, "shim")
    os.makedirs(sd, exist_ok=True)
    for name, body in body_by_name.items():
        p = os.path.join(sd, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)
        os.chmod(p, 0o755)
    return sd


def survivors(nonce):
    key = f"SOUJI_R79_NONCE={nonce}".encode()
    out = []
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            e = open(f"/proc/{d}/environ", "rb").read().split(b"\0")
            st = open(f"/proc/{d}/stat", "rb").read().rsplit(b")", 1)[1].split()[0]
        except OSError:
            continue
        if key in e and st != b"Z":
            out.append(int(d))
    return out


def reap(p, nonce):
    for pid in survivors(nonce):
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except OSError:
        pass
    if p.poll() is None:
        p.kill()
        p.wait()


def run_gate(gate_dir, d, env_extra, signal_spec=None):
    """signal_spec: (signo, count, gap) sent to the gate pid once the mark appears."""
    clone, report, prereg = P.build(os.path.join(d, "row"))
    tmpdir = os.path.join(d, "tmp")
    os.makedirs(tmpdir)
    nonce = secrets.token_hex(8)
    env = P.env_clean({"PATH": os.path.join(d, "shim") + os.pathsep + os.environ["PATH"], "TMPDIR": tmpdir,
                       "SOUJI_R79_NONCE": nonce})
    env.update(env_extra)
    p = subprocess.Popen(["bash", os.path.join(gate_dir, "souji-pre-report-gate.sh"), "--lane", clone,
                          "--branch", "master", "--report", report, "--prereg", prereg],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                         env=env, start_new_session=True, cwd=d)
    mark = env_extra.get("MARK")
    t0 = time.monotonic()
    if mark:
        while not os.path.exists(mark) and p.poll() is None and time.monotonic() - t0 < 30:
            time.sleep(0.02)
        if os.path.exists(mark):
            time.sleep(0.3)
            signo, count, gap = signal_spec
            for _ in range(count):
                os.kill(p.pid, signo)
                time.sleep(gap)
    try:
        out, err = p.communicate(timeout=8)
        exited = True
    except subprocess.TimeoutExpired:
        out, err = b"", b""
        exited = False
    time.sleep(1.0)
    surv = survivors(nonce)
    left = []
    for dp, dns, fns in os.walk(tmpdir):
        left += dns + fns
    reap(p, nonce)
    text = (out + err).decode("utf-8", "replace")
    return {"exited": exited, "rc": p.returncode, "survivors": len(surv), "tmpleft": len(left),
            "signal_line": "check-signal=FAIL" in out.decode("utf-8", "replace"),
            "class": "RECEIPT-GATE-SIGNALED" in text,
            "clean": next((l for l in out.decode("utf-8", "replace").splitlines()
                           if l.startswith("check-clean")), "-"),
            "detail": next((l for l in text.splitlines() if l.startswith("detail-clean")), "-")}


# ---------------------------------------------------------------- row A: blocked grandchild
A_SHIM = """#!/bin/bash
if [[ -n ${HANG:-} ]]; then
  case " $* " in *"$HANG"*) printf '%s\\n' "$$" > "$MARK"; sleep 600 & wait ;; esac
fi
exec REALGIT "$@"
""".replace("REALGIT", REAL_GIT)


def rowA(gate_dir, label):
    d = fresh("rowA-" + label)
    shim_dir(d, {"git": A_SHIM})
    return run_gate(gate_dir, d, {"HANG": "status --porcelain", "MARK": os.path.join(d, "mark")},
                    (signal.SIGTERM, 1, 0))


# ---------------------------------------------------------------- row B: timeout that does not setpgid
B_TIMEOUT = """#!/bin/bash
[[ $1 == -k ]] && shift 2
shift
exec "$@"
"""


def rowB(gate_dir, label):
    d = fresh("rowB-" + label)
    shim_dir(d, {"timeout": B_TIMEOUT,
                 "git": """#!/bin/bash
if [[ -n ${HANG:-} ]]; then
  case " $* " in *"$HANG"*) printf '%s\\n' "$$" > "$MARK"; exec sleep 600 ;; esac
fi
exec REALGIT "$@"
""".replace("REALGIT", REAL_GIT)})
    return run_gate(gate_dir, d, {"HANG": "status --porcelain", "MARK": os.path.join(d, "mark")},
                    (signal.SIGTERM, 1, 0))


# ---------------------------------------------------------------- row C: untracked file hidden by info/exclude
def rowC(gate_dir, label):
    d = fresh("rowC-" + label)
    shim_dir(d, {})
    clone, report, prereg = P.build(os.path.join(d, "row"))
    with open(os.path.join(clone, "hidden-payload"), "wb") as f:
        f.write(b"payload the lane must not hide\n")
    with open(os.path.join(clone, ".git", "info", "exclude"), "a", encoding="utf-8") as f:
        f.write("hidden-payload\n")
    tmpdir = os.path.join(d, "tmp")
    os.makedirs(tmpdir)
    nonce = secrets.token_hex(8)
    env = P.env_clean({"PATH": os.path.join(d, "shim") + os.pathsep + os.environ["PATH"], "TMPDIR": tmpdir,
                       "SOUJI_R79_NONCE": nonce})
    p = subprocess.run(["bash", os.path.join(gate_dir, "souji-pre-report-gate.sh"), "--lane", clone,
                        "--branch", "master", "--report", report, "--prereg", prereg],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                       env=env, cwd=d, timeout=120)
    text = (p.stdout + p.stderr).decode("utf-8", "replace")
    return {"rc": p.returncode,
            "clean": next((l for l in p.stdout.decode().splitlines() if l.startswith("check-clean")), "-"),
            "detail": next((l for l in text.splitlines() if l.startswith("detail-clean")), "-")}


# ---------------------------------------------------------------- row D: TERM burst (re-entrancy guard)
def rowD(gate_dir, label):
    d = fresh("rowD-" + label)
    shim_dir(d, {"git": """#!/bin/bash
if [[ -n ${HANG:-} ]]; then
  case " $* " in *"$HANG"*) printf '%s\\n' "$$" > "$MARK"; exec sleep 600 ;; esac
fi
exec REALGIT "$@"
""".replace("REALGIT", REAL_GIT)})
    return run_gate(gate_dir, d, {"HANG": "status --porcelain", "MARK": os.path.join(d, "mark")},
                    (signal.SIGTERM, 60, 0.001))


def main():
    base = os.path.join(S, "base", "g")
    m = lambda x: os.path.join(S, "mutants", x, "g")
    cases = [
        ("A grandchild blocked (kills M01)", rowA, [("base", base), ("M01", m("M01-drop-group-kill"))]),
        ("B timeout without setpgid (kills M02)", rowB, [("base", base), ("M02", m("M02-drop-pid-kill"))]),
        ("C untracked file hidden by info/exclude (kills M09)", rowC, [("base", base), ("M09", m("M09-no-stdin-restore"))]),
        ("D TERM burst (kills M11)", rowD, [("base", base), ("M11", m("M11-no-reentrancy-guard"))]),
    ]
    for title, fn, arms in cases:
        print(f"=== {title} ===")
        for label, gd in arms:
            r = fn(gd, label)
            print(f"  {label:5s} " + " ".join(f"{k}={v}" for k, v in r.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
