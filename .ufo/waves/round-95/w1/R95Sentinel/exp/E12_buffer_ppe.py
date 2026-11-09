#!/usr/bin/env python3
"""E12: precise buffering + non-counter multiprocessing damage.

B1  plain os._exit(0) with UNFLUSHED stdout: is the buffered text lost? (os._exit does not flush)
B2  the same under the sentinel: the sentinel flushes stdout before exiting 70 -> the text is KEPT.
    So the sentinel CHANGES the discard-on-os._exit semantics into keep-on-crash.
B3  a ProcessPoolExecutor whose worker is a module-level function: under the sentinel the worker's own
    os._exit(0) at the end of its life becomes exit 70, and concurrent.futures checks the worker's exit status.
"""
import os
import subprocess
import sys
import time

PY = sys.executable
HERE = os.path.dirname(os.path.abspath(__file__))

BUF = """import os, sys
sys.stdout.write("PARTIAL-ROW-LINE-NO-NEWLINE")
sys.stdout.flush()
sys.stderr.write("PARTIAL-STDERR")
os._exit(0)
"""

PPE = """import concurrent.futures as cf, os, sys, time
def work(x):
    return x * 2
if __name__ == "__main__":
    try:
        with cf.ProcessPoolExecutor(1) as ex:
            r = ex.submit(work, 21).result(timeout=30)
            print("ppe result:", r)
            time.sleep(1.5)
            print("ppe still alive")
    except Exception as exc:
        print("ppe-raised:", type(exc).__name__, exc)
        sys.exit(9)
"""


def main():
    hook_dir = sys.argv[1]
    base = dict(os.environ)
    hooked = dict(base)
    hooked["PYTHONPATH"] = hook_dir + (os.pathsep + base["PYTHONPATH"] if base.get("PYTHONPATH") else "")
    path = os.path.join(HERE, "child_buf.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(BUF)
    for mode, env in (("plain", base), ("hooked", hooked)):
        p = subprocess.run([PY, "-B", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=30)
        print(f"[B {mode:6}] rc={p.returncode} stdout={p.stdout.decode()!r} stderr={p.stderr.decode()!r}")
    ppe = os.path.join(HERE, "child_ppe.py")
    with open(ppe, "w", encoding="utf-8") as f:
        f.write(PPE)
    for mode, env in (("plain", base), ("hooked", hooked)):
        p = subprocess.run([PY, "-B", ppe], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=60)
        print(f"[PPE {mode:6}] rc={p.returncode} stdout={p.stdout.decode().strip()!r} "
              f"stderr={p.stderr.decode(errors='replace').strip()[:200]!r}")


if __name__ == "__main__":
    main()
