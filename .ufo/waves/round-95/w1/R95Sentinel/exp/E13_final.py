#!/usr/bin/env python3
"""E13: final decisive checks.

(a) buffering precision: does the sentinel's exit-70 path LOSE buffered stdout, or keep it?
(b) fork duplication: the sentinel flushes stdout in a forked child -> the parent's unflushed buffer is
    written TWICE (plain os._exit does not flush, so it appears once).
(c) relative-path invocation: the SystemExit leg matches sys.modules['__main__'].__file__ against the RAISE
    callback's code.co_filename. Are they the same when the script is invoked by a RELATIVE path?
(d) fail-closed: if no sys.monitoring tool id is free, the sentinel's RAISE callback is never registered; the
    search's own CHECK script then sees a different exit status and the search must refuse to run.
"""
import os
import subprocess
import sys
import textwrap
import time

PY = sys.executable
HERE = os.path.dirname(os.path.abspath(__file__))
HOOK_DIR = "/fast/scratch/hyaku/souji-r95/R95Sentinel/hook"

NOFLUSH = """import os, sys
sys.stdout.write("BUFFERED-NOT-FLUSHED")
sys.stderr.write("ERR-NOT-FLUSHED")
os._exit(0)
"""

FORKDUP = """import os, sys
sys.stdout.write("PARENT-BUFFERED-TEXT")
pid = os.fork()
if pid == 0:
    os._exit(0)
os.waitpid(pid, 0)
sys.stdout.write("|PARENT-AFTER")
sys.stdout.flush()
"""

SE_IN_FUNC = """import sys
def helper():
    raise SystemExit("sysexit-in-function")
sys.exit(helper())
"""


def hooked_env():
    env = dict(os.environ)
    env["PYTHONPATH"] = HOOK_DIR + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return env


def a_buffering():
    path = os.path.join(HERE, "child_noflush.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(NOFLUSH)
    for mode, env in (("plain", dict(os.environ)), ("hooked", hooked_env())):
        p = subprocess.run([PY, "-B", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=30)
        print(f"[a buffering {mode:6}] rc={p.returncode} stdout={p.stdout.decode()!r} stderr={p.stderr.decode()!r}")


def b_fork_dup():
    path = os.path.join(HERE, "child_forkdup.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(FORKDUP)
    for mode, env in (("plain", dict(os.environ)), ("hooked", hooked_env())):
        p = subprocess.run([PY, "-B", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=30)
        print(f"[b fork-dup {mode:6}] rc={p.returncode} stdout={p.stdout.decode()!r} "
              f"stderr={p.stderr.decode(errors='replace').strip()[:120]!r}")


def c_relative_path():
    d = os.path.join(HERE, "relpath")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "child_se.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(SE_IN_FUNC)
    env = hooked_env()
    # absolute invocation
    p = subprocess.run([PY, "-B", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=30, cwd=d)
    print(f"[c abs  ] rc={p.returncode} stderr={p.stderr.decode(errors='replace').strip()[:140]!r}")
    # relative invocation (cwd = d, script named child_se.py)
    p = subprocess.run([PY, "-B", "child_se.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=30,
                       cwd=d)
    print(f"[c rel  ] rc={p.returncode} stderr={p.stderr.decode(errors='replace').strip()[:140]!r}")
    # -c invocation (no __main__.__file__ at all)
    p = subprocess.run([PY, "-B", "-c", "import sys\ndef h():\n    raise SystemExit('x')\nsys.exit(h())\n"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=30)
    print(f"[c -c   ] rc={p.returncode} stderr={p.stderr.decode(errors='replace').strip()[:140]!r}")


def d_fail_closed():
    """Reproduce the search's CHECK script with no free monitoring tool id and show the exit status differs."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("r95search", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-95/c1-survivor-search.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    d = os.path.join(HERE, "failclosed")
    os.makedirs(d, exist_ok=True)
    chk = os.path.join(d, "souji_r95_check.py")
    with open(chk, "w", encoding="utf-8") as f:
        f.write(mod.CHECK)
    hook_src = os.path.join(HOOK_DIR, "sitecustomize.py")
    sc = os.path.join(d, "sitecustomize.py")
    with open(sc, "w", encoding="utf-8") as f:
        f.write("import sys\n"
                "sys.monitoring.use_tool_id(3, 'other-tool')\n"
                "sys.monitoring.use_tool_id(4, 'other-tool')\n"
                "sys.monitoring.use_tool_id(5, 'other-tool')\n"
                "exec(compile(open(%r, encoding='utf-8').read(), 'sitecustomize.py', 'exec'))\n" % hook_src)
    env = dict(os.environ)
    env["PYTHONPATH"] = d
    for mode in ("sysexit", "declared"):
        p = subprocess.run([PY, "-B", chk, mode], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=60)
        print(f"[d fail-closed {mode:8}] rc={p.returncode} (search wants {70 if mode=='sysexit' else 1}) "
              f"stderr={p.stderr.decode(errors='replace').strip()[:120]!r}")


if __name__ == "__main__":
    a_buffering()
    b_fork_dup()
    c_relative_path()
    d_fail_closed()
