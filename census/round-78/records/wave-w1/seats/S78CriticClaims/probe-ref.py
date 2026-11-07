#!/usr/bin/env python3
"""Loose-ref probe: pack refs, then replace $GIT_DIR/refs/heads/master with a FIFO; run the gate.
Usage: probe-ref.py GATE_DIR WORK_DIR"""
import importlib.util
import os
import subprocess
import sys
import time

C = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-78/c1-gitsrc-counter.py"
spec = importlib.util.spec_from_file_location("c1c", C)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
P = mod.P

gate_dir, work = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
gate = os.path.join(gate_dir, "souji-pre-report-gate.sh")
rowdir = os.path.join(work, "loose-ref-fifo")
clone, report, prereg = P.build(rowdir)
P.git(clone, "pack-refs", "--all", "--prune")
ref = os.path.join(clone, ".git", "refs", "heads", "master")
assert not os.path.lexists(ref), ref
os.mkfifo(ref)
print("fixture:", clone, "ref is fifo:", os.path.exists(ref) and not os.path.isfile(ref))
env = P.env_clean({})
t0 = time.monotonic()
p = subprocess.Popen(["bash", gate, "--lane", clone, "--branch", "master", "--report", report,
                      "--prereg", prereg], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                     stdin=subprocess.DEVNULL, env=env, start_new_session=True,
                     cwd=os.path.dirname(clone))
try:
    out, err = p.communicate(timeout=100)
    rc = p.returncode
except subprocess.TimeoutExpired:
    os.killpg(p.pid, 9)
    out, err = p.communicate()
    rc = "HANG"
print(f"=== loose-ref-fifo rc={rc} secs={time.monotonic() - t0:.1f}")
print((out + err).decode("utf-8", "replace"))
