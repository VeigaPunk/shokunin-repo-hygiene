#!/usr/bin/env python3
"""R42w2critic04: run every survey mutant (mutants.py) against the landed C3 fixture and the eight
prior drift fixtures, 8 workers. Scratch lives under /fast/scratch/hyaku/souji-r42/R42w2critic04.
Writes matrix.json (raw per-run records) and matrix.tsv (one row per mutant) into the seat directory.
Kill rule = census/round-42/c3-counter.py killed(): cases is not None, rc == 1, failed > 0, no traceback.
"""
import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2critic04"
S = "/fast/scratch/hyaku/souji-r42/R42w2critic04"
sys.path.insert(0, SEAT)
from mutants import MUTANTS  # noqa: E402

PRISTINE = "b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6"
LANDED = "r42-drift-conditions.py"
PRIOR = ["r36-worktree-drift.py", "r37-drift-discrimination.py", "r38-drift-record.py",
         "r38-drift-write-envelope.py", "r39-drift-record-rules.py", "r40-drift-record-branches.py",
         "r41-drift-record-order.py", "r41-refusal-sites.py"]
FIX = [LANDED] + PRIOR
SUMMARY = re.compile(r"^SUMMARY (?:cases|probes)=(\d+) pass=(\d+) fail=(\d+)", re.M)
FAILLINE = re.compile(r"^(\S+)=FAIL$", re.M)
ENV_BASE = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}


def run(job):
    mid, fx = job
    tool = os.path.join(S, "fx", "tool.py") if mid == "PRISTINE" else os.path.join(S, "mut", mid + ".py")
    work = os.path.join(S, "work", mid, fx[:-3])
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    env = dict(ENV_BASE)
    env["PATH"] = os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")
    env["TMPDIR"] = work
    t0 = time.monotonic()
    timed_out = False
    try:
        p = subprocess.run(["python3", "-B", os.path.join(S, "fx", fx), "--tool", tool, "--work", work],
                           capture_output=True, text=True, env=env, timeout=900, check=False)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        rc = 124
        out = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = ""
    secs = round(time.monotonic() - t0, 1)
    m = SUMMARY.findall(out)
    cases = int(m[-1][0]) if m else None
    failed = int(m[-1][2]) if m else None
    crash = "Traceback (most recent call last)" in err
    killed = cases is not None and rc == 1 and failed > 0 and not crash
    fails = FAILLINE.findall(out)
    shutil.rmtree(work, ignore_errors=True)
    return {"mutant": mid, "fixture": fx, "rc": rc, "cases": cases, "failed": failed, "crash": crash,
            "timeout": timed_out, "killed": killed, "fails": fails, "secs": secs,
            "summary": (out.strip().splitlines() or [""])[-1][:160]}


def main():
    src = open(os.path.join(S, "fx", "tool.py"), encoding="utf-8").read()
    if hashlib.sha256(src.encode("utf-8")).hexdigest() != PRISTINE:
        sys.exit("pinned tool sha256 differs")
    ids = [m[0] for m in MUTANTS]
    assert len(set(ids)) == len(ids), "duplicate ids"
    os.makedirs(os.path.join(S, "mut"), exist_ok=True)
    for mid, desc, old, new in MUTANTS:
        n = src.count(old)
        if n != 1:
            sys.exit("ANCHOR %s occurs %d times" % (mid, n))
        if old == new:
            sys.exit("NOOP %s" % mid)
        body = src.replace(old, new)
        with open(os.path.join(S, "mut", mid + ".py"), "w", encoding="utf-8") as h:
            h.write(body)
        print("MADE %s bytes=%d delta=%+d" % (mid, len(body), len(body) - len(src)), flush=True)
    jobs = [("PRISTINE", f) for f in FIX] + [(m[0], f) for m in MUTANTS for f in FIX]
    t0 = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(run, jobs))
    print("RAN %d runs in %.1fs" % (len(results), time.monotonic() - t0), flush=True)
    with open(os.path.join(SEAT, "matrix.json"), "w", encoding="utf-8") as h:
        json.dump(results, h, indent=1, sort_keys=True)
    by = {}
    for r in results:
        by.setdefault(r["mutant"], {})[r["fixture"]] = r
    pristine = by.pop("PRISTINE")
    print("PRISTINE " + " ".join("%s=%s" % (f[:12], "clean" if (r["rc"] == 0 and r["failed"] == 0) else "DIRTY")
                                  for f, r in pristine.items()), flush=True)
    rows = ["mutant\tlanded\tprior_killers\tlanded_fails\ttimeouts\tcrashes\tdescription"]
    for mid, desc, old, new in MUTANTS:
        row = by[mid]
        land = row[LANDED]
        pk = [f[:-3] for f in PRIOR if row[f]["killed"]]
        lf = ",".join(land["fails"]) or "-"
        to = sum(1 for r in row.values() if r["timeout"])
        cr = sum(1 for r in row.values() if r["crash"])
        rows.append("%s\t%s\t%s\t%s\t%d\t%d\t%s" % (mid, "KILLED" if land["killed"] else "survived",
                                                 ",".join(pk) or "-", lf, to, cr, desc))
    text = "\n".join(rows) + "\n"
    open(os.path.join(SEAT, "matrix.tsv"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
