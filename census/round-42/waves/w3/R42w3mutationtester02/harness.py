#!/usr/bin/env python3
"""R42w3mutationtester02 harness: fixture-mutant x tool grid for the landed C3 fixture.

Read-only w.r.t. the lane. Reads:
  - the landed fixture blob and the pinned tool blob at the tip revision (git show, read-only)
  - the frozen MUTANTS/EQUIV tables from census/round-42/c3-counter.py (imported, never edited)
Writes only into this seat's directory and its scratch.
Each completed (fixture_mutant, tool) cell is appended to grid-w3.jsonl immediately, so a rerun resumes.

Kill/clean semantics are the frozen counter's (c3-counter.py killed()/clean()):
  KILL(F,T)  = rc==1 and SUMMARY fail>0 and no traceback
  CLEAN(F,T) = rc==0 and fail==0 and pass==cases and no traceback
"""
import argparse
import concurrent.futures
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
TIP = "6a3f75941d3604e3459011d599c2c16f3a97b44c"
SEAT = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w3mutationtester02"
FIXTURE_PATH = "tests/fixtures/r42-drift-conditions.py"
TOOL_PATH = "tools/souji-worktree-drift.py"
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}
SUMMARY_RE = re.compile(r"^SUMMARY (?:cases|probes)=(\d+) pass=(\d+) fail=(\d+)", re.M)
CASE_RE = re.compile(r"^case-(.+)=(PASS|FAIL)$", re.M)


def uptime():
    try:
        return open("/proc/loadavg").read().strip()
    except OSError:
        return "?"


def git_show(rev, path):
    p = subprocess.run(["git", "-C", LANE, "show", "%s:%s" % (rev, path)], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=dict(os.environ, **GIT_ENV), check=False)
    if p.returncode != 0:
        raise SystemExit("git show failed for %s:%s" % (rev, path))
    return p.stdout


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_fixture(fixture, tool, scratch):
    """Run one fixture against one tool. Return a dict: rc, cases, passed, failed, crash, failing."""
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
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", default=os.path.join(SEAT, "grid-w3.jsonl"))
    ap.add_argument("--only", default="", help="comma list of fixture-mutant ids to run")
    ap.add_argument("--base", action="store_true", help="also run the unmutated landed fixture (id BASE)")
    ap.add_argument("--equiv", action="store_true", help="also run the 6 EQUIV tool mutants")
    a = ap.parse_args()

    os.makedirs(SCRATCH, exist_ok=True)
    counter = load_module(os.path.join(LANE, "census/round-42/c3-counter.py"), "c3counter")
    tool_src = git_show(TIP, TOOL_PATH).decode("utf-8")
    fixture_src = git_show(TIP, FIXTURE_PATH).decode("utf-8")
    mutants = load_module(os.path.join(SEAT, "mutants.py"), "r42w3mut2")

    tools = {"pristine": os.path.join(SCRATCH, "tool-pristine.py")}
    with open(tools["pristine"], "w") as fh:
        fh.write(tool_src)
    os.chmod(tools["pristine"], 0o755)
    for mid, _d, old, new in counter.MUTANTS:
        assert tool_src.count(old) == 1, mid
        p = os.path.join(SCRATCH, "tool-%s.py" % mid)
        with open(p, "w") as fh:
            fh.write(tool_src.replace(old, new))
        os.chmod(p, 0o755)
        tools[mid] = p
    if a.equiv:
        for mid, _d, old, new in counter.EQUIV:
            assert tool_src.count(old) == 1, mid
            p = os.path.join(SCRATCH, "tool-%s.py" % mid)
            with open(p, "w") as fh:
                fh.write(tool_src.replace(old, new))
            os.chmod(p, 0o755)
            tools[mid] = p

    fixture_mutants = {}
    if a.base:
        fixture_mutants["BASE"] = {"category": "BASE", "description": "the landed fixture, unmutated",
                                   "source": fixture_src, "old": "", "new": ""}
    fixture_mutants.update(mutants.build(fixture_src))
    if a.only:
        want = set(a.only.split(","))
        fixture_mutants = {k: v for k, v in fixture_mutants.items() if k in want}

    done = set()
    if os.path.exists(a.out):
        with open(a.out) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    done.add((rec.get("fixture_mutant"), rec.get("tool")))
        print("resume: %d cells already done" % len(done), flush=True)

    scratch = tempfile.mkdtemp(prefix="grid.", dir=SCRATCH)
    try:
        fixtures = {}
        for mid, spec in fixture_mutants.items():
            fpath = os.path.join(scratch, "fx-%s.py" % mid)
            with open(fpath, "w") as fh:
                fh.write(spec["source"])
            fixtures[mid] = fpath
        pop_ids = {m[0] for m in counter.MUTANTS}
        plan = [(mid, tid) for mid in fixtures for tid in tools
                if (mid, tid) not in done and (tid == "pristine" or tid in pop_ids
                                               or (a.equiv and tid in {m[0] for m in counter.EQUIV}))]
        print("BATCH start: %d cells, workers=%d, load=%s" % (len(plan), a.workers, uptime()),
              flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
            futs = {}
            for mid, tid in plan:
                futs[pool.submit(run_fixture, fixtures[mid], tools[tid], scratch)] = (mid, tid)
            done_n = 0
            for fut in concurrent.futures.as_completed(futs):
                mid, tid = futs[fut]
                res = fut.result()
                with open(a.out, "a") as fh:
                    fh.write(json.dumps({"fixture_mutant": mid, "tool": tid, **res}) + "\n")
                done_n += 1
                print("%-6s %-9s rc=%s cases=%s pass=%s fail=%s crash=%s failing=%s" % (
                    mid, tid, res["rc"], res["cases"], res["passed"], res["failed"],
                    res["crash"], ",".join(res["failing"])), flush=True)
                if done_n % 20 == 0:
                    print("... %d/%d cells, load=%s" % (done_n, len(plan), uptime()), flush=True)
        print("BATCH end: %d cells, load=%s" % (len(plan), uptime()), flush=True)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
