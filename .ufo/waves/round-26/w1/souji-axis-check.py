#!/usr/bin/env python3
"""souji-axis-check.py — preregistration axis-of-surface checker (round 26 C3).

CLI:
  python3 tools/souji-axis-check.py --prereg PATH --scorecard PATH

Parses the preregistration's `## MACHINE BLOCK` section only (the marker line
through the terminating `END` line). Each `CLAIM <id>` block carries `axis:`,
`surface-class:` and optional `enumerate:` lines. Read-only; no writes.

Rules, checked in order:
  R1  every declared axis is one of the lane's owned, non-retired axes:
      calibration, operability, coverage.
  R2  axis/surface-class consistency: fixture-expansion only on coverage;
      bookkeeping-file only on calibration; knowledge-entry and registry-append
      only on coverage; instrument-acquisition only on operability.
      receipt-binding and measurement are neutral; unknown classes are neutral.
  R3  at least one claim declares the lowest-scoring non-retired axis of the
      SCORECARD axes table (rows `| <axis> | <score> | ...`; rows inside a
      `## Retired` section or carrying `retired` are skipped).
  R4  a claim block containing a whole-word all/every/complete/none/no without
      an `enumerate:` line in the same block is flagged.

stdout: `claims=<C> flags=<F>` then one `FLAG <claim> <rule> <detail>` line per
finding. Exit 0 iff F == 0; 1 on any flag; 2 on usage or malformed input. A
refusal prints a stderr reason and no FLAG lines.

Frozen contract: .ufo/waves/round-26/preregistration.txt (claim C3).
"""
from __future__ import annotations

import argparse
import re
import sys

OWNED_AXES = ("calibration", "operability", "coverage")

# surface-class -> the one axis it may be declared on
SURFACE_AXIS = {
    "fixture-expansion": "coverage",
    "bookkeeping-file": "calibration",
    "knowledge-entry": "coverage",
    "registry-append": "coverage",
    "instrument-acquisition": "operability",
}
NEUTRAL_SURFACES = frozenset({"receipt-binding", "measurement"})

UNIVERSAL_RE = re.compile(r"\b(all|every|complete|none|no)\b", re.IGNORECASE)
SPLIT_RE = re.compile(r"\s*[+,/]\s*")
CLAIM_RE = re.compile(r"^CLAIM\s+(\S+)\s*$")
AXIS_RE = re.compile(r"^\s*axis\s*:\s*(\S.*?)\s*$")
SURFACE_RE = re.compile(r"^\s*surface-class\s*:\s*(\S.*?)\s*$")
ENUM_RE = re.compile(r"^\s*enumerate\s*:")
BLOCK_RE = re.compile(r"^#{2,}\s*MACHINE\s+BLOCK\b", re.IGNORECASE)
HEADING_RE = re.compile(r"^#{1,6}\s*(.*?)\s*$")
ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|")


class Refusal(Exception):
    """Malformed or unusable input: exit 2 with a stderr reason, no flags."""


def parse_prereg(path: str):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        raise Refusal(f"cannot read prereg {path}: {exc.strerror or exc}") from exc

    start = None
    for i, line in enumerate(lines):
        if BLOCK_RE.match(line):
            start = i + 1
            break
    if start is None:
        raise Refusal(f"no '## MACHINE BLOCK' section in {path}")

    end = None
    for j in range(start, len(lines)):
        if lines[j].strip() == "END":
            end = j
            break
    if end is None:
        raise Refusal(f"MACHINE BLOCK in {path} is not terminated by an 'END' line")

    claims = []
    current = None
    for line in lines[start:end]:
        m = CLAIM_RE.match(line.strip())
        if m:
            current = {"id": m.group(1), "axis": None, "surfaces": [],
                       "enumerate": False, "text": [line]}
            claims.append(current)
            continue
        if current is None:
            # prose between the marker and the first CLAIM is not a claim block
            continue
        current["text"].append(line)
        if ENUM_RE.match(line):
            current["enumerate"] = True
            continue
        m = AXIS_RE.match(line)
        if m and current["axis"] is None:
            current["axis"] = m.group(1).strip().lower()
            continue
        m = SURFACE_RE.match(line)
        if m:
            for token in SPLIT_RE.split(m.group(1).strip().lower()):
                if token:
                    current["surfaces"].append(token)

    for claim in claims:
        if not claim["axis"]:
            raise Refusal(f"CLAIM {claim['id']} declares no 'axis:' line")
    return claims


