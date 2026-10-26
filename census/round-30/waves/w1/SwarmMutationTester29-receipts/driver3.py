#!/usr/bin/env python3
"""Phase 3: m8 (lane-worktree gate) against a junk state held in a clone whose
worktree is checked out at BASE (worktree gate bytes = base gate bytes), so the
mutant's GATE leg really runs non-REV bytes."""
import os, subprocess, sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
BASE = "9420341d9a814cb6089c25fb03a4cc9b23dc0d1b"
JUNK = "db156ef836bdf1f9b280ac6c976ae3fbfcb93497"
S = "/fast/scratch/hyaku/souji-r30/MutateC2Counter"
C = os.path.join(S, "states/c")
D = os.path.join(S, "states/d")


def log(m):
    print(m, flush=True)


def sh(argv, cwd=None):
    p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True)
    if p.returncode:
        raise SystemExit(f"FAILED {argv}\n{p.stdout}\n{p.stderr}")
    return p


shutil = __import__("shutil")
shutil.rmtree(D, ignore_errors=True)
os.makedirs(os.path.dirname(D), exist_ok=True)
sh(["git", "clone", "-q", "--no-local", "--no-checkout", LANE, D])
sh(["git", "-C", D, "remote", "remove", "origin"])
top = sh(["git", "-C", D, "rev-parse", "--show-toplevel"]).stdout.strip()
assert top == D, top
sh(["git", "-C", D, "checkout", "-qf", "--detach", BASE])
head = sh(["git", "-C", D, "rev-parse", "HEAD"]).stdout.strip()
assert head == BASE, head
# bring the junk commit in without touching D's worktree
sh(["git", "-C", D, "fetch", "-q", C, JUNK])
sh(["git", "-C", D, "update-ref", f"refs/heads/junk-rig", JUNK])
log(f"D ready: worktree@{head}, junk commit {JUNK} present as refs/heads/junk-rig")

env = dict(os.environ, TMPDIR=os.path.join(S, "tmp"))
outp = os.path.join(S, "out", "p3-m8-lane-worktree-gate__junk.txt")
argv = [sys.executable, "-B", os.path.join(S, "mutants/m8-lane-worktree-gate.py"),
        "--root", D, "--rev", JUNK, "--base", BASE, "--fleet-root", FLEET,
        "--scratch", os.path.join(S, "counter-scratch")]
p = subprocess.run(argv, capture_output=True, text=True, env=env, timeout=1200)
with open(outp, "w") as fh:
    fh.write(f"# mutant=m8 state=junk(root=D, worktree@BASE) rev={JUNK}\n# rc={p.returncode}\n"
             + p.stdout + ("\n--stderr--\n" + p.stderr if p.stderr else ""))
summary = [l for l in p.stdout.splitlines() if l.startswith("SUMMARY")]
log(f"[m8 / junk(root=D)] rc={p.returncode} {summary[0] if summary else 'NO-SUMMARY'}")
log("== phase3 done ==")
