#!/usr/bin/env python3
"""tests/fixtures/r26-axis-check.py — round-26 C3 falsification fixture.

CLI:
  python3 -B tests/fixtures/r26-axis-check.py --tool PATH

Target (frozen contract, round-26 preregistration C3):
  python3 tools/souji-axis-check.py --prereg PATH --scorecard PATH
  parses the `## MACHINE BLOCK` section only; CLAIM blocks carry `axis:`,
  `surface-class:` and `enumerate:` lines; stdout `claims=C flags=F` plus one
  `FLAG <claim> <rule> <detail>` per finding; exit 0 iff F=0, 1 on flags,
  2 on usage/malformed input.

The twelve frozen cases (no case may be dropped or re-specified):
   1  r25-C2 replica: fixture-expansion declared on operability is flagged
      (discriminator: the always-green stub must NOT flag it -> case fails)
   2  well-formed 3-claim prereg -> 0 flags, exit 0
   3  R1: declared axis outside the owned set is flagged
   4  R2: fixture-expansion on operability is flagged
   5  R2: bookkeeping-file on coverage is flagged
   6  R2: instrument-acquisition on calibration is flagged
   7  R3: no claim declares the lowest-scoring axis is flagged
   8  R4: universal clause without an `enumerate:` line is flagged
   9  R4: universal clause WITH an `enumerate:` line passes
  10  well-formed claim carrying surface-class + enumerate lines passes
  11  malformed prereg (claim missing its `axis:` line) -> exit 2, no FLAG lines
  12  control arm: a stub that always prints `claims=1 flags=0` must be
      rejected (FALSE-GREEN-ACCEPTED arm), case 1 included

Output: one `CASE <n> <name> PASS|FAIL <detail>` line per case, then the last
line `cases=12 pass=<P> control=FALSE-GREEN-REJECTED|FALSE-GREEN-ACCEPTED`.
Exit 0 iff P==12 AND the control spelling is FALSE-GREEN-REJECTED.

Every case owns an isolated world under /var/tmp/souji-r26-ExecAxisFixture/
(a fresh run directory per invocation), removed in a finally block. Nothing is
executed against the lane's real preregistration or SCORECARD.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys

SCRATCH_BASE = "/var/tmp/souji-r26-ExecAxisFixture"
SCRATCH_PREFIX = "/var/tmp/souji-r26-"

# Synthetic axes table mirroring the lane's round-26 declarations
# (calibration 7 lowest non-retired, operability 8, coverage 8). Case 1 is
# deliberately paired with this table so the r25-C2 shape is flagged.
SCORECARD = """\
# synthetic SCORECARD for round-26 C3 fixture cases (not lane data)

## Axes

| axis | score | verdict / observation | counting command | measured commit | last change |
|---|---|---|---|---|---|
| calibration | 7 | synthetic row: lowest non-retired axis | n/a | synthetic | n/a |
| operability | 8 | synthetic row | n/a | synthetic | n/a |
| coverage | 8 | synthetic row | n/a | synthetic | n/a |

## Retired

None.
"""

# Case 1 world: the round-25 C2 claim reconstructed from the committed
# round-25 preregistration (6e4737ea:.ufo/waves/round-25/preregistration.txt):
# a fixture-expansion move declared on the frozen operability axis.
R25C2_REPLICA = """\
Souji round 25 C2 replica — synthetic prereg for round-26 C3 fixture case 1
(synthetic; not lane data). Round-25 lanes: calibration 7 (lowest), operability 8,
coverage 8.

## MACHINE BLOCK
CLAIM C2
axis: operability
surface-class: fixture-expansion
enumerate: python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py
END

