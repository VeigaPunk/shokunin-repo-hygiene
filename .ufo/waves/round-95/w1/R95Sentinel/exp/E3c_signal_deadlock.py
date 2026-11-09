#!/usr/bin/env python3
"""E3c: the sentinel's exit-70 path from a SIGNAL HANDLER with an undrained stderr pipe.

os._exit is documented async-signal-safe: it does no I/O and no allocation, so it may be called from a signal
handler.  The r95 sentinel replaces os._exit with a Python function that does sys.stderr.write(...), flushes
sys.stdout and sys.stderr, then calls the real os._exit.

Scenario: the main thread is blocked inside sys.stderr.write() (stderr is a pipe nobody drains) and therefore
HOLDS the TextIOWrapper lock; SIGALRM fires and the handler calls os._exit(0).
  plain  : os._exit(0) leaves the process at once.
  hooked : the sentinel's sys.stderr.write in the handler needs the very lock the interrupted main thread holds
           -> deadlock (the process hangs instead of exiting).
"""
import os
import signal
import subprocess
import sys
import time

PY = sys.executable

CHILD = """import os, signal, sys, time
def handler(signum, frame):
    os._exit(0)
signal.signal(signal.SIGALRM, handler)
signal.setitimer(signal.ITIMER_REAL, 1.0)
try:
    sys.stderr.write("X" * 400000)
    sys.stderr.flush()
except Exception as exc:
    pass
time.sleep(5)
print("STILL-ALIVE")
"""


def run(label, env):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "child_sig2.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(CHILD)
    # stderr -> a pipe that is never drained; stdout -> devnull
    r, w = os.pipe()
    t0 = time.time()
    p = subprocess.Popen([PY, "-B", path], stdout=subprocess.DEVNULL, stderr=w, env=env)
    os.close(w)
    try:
        p.wait(timeout=12)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        p.kill()
        p.wait()
        rc = "HUNG"
    os.close(r)
    print(f"[{label:7}] rc={rc} elapsed={time.time()-t0:.1f}s")


def main():
    hook_dir = sys.argv[1]
    base = dict(os.environ)
    hooked = dict(base)
    hooked["PYTHONPATH"] = hook_dir + (os.pathsep + base["PYTHONPATH"] if base.get("PYTHONPATH") else "")
    run("plain", base)
    run("hooked", hooked)


if __name__ == "__main__":
    main()
