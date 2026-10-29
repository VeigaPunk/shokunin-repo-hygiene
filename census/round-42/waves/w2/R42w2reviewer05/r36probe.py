#!/usr/bin/env python3
"""R42w2reviewer05: which r36 case fails on a mutant, and does it fail only under load?

Runs the prior fixture tests/fixtures/r36-worktree-drift.py (pinned at the tip) once per
MUTANT/EQUIV of the frozen counter (same mutation as the counter: source.replace(old, new)
on the pinned tool blob), twice in sequence, and records every `case-*=FAIL` line. The
frozen counter discards prior-fixture output, so this is the only way to see which r36
case is the old_killed kill. Run it once quiet and once under the stress load.

Usage: r36probe.py <label>
"""
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
SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2reviewer05"
REV = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
SCRATCH_ROOT = "/fast/scratch/hyaku/souji-r42/R42w2reviewer05"
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}
FAIL_RE = re.compile(r"^case-([a-z0-9\-]+)=FAIL(.*)$", re.M)
SUM_RE = re.compile(r"^SUMMARY cases=(\d+) pass=(\d+) fail=(\d+)", re.M)


def git_show(path):
    p = subprocess.run(["git", "-C", LANE, "show", "%s:%s" % (REV, path)], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=dict(GIT_ENV, PATH=os.environ["PATH"]), check=False)
    if p.returncode != 0:
        raise SystemExit("git show failed %s" % path)
    return p.stdout


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "r36"
    spec = importlib.util.spec_from_file_location("c3counter", os.path.join(LANE, "census/round-42/c3-counter.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    scratch = tempfile.mkdtemp(prefix="r36probe.", dir=SCRATCH_ROOT)
    try:
        source = git_show("tools/souji-worktree-drift.py").decode("utf-8")
        fx = os.path.join(scratch, "r36.py")
        with open(fx, "wb") as h:
            h.write(git_show("tests/fixtures/r36-worktree-drift.py"))
        jobs = []
        for mid, _d, old, new in mod.MUTANTS + mod.EQUIV:
            mp = os.path.join(scratch, "mut-%s.py" % mid)
            with open(mp, "w", encoding="utf-8") as h:
                h.write(source.replace(old, new))
            os.chmod(mp, 0o755)
            jobs.append((mid, mp))
        pristine = os.path.join(scratch, "pristine.py")
        with open(pristine, "w", encoding="utf-8") as h:
            h.write(source)
        os.chmod(pristine, 0o755)
        jobs.insert(0, ("PRISTINE", pristine))

        def one(mid, tool, rep):
            work = tempfile.mkdtemp(prefix="w36.", dir=scratch)
            try:
                e = dict(GIT_ENV, PATH=os.environ["PATH"], TMPDIR=work)
                t0 = time.monotonic()
                p = subprocess.run(["python3", "-B", fx, "--tool", tool, "--work", work],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=e,
                                   timeout=300, check=False)
                s = SUM_RE.findall(p.stdout)
                return {"mid": mid, "rep": rep, "rc": p.returncode, "summary": s[-1] if s else None,
                        "fails": [(m.group(1), m.group(2).strip()) for m in FAIL_RE.finditer(p.stdout)],
                        "elapsed": round(time.monotonic() - t0, 2),
                        "stderr_tail": p.stderr[-300:]}
            finally:
                shutil.rmtree(work, ignore_errors=True)

        out = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            for rep in (1, 2):
                futs = [pool.submit(one, mid, tool, rep) for mid, tool in jobs]
                out.extend(f.result() for f in futs)
        with open(os.path.join(SEAT, "r36probe-%s.json" % label), "w") as h:
            json.dump(out, h, indent=1)
        lines = []
        for r in out:
            lines.append("%-8s rep=%d rc=%s summary=%s elapsed=%s fails=%s" % (
                r["mid"], r["rep"], r["rc"], r["summary"], r["elapsed"],
                ";".join("%s(%s)" % (n, d) for n, d in r["fails"]) or "-"))
        text = "\n".join(lines) + "\n"
        with open(os.path.join(SEAT, "r36probe-%s.txt" % label), "w") as h:
            h.write(text)
        print(text)
        return 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
