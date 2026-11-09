#!/usr/bin/env python3
"""E3b: does the sentinel's exit-70 path deadlock when os._exit is called from a signal handler?

os._exit is documented as safe to call from a signal handler (it does no allocation, no I/O).  The r95 sentinel
replaces os._exit with a Python function that writes to sys.stderr and flushes sys.stdout/sys.stderr, so the
replacement is NOT async-signal-safe.

Scenario: the main thread is blocked writing to a full stderr pipe (it holds the stderr lock), a SIGALRM arrives
and the handler calls os._exit(0).
  plain  : os._exit(0) leaves the process at once (async-signal-safe).
  hooked : the sentinel writes to sys.stderr from the handler -> needs the stderr lock the interrupted main
           thread still holds -> the process hangs instead of exiting.

A second scenario: the handler calls os._exit(0) while the main thread holds the *stdout* lock.
"""
import os
import subprocess
import sys
import time

PY = sys.executable
SIG_STDERR = """import os, signal, sys, time
def handler(signum, frame):
    os._exit(0)
signal.signal(signal.SIGALRM, handler)
signal.setitimer(signal.ITIMER_REAL, 1.0)
try:
    sys.stderr.write("X" * 400000)
    sys.stderr.flush()
except Exception as exc:
    pass
time.sleep(6)
print("STILL-ALIVE")
"""

SIG_STDOUT = """import os, signal, sys, time
def handler(signum, frame):
    os._exit(0)
signal.signal(signal.SIGALRM, handler)
sys.stdout.write("Y" * 400000)
sys.stdout.flush()
signal.setitimer(signal.ITIMER_REAL, 1.0)
time.sleep(6)
print("STILL-ALIVE")
"""


def main():
    hook_dir = sys.argv[1]
    base = dict(os.environ)
    hooked = dict(base)
    hooked["PYTHONPATH"] = hook_dir + (os.pathsep + base["PYTHONPATH"] if base.get("PYTHONPATH") else "")
    here = os.path.dirname(os.path.abspath(__file__))
    for label, src in (("signal->os._exit, stderr full", SIG_STDERR), ("signal->os._exit, stdout full", SIG_STDOUT)):
        path = os.path.join(here, "child_sig.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(src)
        for mode, env in (("plain", base), ("hooked", hooked)):
            t0 = time.time()
            try:
                p = subprocess.run([PY, "-B", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                                   timeout=12)
                print(f"[{mode:6}] {label:30} rc={p.returncode} t={time.time()-t0:.1f}s "
                      f"stdout={p.stdout.decode(errors='replace')[-60:]!r}")
            except subprocess.TimeoutExpired as exc:
                print(f"[{mode:6}] {label:30} HUNG (12s timeout, expected exit) "
                      f"stdout={exc.stdout!r}")


if __name__ == "__main__":
    main()
