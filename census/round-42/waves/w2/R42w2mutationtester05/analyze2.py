#!/usr/bin/env python3
"""Noise-aware classification of the counter-mutant matrix (R42w2mutationtester05).

Each mutant's printed SUMMARY is compared field-by-field with the pristine counter's SUMMARY for the
same artifact.  Field classes:
  DET    killed survived equiv equiv_killed mutants pristine anchors cases: the three replicate
         runs of the pristine counter reproduced these exactly.  Any change is a DET change.
  FLAKY  old_killed (observed 0..3 across identical pristine runs under load) and prior (observed
         8/8 and, once per load-spike, 7/8).  A value inside the observed flake range is
         NOISE-CONSISTENT (not separable from a flake in one run); a value outside it is DET.
Verdicts per mutant:
  DET-VISIBLE          at least one DET change on at least one artifact
  NOISE-CONSISTENT     no DET change; only flaky fields moved, inside their observed range
  BLIND                no printed field moved on any artifact (strict reading of the acceptance)
The exit code is reported alongside; met (exit) depends on old_killed==0 and prior_ok==8, so an exit
change is attributed to a flake when the only moved fields are FLAKY.
"""
import json
import os
import sys

SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2mutationtester05"
RECDIR = os.path.join(SEAT, "receipts")
ARTIFACTS = ("stub-allpass", "stub-sniff", "landed-fixture")
DET = ("mutants", "killed", "survived", "pristine", "equiv", "equiv_killed", "anchors", "cases")
OLD_KILLED_FLAKE = {"0", "1", "2", "3"}
PRIOR_FLAKE = {"7/8", "8/8"}

sys.path.insert(0, SEAT)
import driver  # noqa: E402


def parse(summary):
    if not summary:
        return None
    out = {}
    for tok in summary.split()[1:]:
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


def load():
    recs = {}
    for name in os.listdir(RECDIR):
        if not name.endswith(".json") or name in ("all-records.json", "table.json", "table2.json"):
            continue
        with open(os.path.join(RECDIR, name)) as h:
            r = json.load(h)
        recs[(r["mutant"], r["artifact"])] = r
    return recs


def classify(base_summary, mut_summary):
    bp, mp = parse(base_summary), parse(mut_summary)
    if bp is None or mp is None:
        return ["SUMMARY-ABSENT"], []
    det, noise = [], []
    for f in DET:
        if bp.get(f) != mp.get(f):
            det.append("%s:%s->%s" % (f, bp.get(f), mp.get(f)))
    if bp.get("old_killed") != mp.get("old_killed"):
        v = mp.get("old_killed")
        (noise if v in OLD_KILLED_FLAKE else det).append("old_killed:%s->%s" % (bp.get("old_killed"), v))
    if bp.get("prior") != mp.get("prior"):
        v = mp.get("prior")
        (noise if v in PRIOR_FLAKE else det).append("prior:%s->%s" % (bp.get("prior"), v))
    return det, noise


def main():
    recs = load()
    base = {a: recs[("PRISTINE", a)]["summary"] for a in ARTIFACTS}
    base_rc = {a: recs[("PRISTINE", a)]["rc"] for a in ARTIFACTS}
    rows = []
    for mid, cat, old, new in driver.MUTANTS:
        per = {}
        any_det = any_noise = any_raw = False
        for a in ARTIFACTS:
            r = recs.get((mid, a))
            if r is None:
                per[a] = {"missing": True}
                continue
            det, noise = classify(base[a], r["summary"])
            raw = r["summary"] != base[a]
            any_det |= bool(det)
            any_noise |= bool(noise)
            any_raw |= raw
            per[a] = {"summary": r["summary"], "rc": r["rc"], "rc_diff": r["rc"] != base_rc[a],
                      "det": det, "noise": noise, "raw_diff": raw}
        if any_det:
            verdict = "DET-VISIBLE"
        elif any_noise:
            verdict = "NOISE-CONSISTENT"
        else:
            verdict = "BLIND"
        rows.append({"id": mid, "cat": cat, "old": old, "new": new, "per": per, "verdict": verdict,
                     "raw_any": any_raw})
    rep = {}
    for k in ("REP1", "REP2", "REP3"):
        for a in ARTIFACTS:
            r = recs.get((k, a))
            if r:
                rep.setdefault(a, []).append({"rc": r["rc"], "summary": r["summary"]})
    out = {"baseline": {a: {"summary": base[a], "rc": base_rc[a]} for a in ARTIFACTS},
           "replicates": rep, "rows": rows}
    with open(os.path.join(RECDIR, "table2.json"), "w") as h:
        json.dump(out, h, indent=1)

    print("== PRISTINE BASELINE ==")
    for a in ARTIFACTS:
        print("%-15s rc=%s %s" % (a, base_rc[a], base[a]))
    print("\n== REPLICATES OF THE PRISTINE COUNTER (identical bytes, identical command) ==")
    for a in ARTIFACTS:
        for x in rep.get(a, []):
            print("%-15s rc=%s %s" % (a, x["rc"], x["summary"]))
    print("\n== PER-MUTANT ==")
    for r in rows:
        print("%-4s %-18s %s" % (r["id"], r["cat"], r["verdict"]))
        for a in ARTIFACTS:
            p = r["per"][a]
            if p.get("missing"):
                print("      %-15s MISSING" % a)
                continue
            print("      %-15s rc=%s rc_diff=%s det=%s noise=%s" % (
                a, p["rc"], p["rc_diff"], p["det"] or "-", p["noise"] or "-"))
    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    print("\n== VERDICT COUNTS ==", counts)
    print("== STRICT BLIND (no printed SUMMARY field differs on any artifact) ==")
    for r in rows:
        if not r["raw_any"]:
            print("  %-4s %-18s [%s] -> [%s]" % (r["id"], r["cat"], r["old"], r["new"]))
    print("== NOISE-CONSISTENT (only flaky fields moved; not claimed as killed or blind) ==")
    for r in rows:
        if r["verdict"] == "NOISE-CONSISTENT":
            print("  %-4s %-18s [%s] -> [%s]" % (r["id"], r["cat"], r["old"], r["new"]))


if __name__ == "__main__":
    main()
