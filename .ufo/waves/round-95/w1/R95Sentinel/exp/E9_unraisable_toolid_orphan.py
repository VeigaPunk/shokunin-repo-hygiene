#!/usr/bin/env python3
"""E9/E10/E11 for the sentinel seat.

E9  A benign GC-time exception (__del__ raising) becomes a CRASH under the sentinel
    (sys.unraisablehook is replaced): the whole process exits 70 instead of continuing.
E10 The sentinel's tool-id fallback: when ids 3 and 4 are already taken it reaches id 5
    (sys.monitoring.OPTIMIZER_ID, reserved for the interpreter's optimizer), and when all three are
    taken it prints "no free sys.monitoring tool id" and continues WITHOUT the RAISE callback
    (the SystemExit leg silently degrades).
E11 The arms counter's arm-timeout kill does not reach a fixture the probe started in its own
    session: the fixture survives as an orphan.
"""
import os
import subprocess
import sys
import textwrap
import time

PY = sys.executable
HERE = os.path.dirname(os.path.abspath(__file__))
HOOK_DIR = "/fast/scratch/hyaku/souji-r95/R95Sentinel/hook"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"

DEL = """import gc, sys
class Bad:
    def __del__(self):
        raise RuntimeError("benign gc-time error")
b = Bad()
del b
gc.collect()
print("CONTINUED-AFTER-GC")
sys.stdout.flush()
sys.exit(0)
"""

DEL_SOFT = """import gc, sys
class Bad:
    def __del__(self):
        raise RuntimeError("benign gc-time error")
b = Bad()
del b
gc.collect()
print("CONTINUED-AFTER-GC")
sys.stdout.flush()
sys.exit(0)
"""

# a pre-hook that occupies tool ids 3 and 4 BEFORE the sentinel's sitecustomize runs
PREHOOK = """import sys
sys.monitoring.use_tool_id(3, "other-tool")
sys.monitoring.use_tool_id(4, "other-tool")
exec(compile(open(%r, encoding="utf-8").read(), "sitecustomize.py", "exec"))
"""

PREHOOK_ALL = """import sys
sys.monitoring.use_tool_id(3, "other-tool")
sys.monitoring.use_tool_id(4, "other-tool")
sys.monitoring.use_tool_id(5, "other-tool")
exec(compile(open(%r, encoding="utf-8").read(), "sitecustomize.py", "exec"))
"""


def e9_unraisable():
    path = os.path.join(HERE, "child_del.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(DEL)
    base = dict(os.environ)
    hooked = dict(base)
    hooked["PYTHONPATH"] = HOOK_DIR + (os.pathsep + base["PYTHONPATH"] if base.get("PYTHONPATH") else "")
    for mode, env in (("plain", base), ("hooked", hooked)):
        p = subprocess.run([PY, "-B", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=30)
        print(f"[E9 unraisable {mode:6}] rc={p.returncode} stdout={p.stdout.decode().strip()!r} "
              f"stderr={p.stderr.decode(errors='replace').strip()[:180]!r}")


def e10_toolid_fallback():
    hook_src = os.path.join(HOOK_DIR, "sitecustomize.py")
    for label, pre in (("ids 3+4 taken", PREHOOK), ("ids 3+4+5 taken", PREHOOK_ALL)):
        d = os.path.join(HERE, "e10-" + label.replace(" ", "_").replace("+", ""))
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "sitecustomize.py"), "w", encoding="utf-8") as f:
            f.write(pre % hook_src)
        child = os.path.join(d, "child.py")
        with open(child, "w", encoding="utf-8") as f:
            f.write(textwrap.dedent("""\
                import sys
                from sys import monitoring as m
                print("owners 3/4/5:", m.get_tool(3), m.get_tool(4), m.get_tool(5))
                print("OPTIMIZER_ID =", m.OPTIMIZER_ID)
                """))
        env = dict(os.environ)
        env["PYTHONPATH"] = d
        p = subprocess.run([PY, "-B", child], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=30)
        print(f"[E10 {label:16}] rc={p.returncode} out={p.stdout.decode().strip()!r} "
              f"err={p.stderr.decode(errors='replace').strip()[:200]!r}")


def e11_orphan():
    """The arms counter kills the ARM (the probe) with os.killpg(probe.pid) on --arm-timeout.  The probe
    started its fixture with start_new_session=True, so the fixture is in its OWN session and survives."""
    probe = os.path.join(LANE, "census/round-95/c2-forgery-probe.py")
    tool = os.path.join(LANE, "tools/souji-record-agreement.py")
    before = os.path.join(LANE, "census/round-92/controls/c2-before-tool.py")
    d = os.path.join(HERE, "e11")
    subprocess.run(["rm", "-rf", d])
    os.makedirs(d)
    hang = os.path.join(d, "fixture-hang.py")
    with open(hang, "w", encoding="utf-8") as f:
        f.write("import time\nwhile True:\n    time.sleep(3600)\n")
    work = os.path.join(d, "work")
    os.makedirs(work)
    p = subprocess.Popen([PY, "-B", probe, "--fixture", hang, "--tool", tool, "--before", before,
                          "--work", work, "--timeout", "600"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    time.sleep(4)
    kids = subprocess.run(["pgrep", "-P", str(p.pid)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    fixture_pids = [int(x) for x in kids.stdout.decode().split()]
    print(f"[E11] probe pid={p.pid} fixture children={fixture_pids}")
    # this is exactly what census/round-95/c2-setup-arms.py does on --arm-timeout
    try:
        os.killpg(p.pid, 9)
    except ProcessLookupError:
        pass
    time.sleep(2)
    print(f"[E11] probe alive after killpg: {p.poll() is None}")
    survivors = []
    for pid in fixture_pids:
        try:
            os.kill(pid, 0)
            survivors.append(pid)
        except ProcessLookupError:
            pass
    print(f"[E11] surviving fixture processes after the arm-group kill: {survivors}")
    for pid in survivors:
        try:
            os.kill(pid, 9)
        except OSError:
            pass
    try:
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        p.kill()


if __name__ == "__main__":
    e9_unraisable()
    e10_toolid_fallback()
    e11_orphan()
