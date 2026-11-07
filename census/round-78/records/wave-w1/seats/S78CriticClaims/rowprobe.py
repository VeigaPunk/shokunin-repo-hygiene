#!/usr/bin/env python3
"""Run ONE c1-gitsrc-counter row by hand, printing the gate's full text and timing.
Usage: rowprobe.py GATE_DIR WORK_DIR ROWID [ROWID...]  (reuses the frozen counter's own fixture code)"""
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

gate_dir, work, ids = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3:]
gate = os.path.join(gate_dir, "souji-pre-report-gate.sh")
routes = {r[0]: r for r in mod.ROUTES}
for rid in ids:
    rid_, mut, envkeys, ev, ecls = routes[rid]
    rowdir = os.path.join(work, rid)
    extra = {}
    if mod.HOMEENV in envkeys:
        extra["HOME"] = os.path.join(rowdir, "home")
    if mod.XDGENV in envkeys:
        extra["XDG_CONFIG_HOME"] = os.path.join(rowdir, "xdg")
    clone, report, prereg = P.build(rowdir)
    for d in extra.values():
        os.makedirs(d, exist_ok=True)
    mut(clone, rowdir)
    env = P.env_clean(extra)
    t0 = time.monotonic()
    p = subprocess.Popen(["bash", gate, "--lane", clone, "--branch", "master", "--report", report,
                          "--prereg", prereg], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         stdin=subprocess.DEVNULL, env=env, start_new_session=True,
                         cwd=os.path.dirname(clone))
    try:
        out, err = p.communicate(timeout=120)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, 9)
        out, err = p.communicate()
        rc = "HANG(partial below)"
        print("PARTIAL-OUTPUT:")
        print((out + err).decode("utf-8", "replace"))
    print(f"=== ROW {rid} expect={ev}/{ecls} rc={rc} secs={time.monotonic()-t0:.1f}")
    print((out + err).decode("utf-8", "replace"))
