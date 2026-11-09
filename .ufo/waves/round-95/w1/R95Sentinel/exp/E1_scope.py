#!/usr/bin/env python3
"""E1/E2: what the r95 sitecustomize does to a process that is NOT the counter.

Scenarios, each run as a separate child with (and without) the frozen hook on PYTHONPATH:
  S-A  os._exit(0)      a legitimate clean exit through os._exit
  S-B  os._exit(3)      a legitimate exit with a specific status
  S-C  multiprocessing  a Pool worker (multiprocessing's fork child calls os._exit itself)
  S-D  fork+os._exit    os.fork() then the child exits through os._exit
  S-E  monitorid       a helper that wants sys.monitoring tool id 3
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

CHILDREN = {
    "S-A os._exit(0)": "import os,sys; print('before'); sys.stdout.flush(); os._exit(0)\n",
    "S-B os._exit(3)": "import os,sys; print('before'); sys.stdout.flush(); os._exit(3)\n",
    "S-C multiprocessing": (
        "import multiprocessing, sys\n"
        "def w():\n"
        "    return 42\n"
        "if __name__ == '__main__':\n"
        "    try:\n"
        "        with multiprocessing.Pool(1) as p:\n"
        "            print('map:', p.map(w, [1]))\n"
        "    except Exception as exc:\n"
        "        print('pool-raised:', type(exc).__name__, exc)\n"
        "        sys.exit(9)\n"
    ),
    "S-D fork+os._exit": (
        "import os, sys\n"
        "pid = os.fork()\n"
        "if pid == 0:\n"
        "    os._exit(0)\n"
        "print('child status:', os.waitpid(pid, 0)[1])\n"
    ),
    "S-E monitorid": (
        "import sys\n"
        "from sys import monitoring as m\n"
        "try:\n"
        "    m.use_tool_id(3, 'helper-tool')\n"
        "    print('use_tool_id(3): OK')\n"
        "except ValueError as exc:\n"
        "    print('use_tool_id(3): ValueError:', exc)\n"
        "    sys.exit(4)\n"
    ),
}


def run(label, src, env):
    p = subprocess.run([PY, "-B", "-c", src], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                       timeout=60)
    return p


def main():
    hook_dir = sys.argv[1]
    base = dict(os.environ)
    hooked = dict(base)
    hooked["PYTHONPATH"] = hook_dir + (os.pathsep + base["PYTHONPATH"] if base.get("PYTHONPATH") else "")
    for label, src in CHILDREN.items():
        for mode, env in (("plain", base), ("hooked", hooked)):
            p = run(label, src, env)
            out = p.stdout.decode().strip().replace("\n", " | ")
            err = p.stderr.decode().strip().replace("\n", " | ")
            print(f"[{mode:6}] {label:24} rc={p.returncode} stdout={out!r} stderr={err!r}")


if __name__ == "__main__":
    main()
