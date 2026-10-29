#!/usr/bin/env python3
"""R42w2mutationtester06 — mutation harness for tools/souji-worktree-drift.py.

Usage:
  harness.py check   --scratch DIR           # validate anchors, write mutant files
  harness.py score   --scratch DIR           # run the nine fixtures against every mutant

The harness NEVER writes inside the lane: the pristine tool, the mutant blobs, the fixture
copies and every work directory live under --scratch.
"""
import argparse
import concurrent.futures
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutants import MUTANTS  # noqa: E402

TOOL_REL = "tools/souji-worktree-drift.py"
PRISTINE_SHA256 = "b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6"
FIXTURES = [
    "tests/fixtures/r36-worktree-drift.py",
    "tests/fixtures/r37-drift-discrimination.py",
    "tests/fixtures/r38-drift-record.py",
    "tests/fixtures/r38-drift-write-envelope.py",
    "tests/fixtures/r39-drift-record-rules.py",
    "tests/fixtures/r40-drift-record-branches.py",
    "tests/fixtures/r41-drift-record-order.py",
    "tests/fixtures/r41-refusal-sites.py",
    "tests/fixtures/r42-drift-conditions.py",
]
SUMMARY_RE = re.compile(r"^SUMMARY (?:cases|probes)=(\d+) pass=(\d+) fail=(\d+)", re.M)
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}


def env(scratch):
    e = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": scratch}
    e.update(GIT_ENV)
    return e


def write(path, data, mode=0o644):
    with open(path, "wb") as handle:
        handle.write(data if isinstance(data, bytes) else data.encode("utf-8"))
    os.chmod(path, mode)


def check(scratch):
    """Validate every anchor and materialise the mutant blobs."""
    src = open(os.path.join(scratch, "pristine.py"), "rb").read().decode("utf-8")
    problems = []
    mdir = os.path.join(scratch, "mut")
    os.makedirs(mdir, exist_ok=True)
    for mid, fn, desc, old, new in MUTANTS:
        n = src.count(old)
        if n != 1:
            problems.append("%s anchor occurs %d times (expected 1): %r" % (mid, n, old[:70]))
            continue
        blob = src.replace(old, new)
        if blob == src:
            problems.append("%s is a no-op" % mid)
        path = os.path.join(mdir, "mut-%s.py" % mid)
        write(path, blob, 0o755)
        # syntax check
        p = subprocess.run([sys.executable, "-B", "-c",
                            "import sys;src=open(sys.argv[1],encoding='utf-8').read();compile(src,sys.argv[1],'exec')", path],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if p.returncode != 0:
            problems.append("%s does not compile: %s" % (mid, p.stderr.strip()[-300:]))
    print("MUTANTS total=%d problems=%d" % (len(MUTANTS), len(problems)))
    for p in problems:
        print("PROBLEM %s" % p)
    return 1 if problems else 0


def run_fixture(fixture, tool, scratch, timeout):
    """Return a dict: rc, cases, passed, failed, crash, timeout, summary."""
    work = tempfile.mkdtemp(prefix="w-", dir=scratch)
    try:
        e = env(scratch)
        e["TMPDIR"] = work
        proc = subprocess.run([sys.executable, "-B", fixture, "--tool", tool, "--work", work],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                              check=False, env=e, timeout=timeout)
        crash = "Traceback (most recent call last)" in proc.stderr
        m = SUMMARY_RE.findall(proc.stdout)
        if not m:
            return {"rc": proc.returncode, "cases": None, "passed": None, "failed": None,
                    "crash": crash, "timeout": False,
                    "summary": ""}
        c, p, f = (int(x) for x in m[-1])
        return {"rc": proc.returncode, "cases": c, "passed": p, "failed": f, "crash": crash,
                "timeout": False, "summary": m[-1]}
    except subprocess.TimeoutExpired:
        return {"rc": 124, "cases": None, "passed": None, "failed": None, "crash": True,
                "timeout": True, "summary": ""}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def score(scratch, workers=8, timeout=180, only=None):
    fdir = os.path.join(scratch, "fx")
    fixtures = {}
    for rel in FIXTURES:
        local = os.path.join(fdir, os.path.basename(rel))
        fixtures[rel] = local
    jobs = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        pristine = {rel: pool.submit(run_fixture, local, os.path.join(scratch, "pristine.py"), scratch, timeout)
                    for rel, local in fixtures.items()}
        pres = {rel: f.result() for rel, f in pristine.items()}
        for rel, r in pres.items():
            print("PRISTINE %-46s rc=%s cases=%s pass=%s fail=%s crash=%s timeout=%s"
                  % (os.path.basename(rel), r["rc"], r["cases"], r["passed"], r["failed"], r["crash"], r["timeout"]))
        bad = [rel for rel, r in pres.items() if not (r["cases"] is not None and r["rc"] == 0
                                                     and r["failed"] == 0 and not r["crash"])]
        if bad:
            print("BASELINE-NOT-CLEAN %s" % ",".join(bad))
        for mid, fn, desc, old, new in MUTANTS:
            if only and mid not in only:
                continue
            mp = os.path.join(scratch, "mut", "mut-%s.py" % mid)
            if not os.path.exists(mp):
                continue
            for rel, local in fixtures.items():
                jobs[(mid, rel)] = pool.submit(run_fixture, local, mp, scratch, timeout)
        res = {k: v.result() for k, v in jobs.items()}
    rows = []
    for mid, fn, desc, old, new in MUTANTS:
        if only and mid not in only:
            continue
        killers = []
        soft = []
        for rel in FIXTURES:
            r = res.get((mid, rel))
            if r is None:
                continue
            pr = pres[rel]
            # the lane's own kill predicate (c3-counter.py killed()): rc==1 and failed>0 and no crash
            strict = (r["cases"] is not None and r["rc"] == 1 and r["failed"] > 0 and not r["crash"])
            # any observable difference against the pristine baseline for this fixture
            diff = (r["rc"] != pr["rc"] or r["failed"] != pr["failed"] or
                    r["passed"] != pr["passed"] or r["crash"] != pr["crash"] or
                    r["cases"] != pr["cases"])
            if strict:
                killers.append((os.path.basename(rel), r))
            elif diff:
                soft.append((os.path.basename(rel), r))
        rows.append({"id": mid, "function": fn, "description": desc,
                     "killed_by": killers, "soft_by": soft})
        verdict = ("KILLED by " + ",".join(k[0] for k in killers)) if killers else (
                  ("SOFT-DIFF by " + ",".join(k[0] for k in soft)) if soft else "SURVIVED")
        print("MUTANT %-6s %-22s %s" % (mid, fn, verdict))
    import json
    with open(os.path.join(scratch, "scores.json"), "w") as h:
        json.dump({"baseline": {rel: pres[rel] for rel in FIXTURES},
                   "rows": [{"id": r["id"], "function": r["function"], "description": r["description"],
                             "killed_by": [k[0] for k in r["killed_by"]],
                             "soft_by": [k[0] for k in r["soft_by"]],
                             "detail": [{"fixture": k[0], **k[1]} for k in r["killed_by"] + r["soft_by"]]}
                            for r in rows]}, h, indent=1, sort_keys=True)
    print("WROTE %s" % os.path.join(scratch, "scores.json"))
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["check", "score"])
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--only", nargs="*", default=None)
    a = ap.parse_args(argv)
    os.makedirs(a.scratch, exist_ok=True)
    if a.mode == "check":
        return check(a.scratch)
    return score(a.scratch, a.workers, a.timeout, a.only)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
