#!/usr/bin/env python3
"""E7: the sentinel's exit-70 path from a WORKER THREAD while the main thread holds the stderr lock.

Plain os._exit(0) from a worker thread terminates the process at once.  The r95 sentinel's replacement writes to
sys.stderr first; sys.stderr's buffered writer holds a lock, so the worker's write blocks until the main thread
releases it.  If the main thread is blocked inside its own stderr write (an undrained pipe), the lock is never
released and the process hangs instead of exiting 70.

Also re-checks buffered-stdout behaviour on the os._exit path (does the sentinel's flush keep it?).
"""
import os
import subprocess
import sys
import time

PY = sys.executable
HERE = os.path.dirname(os.path.abspath(__file__))

THREAD_CASE = """import os, sys, threading, time
def worker():
    time.sleep(1.0)
    os._exit(0)
t = threading.Thread(target=worker)
t.start()
sys.stderr.write("X" * 400000)
sys.stderr.flush()
time.sleep(10)
"""

FLUSH_CASE = """import os, sys
sys.stdout.write("BUFFERED-OUTPUT-NO-FLUSH")
os._exit(0)
"""

FLUSH_CASE_PLAIN = """import os, sys
sys.stdout.write("BUFFERED-OUTPUT-NO-FLUSH")
sys.stdout.flush()
os._exit(0)
"""


def with_undrained_stderr(env, path, label):
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
    print(f"[{label:26}] rc={rc} elapsed={time.time()-t0:.1f}s")


def main():
    hook_dir = sys.argv[1]
    base = dict(os.environ)
    hooked = dict(base)
    hooked["PYTHONPATH"] = hook_dir + (os.pathsep + base["PYTHONPATH"] if base.get("PYTHONPATH") else "")
    tpath = os.path.join(HERE, "child_thread.py")
    with open(tpath, "w", encoding="utf-8") as f:
        f.write(THREAD_CASE)
    with_undrained_stderr(base, tpath, "thread os._exit plain")
    with_undrained_stderr(hooked, tpath, "thread os._exit hooked")
    for label, src in (("buffered stdout, no flush", FLUSH_CASE),
                       ("buffered stdout, flushed", FLUSH_CASE_PLAIN)):
        path = os.path.join(HERE, "child_flush.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(src)
        for mode, env in (("plain", base), ("hooked", hooked)):
            p = subprocess.run([PY, "-B", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=20)
            print(f"[{mode:6}] {label:32} rc={p.returncode} stdout={p.stdout.decode()!r}")


if __name__ == "__main__":
    main()
