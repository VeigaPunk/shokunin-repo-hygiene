#!/usr/bin/env python3
"""R91ReviewerC1: score the SIX new mutants on EVERY prior pinned population (r83..r90).

The C1 sentence under test says the six "survive every population the lane has pinned before this
round". The filed predicate only scores r90 and r91; this driver scores r83..r90 so the word "every"
is measured, not inferred from nesting (the r86->r87 pair is NOT a byte prefix).
"""
import concurrent.futures as cf
import hashlib
import json
import os
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEAT = os.path.join(LANE, ".ufo/waves/round-91/w1/R91ReviewerC1")
SCRATCH = "/fast/scratch/hyaku/souji-r91/R91ReviewerC1/prior"
HARNESS = os.path.join(SEAT, "derived-harness.py")
COUNTER = os.path.join(LANE, "census/round-87/c1-pointer-counter.py")
MUTANTS = os.path.join(LANE, "census/round-91/c1-mutants.json")
NEW = ("ld1c-class-keyed", "ld1d-conflict-keyed", "nf6i2-last-occurrence", "nf6j-pathch-narrow",
       "s1-exact-width", "s3-equal-two")
LABELS = ("r83", "r84", "r85", "r86", "r87", "r88", "r89", "r90")


def main():
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH)
    src = open(COUNTER, encoding="utf-8").read()
    members = {m["id"]: m for m in json.load(open(MUTANTS))["members"]}
    arms = {}
    for mid in ("pristine",) + NEW:
        if mid == "pristine":
            body = src
        else:
            m = members[mid]
            assert src.count(m["old"]) == 1, mid
            body = src.replace(m["old"], m["new"])
        p = os.path.join(SCRATCH, mid + ".py")
        open(p, "w", encoding="utf-8").write(body)
        arms[mid] = p

    def one(job):
        label, arm = job
        w = os.path.join(SCRATCH, "work", f"{label}--{arm}")
        os.makedirs(w, exist_ok=True)
        p = subprocess.run([sys.executable, "-B", HARNESS, "--counter", arms[arm], "--lane", LANE,
                            "--fleet-root", "/home/vgpnk/Projects/shokunin", "--work", w,
                            "--population", os.path.join(LANE, f"census/round-{label[1:]}/c1-false-rows.tsv")],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=LANE, timeout=600)
        out = p.stdout.decode("utf-8", "replace")
        red = [l.split()[1] for l in out.splitlines() if l.startswith("ROW ") and "match=no" in l]
        err = [l.split()[1] for l in out.splitlines() if l.startswith("ROW ") and "match=error" in l]
        summ = [l for l in out.splitlines() if l.startswith("SUMMARY")]
        stderr = p.stderr.decode("utf-8", "replace")[:200]
        shutil.rmtree(w, ignore_errors=True)  # keep the peak footprint one fixture
        return {"population": label, "arm": arm, "exit": p.returncode,
                "killed": p.returncode != 0 or bool(red) or bool(err),
                "summary": summ[-1] if summ else "-", "red": red, "err": err,
                "stderr": stderr}

    jobs = [(l, a) for l in LABELS for a in ("pristine",) + NEW]
    rows = []
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        for r in ex.map(one, jobs):
            rows.append(r)
    outdir = os.path.join(SEAT, "receipts", "prior")
    os.makedirs(outdir, exist_ok=True)
    for r in rows:
        print(f"{r['population']:<4} {r['arm']:<24} exit={r['exit']} killed={r['killed']} red={r['red']} {r['summary']}")
    json.dump(rows, open(os.path.join(SEAT, "receipts", "prior-table.json"), "w"), indent=1)
    bad = [r for r in rows if r["arm"] != "pristine" and r["killed"]]
    pristine_red = [r for r in rows if r["arm"] == "pristine" and r["exit"] != 0]
    print(f"\nSURVIVORS-DEAD-ON-A-PRIOR-POPULATION={len(bad)}")
    for r in bad:
        print("  DEAD", r["population"], r["arm"], r["summary"])
    print(f"PRISTINE-RED={len(pristine_red)}")
    shutil.rmtree(SCRATCH, ignore_errors=True)


if __name__ == "__main__":
    main()
