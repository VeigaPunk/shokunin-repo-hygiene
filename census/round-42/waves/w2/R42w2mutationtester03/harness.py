#!/usr/bin/env python3
"""R42w2mutationtester03 harness: fixture-mutant x population-mutant grid.

Read-only w.r.t. the lane. Reads:
  - the landed fixture blob at the tip revision (git show)
  - the frozen MUTANTS table from census/round-42/c3-counter.py (imported, never edited)
  - tools/souji-worktree-drift.py at the tip (the pristine tool)
Writes only into this seat's directory and its scratch.
Each completed (fixture_mutant, tool) cell is appended to grid.jsonl immediately, so a rerun resumes.
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

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
TIP = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
SEAT = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w2mutationtester03"
FIXTURE_PATH = "tests/fixtures/r42-drift-conditions.py"
TOOL_PATH = "tools/souji-worktree-drift.py"
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}
SUMMARY_RE = re.compile(r"^SUMMARY (?:cases|probes)=(\d+) pass=(\d+) fail=(\d+)", re.M)
CASE_RE = re.compile(r"^case-(.+)=(PASS|FAIL)$", re.M)


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
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", default=os.path.join(SEAT, "grid.jsonl"))
    ap.add_argument("--only", default="", help="comma list of fixture-mutant ids to run")
    a = ap.parse_args()

    os.makedirs(SCRATCH, exist_ok=True)
    counter = load_module(os.path.join(LANE, "census/round-42/c3-counter.py"), "c3counter")
    tool_src = git_show(TIP, TOOL_PATH).decode("utf-8")
    fixture_src = git_show(TIP, FIXTURE_PATH).decode("utf-8")
    mutants = load_module(os.path.join(SEAT, "mutants.py"), "r42w2mut3")

    # tools: pristine + the 13 frozen population mutants (same anchors the frozen counter uses)
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

    fixture_mutants = mutants.build(fixture_src)
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
        with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
            futs = {}
            for mid, fpath in fixtures.items():
                for tid, tpath in tools.items():
                    if (mid, tid) in done:
                        continue
                    if tid != "pristine" and tid not in {m[0] for m in counter.MUTANTS}:
                        continue
                    fut = pool.submit(run_fixture, fpath, tpath, scratch)
                    futs[fut] = (mid, tid)
            for fut in concurrent.futures.as_completed(futs):
                mid, tid = futs[fut]
                res = fut.result()
                with open(a.out, "a") as fh:
                    fh.write(json.dumps({"fixture_mutant": mid, "tool": tid, **res}) + "\n")
                print("%-6s %-9s rc=%s cases=%s pass=%s fail=%s crash=%s failing=%s" % (
                    mid, tid, res["rc"], res["cases"], res["passed"], res["failed"],
                    res["crash"], ",".join(res["failing"])), flush=True)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
