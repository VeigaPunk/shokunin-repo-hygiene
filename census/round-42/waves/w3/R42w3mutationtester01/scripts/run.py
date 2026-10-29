#!/usr/bin/env python3
"""Runner for souji r42 wave-3 seat R42w3mutationtester01.

For each mutant of tools/souji-freeze-check.py (part A, the first half of the file):
  1. run the mutant's OWN --selftest  (the tool's own detector)
  2. score it with the frozen counter's CASE TABLE ONLY, via score-candidate.sh
     (the case-table leg is read from the SUMMARY's cases=/pass=/fail= tokens)

Classification (the assignment's three classes):
  killed by counter cases   the counter's 37-case table reports fail>0
  killed only by --selftest  the case table passes but the mutant's own --selftest fails
  SURVIVES both             neither kills it -> triage further (equivalent vs gap)

Nothing is written into the lane; everything lives under the seat scratch.
"""
import concurrent.futures as cf
import os
import re
import subprocess
import sys

SEAT = "/fast/scratch/hyaku/souji-r42/R42w3mutationtester01"
MUTDIR = os.path.join(SEAT, "mutants")
SCORE = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/score-candidate.sh"
WORK = os.path.join(SEAT, "work")
STDIR = os.path.join(SEAT, "selftest-tmp")

SELFTEST_RE = re.compile(r"^SELFTEST cases=(\d+) pass=(\d+) fail=(\d+)\s*$", re.M)
SUMMARY_RE = re.compile(r"^SUMMARY cases=(\d+) pass=(\d+) fail=(\d+)(.*)$", re.M)


def run_selftest(path, idx):
    d = os.path.join(STDIR, "m%02d" % idx)
    os.makedirs(d, exist_ok=True)
    env = dict(os.environ)
    env["TMPDIR"] = d
    try:
        p = subprocess.run(["python3", "-B", path, "--selftest"], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True, check=False, env=env, timeout=900, cwd=d)
    except subprocess.TimeoutExpired:
        return {"rc": 124, "cases": None, "crash": True, "stderr": "TIMEOUT"}
    m = SELFTEST_RE.findall(p.stdout)
    crash = "Traceback (most recent call last)" in p.stderr
    return {"rc": p.returncode, "cases": m[-1] if m else None, "crash": crash,
            "stderr": p.stderr[-300:] if p.stderr else ""}


def run_counter(path, idx):
    d = os.path.join(WORK, "m%02d" % idx)
    os.makedirs(d, exist_ok=True)
    env = dict(os.environ)
    env["TMPDIR"] = d
    p = subprocess.run(["bash", SCORE, "c2", SEAT, "tools/souji-freeze-check.py=" + path],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
                       env=env, timeout=1800, cwd=d)
    out = p.stdout
    m = SUMMARY_RE.search(out)
    failed = re.findall(r"^case-(.+?)=FAIL", out, re.M)
    legs = {}
    if m:
        for tok in m.group(4).split():
            if "=" in tok:
                k, v = tok.split("=", 1)
                legs[k] = v
        legs["cases"] = m.group(1)
        legs["pass"] = m.group(2)
        legs["fail"] = m.group(3)
    return {"summary": m.group(0) if m else "(no SUMMARY)", "legs": legs, "failed_cases": failed,
            "rc": p.returncode, "stdout_tail": out[-1200:] if not m else "",
            "stderr": p.stderr[-300:]}


def one(item):
    idx, mid, path = item
    st = run_selftest(path, idx)
    ct = run_counter(path, idx)
    cases_fail = ct["legs"].get("fail")
    st_ok = (st["rc"] == 0 and st["cases"] is not None and int(st["cases"][2]) == 0
             and int(st["cases"][1]) == int(st["cases"][0]) and not st["crash"])
    other = []
    for k, want in (("control_clean", "REJECTED"), ("control_findings", "REJECTED"), ("real", "ok"),
                    ("retro", "red"), ("retro_clean", "ok"), ("selftest", "ok"), ("patches", "3/3")):
        got = ct["legs"].get(k)
        if got is not None and got != want:
            other.append("%s=%s(want %s)" % (k, got, want))
    if cases_fail is not None and int(cases_fail) > 0:
        verdict = "killed by counter cases"
    elif not st_ok:
        verdict = "killed only by --selftest"
    else:
        verdict = "SURVIVES both"
    return {"id": mid, "path": path, "verdict": verdict, "other_legs": ",".join(other),
            "counter_summary": ct["summary"], "counter_legs": ct["legs"],
            "failed_cases": ct["failed_cases"], "counter_rc": ct["rc"],
            "selftest_rc": st["rc"],
            "selftest_line": ("SELFTEST cases=%s pass=%s fail=%s" % st["cases"]) if st["cases"] else "(none)",
            "selftest_stderr": st["stderr"]}


def main():
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(STDIR, exist_ok=True)
    ids = sorted(f[:-3] for f in os.listdir(MUTDIR) if f.endswith(".py"))
    items = [(i + 1, mid, os.path.join(MUTDIR, mid + ".py")) for i, mid in enumerate(ids)]
    results = []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for res in ex.map(one, items):
            results.append(res)
            print("%s %s | %s | %s" % (res["id"], res["verdict"], res["counter_summary"],
                                       res["selftest_line"]), flush=True)
    out = os.path.join(SEAT, "results.tsv")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("id\tverdict\tcounter_cases_pass\tcounter_cases_fail\tcounter_legs\tother_legs_off_target\tfailed_cases\tselftest_rc\tselftest_line\tcounter_summary\n")
        for r in results:
            fh.write("\t".join([
                r["id"], r["verdict"], str(r["counter_legs"].get("pass", "")), str(r["counter_legs"].get("fail", "")),
                " ".join("%s=%s" % (k, v) for k, v in sorted(r["counter_legs"].items())),
                r["other_legs"], ",".join(r["failed_cases"]), str(r["selftest_rc"]),
                r["selftest_line"], r["counter_summary"]]) + "\n")
    n_kc = sum(1 for r in results if r["verdict"] == "killed by counter cases")
    n_ks = sum(1 for r in results if r["verdict"] == "killed only by --selftest")
    n_surv = sum(1 for r in results if r["verdict"] == "SURVIVES both")
    print("TOTAL=%d killed_by_counter=%d killed_only_selftest=%d survivors=%d"
          % (len(results), n_kc, n_ks, n_surv))


if __name__ == "__main__":
    main()
