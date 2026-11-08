#!/usr/bin/env python3
"""S88MutCounter: score arbitrary single-edit counter variants on the two pinned C1 populations, in parallel.

Same kill rule as census/round-88/c1-clause-battery.py: KILLED iff the r88 harness exits non-zero or
prints mismatches>0 / errors>0 for that population. Each (variant, population) is one fresh harness run.
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
HARNESS = os.path.join(LANE, "census/round-88/c1-false-row-harness.py")
COUNTER = os.path.join(LANE, "census/round-87/c1-pointer-counter.py")
POP = {"r87": os.path.join(LANE, "census/round-87/c1-false-rows.tsv"),
       "r88": os.path.join(LANE, "census/round-88/c1-false-rows.tsv")}


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def score(job):
    mid, counter, lbl, work = job
    d = os.path.join(work, f"run-{lbl}-{mid}")
    p = subprocess.run([sys.executable, "-B", HARNESS, "--counter", counter, "--lane", LANE,
                        "--fleet-root", FLEET, "--work", d, "--population", POP[lbl]],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=LANE)
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    m = re.search(r"^SUMMARY rows=(\d+) mismatches=(\d+) accepted=(\d+) refused_true=(\d+) errors=(\d+)$", out, re.M)
    red = []
    if m:
        rows, mism, errs = int(m.group(1)), int(m.group(2)), int(m.group(5))
        red = [l for l in out.splitlines() if l.startswith("ROW ") and "match=no" in l]
    else:
        rows = mism = errs = None
    red += [l for l in out.splitlines() + err.splitlines() if "FATAL" in l]
    return mid, lbl, rows, mism, errs, p.returncode, red[:4], err[:200]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--only", default="r87,r88")
    ap.add_argument("--jobs", type=int, default=5)
    ns = ap.parse_args()
    work = os.path.abspath(ns.work)
    src = open(COUNTER, encoding="utf-8").read()
    specs = json.load(open(ns.variants, encoding="utf-8"))["members"]
    os.makedirs(os.path.join(work, "counters"), exist_ok=True)
    sets = [x for x in ns.only.split(",") if x]
    counters = {}
    for m in specs:
        mid = m["id"]
        n = src.count(m["old"])
        if n != 1:
            print(f"VARIANT {mid} FATAL old occurs {n} times")
            continue
        path = os.path.join(work, "counters", mid + ".py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(src.replace(m["old"], m["new"]) if m["old"] != m["new"] else src)
        counters[mid] = path
        print(f"VARIANT {mid} sha256={sha(path)}", flush=True)
    jobs = [(mid, path, lbl, work) for mid, path in counters.items() for lbl in sets]
    results = {}
    with cf.ThreadPoolExecutor(max_workers=ns.jobs) as ex:
        for mid, lbl, rows, mism, errs, rc, red, err in ex.map(score, jobs):
            results[(mid, lbl)] = (rows, mism, errs, rc, red, err)
            print(f"RUN {mid} pop={lbl} rows={rows} mismatches={mism} errors={errs} exit={rc} "
                  f"killed={'yes' if (rc != 0 or (mism or 0) > 0 or (errs or 0) > 0) else 'no'}"
                  + (f" red={' | '.join(red)}" if red else ""), flush=True)
    print("=== SUMMARY TABLE ===", flush=True)
    for mid in counters:
        cells = []
        for lbl in sets:
            rows, mism, errs, rc, red, err = results[(mid, lbl)]
            k = "FATAL" if rows is None else ("yes" if (rc != 0 or mism > 0 or errs > 0) else "no")
            cells.append(f"r{lbl[1:]}={k}(m={mism},e={errs},rc={rc})")
        print(f"VARIANT {mid:32s} " + " ".join(cells), flush=True)


if __name__ == "__main__":
    main()
