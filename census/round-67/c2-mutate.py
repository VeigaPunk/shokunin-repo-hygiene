#!/usr/bin/env python3
"""c2-mutate.py — souji round-67 C2 counter-mutant recipes (M4 revert kill; M5 enum-weakness kill).

Builds two frozen mutants from the round-67 C2 counter's own bytes. These are COUNTER mutations
(the instrument, not the receipt writer); each demonstrates a guard is real by showing the guard's
removal changes an observable outcome. Every other byte is unchanged.

  * reverted-rule  (round-66 M4 fix kill): the live-marker emission filter falls back to the
    round-65 rule — any uncommented line carrying the bare substring `return` counts as an
    emission path — by replacing `or RETURN_LITERAL.search(raw))` with `or "return" in raw)`.
    Observable outcome: the r67 counter's `--selftest` must FAIL (case
    `m10-s5-assertion-line-not-live` MISMATCHes: its writer stub carries the env needles only on
    `r.returncode` assertion lines, live under the reverted rule). The r66 selftest case
    `m10-returncode-line-not-live` stayed green under the same revert — that vacuity is the M4
    defect these bytes close.
  * enum-weakened  (round-66 M5 kill): the `redirects_closed` requirement drops the cdred marker —
    `"redirects_closed": ("envred", "cdred"),` -> `"redirects_closed": ("envred",),`. Observable
    outcome: the corrected counter run at the pinned r66 state (SKILL.md and writer at
    c13fbb4e1b563a78278ddc14316c20252e9a6d8d, the r67 population) prints `findings=0 verdict=PASS`
    where the unmutated counter prints `findings=1` with `SCOPE-OVERREACH s5` — the finding is
    enumeration-driven, not hardcoded text.

Each recipe refuses (exit 2, nothing written) unless: the anchor occurs exactly once, and the
mutant still compiles (compile() only; no cache file). Usage:

  python3 -B census/round-67/c2-mutate.py --counter census/round-67/c2-counter.py \
      --mutant reverted-rule --out DIR/c2-counter-reverted.py
  python3 -B census/round-67/c2-mutate.py --counter census/round-67/c2-counter.py \
      --mutant enum-weakened --out DIR/c2-counter-enumweak.py

Exit: 0 mutant written; 2 anchor absent/ambiguous, or mutant does not compile.
Pure stdlib; writes only --out. Never executes the counter.
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile

MUTANTS = {
    "reverted-rule": (
        "or RETURN_LITERAL.search(raw))",
        'or "return" in raw)',
    ),
    "enum-weakened": (
        '"redirects_closed": ("envred", "cdred"),',
        '"redirects_closed": ("envred",),',
    ),
}


def mutate(src: str, mutant: str) -> str:
    anchor, replacement = MUTANTS[mutant]
    hits = src.count(anchor)
    if hits != 1:
        raise SystemExit(f"c2-mutate: refused: anchor {anchor!r} occurs {hits} times (need exactly 1)")
    return src.replace(anchor, replacement)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="c2-mutate.py")
    ap.add_argument("--counter", required=True, help="path to the round-67 c2-counter.py bytes")
    ap.add_argument("--mutant", required=True, choices=sorted(MUTANTS))
    ap.add_argument("--out", required=True)
    ns = ap.parse_args(argv)
    if os.path.lexists(ns.out):
        print(f"c2-mutate: refused: out already exists ({ns.out})", file=sys.stderr)
        return 2
    try:
        with open(ns.counter, "r", encoding="utf-8") as f:
            src = f.read()
    except OSError as exc:
        print(f"c2-mutate: refused: cannot read counter: {exc}", file=sys.stderr)
        return 2
    try:
        mutant_src = mutate(src, ns.mutant)
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 2
    fd, tmp = tempfile.mkstemp(prefix=f"c2-{ns.mutant}.", suffix=".py",
                               dir=os.path.dirname(os.path.abspath(ns.out)))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(mutant_src)
        try:
            # compile() alone: byte-compiled output is never written, so no cache file is created.
            with open(tmp, "rb") as f:
                compile(f.read(), tmp, "exec")
        except SyntaxError as exc:
            print(f"c2-mutate: refused: mutant does not compile: {exc}", file=sys.stderr)
            return 2
        os.replace(tmp, ns.out)
        tmp = None
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)
    print(f"MUTANT {ns.mutant} written {ns.out} anchor_replaced=1")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