def parse_scores(path: str):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        raise Refusal(f"cannot read scorecard {path}: {exc.strerror or exc}") from exc

    window = lines
    for i, line in enumerate(lines):
        if re.match(r"^#{2,}\s*Axes\b", line, re.IGNORECASE):
            window = lines[i + 1:]
            for j, candidate in enumerate(window):
                if candidate.startswith("#"):
                    window = window[:j]
                    break
            break

    rows = {}
    retired = False
    for line in window:
        heading = HEADING_RE.match(line)
        if heading:
            retired = "retired" in heading.group(1).lower()
            continue
        if retired or "retired" in line.lower():
            continue
        m = ROW_RE.match(line)
        if not m:
            continue
        axis = m.group(1).strip().lower()
        if not axis or axis == "axis":
            continue
        rows.setdefault(axis, int(m.group(2)))

    if not rows:
        raise Refusal(f"no parseable axes table rows '| <axis> | <score> |' in {path}")
    return rows


def check(claims, scores):
    flags = []

    # R1 — owned, non-retired axes only
    for claim in claims:
        if claim["axis"] not in OWNED_AXES:
            flags.append((claim["id"], "R1",
                          f"axis={claim['axis']} not in "
                          f"{{{','.join(OWNED_AXES)}}}"))

    # R2 — axis/surface-class consistency
    for claim in claims:
        for surface in claim["surfaces"]:
            if surface in NEUTRAL_SURFACES or surface not in SURFACE_AXIS:
                continue
            required = SURFACE_AXIS[surface]
            if claim["axis"] != required:
                flags.append((claim["id"], "R2",
                              f"surface-class={surface} requires axis={required} "
                              f"(declared axis={claim['axis']})"))

    # R3 — the lowest-scoring non-retired axis must be declared by >=1 claim
    lowest = min(scores.values())
    targets = sorted(axis for axis, score in scores.items() if score == lowest)
    if not any(claim["axis"] in targets for claim in claims):
        flags.append(("PREREG", "R3",
                      f"lowest_axis={'+'.join(targets)} score={lowest} "
                      f"declared by no claim"))

    # R4 — universal clause without an enumerate: line in the same block
    for claim in claims:
        if claim["enumerate"]:
            continue
        words = []
        for match in UNIVERSAL_RE.finditer("\n".join(claim["text"])):
            word = match.group(1).lower()
            if word not in words:
                words.append(word)
        if words:
            flags.append((claim["id"], "R4",
                          f"universal word(s) {','.join(words)} without an "
                          f"enumerate: line"))
    return flags


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="souji-axis-check.py",
        description="Check preregistered claim axes against declared surface classes.")
    ap.add_argument("--prereg", required=True, metavar="PATH",
                    help="preregistration file carrying a '## MACHINE BLOCK'")
    ap.add_argument("--scorecard", required=True, metavar="PATH",
                    help="SCORECARD file carrying the '| axis | score |' table")
    args = ap.parse_args()

    try:
        claims = parse_prereg(args.prereg)
        scores = parse_scores(args.scorecard)
    except Refusal as exc:
        print(f"souji-axis-check: refused: {exc}", file=sys.stderr)
        return 2

    flags = check(claims, scores)
    for claim, rule, detail in flags:
        print(f"FLAG {claim} {rule} {detail}")
    print(f"claims={len(claims)} flags={len(flags)}")
    return 0 if not flags else 1


if __name__ == "__main__":
    sys.exit(main())
