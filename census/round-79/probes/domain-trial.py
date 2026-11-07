#!/usr/bin/env python3
"""souji r79 domain trial (C1 conjunct; r78 routed defect 4 answered: the report is graded on its filed bytes).

Usage: python3 -B census/round-79/probes/domain-trial.py --report REPORT --prereg PREREG --out OUT
Runs the lane's committed gate over the lane itself, twice, and writes OUT outside the lane:
  arm 1 (no signal): the gate's check lines and exit code; the conjunct is check-gitsource=PASS, check-tip=PASS,
        check-clean=PASS and no check-signal line;
  arm 2 (real signal, no shim): the gate is started in its own session with a marker env var, receives SIGTERM
        on its pid after DELAY seconds (it is then inside one of its own children on the real lane), and the
        trial records the exit code, the check-signal line and every process still carrying the marker 5 s later
        (they are SIGKILLed after being counted).
The receipt binds the trial script's bytes and blob at master, the gate bytes run and the candidate blob of W1
(amendment=none when equal), the writer, and report_sha256 over the report's bytes with its `Final lane hash:`
line(s) removed (that line can only be written after the lane lands; every other byte of the filed report is
graded).
"""
import argparse
import hashlib
import os
import secrets
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
W1 = "c8c3fbca5ac44184feac3a01ee964139f86c02a4"
DELAY = 3.0
SETTLE = 5.0
LANE = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
SELF = "census/round-79/probes/domain-trial.py"


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", LANE, *args], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout


def marked(nonce):
    key = f"SOUJI_R79_TRIAL={nonce}".encode()
    out = []
    for d in os.listdir("/proc"):
        if d.isdigit():
            try:
                with open(f"/proc/{d}/environ", "rb") as f:
                    if key in f.read().split(b"\0"):
                        with open(f"/proc/{d}/stat", "rb") as g:
                            if g.read().rsplit(b")", 1)[1].split()[0] != b"Z":
                                out.append(int(d))
            except OSError:
                pass
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True)
    ap.add_argument("--prereg", required=True)
    ap.add_argument("--out", required=True)
    ns = ap.parse_args(argv)
    if os.path.realpath(os.path.abspath(__file__)) != os.path.join(LANE, SELF):
        print(f"domain-trial: run the committed script at {LANE}/{SELF}", file=sys.stderr)
        return 2
    out = os.path.abspath(ns.out)
    if os.path.exists(out) or os.path.realpath(out).startswith(LANE + "/"):
        print("domain-trial: OUT exists or is inside the lane", file=sys.stderr)
        return 2
    gate = os.path.join(LANE, "tools/souji-pre-report-gate.sh")
    with open(gate, "rb") as f:
        run_sha = sha_bytes(f.read())
    w_sha = sha_bytes(git("show", f"{W1}:tools/souji-pre-report-gate.sh"))
    with open(ns.report, "rb") as f:
        rep = f.read()
    graded = b"".join(l for l in rep.splitlines(keepends=True) if not l.startswith(b"Final lane hash:"))
    lines = []
    p = lambda s: lines.append(s)
    with open(os.path.abspath(__file__), "rb") as f:
        p(f"command=python3 -B {SELF} --report {ns.report} --prereg {ns.prereg} --out {ns.out}")
        p(f"rev={git('rev-parse', 'master').decode().strip()}")
        p(f"trial_script={SELF} sha256={sha_bytes(f.read())}")
    p(f"trial_script_blob_at_master_sha256={sha_bytes(git('show', 'master:' + SELF))}")
    p(f"gate=tools/souji-pre-report-gate.sh sha256={run_sha}")
    p(f"gate_blob_at_master_sha256={sha_bytes(git('show', 'master:tools/souji-pre-report-gate.sh'))}")
    p(f"candidate_W1={W1} gate_blob_sha256={w_sha}")
    p("amendment=none" if run_sha == w_sha else f"amendment={w_sha} -> {run_sha}")
    with open(os.path.join(LANE, "tools/souji-receipt-write.py"), "rb") as f:
        p(f"writer sha256={sha_bytes(f.read())}")
    p(f"report={ns.report} report_bytes={len(rep)} graded_bytes={len(graded)} report_sha256={sha_bytes(graded)}"
      " (Final lane hash: line(s) removed)")
    p(f"remote_tip={git('ls-remote', 'origin', 'refs/heads/master').decode().split()[0]}")
    p(f"# host={os.uname().sysname} {os.uname().release}; sigint_at_start={signal.getsignal(signal.SIGINT)}")
    argvg = ["bash", gate, "--lane", LANE, "--branch", "master", "--report", ns.report, "--prereg", ns.prereg]
    # arm 1
    t0 = time.monotonic()
    r = subprocess.run(argvg, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                       preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_DFL))
    a1 = r.stdout.decode("utf-8", "replace").splitlines()
    for l in a1:
        p("ARM1 " + l)
    p(f"ARM1 wall_seconds={time.monotonic() - t0:.3f} EXIT={r.returncode}")
    need = ("check-gitsource=PASS", "check-tip=PASS", "check-clean=PASS")
    ok1 = all(n in a1 for n in need) and not any(l.startswith("check-signal") for l in a1)
    p(f"ARM1 conjunct={'PASS' if ok1 else 'FAIL'}")
    # arm 2
    nonce = secrets.token_hex(8)
    env = dict(os.environ, SOUJI_R79_TRIAL=nonce)
    g = subprocess.Popen(argvg, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                         env=env, start_new_session=True,
                         preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_DFL))
    time.sleep(DELAY)
    before = len(marked(nonce))
    exited = False
    if g.poll() is None:
        os.kill(g.pid, signal.SIGTERM)
        try:
            g.wait(timeout=SETTLE)
            exited = True
        except subprocess.TimeoutExpired:
            pass
        time.sleep(SETTLE)
    surv = marked(nonce)
    for pid in surv:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    try:
        os.killpg(g.pid, signal.SIGKILL)
    except OSError:
        pass
    a2 = g.communicate()[0].decode("utf-8", "replace").splitlines()
    for l in a2:
        p("ARM2 " + l)
    p(f"ARM2 delay={DELAY}s marked_before_signal={before} exited_within_{SETTLE:.0f}s={'y' if exited else 'n'} "
      f"rc={g.returncode} survivors={len(surv)}")
    ok2 = exited and g.returncode == 143 and "check-signal=FAIL" in a2 and not surv and before > 1
    p(f"ARM2 conjunct={'PASS' if ok2 else 'FAIL'}")
    p(f"EXIT={0 if ok1 and ok2 else 1}")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if ok1 and ok2 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
