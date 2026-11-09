#!/usr/bin/env python3
"""Offline evaluation of candidate kill rules over the no-sentinel (r93-rule) harness outputs.
Each harness.out is: harness stdout + "\n--stderr--\n" + counter/harness stderr.
A candidate rule is a function of the 66 ROW lines (id, where, rev, item, class, expect, got, rc, match).
"""
import glob, os
C11 = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-94/w1/R94Critic/receipts/eval-tmp"
IDS = ["a127c26-True-to-False", "a491c22-<-to-<=", "h-ok-admits-one", "h-crash-late", "h-crash-index"]
def rows(d):
    t = open(os.path.join(d, "harness.out")).read()
    return [l for l in t.splitlines() if l.startswith("ROW ")]
def r93(rs):  # the filed r93 rule
    if all(l.endswith(" match=yes") for l in rs): return "no"
    if any(l.endswith(" match=no") for l in rs): return "yes"
    return "errored"
def r_merr(rs):
    if any(l.endswith(" match=error") for l in rs): return "errored"
    return r93(rs)
def r_gotminus(rs):
    if any(" got=- " in l for l in rs): return "errored"
    return r93(rs)
def r_allrc1(rs):
    if all(" rc=1 match=" in l for l in rs): return "errored"
    return r93(rs)
def r_pattern(rs):  # composite: got=- OR all rows rc=1
    if any(" got=- " in l for l in rs) or all(" rc=1 match=" in l for l in rs): return "errored"
    return r93(rs)
CAND = {"r93-filed": r93, "match=error": r_merr, "got=-": r_gotminus, "all-rows-rc=1": r_allrc1,
        "composite(got=-|allrc1)": r_pattern}
for name, fn in CAND.items():
    vs = {mid: fn(rows(os.path.join(C11, f"m{i:04d}/"))) for i, mid in enumerate(IDS)}
    s = (sum(v == "errored" for v in vs.values()), sum(v == "yes" for v in vs.values()), sum(v == "no" for v in vs.values()))
    print(f"rule {name}: errored,killed,survived={s} per-mutant={vs}")
PRED = (2, 2, 1)
