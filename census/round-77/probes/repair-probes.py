#!/usr/bin/env python3
"""souji r77 wave-repair probes (after measurement; the frozen 16-row counter cannot see these routes).

Each arm builds a fresh fixture (census/round-74 evade-probe build(), imported through the frozen C1 counter),
applies one route, and runs two gate copies, W (the measured C1 candidate, blob at 9b496b08) and R (the
repaired gate), each in its own session with a 20 s bound and a process-group kill. Both copies are run with
`gate_timeout=5` patched in (the only edit; the patched digests are printed) so a check-4 stall shows as a
timed-out FAIL within the bound instead of 300 s. An arm is as expected when both arms print the expected
verdict and class: class NONREG = `RECEIPT-NONREGULAR-SOURCE` in detail-clean, TIMEOUT = a FAIL whose
detail names the timeout/failed status and not NONREG, SCAN = the NONREG class with `source scan failed`,
`-` = no class requirement.

Usage: repair-probes.py --w-gate W.sh --r-gate R.sh --writer WRITER.py --work EMPTY_DIR
Output: `ARM <id> W=<verdict>/<class> R=<verdict>/<class> want W=<..> R=<..> as_expected=<yes|no>` per arm,
then `SUMMARY arms=<n> as_expected=<m>`; exit 0 iff m == n.
"""
import argparse
import hashlib
import importlib.util
import os
import shutil
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("c77", os.path.join(HERE, "..", "c1-nonreg-counter.py"))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
P = C.P
NONREG = "RECEIPT-NONREGULAR-SOURCE"


def patched(src, dst):
    s = open(src, encoding="utf-8").read()
    assert s.count("gate_timeout=300\n") == 1, src
    s = s.replace("gate_timeout=300\n", "gate_timeout=5\n")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(s)
    return hashlib.sha256(s.encode()).hexdigest()


def run(gate_dir, clone, report, prereg, extra_env=None, branch="master"):
    env = P.env_clean()
    if extra_env:
        env.update(extra_env)
    t0 = time.monotonic()
    p = subprocess.Popen(["bash", os.path.join(gate_dir, "souji-pre-report-gate.sh"), "--lane", clone,
                          "--branch", branch, "--report", report, "--prereg", prereg],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, env=env,
                         start_new_session=True)
    try:
        out, err = p.communicate(timeout=20)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        p.communicate()
        return "HANG", "-", time.monotonic() - t0
    text = out.decode("utf-8", "replace") + err.decode("utf-8", "replace")
    clean = next((l.split("=", 1)[1] for l in text.splitlines() if l.startswith("check-clean=")), "-")
    det = " ".join(l for l in text.splitlines() if l.startswith("detail-clean"))
    if NONREG in det:
        cls = "SCAN" if "source scan failed" in det else "NONREG"
    elif clean == "FAIL" and ("timed out" in det or "failed" in det or "no output" in det):
        cls = "TIMEOUT"
    else:
        cls = "-"
    return clean, cls, time.monotonic() - t0


def commit_push(c, *paths):
    P.git(c, "add", "--", *paths)
    P.git(c, "commit", "-q", "-m", "fixture")
    P.git(c, "push", "-q", "origin", "master")


# ---------------------------------------------------------------- arms: mutate(clone, rowdir) -> (lane, env)
def a_commondir(c, w):
    """lane = a linked worktree; FIFO at the COMMON info/exclude (git reads it there)."""
    wt = os.path.join(w, "wt")
    P.git(c, "worktree", "add", "-q", "--detach", wt)
    P.git(wt, "checkout", "-q", "-B", "master2")
    P.git(wt, "push", "-q", "origin", "master2")
    C._fifo(os.path.join(c, ".git", "info", "exclude"))
    return wt, None, "master2"


def a_symlink_regular(c, w):
    """honest: a committed sub/.gitignore that is a symlink to a committed regular rules file."""
    C._write(os.path.join(c, "rules.txt"), b"*.tmp\n")
    os.symlink("../rules.txt", os.path.join(c, "sub", ".gitignore"))
    commit_push(c, "rules.txt", "sub/.gitignore")
    return c, None, "master"


def a_unreadable(c, w):
    """a new untracked directory the scan cannot read, holding a FIFO .gitignore (mode 000)."""
    d = os.path.join(c, "locked")
    C._fifo(os.path.join(d, ".gitignore"))
    os.chmod(d, 0)
    return c, None, "master"


def a_unreadable_ignored(c, w):
    """the same unreadable FIFO directory under a tracked rule that ignores it, so status reads clean."""
    with open(os.path.join(c, ".gitignore"), "ab") as f:
        f.write(b"/locked/\n")
    commit_push(c, ".gitignore")
    return a_unreadable(c, w)


def a_devnull(c, w):
    """honest: core.excludesFile=/dev/null (the documented way to disable it)."""
    P.git(c, "config", "core.excludesFile", "/dev/null")
    return c, None, "master"


def a_index_fifo(c, w):
    """$GIT_DIR/index replaced by a FIFO."""
    C._fifo(os.path.join(c, ".git", "index"))
    return c, None, "master"