=====================================================================
CLAIM C2 — operability (8). Size-census refusal surfaces covered by the
frozen fixture.
Declared axis: operability. Surface class: fixture-expansion (test-fixture
edge classes only, no runnable entry-command behaviour change).
"""

STUB_SOURCE = '''\
#!/usr/bin/env python3
"""Always-green stub: prints claims=1 flags=0 and exits 0 for any input."""
import sys

sys.argv = sys.argv[:1]
print("claims=1 flags=0")
raise SystemExit(0)
'''

COUNT_RE = re.compile(r"^claims=(\d+)\s+flags=(\d+)\s*$", re.M)
FLAG_RE = re.compile(r"^FLAG\s+(\S+)\s+(R\d+)\b", re.M)


def synth(claims, note="synthetic fixture prereg"):
    """Build a synthetic preregistration holding only a MACHINE BLOCK."""
    out = [f"Souji round 26 C3 fixture — {note} (synthetic; not lane data).", ""]
    out.append("## MACHINE BLOCK")
    for cid, lines in claims:
        out.append(f"CLAIM {cid}")
        out.extend(lines)
    out.append("END")
    out.append("")
    return "\n".join(out)


CASES = [
    {
        "n": 1,
        "name": "r25-c2-replica-fixture-expansion-on-operability",
        "prereg": R25C2_REPLICA,
        "expect": {"rc": 1, "claims": 1, "min_flags": 1, "must_rules": {"R2"}},
    },
    {
        "n": 2,
        "name": "wellformed-3claim",
        "prereg": synth(
            [
                ("C1", ["axis: calibration", "surface-class: bookkeeping-file",
                        "enumerate: bash census/round-26/c1-counter.sh"]),
                ("C2", ["axis: coverage", "surface-class: knowledge-entry",
                        "enumerate: bash census/round-26/c2-counter.sh"]),
                ("C3", ["axis: operability", "surface-class: instrument-acquisition",
                        "enumerate: bash census/round-26/c3-counter.sh"]),
            ]
        ),
        "expect": {"rc": 0, "claims": 3, "flags": 0},
    },
    {
        "n": 3,
        "name": "r1-axis-not-owned",
        "prereg": synth(
            [
                ("C1", ["axis: quality", "surface-class: measurement",
                        "enumerate: bash census/round-26/c1-counter.sh"]),
                ("C2", ["axis: calibration", "surface-class: bookkeeping-file",
                        "enumerate: bash census/round-26/c1-counter.sh"]),
            ]
        ),
        "expect": {"rc": 1, "claims": 2, "min_flags": 1, "must_rules": {"R1"}, "exact_rules": True},
    },
    {
        "n": 4,
        "name": "r2-fixture-expansion-on-operability",
        "prereg": synth(
            [
                ("C1", ["axis: calibration", "surface-class: bookkeeping-file",
                        "enumerate: bash census/round-26/c1-counter.sh"]),
                ("C2", ["axis: operability", "surface-class: fixture-expansion",
                        "enumerate: bash census/round-26/c3-counter.sh"]),
            ]
        ),
        "expect": {"rc": 1, "claims": 2, "min_flags": 1, "must_rules": {"R2"}, "exact_rules": True},
    },
    {
        "n": 5,
        "name": "r2-bookkeeping-file-on-coverage",
        "prereg": synth(
            [
                ("C1", ["axis: calibration", "surface-class: bookkeeping-file",
                        "enumerate: bash census/round-26/c1-counter.sh"]),
                ("C2", ["axis: coverage", "surface-class: bookkeeping-file",
                        "enumerate: bash census/round-26/c2-counter.sh"]),
            ]
        ),
        "expect": {"rc": 1, "claims": 2, "min_flags": 1, "must_rules": {"R2"}, "exact_rules": True},
    },
    {
        "n": 6,
        "name": "r2-instrument-acquisition-on-calibration",
        "prereg": synth(
            [
                ("C1", ["axis: calibration", "surface-class: bookkeeping-file",
                        "enumerate: bash census/round-26/c1-counter.sh"]),
                ("C2", ["axis: calibration", "surface-class: instrument-acquisition",
                        "enumerate: bash census/round-26/c3-counter.sh"]),
            ]
        ),
        "expect": {"rc": 1, "claims": 2, "min_flags": 1, "must_rules": {"R2"}, "exact_rules": True},
    },
    {
        "n": 7,
        "name": "r3-no-claim-on-lowest-axis",
        "prereg": synth(
            [
                ("C1", ["axis: operability", "surface-class: measurement",
                        "enumerate: bash census/round-26/c3-counter.sh"]),
                ("C2", ["axis: coverage", "surface-class: measurement",
                        "enumerate: bash census/round-26/c2-counter.sh"]),
            ]
        ),
        "expect": {"rc": 1, "claims": 2, "min_flags": 1, "must_rules": {"R3"}, "exact_rules": True},
    },
    {
        "n": 8,
        "name": "r4-universal-clause-without-enumerate",
        "prereg": synth(
            [
                ("C1", ["axis: calibration", "surface-class: bookkeeping-file",
                        "text: every bookkeeping counter is complete"]),
            ]
        ),
        "expect": {"rc": 1, "claims": 1, "min_flags": 1, "must_rules": {"R4"}, "exact_rules": True},
    },
    {
        "n": 9,
        "name": "r4-universal-clause-with-enumerate",
        "prereg": synth(
            [
                ("C1", ["axis: calibration", "surface-class: bookkeeping-file",
                        "text: every bookkeeping counter is complete",
                        "enumerate: bash census/round-26/c1-counter.sh"]),
            ]
        ),
        "expect": {"rc": 0, "claims": 1, "flags": 0},
    },
    {
        "n": 10,
        "name": "wellformed-surface-class-and-enumerate",
        "prereg": synth(
            [
                ("C1", ["axis: calibration", "surface-class: measurement",
                        "enumerate: bash census/round-26/c1-counter.sh"]),
            ]
        ),
        "expect": {"rc": 0, "claims": 1, "flags": 0},
    },
    {
        "n": 11,
        "name": "malformed-missing-axis-line",
        "prereg": synth(
            [
                ("C1", ["surface-class: measurement",
                        "enumerate: bash census/round-26/c1-counter.sh"]),
            ]
        ),
        "expect": {"rc": 2, "refuse": True},
    },
]


def parse_counts(out):
    m = COUNT_RE.search(out)
    return (int(m.group(1)), int(m.group(2))) if m else None


def parse_flags(out):
    return [(m.group(1), m.group(2)) for m in FLAG_RE.finditer(out)]


def one_line(text, limit=160):
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def evaluate(expect, rc, out, err):
    """Return (ok, detail). Detail always names what the tool actually did."""
    problems = []
    flags = parse_flags(out)
    counts = parse_counts(out)
    rules = sorted({rule for _, rule in flags})

    if rc != expect["rc"]:
        problems.append(f"rc={rc} expected {expect['rc']}")

    if expect.get("refuse"):
        if flags:
            problems.append(f"refusal printed {len(flags)} FLAG line(s)")
    else:
        if counts is None:
            problems.append("missing `claims=C flags=F` line")
        else:
            claims, nflags = counts
            if "claims" in expect and claims != expect["claims"]:
                problems.append(f"claims={claims} expected {expect['claims']}")
            if "flags" in expect and nflags != expect["flags"]:
                problems.append(f"flags={nflags} expected {expect['flags']}")
            if nflags != len(flags):
                problems.append(f"counts line flags={nflags} but {len(flags)} FLAG line(s)")
        if "min_flags" in expect and len(flags) < expect["min_flags"]:
            problems.append(f"{len(flags)} FLAG line(s), expected >={expect['min_flags']}")
        gap = sorted(expect.get("must_rules", set()) - set(rules))
        if gap:
            problems.append(f"missing rule(s) {','.join(gap)}; saw {','.join(rules) or '-'}")
        if expect.get("exact_rules") and set(rules) != set(expect.get("must_rules", set())):
            problems.append(f"rules {','.join(rules) or '-'} != {'/'.join(sorted(expect['must_rules']))}")
        if expect.get("flags") == 0 and flags:
            problems.append(f"clean case printed {len(flags)} FLAG line(s)")

    detail = (
        f"rc={rc} claims={counts[0] if counts else '-'} "
        f"flags={counts[1] if counts else '-'} rules={','.join(rules) or '-'}"
    )
    if problems:
        detail += " | " + "; ".join(problems)
        if err.strip():
            detail += f" | stderr={one_line(err, 100)}"
    return (not problems), detail


def run_tool(tool, case_dir, prereg_path, scorecard_path):
    cmd = [sys.executable or "python3", "-B", tool,
           "--prereg", prereg_path, "--scorecard", scorecard_path]
    try:
        proc = subprocess.run(cmd, cwd=case_dir, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return 124, "", "timeout after 120s"
    return proc.returncode, proc.stdout, proc.stderr


def write_case(run_dir, case, scorecard_path):
    case_dir = os.path.join(run_dir, f"case-{case['n']:02d}")
    os.makedirs(case_dir, exist_ok=True)
    prereg_path = os.path.join(case_dir, "prereg.txt")
    with open(prereg_path, "w", encoding="utf-8") as fh:
        fh.write(case["prereg"])
    return case_dir, prereg_path, scorecard_path


def main() -> int:
    ap = argparse.ArgumentParser(prog="r26-axis-check.py")
    ap.add_argument("--tool", required=True, help="path to tools/souji-axis-check.py")
    args = ap.parse_args()

    tool = os.path.abspath(args.tool)
    if not os.path.isfile(tool):
        print(f"r26-axis-check: tool not found: {args.tool}", file=sys.stderr)
        return 2

    if not SCRATCH_BASE.startswith(SCRATCH_PREFIX) or os.path.islink(SCRATCH_BASE):
        print(f"r26-axis-check: unsafe scratch base {SCRATCH_BASE}", file=sys.stderr)
        return 2
    if os.path.exists(SCRATCH_BASE) and not os.path.isdir(SCRATCH_BASE):
        print(f"r26-axis-check: scratch base is not a directory: {SCRATCH_BASE}", file=sys.stderr)
        return 2

    os.makedirs(SCRATCH_BASE, exist_ok=True)
    run_dir = os.path.join(SCRATCH_BASE, f"run-{os.getpid()}")
    suffix = 0
    while os.path.exists(run_dir):
        suffix += 1
        run_dir = os.path.join(SCRATCH_BASE, f"run-{os.getpid()}-{suffix}")
    os.makedirs(run_dir)

    passed = 0
    try:
        scorecard_path = os.path.join(run_dir, "scorecard.txt")
        with open(scorecard_path, "w", encoding="utf-8") as fh:
            fh.write(SCORECARD)

        worlds = []
        for case in CASES:
            case_dir, prereg_path, scorecard = write_case(run_dir, case, scorecard_path)
            rc, out, err = run_tool(tool, case_dir, prereg_path, scorecard)
            ok, detail = evaluate(case["expect"], rc, out, err)
            worlds.append({"case": case, "dir": case_dir, "prereg": prereg_path,
                           "scorecard": scorecard, "ok": ok, "detail": detail})
            passed += 1 if ok else 0
            print(f"CASE {case['n']} {case['name']} {'PASS' if ok else 'FAIL'} {detail}")

        # Case 12 — control arm: the always-green stub is run against every
        # generated world. It may not pass case 1 (the r25-C2 discriminator).
        case12_dir = os.path.join(run_dir, "case-12")
        os.makedirs(case12_dir, exist_ok=True)
        stub = os.path.join(case12_dir, "souji-axis-check-stub.py")
        with open(stub, "w", encoding="utf-8") as fh:
            fh.write(STUB_SOURCE)
        stub_ok = []
        for world in worlds:
            rc, out, err = run_tool(stub, case12_dir, world["prereg"], world["scorecard"])
            ok, _ = evaluate(world["case"]["expect"], rc, out, err)
            stub_ok.append(ok)
        stub_passed = sum(1 for ok in stub_ok if ok)
        discriminator = not stub_ok[0]
        control = ("FALSE-GREEN-REJECTED"
                   if stub_passed < len(worlds) and discriminator
                   else "FALSE-GREEN-ACCEPTED")
        case12_ok = control == "FALSE-GREEN-REJECTED" and discriminator
        detail = (f"stub_passed={stub_passed}/{len(worlds)} "
                  f"discriminator={'PASS' if discriminator else 'FAIL'} "
                  f"control={control}")
        passed += 1 if case12_ok else 0
        print(f"CASE 12 control-always-green-stub {'PASS' if case12_ok else 'FAIL'} {detail}")

        total = len(worlds) + 1
        print(f"cases={total} pass={passed} control={control}")
        return 0 if passed == total and control == "FALSE-GREEN-REJECTED" else 1
    finally:
        shutil.rmtree(run_dir, ignore_errors=True)
        try:
            os.rmdir(SCRATCH_BASE)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
