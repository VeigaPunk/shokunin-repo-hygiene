#!/usr/bin/env python3
"""R42w3mutationtester02: serial re-verification of the load-sensitive cells.

The fixture's default-timeout case asserts `elapsed >= 5.0` on a run whose tool default timeout
is 20 s.  The G3 population mutant lowers that default to 1 s, so on G3 the case must FAIL
(elapsed well under 5 s) for the fixture to kill G3.  Under heavy machine load the 1 s run can
overrun 5 s of wall clock, which would make the case PASS and G3 appear to survive -- a false
"the fixture does not observe the default timeout" reading.

This script re-runs the G3 column (and, for completeness, the pristine column) ONE cell at a
time, never in parallel, and reports the machine load before each cell, so a G3 verdict can be
confirmed at low load.  It writes grid-reverify.jsonl and prints the load at every step.
"""
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
TIP = "6a3f75941d3604e3459011d599c2c16f3a97b44c"
SEAT = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w3mutationtester02"
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}
SUMMARY_RE = __import__("re").compile(r"^SUMMARY (?:cases|probes)=(\d+) pass=(\d+) fail=(\d+)", __import__("re").M)
CASE_RE = __import__("re").compile(r"^case-(.+)=(PASS|FAIL)$", __import__("re").M)


def uptime():
    try:
        return open("/proc/loadavg").read().strip()
    except OSError:
        return "?"


def git_show(path):
    p = subprocess.run(["git", "-C", LANE, "show", "%s:%s" % (TIP, path)], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=dict(os.environ, **GIT_ENV), check=False)
    if p.returncode != 0:
        raise SystemExit("git show failed: %s" % path)
    return p.stdout


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_fixture(fixture, tool, scratch):
    work = tempfile.mkdtemp(prefix="w.", dir=scratch)
    try:
        e = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": work}
        e.update(GIT_ENV)
        try:
            proc = subprocess.run(["python3", "-B", fixture, "--tool", tool, "--work", work],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                  check=False, env=e, timeout=1500)
        except subprocess.TimeoutExpired:
            return {"rc": 124, "cases": None, "passed": None, "failed": None, "crash": True,
                    "failing": [], "timeout": True}
        crash = "Traceback (most recent call last)" in proc.stderr
        m = SUMMARY_RE.findall(proc.stdout)
        cases = passed = failed = None
        if m:
            cases, passed, failed = (int(x) for x in m[-1])
        failing = [n for n, v in CASE_RE.findall(proc.stdout) if v == "FAIL"]
        return {"rc": proc.returncode, "cases": cases, "passed": passed, "failed": failed,
                "crash": crash, "failing": failing, "timeout": False}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tools", default="G3")
    ap.add_argument("--out", default=os.path.join(SEAT, "grid-reverify.jsonl"))
    ap.add_argument("--only", default="")
    a = ap.parse_args()

    os.makedirs(SCRATCH, exist_ok=True)
    counter = load_module(os.path.join(LANE, "census/round-42/c3-counter.py"), "c3counter")
    tool_src = git_show("tools/souji-worktree-drift.py").decode("utf-8")
    fixture_src = git_show("tests/fixtures/r42-drift-conditions.py").decode("utf-8")
    mutants = load_module(os.path.join(SEAT, "mutants.py"), "r42w3mut2")
    fx = mutants.build(fixture_src)

    tools = {}
    for mid in [t for t in a.tools.split(",") if t]:
        if mid == "pristine":
            p = os.path.join(SCRATCH, "tool-pristine.py")
            open(p, "w").write(tool_src)
        else:
            row = [r for r in counter.MUTANTS if r[0] == mid][0]
            p = os.path.join(SCRATCH, "tool-%s.py" % mid)
            open(p, "w").write(tool_src.replace(row[2], row[3]))
        os.chmod(p, 0o755)
        tools[mid] = p

    ids = ["BASE"] + sorted(fx)
    if a.only:
        want = set(a.only.split(","))
        ids = [i for i in ids if i in want]

    scratch = tempfile.mkdtemp(prefix="reverify.", dir=SCRATCH)
    try:
        for mid in ids:
            spec = {"BASE": {"source": fixture_src}}.get(mid, fx.get(mid))
            if spec is None:
                continue
            fpath = os.path.join(scratch, "fx-%s.py" % mid)
            open(fpath, "w").write(spec["source"])
            for tid, tpath in tools.items():
                print("load-before %-6s %-9s load=%s" % (mid, tid, uptime()), flush=True)
                res = run_fixture(fpath, tpath, scratch)
                rec = {"fixture_mutant": mid, "tool": tid, "load": uptime(), **res}
                with open(a.out, "a") as fh:
                    fh.write(json.dumps(rec) + "\n")
                print("  -> %-6s %-9s rc=%s cases=%s pass=%s fail=%s failing=%s load=%s" % (
                    mid, tid, res["rc"], res["cases"], res["passed"], res["failed"],
                    ",".join(res["failing"]), uptime()), flush=True)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
