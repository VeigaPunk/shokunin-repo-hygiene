#!/usr/bin/env python3
"""R42w3mutationtester02: build the evidence report from grid-w3.jsonl.

Kill/clean semantics are the frozen counter's (census/round-42/c3-counter.py):
  KILL(F,T)  = rc==1 and SUMMARY fail>0 and no traceback
  CLEAN(F,T) = rc==0 and fail==0 and pass==cases and no traceback
  pristine_ok(F) = CLEAN(F, pinned tool) and cases >= 13
"""
import json
import os
import subprocess
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
ALL_CASES = sorted(POP_CASE.values())


def kill(rec):
    return bool(rec) and rec.get("cases") is not None and rec.get("rc") == 1 \
        and (rec.get("failed") or 0) > 0 and not rec.get("crash")


def counter_clean(rec):
    return bool(rec) and rec.get("cases") is not None and rec.get("rc") == 0 \
        and rec.get("failed") == 0 and rec.get("passed") == rec.get("cases") \
        and not rec.get("crash")


def pristine_ok(rec):
    return counter_clean(rec) and rec.get("cases") is not None and rec.get("cases") >= 13


def load(path=GRID):
    cells = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rec = json.loads(line)
                cells[(rec["fixture_mutant"], rec["tool"])] = rec
    return cells


def uptime():
    try:
        return open("/proc/loadavg").read().strip()
    except OSError:
        return "?"


def main():
    cells = load()
    cats = {}
    sys.path.insert(0, HERE)
    import mutants as M
    cats = {mid: spec["category"] for mid, spec in
            M.build(subprocess.run(["git", "-C", "/home/vgpnk/Projects/shokunin/souji-shokunin",
                                    "show", "6a3f75941d3604e3459011d599c2c16f3a97b44c:tests/fixtures/"
                                    "r42-drift-conditions.py"], stdout=subprocess.PIPE,
                                   check=True).stdout.decode("utf-8")).items()}

    mids = [m for m in sorted(cats) if m != "BASE" and (m, "pristine") in cells]
    base = cells.get(("BASE", "pristine"))
    print("### fixture-mutant grid (wave 3)\n")
    print("| fixture mutant | cat | pristine (pinned tool) | population mutants still killed | lost kills | verdict |")
    print("|---|---|---|---|---|---|")
    verdict_of = {}
    for mid in mids:
        pre = cells.get((mid, "pristine"))
        killed = [p for p in POP if kill(cells.get((mid, p)))]
        lost = [p for p in POP if p not in killed]
        if not counter_clean(pre):
            v = "CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool)"
        elif not pristine_ok(pre):
            v = "DROPPED-CASE (cases<13: not pristine under the counter's cases>=13 rule)"
        elif lost:
            v = "LOAD-BEARING (removing it loses a kill)"
        else:
            v = "REDUNDANT (still kills all 13: vacuous for the population)"
        verdict_of[mid] = (v, killed, lost)
        print("| %s | %s | %s | %d/13 | %s | %s |" % (
            mid, cats[mid],
            "clean rc=0 fail=0 pass=%s/%s" % (pre.get("passed"), pre.get("cases"))
            if counter_clean(pre) else "FAIL rc=%s fail=%s" % (pre.get("rc"), pre.get("failed")),
            len(killed), ",".join(lost) or "-", v))

    print("\n### BASE row: which case kills which population mutant (landed fixture, unmutated)\n")
    print("| population mutant | killed by the landed fixture | failing case(s) |")
    print("|---|---|---|")
    bycase = {}
    for p in POP:
        rec = cells.get(("BASE", p))
        failing = list((rec or {}).get("failing", []))
        for c in failing:
            bycase.setdefault(c, []).append(p)
        print("| %s | %s | %s |" % (p, "yes" if kill(rec) else "NO", ",".join(failing) or "-"))
    print("\n### cases and the population mutants they catch\n")
    for c in ALL_CASES:
        print("- `%s`: %s" % (c, ",".join(bycase.get(c, [])) or "NEVER (assertion never fires against the population)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
