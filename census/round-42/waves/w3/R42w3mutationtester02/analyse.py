#!/usr/bin/env python3
"""R42w3mutationtester02: analyse the fixture-mutant x tool grid.

Semantics are the frozen counter's (census/round-42/c3-counter.py killed()/clean()):
  KILL(F,T)  = rc==1 and SUMMARY fail>0 and no traceback
  CLEAN(F,T) = rc==0 and fail==0 and pass==cases and no traceback
The counter's pristine_ok additionally requires cases >= 13 (c3-counter.py line: cand_pre[1] >= 13),
so a fixture mutant that drops a case cannot be pristine under the counter's definition.

For each fixture mutant M:
  pristine   CLEAN(M, pristine)
  pop_killed { p in POP : KILL(M, p) }
  lost       POP - pop_killed

Verdicts:
  CAUGHT-BY-PRISTINE  M fails the pinned tool (self-inconsistent: changed token / narrowed bound).
  NO-POP-COVER        M drops a case, so it is not pristine under the counter's cases>=13 rule.
  LOAD-BEARING        M passes pristine (cases>=13) but loses >=1 population kill.
  REDUNDANT           M passes pristine (cases>=13) and still kills all 13 population mutants:
                      the removed/weakened assertion was not load-bearing for the population.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GRID = os.path.join(HERE, "grid-w3.jsonl")
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
    """The frozen counter's killed(): rc==1, SUMMARY fail>0, no traceback."""
    return bool(rec) and rec.get("cases") is not None and rec.get("rc") == 1 \
        and (rec.get("failed") or 0) > 0 and not rec.get("crash")


def counter_clean(rec):
    """The frozen counter's clean(): rc==0, fail==0, pass==cases, no traceback."""
    return bool(rec) and rec.get("cases") is not None and rec.get("rc") == 0 \
        and rec.get("failed") == 0 and rec.get("passed") == rec.get("cases") \
        and not rec.get("crash")


def pristine_ok(rec):
    """The frozen counter's pristine_ok: clean() and cases >= 13."""
    return counter_clean(rec) and rec.get("cases") >= 13


def load(path=GRID):
    cells = {}
    with open(path) as fh:
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
        killed = [p for p in POP if kill(cells.get((mid, p)))]
        lost = [p for p in POP if p not in killed]
        missing = [p for p in POP if (mid, p) not in cells]
        pre_ok = pristine_ok(pre)
        if not counter_clean(pre):
            verdict = "CAUGHT-BY-PRISTINE"
        elif not pre_ok:
            # clean but fewer than 13 cases: the counter's pristine_ok requires cases >= 13
            verdict = "DROPPED-CASE"
        elif missing:
            verdict = "INCOMPLETE"
        elif lost:
            verdict = "LOAD-BEARING"
        else:
            verdict = "REDUNDANT"
        rows.append((mid, pre_ok, len(killed), ",".join(lost) or "-", verdict, missing))
    print("fixture_mutant | pristine_ok | pop_killed | lost | verdict")
    for r in rows:
        print("%-4s | %-5s | %2d/13 | %-22s | %s" % (r[0], r[1], r[2], r[3], r[4]))

    # Which case kills which population mutant, read off the BASE row.
    base = cells.get(("BASE", "pristine"))
    print("\nBASE pristine cell: rc=%s cases=%s pass=%s fail=%s" % (
        base["rc"], base["cases"], base["passed"], base["failed"]))
    killers = {}
    for p in POP:
        rec = cells.get(("BASE", p))
        failing = [n for n in (rec or {}).get("failing", [])]
        killers[p] = failing
        print("  %-3s killed=%-5s failing_cases=%s" % (p, kill(rec), ",".join(failing) or "-"))

    # A case is load-bearing when removing it (a DROP mutant) loses a population kill.
    print("\ncase -> population mutants it is the sole killer of (from BASE failing lists):")
    bycase = {}
    for p in POP:
        for c in killers.get(p, []):
            bycase.setdefault(c, []).append(p)
    for c in sorted(bycase):
        print("  %-46s %s" % (c, ",".join(bycase[c])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
