#!/usr/bin/env python3
"""R42w2reviewer05: reproduce the frozen C3 counter's EXACT job grid, instrumented.

The frozen counter (census/round-42/c3-counter.py) submits, on a ThreadPoolExecutor with
max_workers=8:
  - the 9 "pre" jobs (8 PRIOR fixtures + the candidate) against the pristine tool,
  - 19 candidate-fixture jobs (one per MUTANT/EQUIV),
  - 19 x 8 prior-fixture jobs (one per mutant per prior fixture).
This script reproduces that grid byte-for-byte (same tables, same mutation, same run(),
same killed()/clean()) but records rc / cases / pass / fail / crash / elapsed / stdout tail /
stderr tail for every job, so a load-induced difference in the SUMMARY can be attributed to
specific jobs.

Usage: grid.py <label>
"""
import concurrent.futures
import hashlib
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
SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2reviewer05"
REV = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
TOOL = "tools/souji-worktree-drift.py"
CANDIDATE = "tests/fixtures/r42-drift-conditions.py"
SCRATCH_ROOT = "/fast/scratch/hyaku/souji-r42/R42w2reviewer05"
SUMMARY_RE = re.compile(r"^SUMMARY (?:cases|probes)=(\d+) pass=(\d+) fail=(\d+)", re.M)
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}


def env(scratch):
    e = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": scratch}
    e.update(GIT_ENV)
    return e


def git_show(root, rev, path, scratch):
    p = subprocess.run(["git", "-C", root, "show", "%s:%s" % (rev, path)], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=env(scratch), check=False)
    return p.stdout if p.returncode == 0 else None


def write(path, data, mode=0o644):
    with open(path, "wb") as handle:
        handle.write(data if isinstance(data, bytes) else data.encode("utf-8"))
    os.chmod(path, mode)


def run(fixture, tool, scratch, tag):
    """The frozen counter's run(), instrumented."""
    work = tempfile.mkdtemp(prefix="w-%s." % tag, dir=scratch)
    try:
        e = env(scratch)
        e["TMPDIR"] = work
        t0 = time.monotonic()
        try:
            proc = subprocess.run(["python3", "-B", fixture, "--tool", tool, "--work", work],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                  check=False, env=e, timeout=300)
        except subprocess.TimeoutExpired:
            return {"rc": 124, "cases": None, "pass": None, "fail": None, "crash": True,
                    "elapsed": round(time.monotonic() - t0, 2), "stdout": "", "stderr": "COUNTER-300s-TIMEOUT"}
        elapsed = round(time.monotonic() - t0, 2)
        m = SUMMARY_RE.findall(proc.stdout)
        crash = "Traceback (most recent call last)" in proc.stderr
        rec = {"rc": proc.returncode, "crash": crash, "elapsed": elapsed,
               "stdout_tail": proc.stdout[-1500:], "stderr_tail": proc.stderr[-1500:]}
        if not m:
            rec.update({"cases": None, "pass": None, "fail": None})
            return rec
        c, p, f = (int(x) for x in m[-1])
        rec.update({"cases": c, "pass": p, "fail": f})
        return rec
    finally:
        shutil.rmtree(work, ignore_errors=True)


def killed(res):
    return res["cases"] is not None and res["rc"] == 1 and res["fail"] > 0 and not res["crash"]


