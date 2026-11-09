#!/usr/bin/env python3
"""E16 (corrected): the r95 crash path's I/O can block where r94's had no window.

Design: stderr is a pipe with NO reader.  The child writes exactly the pipe capacity (so its own write SUCCEEDS
and returns), then calls os._exit(1).
  plain  : os._exit(1) ends the process at once with status 1 (r94 behaved this way too).
  hooked : the r95 sentinel first writes "SOUJI-R95-CRASH os._exit(1)" to stderr.  The pipe buffer is already
           full, so that write blocks -> the process NEVER exits 70; it hangs until killed.
That is the widened channel's own cost: the os._exit channel now needs stderr to have room.
"""
import os
import subprocess
import sys
import time

PY = sys.executable
HERE = os.path.dirname(os.path.abspath(__file__))
HOOK_DIR = "/fast/scratch/hyaku/souji-r95/R95Sentinel/hook"

CHILD = """import os, sys
n = int(os.environ.get("FILL_BYTES", "65536"))
try:
    sys.stderr.write("X" * n)
    sys.stderr.flush()
except Exception as exc:
    sys.stderr.write("fill failed: %r\\n" % (exc,))
    sys.stderr.flush()
sys.stderr.write("[fill done, calling os._exit]\\n")
sys.stderr.flush()
os._exit(1)
"""


def main():
    path = os.path.join(HERE, "child_fill.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(CHILD)
    base = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}
    hooked = dict(base)
    hooked["PYTHONPATH"] = HOOK_DIR
    for label, env in (("plain", base), ("hooked", hooked)):
        r, w = os.pipe()
        # find the pipe capacity
        import fcntl
        cap = fcntl.fcntl(w, 1032)  # F_GETPIPE_SZ
        env2 = dict(env)
        env2["FILL_BYTES"] = str(cap)
        t0 = time.time()
        p = subprocess.Popen([PY, "-B", path], stdout=subprocess.DEVNULL, stderr=w, env=env2)
        os.close(w)
        try:
            p.wait(timeout=8)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
            rc = "HUNG (never exited 70)"
        # drain whatever is in the pipe so we can see the tail
        try:
            os.set_blocking(r, False)
            tail = os.read(r, 200000)[-120:]
        except OSError:
            tail = b""
        os.close(r)
        print(f"[{label:6}] pipe_cap={cap} rc={rc} elapsed={time.time()-t0:.1f}s tail={tail[-90:]!r}")


if __name__ == "__main__":
    main()
