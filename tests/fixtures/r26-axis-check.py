#!/usr/bin/env python3
"""tests/fixtures/r26-axis-check.py — round-26 C3 fixture.

11 cases over tools/souji-axis-check.py --prereg PATH --scorecard PATH.
Cases are self-contained: each writes a scratch preregistration file into a
temp dir; the scorecard is a small synthetic table unless the case needs a
real one (no — every case uses the same synthetic axes table: coverage 8,
calibration 7, operability 8, so the lowest non-retired axis is calibration).

Expectations per case:
  rc          expected tool exit code (0 clean, 1 flagged, 2 refused)
  min_flags   minimum number of FLAG lines the run must print (0 = none)
  rule        R-code that must appear in at least one FLAG line, or None

Cases:
  1 axis not owned by souji (freshness)             rc1 flags>=1 R1
  2 owned axis + consistent surface-class            rc0 flags=0
  3 surface-class mismatch (fixture-expansion on
    calibration)                                     rc1 flags>=1 R2
  4 no claim on lowest axis                          rc1 flags>=1 R3
  5 multi-claim, wrong rule applied                  rc1 flags>=1 R3
  6 multi-claim, right rule                          rc0 flags=0
  7 machine-block claim missing enumerate            rc1 flags>=1 R4
  8 enumerate line containing a universal quantifier rc1 flags>=1 R4
  9 consistent surface-class under each axis         rc0 flags=0
 10 multi-surface claim (extra surface-class lines)  rc0 flags=0
 11 malformed prereg (claim without axis)            rc2 flags=0 refusal

Control arm: `--stub` re-runs cases 1,3,4,5,7,8,11 through a tool stub that
prints `claims=N flags=0` rc 0 (case 11 also rc 0). Every must-flag/refuse
case then fails => fixture prints control=FALSE-GREEN-REJECTED, rc 1.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOL = os.path.join(ROOT, "tools", "souji-axis-check.py")

SCORECARD = """\
## Axes

| axis | score | verdict / observation | counting command | measured commit | last change |
|---|---|---|---|---|---|
| coverage | 8 | R21 bounded sink repair | cmd=reason/2/2 | abc1234 | r21 |
| calibration | 7 | lowest | self | def5678 | r25 |
| operability | 8 | receipts green | receipts | 9ab0000 | r23 |

## Retired

