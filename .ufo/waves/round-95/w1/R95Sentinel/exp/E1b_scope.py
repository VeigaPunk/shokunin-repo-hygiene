#!/usr/bin/env python3
"""E1b: scope of the r95 sitecustomize over processes that are NOT the counter.

Run as a child with (and without) the frozen hook on PYTHONPATH:
  S-C  multiprocessing Pool worker (the fork/forkserver child calls os._exit itself)
  S-D  os.fork() then the child exits through os._exit
  S-E  a helper that wants sys.monitoring tool id 3 (a coverage-like tool)
  S-F  a helper that exits cleanly through os._exit(0) (a "helper finished" path)
  S-G  concurrent.futures.ProcessPoolExecutor worker
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

MP = """import multiprocessing, sys
def w(x):
    return x * 2
if __name__ == "__main__":
    try:
        with multiprocessing.Pool(1) as p:
            print("map:", p.map(w, [21]))
    except Exception as exc:
        print("pool-raised:", type(exc).__name__, exc)
        sys.exit(9)
    print("pool-ok")
"""

FORK = """import os, sys
pid = os.fork()
if pid == 0:
    os._exit(0)
print("child status:", os.waitpid(pid, 0)[1])
"""

TOOLID = """import sys
from sys import monitoring as m
try:
    m.use_tool_id(3, "helper-tool")
    print("use_tool_id(3): OK")
except ValueError as exc:
    print("use_tool_id(3): ValueError:", exc)
    sys.exit(4)
"""

CLEAN = """import os, sys
print("helper done")
sys.stdout.flush()
os._exit(0)
"""

PPE = """import concurrent.futures as cf, sys
if __name__ == "__main__":
    try:
        with cf.ProcessPoolExecutor(1) as ex:
            print("ppe:", ex.submit(lambda x: x * 2, 21).result())
    except Exception as exc:
        print("ppe-raised:", type(exc).__name__, exc)
        sys.exit(9)
"""

CASES = [("S-C multiprocessing", MP), ("S-D fork+os._exit", FORK), ("S-E monitor id 3", TOOLID),
         ("S-F clean os._exit(0)", CLEAN), ("S-G ProcessPoolExecutor", PPE)]


def main():
    hook_dir = sys.argv[1]
    base = dict(os.environ)
    hooked = dict(base)
    hooked["PYTHONPATH"] = hook_dir + (os.pathsep + base["PYTHONPATH"] if base.get("PYTHONPATH") else "")
    for label, src in CASES:
        path = os.path.join(HERE, "child_" + label.split()[0].replace("-", "_") + ".py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(src)
        for mode, env in (("plain", base), ("hooked", hooked)):
            t0 = time.time()
            try:
                p = subprocess.run([PY, "-B", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                                   timeout=30)
                out = p.stdout.decode(errors="replace").strip().replace("\n", " | ")
                err = p.stderr.decode(errors="replace").strip().replace("\n", " | ")
                print(f"[{mode:6}] {label:26} rc={p.returncode} t={time.time()-t0:.1f}s stdout={out!r} stderr={err[-160:]!r}")
            except subprocess.TimeoutExpired as exc:
                print(f"[{mode:6}] {label:26} TIMEOUT(30s) stdout={exc.stdout!r} stderr={exc.stderr!r}")


if __name__ == "__main__":
    main()
