#!/usr/bin/env python3
"""E3: buffering and deadlock behaviour of the sentinel's exit-70 path.

  B1 buffered stdout then an uncaught exception: is the buffered text lost?
  B2 buffered stdout then os._exit(0): is the buffered text lost? (r94 os._exit loses it by definition)
  B3 os._exit called from a WORKER THREAD while the main thread holds the stderr lock
     (the lock is a real, non-reentrant lock -> the sentinel's sys.stderr.write can block forever)
  B4 os._exit called from a SIGNAL HANDLER while another thread holds the stderr lock
     (os._exit is documented async-signal-safe; the replacement does Python-level I/O)
  B5 os._exit called from a signal handler with a full stderr pipe (nobody drains it)
"""
import os
import subprocess
import sys

PY = sys.executable
CHILDREN = {
    "B1 buffered+raise": (
        "import sys\n"
        "print('BUFFERED-LINE')\n"
        "raise RuntimeError('boom')\n"
    ),
    "B2 buffered+os._exit": (
        "import os, sys\n"
        "print('BUFFERED-LINE')\n"
        "os._exit(0)\n"
    ),
    "B3 os._exit in thread, stderr lock held": (
        "import os, sys, threading, time\n"
        "lock = sys.stderr.lock if hasattr(sys.stderr, 'lock') else None\n"
        "sys.stderr.write('HELD\\n'); sys.stderr.flush()\n"
        "import io\n"
        "raw = sys.stderr.buffer\n"
        "raw.lock.acquire()\n"
        "def worker():\n"
        "    os._exit(5)\n"
        "t = threading.Thread(target=worker); t.start()\n"
        "time.sleep(6)\n"
        "print('STILL-ALIVE (no deadlock-free exit)')\n"
    ),
    "B4 os._exit in signal handler, stderr lock held by another thread": (
        "import os, signal, sys, threading, time\n"
        "raw = sys.stderr.buffer\n"
        "raw.lock.acquire()\n"
        "def handler(signum, frame):\n"
        "    os._exit(6)\n"
        "signal.signal(signal.SIGALRM, handler)\n"
        "signal.alarm(2)\n"
        "time.sleep(8)\n"
        "print('STILL-ALIVE')\n"
    ),
    "B5 os._exit in signal handler, stderr pipe full": (
        "import os, signal, sys, time\n"
        "def handler(signum, frame):\n"
        "    os._exit(7)\n"
        "signal.signal(signal.SIGALRM, handler)\n"
        "os.set_blocking(sys.stderr.fileno(), True)\n"
        "sys.stderr.write('X' * 200000)\n"
        "sys.stderr.flush()\n"
        "signal.alarm(2)\n"
        "time.sleep(8)\n"
        "print('STILL-ALIVE')\n"
    ),
}


def main():
    hook_dir = sys.argv[1]
    base = dict(os.environ)
    hooked = dict(base)
    hooked["PYTHONPATH"] = hook_dir + (os.pathsep + base["PYTHONPATH"] if base.get("PYTHONPATH") else "")
    for label, src in CHILDREN.items():
        for mode, env in (("plain", base), ("hooked", hooked)):
            try:
                p = subprocess.run([PY, "-B", "-c", src], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                                   timeout=20)
                out = p.stdout.decode(errors="replace").strip().replace("\n", " | ")
                err = p.stderr.decode(errors="replace").strip().replace("\n", " | ")
                print(f"[{mode:6}] {label:48} rc={p.returncode} stdout={out[-120:]!r} stderr={err[-200:]!r}")
            except subprocess.TimeoutExpired as exc:
                print(f"[{mode:6}] {label:48} TIMEOUT(20s) stdout={exc.stdout!r} stderr={exc.stderr!r}")


if __name__ == "__main__":
    main()
