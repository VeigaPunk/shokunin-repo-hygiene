#!/usr/bin/env python3
"""probe-carry-invariants — deterministic in-memory invariants for Q36.

Loads `tools/souji-landing-gate.py` as a module (no CLI, no repo writes) and
checks, over seeded synthetic STATUS paragraphs:

  1. a complete normalized paragraph always carries;
  2. an unmarked first-physical-line cut never carries (multi-line blocks);
  3. a cut marked with an ellipsis exactly at a physical-line boundary always
     carries;
  4. a cut marked mid-line never carries (boundary and boundary+1 positions
     are excluded: normalization makes those whitespace-equivalent).

This is a probe, not a gate: it reads committed/integrated bytes and prints a
SUMMARY. It never touches the fleet, never signals, and writes nothing.
Exit: 0 all invariants held; 1 a violation; 2 prerequisite.
"""
from __future__ import annotations

import importlib.util
import random
import sys
from pathlib import Path

LANE = Path(__file__).resolve().parents[2]
GATE = LANE / "tools" / "souji-landing-gate.py"
WORDS = ["guarded", "repos", "measured", "and", "the", "remaining", "arm",
         "never", "runs", "under", "a", "bound", "partial", "open"]


def load_gate():
    spec = importlib.util.spec_from_file_location("souji_landing_gate", GATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    if not GATE.is_file():
        print("probe-carry-invariants: prerequisite: %s absent" % GATE,
              file=sys.stderr)
        return 2
    gate = load_gate()
    rng = random.Random(19)
    violations = []
    paragraphs = 400
    midline = 0
    boundary = 0

    def para(n):
        return [" ".join(rng.choice(WORDS) for _ in range(rng.randint(2, 7)))
                for _ in range(n)]

    for _ in range(paragraphs):
        block = ["STATUS: PARTIAL \u2014 " + para(1)[0]] + para(rng.randint(0, 3))
        full = gate.norm_line(" ".join(block))
        if not gate.carries(block, full):
            violations.append(("complete", block))
        if len(block) > 1:
            if gate.carries(block, gate.norm_line(block[0])):
                violations.append(("unmarked", block))
            bounds = set()
            pos = 0
            for line in block[:-1]:
                pos += len(gate.norm_line(line))
                bounds.update({pos, pos + 1})
                pos += 1
            for cut in range(1, len(block)):
                prefix = gate.norm_line(" ".join(block[:cut]))
                end = len(prefix)
                if end in bounds:
                    boundary += 1
                    if not gate.carries(block, prefix + " \u2026"):
                        violations.append(("marked-boundary", cut, block))
            for _ in range(3):
                p = rng.randint(1, max(1, len(full) - 2))
                if p in bounds:
                    continue
                midline += 1
                if gate.carries(block, full[:p] + " \u2026"):
                    violations.append(("midline", p, block))

    print("SUMMARY paragraphs=%d boundary_cuts=%d midline_cuts=%d violations=%d"
          % (paragraphs, boundary, midline, len(violations)))
    for item in violations[:5]:
        print("VIOLATION\t%s" % (item,))
    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
