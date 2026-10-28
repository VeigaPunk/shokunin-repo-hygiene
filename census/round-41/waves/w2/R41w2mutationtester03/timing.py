#!/usr/bin/env python3
"""R41w2mutationtester03: observability probe for mutant G3 (argparse --timeout default 20 -> 1).

A FIFO HEAD makes every git call block, so the tool reports UNREACHABLE:list-timeout after the
effective timeout. With no --timeout flag the elapsed time equals the default (two blocked git
calls: the rev-parse precheck and worktree list). Runs against the BASE tool and the G3 mutant."""
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness as h  # noqa: E402


def probe(tool, tag):
    W = os.path.realpath(os.path.join(h.S, "work", tag, "x19"))
    shutil.rmtree(W, ignore_errors=True)
    os.makedirs(W)
    tmp = os.path.join(h.S, "tmp", tag)
    os.makedirs(tmp, exist_ok=True)
    R, O = h.base(W, tmp)
    h.git_init(R + "/t", tmp)
    os.remove(R + "/t/.git/HEAD")
    os.mkfifo(R + "/t/.git/HEAD")
    rec = h.write(O + "/rec", "REPO\tt\tregs=1\tprunable=0\n")
    t0 = time.monotonic()
    p = h.run_tool(tool, tmp, ["--root", R, "--record", rec, "--skip-unrecorded"], timeout=200)
    elapsed = time.monotonic() - t0
    shutil.rmtree(W, ignore_errors=True)
    ok = p is not None and p.returncode == 1 and "UNREACHABLE:list-timeout" in p.stdout
    return ok, elapsed, (p.returncode if p else "timeout"), (p.stdout.strip() if p else "")


if __name__ == "__main__":
    for tag in ("BASE", "G3"):
        tool = h.S + "/mut/BASE.py" if tag == "BASE" else h.S + "/mut/G3.py"
        ok, elapsed, rc, out = probe(tool, tag)
        print("X19-default-timeout tag=%s sha=%s elapsed=%.1fs rc=%s stdout=%s verdict=%s" % (
            tag, h.sha(tool), elapsed, rc, out.replace("\t", " | "), "PASS" if ok and elapsed >= 15 else "FAIL-or-short"))
