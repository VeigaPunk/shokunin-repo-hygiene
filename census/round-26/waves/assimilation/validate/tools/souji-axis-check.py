#!/usr/bin/env python3
"""souji-axis-check.py — preregistration axis-of-surface checker (round 26 C3).

CLI:
  python3 tools/souji-axis-check.py --prereg PATH --scorecard PATH

Reads the preregistration's `## MACHINE BLOCK` section only (between the
`## MACHINE BLOCK` marker line and `END`): CLAIM <id> blocks carrying
`axis:`, `surface-class:` and `enumerate:` lines.

Checks:
  R1: every declared axis is one of the lane's owned, non-retired axes.
  R2: axis/surface-class consistency — fixture-expansion only on coverage;
      bookkeeping-file only on calibration; knowledge-entry/registry-append
      only on coverage; instrument-acquisition only on operability.
      Other surface-classes (receipt-binding, measurement) are neutral.
  R3: at least one claim declares the lowest-scoring non-retired axis of
      the SCORECARD axes table.
  R4: a claim block containing a whole-word all/every/complete/none/no
      without an `enumerate:` line in the same block is flagged.

stdout: `claims=C flags=F` plus one `FLAG <claim> <rule> <detail>` per
finding. Exit 0 iff F=0; 1 on any flag; 2 on usage/malformed input.
"""
from __future__ import annotations

import argparse
import re
import sys

OWNED_AXES = ("calibration", "operability", "coverage")

# surface-class -> the single axis it may be declared on
SURFACE_AXIS = {
    "fixture-expansion": "coverage",
    "bookkeeping-file": "calibration",
    "knowledge-entry": "coverage",
    "registry-append": "coverage",
    "instrument-acquisition": "operability",
}
NEUTRAL_SURFACES = {"receipt-binding", "measurement"}

UNIVERSAL_WORDS = ("all", "every", "complete", "none", "no")


def fail2(msg: str) -> int:
    print(f"souji-axis-check: refused: {msg}", file=sys.stderr)
    return 2


def parse_prereg(path: str):
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as exc:
        return None, f"cannot read prereg: {exc}"
    m = re.search(r"^## MACHINE BLOCK.*?\n(.*?)\nEND[ \t]*$", text, re.S | re.M)
    if not m:
        return None, "no `## MACHINE BLOCK ... END` section found"
    block = m.group(1)
    claims = {}
    order = []
    raw = {}
    cur = None
    buf = []
    for line in block.splitlines():
        cm = re.match(r"^CLAIM\s+(\S+)\s*$", line)
        if cm:
            if cur is not None:
                raw[cur] = buf
            cur = cm.group(1)
            claims[cur] = {}
            order.append(cur)
            buf = []
            continue
        if cur is None:
            continue
        buf.append(line)
        kv = re.match(r"^(axis|surface-class|enumerate)\s*:\s*(.+?)\s*$", line)
        if kv:
            claims[cur][kv.group(1)] = kv.group(2)
    if cur is not None:
        raw[cur] = buf
    if not order:
        return None, "MACHINE BLOCK contains no CLAIM blocks"
    for cid in order:
        if "axis" not in claims[cid]:
            return None, f"CLAIM {cid} has no `axis:` line"
    return claims, order, raw, text


def parse_scores(path: str):
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as exc:
        return None, f"cannot read scorecard: {exc}"
    scores = {}
    axes_sec = re.search(r"^## Axes\b(.*?)(?=^## )", text, re.S | re.M)
    if not axes_sec:
        return None, "no `## Axes` section in scorecard"
    for line in axes_sec.group(1).splitlines():
        mm = re.match(r"^\|\s*(\w+)\s*\|\s*(\d+)\s*\|", line)
        if mm and mm.group(1) in OWNED_AXES:
            scores[mm.group(1)] = int(mm.group(2))
    if not scores:
        return None, "no owned-axis score rows parsed from `## Axes`"
    return scores, None


def check(claims, order, scores, raw=None):
    flags = []
    raw = raw or {}
    for cid in order:
        c = claims[cid]
        axis = c.get("axis", "")
        # R1
        if axis not in OWNED_AXES:
            flags.append((cid, "R1", f"axis {axis!r} not in owned axes {OWNED_AXES}"))
        # R2
        sc = c.get("surface-class")
        if sc is None:
            flags.append((cid, "R2", "no `surface-class:` line"))
        elif sc in SURFACE_AXIS and axis in OWNED_AXES and axis != SURFACE_AXIS[sc]:
            flags.append((cid, "R2", f"surface-class {sc!r} declared on {axis!r}; allowed only on {SURFACE_AXIS[sc]!r}"))
        # R4: a whole-word universal quantifier in the claim text without a
        # same-claim `enumerate:` line naming its counting command is flagged.
        if "enumerate" not in c:
            block_text = " ".join(raw.get(cid, []))
            if any(re.search(rf"\b{w}\b", block_text) for w in UNIVERSAL_WORDS):
                flags.append((cid, "R4", "universal quantifier in claim text without `enumerate:` line"))
    # R3
    if scores:
        lowest = min(scores, key=lambda a: scores[a])
        if not any(claims[cid].get("axis") == lowest for cid in order):
            flags.append(("-", "R3", f"no claim declares the lowest-scoring non-retired axis {lowest!r} ({scores})"))
    return flags


def main() -> int:
    ap = argparse.ArgumentParser(prog="souji-axis-check.py")
    ap.add_argument("--prereg", required=True)
    ap.add_argument("--scorecard", required=True)
    args = ap.parse_args()

    claims_out = parse_prereg(args.prereg)
    if claims_out[0] is None:
        return fail2(claims_out[1])
    claims, order, raw, _ = claims_out
    scores_out = parse_scores(args.scorecard)
    if scores_out[0] is None:
        return fail2(scores_out[1])
    scores = scores_out[0]

    flags = check(claims, order, scores, raw)


    for cid, rule, detail in flags:
        print(f"FLAG {cid} {rule} {detail}")
    print(f"claims={len(order)} flags={len(flags)}")
    return 0 if not flags else 1


if __name__ == "__main__":
    sys.exit(main())
