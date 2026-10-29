#!/usr/bin/env python3
"""R42w2mutationtester03: analyse the fixture-mutant x tool grid in grid.jsonl.

Semantics (identical to the frozen counter's killed()/clean()):
  KILL(fixture F, tool T) = rc==1 and SUMMARY fail>0 and no traceback.
  CLEAN(fixture F, tool T) = rc==0 and fail==0 and pass==cases and no traceback.

For each fixture mutant M:
  pristine   = CLEAN(M, pristine)            # M still passes the pinned tool
  pop_killed = { p in POP : KILL(M, p) }     # population mutants M still kills
  lost       = POP - pop_killed              # population kills M loses

Verdicts:
  CAUGHT-BY-PRISTINE  M fails the pinned tool: M asserts something the pinned tool does not do.
                      It is not a survivor; it is a self-inconsistency (a changed token/bound).
  LOAD-BEARING        M passes pristine but loses >=1 population kill.
  REDUNDANT           M passes pristine and still kills all 13 population mutants
                      (the removed/weakened assertion was not load-bearing for the population).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GRID = os.path.join(HERE, "grid.jsonl")
POP = ("B1", "E2", "E4", "G2", "G3", "G4", "G5", "H1", "H2", "I1", "J9", "M1", "D4")
POP_CASE = {
    "B1": "fifo-record-is-refused-not-blocked",
    "E2": "root-sibling-prefix-is-outside",
    "E4": "gitdir-sibling-prefix-is-outside",
    "G2": "timeout-of-one-is-accepted",
    "G3": "default-timeout-outlasts-a-blocked-git",
    "G4": "list-timeout-is-reported-unreachable",
    "G5": "list-nonzero-rc-is-reported-unreachable",
    "H1": "root-option-is-required",
    "H2": "record-option-is-required",
    "I1": "symlinked-child-is-not-discovered",
    "J9": "two-digit-regs-are-read-whole",
    "M1": "longer-old-json-is-truncated-on-write",
    "D4": "invalid-utf8-in-record-becomes-replacement-char",
}


def kill(rec):
    return bool(rec) and rec.get("cases") is not None and rec.get("rc") == 1 \
        and (rec.get("failed") or 0) > 0 and not rec.get("crash")


def clean(rec):
    return bool(rec) and rec.get("cases") is not None and rec.get("rc") == 0 \
        and rec.get("failed") == 0 and rec.get("passed") == rec.get("cases") \
        and not rec.get("crash") and rec.get("cases") >= 13


def load():
    cells = {}
    with open(GRID) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rec = json.loads(line)
                cells[(rec["fixture_mutant"], rec["tool"])] = rec
    return cells


def main():
    cells = load()
    mids = sorted({k[0] for k in cells})
    rows = []
    for mid in mids:
        pre = cells.get((mid, "pristine"))
        if pre is None:
            continue
        pop_killed = [p for p in POP if kill(cells.get((mid, p)))]
        lost = [p for p in POP if p not in pop_killed]
        missing = [p for p in POP if (mid, p) not in cells]
        pre_ok = clean(pre)
        if not pre_ok:
            verdict = "CAUGHT-BY-PRISTINE"
        elif lost:
            verdict = "LOAD-BEARING"
        else:
            verdict = "REDUNDANT"
        rows.append({
            "id": mid, "pristine_clean": pre_ok,
            "pristine_detail": "rc=%s cases=%s pass=%s fail=%s failing=%s" % (
                pre.get("rc"), pre.get("cases"), pre.get("passed"), pre.get("failed"),
                ",".join(pre.get("failing") or []) or "-"),
            "pop_killed": pop_killed, "lost": lost, "missing": missing, "verdict": verdict,
        })
    with open(os.path.join(HERE, "rows.json"), "w") as fh:
        json.dump(rows, fh, indent=1)
    print("| fixture mutant | pristine | population mutants still killed | verdict |")
    print("|---|---|---|---|")
    for r in rows:
        pk = "%d/13" % len(r["pop_killed"])
        if r["lost"]:
            pk += " (lost %s)" % ",".join(r["lost"])
        if r["missing"]:
            pk += " (no cell: %s)" % ",".join(r["missing"])
        print("| %s | %s: %s | %s | %s |" % (
            r["id"], "clean" if r["pristine_clean"] else "FAILS", r["pristine_detail"], pk, r["verdict"]))
    print()
    print("=== population mutant -> fixture mutants whose change loses its kill ===")
    for p in POP:
        hits = [r["id"] for r in rows if p in r["lost"]]
        print("%s (%s): %s" % (p, POP_CASE[p], ",".join(hits) or "none"))
    print()
    print("=== non-redundant/-caught summary ===")
    print("LOAD-BEARING: %s" % ",".join(r["id"] for r in rows if r["verdict"] == "LOAD-BEARING"))
    print("REDUNDANT:    %s" % ",".join(r["id"] for r in rows if r["verdict"] == "REDUNDANT"))
    print("CAUGHT-BY-PRISTINE: %s" % ",".join(r["id"] for r in rows if r["verdict"] == "CAUGHT-BY-PRISTINE"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