def clean(res):
    return res["cases"] is not None and res["rc"] == 0 and res["fail"] == 0 and res["pass"] == res["cases"] and not res["crash"]


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "grid"
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        print("refusing to run as root")
        return 2
    spec = importlib.util.spec_from_file_location("c3counter", os.path.join(LANE, "census/round-42/c3-counter.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    PRIOR = mod.PRIOR
    MUTANTS = mod.MUTANTS
    EQUIV = mod.EQUIV
    scratch = tempfile.mkdtemp(prefix="souji-r42-c3.", dir=SCRATCH_ROOT)
    try:
        tool_b = git_show(LANE, REV, TOOL, scratch)
        source = tool_b.decode("utf-8")
        fixtures = {}
        for path in PRIOR + (CANDIDATE,):
            blob = git_show(LANE, REV, path, scratch)
            if blob is not None:
                local = os.path.join(scratch, "fx-" + os.path.basename(path))
                write(local, blob)
                fixtures[path] = local
        pristine = os.path.join(scratch, "pristine.py")
        write(pristine, tool_b, 0o755)
        jobs = {}
        for mid, _d, old, new in MUTANTS + EQUIV:
            mpath = os.path.join(scratch, "mut-%s.py" % mid)
            write(mpath, source.replace(old, new), 0o755)
            jobs[mid] = mpath
        rec = {"label": label, "jobs": {}}
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            pre = {p: pool.submit(run, f, pristine, scratch, "pre") for p, f in fixtures.items()}
            prior_ok = sum(1 for p in PRIOR if p in fixtures and clean(pre[p].result()))
            cand_pre = pre[CANDIDATE].result() if CANDIDATE in fixtures else None
            pristine_ok = (cand_pre is not None and clean(cand_pre) and cand_pre["cases"] >= 13)
            cases = cand_pre["cases"] if cand_pre and cand_pre["cases"] else 0
            rec["pristine"] = cand_pre
            rec["prior_ok"] = prior_ok
            grid = {}
            if CANDIDATE in fixtures:
                for mid, mp in jobs.items():
                    grid[(mid, CANDIDATE)] = pool.submit(run, fixtures[CANDIDATE], mp, scratch, mid)
            for mid, mp in jobs.items():
                for p in PRIOR:
                    if p in fixtures:
                        grid[(mid, p)] = pool.submit(run, fixtures[p], mp, scratch, mid)
            res = {k: v.result() for k, v in grid.items()}
        killed_n = equiv_killed = old_killed = 0
        lines = []
        for mid, desc, _o, _n in MUTANTS:
            cand = killed(res[(mid, CANDIDATE)]) if (mid, CANDIDATE) in res else False
            by = [os.path.basename(p) for p in PRIOR if (mid, p) in res and killed(res[(mid, p)])]
            killed_n += 1 if cand else 0
            old_killed += 1 if by else 0
            r = res[(mid, CANDIDATE)]
            rec["jobs"]["MUTANT " + mid] = {"killed": cand, "prior_killed_by": by, "detail": r}
            lines.append("MUTANT %s candidate=%s prior=%s  [rc=%s cases=%s pass=%s fail=%s crash=%s elapsed=%s]" % (
                mid, "killed" if cand else "SURVIVED", ",".join(by) or "-",
                r["rc"], r["cases"], r["pass"], r["fail"], r["crash"], r["elapsed"]))
            if not cand:
                lines.append("    stdout_tail: %r" % r["stdout_tail"][-400:])
                lines.append("    stderr_tail: %r" % r["stderr_tail"][-400:])
        for mid, _d, _o, _n in EQUIV:
            cand = killed(res[(mid, CANDIDATE)]) if (mid, CANDIDATE) in res else False
            by = [os.path.basename(p) for p in PRIOR if (mid, p) in res and killed(res[(mid, p)])]
            equiv_killed += 1 if cand else 0
            r = res[(mid, CANDIDATE)]
            rec["jobs"]["EQUIV " + mid] = {"killed": cand, "prior_killed_by": by, "detail": r}
            lines.append("EQUIV %s candidate=%s prior=%s  [rc=%s cases=%s pass=%s fail=%s crash=%s elapsed=%s]" % (
                mid, "KILLED" if cand else "survived", ",".join(by) or "-",
                r["rc"], r["cases"], r["pass"], r["fail"], r["crash"], r["elapsed"]))
            if cand:
                lines.append("    stdout_tail: %r" % r["stdout_tail"][-400:])
                lines.append("    stderr_tail: %r" % r["stderr_tail"][-400:])
        summary = ("SUMMARY mutants=%d killed=%d survived=%d pristine=%s prior=%d/8 old_killed=%d equiv=%d "
                   "equiv_killed=%d anchors=ok cases=%d tool_sha=%s" % (
                       len(MUTANTS), killed_n, len(MUTANTS) - killed_n, "ok" if pristine_ok else "FAIL",
                       prior_ok, old_killed, len(EQUIV), equiv_killed, cases,
                       hashlib.sha256(tool_b).hexdigest()[:12]))
        lines.append(summary)
        rec["summary"] = summary
        rec["killed_n"] = killed_n
        rec["equiv_killed"] = equiv_killed
        rec["old_killed"] = old_killed
        text = "\n".join(lines) + "\n"
        with open(os.path.join(SEAT, "grid-%s.txt" % label), "w") as h:
            h.write(text)
        with open(os.path.join(SEAT, "grid-%s.json" % label), "w") as h:
            json.dump(rec, h, indent=1, sort_keys=True)
        print(text)
        return 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
