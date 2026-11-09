#!/usr/bin/env python3
"""E15: two final checks.

P1  The r95 crash path does I/O (sys.stderr.write + flush) before exiting 70.  If stderr is a pipe with a FULL
    buffer and NO reader, that write blocks: the process never exits 70 -- it hangs.  r94's sentinel left
    os._exit alone, so the os._exit channel had no such window.
P2  The C1 HARNESS itself (not just the counter) runs under the sentinel: census/round-95/c1-survivor-search.py
    starts the harness with PYTHONPATH=<hook dir>, so every Python process under it -- the harness, the counter
    and every git helper they spawn -- imports the sitecustomize.  Proof: a wrapper sitecustomize that prints a
    marker, run with the real harness on PYTHONPATH.
"""
import os
import subprocess
import sys
import time

PY = sys.executable
HERE = os.path.dirname(os.path.abspath(__file__))
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
HOOK_DIR = "/fast/scratch/hyaku/souji-r95/R95Sentinel/hook"

FULL_STDERR = """import os, sys
sys.stderr.write("X" * 300000)      # fills the 64 KiB pipe buffer; nobody drains it
sys.stderr.flush()
os._exit(1)                          # the r95 sentinel now writes a marker to stderr before exiting 70
"""

FULL_STDERR_PLAIN = """import os, sys
sys.stderr.write("X" * 300000)
sys.stderr.flush()
os._exit(1)
"""


def p1_full_stderr():
    path = os.path.join(HERE, "child_full_stderr.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(FULL_STDERR)
    base = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}
    hooked = dict(base)
    hooked["PYTHONPATH"] = HOOK_DIR
    for label, env in (("plain", base), ("hooked", hooked)):
        r, w = os.pipe()
        t0 = time.time()
        p = subprocess.Popen([PY, "-B", path], stdout=subprocess.DEVNULL, stderr=w, env=env)
        os.close(w)
        try:
            p.wait(timeout=10)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
            rc = "HUNG (never exited 70)"
        os.close(r)
        print(f"[P1 {label:6}] os._exit(1) with a full stderr pipe -> rc={rc} elapsed={time.time()-t0:.1f}s")


def p2_harness_under_sentinel():
    """A wrapper sitecustomize that prints a marker, then execs the frozen r95 hook.  If the real harness
    imports it, the harness process itself is under the sentinel."""
    d = os.path.join(HERE, "p2")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "sitecustomize.py"), "w", encoding="utf-8") as f:
        f.write("import sys\n"
                "sys.stderr.write('SENTINEL-LOADED-INTO-' + repr(sys.argv[0]) + '\\n')\n"
                "sys.stderr.flush()\n"
                "exec(compile(open(%r, encoding='utf-8').read(), 'sitecustomize.py', 'exec'))\n"
                % os.path.join(HOOK_DIR, "sitecustomize.py"))
    env = dict(os.environ)
    env["PYTHONPATH"] = d
    # run the real harness with a deliberately absent --population so it exits early (cheap, no clone)
    p = subprocess.run([PY, "-B", os.path.join(LANE, "census/round-93/c1-false-row-harness.py"),
                        "--counter", os.path.join(LANE, "census/round-87/c1-pointer-counter.py"),
                        "--lane", LANE, "--fleet-root", "/home/vgpnk/Projects/shokunin",
                        "--work", os.path.join(HERE, "p2work"),
                        "--population", os.path.join(HERE, "no-such-population.tsv")],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=120)
    err = p.stderr.decode(errors="replace")
    print(f"[P2 harness under sentinel] rc={p.returncode} marker_in_stderr={'SENTINEL-LOADED-INTO' in err}")
    for line in err.splitlines():
        if "SENTINEL-LOADED-INTO" in line:
            print(f"    {line}")


if __name__ == "__main__":
    p1_full_stderr()
    p2_harness_under_sentinel()
