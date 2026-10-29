#!/usr/bin/env python3
"""Analyse the counter-mutant matrix: diff each mutant's printed SUMMARY against the pristine
counter's SUMMARY, per artifact.  Emits the acceptance table and the blind-spot list.
"""
import json
import os
import re
import sys

SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2mutationtester05"
RECDIR = os.path.join(SEAT, "receipts")
ARTIFACTS = ("stub-allpass", "stub-sniff", "landed-fixture")
FIELDS = ("mutants", "killed", "survived", "pristine", "prior", "old_killed", "equiv",
          "equiv_killed", "anchors", "cases")

sys.path.insert(0, SEAT)
import driver  # noqa: E402  (for the MUTANTS table)


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
    for name in sorted(os.listdir(RECDIR)):
        if not name.endswith(".json") or name == "all-records.json":
            continue
        with open(os.path.join(RECDIR, name)) as h:
            r = json.load(h)
        recs[(r["mutant"], r["artifact"])] = r
    return recs


def main():
    recs = load()
    base = {}
    for a in ARTIFACTS:
        base[a] = recs.get(("PRISTINE", a))
    print("=== BASELINE (pristine counter copy) ===")
    for a in ARTIFACTS:
        r = base[a]
        print("%-16s rc=%s %s" % (a, r["rc"] if r else "MISSING", r["summary"] if r else "MISSING"))
    print()
    rows = []
    for mid, cat, old, new in driver.MUTANTS:
        cells = {}
        summary_changed = False
        rc_changed = False
        detail = []
        for a in ARTIFACTS:
            r = recs.get((mid, a))
            if r is None:
                cells[a] = ("MISSING", None)
                detail.append("%s=MISSING" % a)
                continue
            bp = parse(base[a]["summary"]) if base[a] else None
            mp = parse(r["summary"])
            diffs = []
            if bp is None or mp is None:
                diffs.append("SUMMARY-ABSENT")
            else:
                for f in FIELDS:
                    if bp.get(f) != mp.get(f):
                        diffs.append("%s:%s->%s" % (f, bp.get(f), mp.get(f)))
            if diffs:
                summary_changed = True
            if r["rc"] != (base[a]["rc"] if base[a] else None):
                rc_changed = True
            cells[a] = (r["summary"], r["rc"])
            detail.append("%s=[%s]" % (a, ",".join(diffs) if diffs else "same"))
        verdict = []
        if summary_changed:
            verdict.append("SUMMARY-DIFFERS")
        else:
            verdict.append("SUMMARY-IDENTICAL")
        if rc_changed:
            verdict.append("EXIT-DIFFERS")
        else:
            verdict.append("EXIT-SAME")
        rows.append({"id": mid, "cat": cat, "old": old, "new": new,
                     "cells": cells, "summary_changed": summary_changed,
                     "rc_changed": rc_changed, "detail": detail,
                     "verdict": " ".join(verdict)})
    with open(os.path.join(RECDIR, "table.json"), "w") as h:
        json.dump({"baseline": {a: (base[a]["summary"], base[a]["rc"]) for a in ARTIFACTS},
                   "rows": rows}, h, indent=1)
    print("=== TABLE ===")
    for r in rows:
        print("%-4s %-20s %s" % (r["id"], r["cat"], r["verdict"]))
        for d in r["detail"]:
            print("        %s" % d)
    print()
    blind = [r for r in rows if not r["summary_changed"]]
    print("=== BLIND SPOTS: SUMMARY identical for ALL THREE artifacts (%d) ===" % len(blind))
    for r in blind:
        print("  %-4s %-20s %s   [%s] -> [%s]" % (
            r["id"], r["cat"], r["verdict"], r["old"], r["new"]))
    print()
    same_exit = [r for r in blind if not r["rc_changed"]]
    print("=== FULLY INVISIBLE: SUMMARY identical AND exit code identical (%d) ===" % len(same_exit))
    for r in same_exit:
        print("  %-4s %-20s [%s] -> [%s]" % (r["id"], r["cat"], r["old"], r["new"]))


if __name__ == "__main__":
    main()