| retired | — | nudge-waived axes land here (none retired) |
"""

HDR = "Souji round 26 — preregistration\n\n## MACHINE BLOCK\n"
FTR = "END\n"


def prereg(claims):
    """claims: list of (id, [(key,value),...] or raw lines)"""
    out = [HDR]
    for cid, fields in claims:
        out.append(f"CLAIM {cid}\n")
        for k, v in fields:
            out.append(f"{k}: {v}\n")
    out.append(FTR)
    return "".join(out)


CASES = [
    # 1: axis not owned
    dict(id=1,
         prereg=prereg([("C1", [("axis", "freshness"),
                                ("surface-class", "bookkeeping-file"),
                                ("enumerate", "the markers")]),
                        ("C2", [("axis", "calibration"),
                                ("surface-class", "bookkeeping-file"),
                                ("enumerate", "the files")])]),
         rc=1, min_flags=1, rule="R1"),
    # 2: owned axis + consistent surface-class
    dict(id=2,
         prereg=prereg([("C1", [("axis", "coverage"),
                                ("surface-class", "fixture-expansion"),
                                ("enumerate", "the cases")]),
                        ("C2", [("axis", "calibration"),
                                ("surface-class", "bookkeeping-file"),
                                ("enumerate", "the files")])]),
         rc=0, min_flags=0, rule=None),
    # 3: surface-class mismatch
    dict(id=3,
         prereg=prereg([("C1", [("axis", "calibration"),
                                ("surface-class", "fixture-expansion"),
                                ("enumerate", "the cases")]),
                        ("C2", [("axis", "calibration"),
                                ("surface-class", "bookkeeping-file"),
                                ("enumerate", "the files")])]),
         rc=1, min_flags=1, rule="R2"),
    # 4: no claim on lowest axis
    dict(id=4,
         prereg=prereg([("C1", [("axis", "coverage"),
                                ("surface-class", "fixture-expansion"),
                                ("enumerate", "the cases")]),
                        ("C2", [("axis", "operability"),
                                ("surface-class", "instrument-acquisition"),
                                ("enumerate", "the tool")])]),
         rc=1, min_flags=1, rule="R3"),
    # 5: multi-claim, wrong rule applied (lowest axis absent again)
    dict(id=5,
         prereg=prereg([("C1", [("axis", "coverage"),
                                ("surface-class", "fixture-expansion"),
                                ("enumerate", "c1")]),
                        ("C2", [("axis", "operability"),
                                ("surface-class", "instrument-acquisition"),
                                ("enumerate", "c2")]),
                        ("C3", [("axis", "coverage"),
                                ("surface-class", "knowledge-entry"),
                                ("enumerate", "c3")])]),
         rc=1, min_flags=1, rule="R3"),
    # 6: multi-claim, right rule
    dict(id=6,
         prereg=prereg([("C1", [("axis", "coverage"),
                                ("surface-class", "fixture-expansion"),
                                ("enumerate", "c1")]),
                        ("C2", [("axis", "calibration"),
                                ("surface-class", "bookkeeping-file"),
                                ("enumerate", "c2")]),
                        ("C3", [("axis", "coverage"),
                                ("surface-class", "knowledge-entry"),
                                ("enumerate", "c3")])]),
         rc=0, min_flags=0, rule=None),
    # 7: missing enumerate
    dict(id=7,
         prereg=prereg([("C1", [("axis", "calibration"),
                                ("surface-class", "bookkeeping-file")]),
                        ("C2", [("axis", "calibration"),
                                ("surface-class", "bookkeeping-file"),
                                ("enumerate", "c2")])]),
         rc=1, min_flags=1, rule="R4"),
    # 8: enumerate containing universal quantifier
    dict(id=8,
         prereg=prereg([("C1", [("axis", "calibration"),
                                ("surface-class", "bookkeeping-file"),
                                ("enumerate", "all of the marker lines")]),
                        ("C2", [("axis", "calibration"),
                                ("surface-class", "bookkeeping-file"),
                                ("enumerate", "the notes")])]),
         rc=1, min_flags=1, rule="R4"),
    # 9: consistent surface-class under each axis (R2 allows one per claim)
    dict(id=9,
         prereg=prereg([("C1", [("axis", "operability"),
                                ("surface-class", "instrument-acquisition"),
                                ("enumerate", "the tools")]),
                        ("C2", [("axis", "calibration"),
                                ("surface-class", "bookkeeping-file"),
                                ("enumerate", "the files")])]),
         rc=0, min_flags=0, rule=None),
    # 10: multi-surface claim (two surface-class lines; both neutral/consistent)
    dict(id=10,
         prereg=prereg([("C1", [("axis", "coverage"),
                                ("surface-class", "knowledge-entry"),
                                ("surface-class", "receipt-binding"),
                                ("enumerate", "the entry and its receipt")]),
                        ("C2", [("axis", "calibration"),
                                ("surface-class", "bookkeeping-file"),
                                ("enumerate", "the files")])]),
         rc=0, min_flags=0, rule=None),
    # 11: malformed prereg — claim without axis line
    dict(id=11,
         prereg=prereg([("C1", [("surface-class", "bookkeeping-file"),
                                ("enumerate", "the files")])]),
         rc=2, min_flags=0, rule=None),
]


def run_case(case, tmpdir, tool):
    ppath = os.path.join(tmpdir, f"prereg-{case['id']}.txt")
    spath = os.path.join(tmpdir, "scorecard.txt")
    open(ppath, "w").write(case["prereg"])
    if not os.path.exists(spath):
        open(spath, "w").write(SCORECARD)
    p = subprocess.run([sys.executable, tool, "--prereg", ppath, "--scorecard", spath],
                       capture_output=True, text=True)
    out = p.stdout + p.stderr
    m = re.search(r"flags=(\d+)", out)
    nflags = int(m.group(1)) if m else 0
    flag_lines = [l for l in out.splitlines() if l.startswith("FLAG ")]
    ok = p.returncode == case["rc"]
    if case["rc"] == 0:
        ok = ok and nflags == 0
    elif case["rc"] == 1:
        ok = ok and nflags >= case["min_flags"]
        if case["rule"]:
            ok = ok and any(case["rule"] in l for l in flag_lines)
    else:  # rc2 refusal: no flags expected
        ok = ok and nflags == 0
    return ok, p.returncode, nflags, flag_lines


def main() -> int:
    stub = "--stub" in sys.argv
    tool = TOOL
    with tempfile.TemporaryDirectory(prefix="souji-r26-axischeck.") as td:
        if stub:
            tool = os.path.join(td, "stub.py")
            open(tool, "w").write(
                "import sys\np=sys.argv[sys.argv.index('--prereg')+1]\n"
                "n=open(p).read().count('CLAIM ')\n"
                "print(f'claims={n} flags=0')\nsys.exit(0)\n")
        npass = 0
        for case in CASES:
            ok, rc, nf, fl = run_case(case, td, tool)
            tag = "PASS" if ok else "FAIL"
            if ok:
                npass += 1
            print(f"case={case['id']} expected_rc={case['rc']} rc={rc} flags={nf} verdict={tag}")
        print(f"cases={len(CASES)} pass={npass}")
        if stub:
            print("control=" + ("FALSE-GREEN-REJECTED" if npass < len(CASES) else "FALSE-GREEN-ACCEPTED"))
        return 0 if (npass == len(CASES) and not stub) else 1


if __name__ == "__main__":
    sys.exit(main())