def a_sparse_fifo(c, w):
    """core.sparseCheckout=true and a FIFO info/sparse-checkout."""
    P.git(c, "config", "core.sparseCheckout", "true")
    C._fifo(os.path.join(c, ".git", "info", "sparse-checkout"))
    return c, None, "master"


def a_fsmonitor_hook(c, w):
    """honest tree; a repository-local core.fsmonitor hook that sleeps (the W status call ran it)."""
    hook = os.path.join(w, "fsm.sh")
    C._write(hook, b"#!/bin/sh\nsleep 600\n")
    os.chmod(hook, 0o755)
    P.git(c, "config", "core.fsmonitor", hook)
    return c, None, "master"


def a_xdg_fifo(c, w):
    """FIFO at $XDG_CONFIG_HOME/git/ignore, core.excludesFile unset (regression: W already refuses)."""
    x = os.path.join(w, "xdg")
    C._fifo(os.path.join(x, "git", "ignore"))
    return c, {"XDG_CONFIG_HOME": x}, "master"


def a_relative_excludesfile(c, w):
    """relative core.excludesFile naming an untracked FIFO in the work tree (regression)."""
    C._fifo(os.path.join(c, "xf-rel"))
    P.git(c, "config", "core.excludesFile", "xf-rel")
    return c, None, "master"


ARMS = [
    # id, builder, want W (verdict, class), want R (verdict, class)
    ("commondir-info-exclude", a_commondir, ("FAIL", "TIMEOUT"), ("FAIL", "NONREG")),
    ("symlink-to-regular-gitignore", a_symlink_regular, ("FAIL", "NONREG"), ("PASS", "-")),
    # run 1 expected W PASS here before observing it; git status lists the unreadable untracked directory
    # (records/wave-repair/attempts/repair-probes-run1.txt). The ignored variant below is the fail-open arm.
    ("unreadable-dir-fifo", a_unreadable, ("FAIL", "-"), ("FAIL", "SCAN")),
    ("unreadable-ignored-dir-fifo", a_unreadable_ignored, ("PASS", "-"), ("FAIL", "SCAN")),
    ("excludesfile-devnull", a_devnull, ("FAIL", "NONREG"), ("PASS", "-")),
    ("index-fifo", a_index_fifo, ("FAIL", "TIMEOUT"), ("FAIL", "NONREG")),
    ("sparse-checkout-fifo", a_sparse_fifo, ("FAIL", "TIMEOUT"), ("FAIL", "NONREG")),
    ("fsmonitor-hook-sleeps", a_fsmonitor_hook, ("FAIL", "TIMEOUT"), ("PASS", "-")),
    ("xdg-ignore-fifo", a_xdg_fifo, ("FAIL", "NONREG"), ("FAIL", "NONREG")),
    ("relative-excludesfile-fifo", a_relative_excludesfile, ("FAIL", "NONREG"), ("FAIL", "NONREG")),
]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--w-gate", required=True)
    ap.add_argument("--r-gate", required=True)
    ap.add_argument("--writer", required=True)
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.exists(work) and os.listdir(work):
        print("PROBE-FATAL: --work not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    gd = {}
    for k, src in (("W", ns.w_gate), ("R", ns.r_gate)):
        d = os.path.join(work, "gate-" + k)
        h = patched(src, os.path.join(d, "souji-pre-report-gate.sh"))
        shutil.copy(ns.writer, os.path.join(d, "souji-receipt-write.py"))
        with open(src, "rb") as f:
            print(f"# {k} source sha256={hashlib.sha256(f.read()).hexdigest()} patched(gate_timeout=5) sha256={h}")
        gd[k] = d
    with open(ns.writer, "rb") as f:
        print(f"# writer sha256={hashlib.sha256(f.read()).hexdigest()}")
    with open(os.path.abspath(__file__), "rb") as f:
        print(f"# probe sha256={hashlib.sha256(f.read()).hexdigest()}")
    ok = 0
    for aid, build, ww, wr in ARMS:
        got = {}
        for k in ("W", "R"):
            rowdir = os.path.join(work, f"{aid}-{k}")
            clone, report, prereg = P.build(rowdir)
            lane, env, branch = build(clone, rowdir)
            clean, cls, secs = run(gd[k], lane, report, prereg, env, branch)
            got[k] = (clean, cls, secs)
            locked = os.path.join(clone, "locked")
            if os.path.isdir(locked):
                os.chmod(locked, 0o755)
        good = got["W"][:2] == ww and got["R"][:2] == wr
        ok += good
        print(f"ARM {aid} W={got['W'][0]}/{got['W'][1]}({got['W'][2]:.1f}s) R={got['R'][0]}/{got['R'][1]}"
              f"({got['R'][2]:.1f}s) want W={ww[0]}/{ww[1]} R={wr[0]}/{wr[1]} as_expected={'yes' if good else 'no'}")
    print(f"SUMMARY arms={len(ARMS)} as_expected={ok}")
    return 0 if ok == len(ARMS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
