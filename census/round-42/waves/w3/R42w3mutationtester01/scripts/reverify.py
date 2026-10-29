#!/usr/bin/env python3
"""Re-verify the SURVIVORS of the batch run, one at a time, on an idle host.

The batch run used 6 parallel workers; the round's lesson (E-1) records that a
counter leg can read differently under load.  This script re-runs the counter's
CASE TABLE leg and the mutant's own --selftest for every mutant the batch run
classified as a survivor, with a small worker count, and prints a line for each
that says whether the re-verification AGREES with the batch verdict.

A disagreement is reported verbatim (both readings), never silently averaged.
"""
import concurrent.futures as cf
import csv
import os
import re
import subprocess
import sys

SEAT = "/fast/scratch/hyaku/souji-r42/R42w3mutationtester01"
MUTDIR = os.path.join(SEAT, "mutants")
SCORE = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/score-candidate.sh"
SUMMARY_RE = re.compile(r"^SUMMARY cases=(\d+) pass=(\d+) fail=(\d+)(.*)$", re.M)
SELFTEST_RE = re.compile(r"^SELFTEST cases=(\d+) pass=(\d+) fail=(\d+)\s*$", re.M)


def counter(path):
    p = subprocess.run(["bash", SCORE, "c2", SEAT, "tools/souji-freeze-check.py=" + path],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
                       env=dict(os.environ, TMPDIR=SEAT), timeout=1800, cwd=SEAT)
    m = SUMMARY_RE.search(p.stdout)
    legs = {}
    if m:
        for tok in m.group(4).split():
            if "=" in tok:
                k, v = tok.split("=", 1)
                legs[k] = v
        legs["cases"], legs["pass"], legs["fail"] = m.group(1), m.group(2), m.group(3)
    return m.group(0) if m else "(no SUMMARY)", legs, p.stdout


def selftest(path):
    d = os.path.join(SEAT, "st-reverify")
    os.makedirs(d, exist_ok=True)
    p = subprocess.run(["python3", "-B", path, "--selftest"], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True, check=False,
                       env=dict(os.environ, TMPDIR=d), timeout=900, cwd=d)
    m = SELFTEST_RE.findall(p.stdout)
    crash = "Traceback (most recent call last)" in p.stderr
    ok = (p.returncode == 0 and m and int(m[-1][2]) == 0 and int(m[-1][1]) == int(m[-1][0]) and not crash)
    return ok, ("SELFTEST cases=%s pass=%s fail=%s" % m[-1]) if m else "(no SELFTEST line)"


def one(mid):
    path = os.path.join(MUTDIR, mid + ".py")
    summ, legs, full = counter(path)
    st_ok, st_line = selftest(path)
    if legs.get("fail") and int(legs["fail"]) > 0:
        verdict = "killed by counter cases"
    elif not st_ok:
        verdict = "killed only by --selftest"
    else:
        verdict = "SURVIVES both"
    return mid, verdict, summ, legs, st_line, st_ok


def main():
    rows = list(csv.DictReader(open(os.path.join(SEAT, "results.tsv")), delimiter="\t"))
    surv = [r["id"] for r in rows if r["verdict"] == "SURVIVES both"]
    print("re-verifying %d batch survivors one at a time (2 workers)" % len(surv))
    disagree = []
    out = []
    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        for mid, verdict, summ, legs, st_line, st_ok in ex.map(one, surv):
            batch = [r["verdict"] for r in rows if r["id"] == mid][0]
            agree = (verdict == batch)
            if not agree:
                disagree.append((mid, batch, verdict, summ))
            out.append("%s %s | %s | %s" % (mid, "AGREE" if agree else "DISAGREE", summ, st_line))
            print(out[-1], flush=True)
    print("\n=== re-verification summary ===")
    print("re-verified=%d agree=%d disagree=%d" % (len(surv), len(surv) - len(disagree), len(disagree)))
    for mid, batch, verdict, summ in disagree:
        print("DISAGREE %s: batch=%s recheck=%s | %s" % (mid, batch, verdict, summ))
    with open(os.path.join(SEAT, "reverify.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    with open(os.path.join(SEAT, "reverify-disagreements.txt"), "w", encoding="utf-8") as fh:
        for mid, batch, verdict, summ in disagree:
            fh.write("%s\tbatch=%s\trecheck=%s\t%s\n" % (mid, batch, verdict, summ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
