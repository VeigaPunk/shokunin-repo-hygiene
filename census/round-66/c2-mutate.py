#!/usr/bin/env python3
"""c2-mutate.py — souji round-66 C2 kill-power mutant recipe (M-ENV).

Builds the frozen mutant M-ENV from a writer's bytes: the round-64 GIT_INDEX_FILE refusal block is
deleted (the `if "GIT_INDEX_FILE" in os.environ:` line and the two-line `refuse(f"RECEIPT-INDEX-ENV-SET ...`
call that follows it). Every other byte is unchanged. The recipe refuses (exit 2, nothing written) unless:
  * the anchor block occurs exactly once,
  * the deleted block carries the refusal needle RECEIPT-INDEX-ENV-SET on its call line,
  * the mutant still compiles (py_compile of the mutant bytes).

Usage:  python3 -B census/round-66/c2-mutate.py --writer PATH --out PATH
Exit:   0 mutant written; 2 anchor absent/ambiguous, needle not in the deleted block, or mutant does not compile.
Pure stdlib; writes only --out. Never executes the writer.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
import os

ANCHOR = 'if "GIT_INDEX_FILE" in os.environ:'
NEEDLE = "RECEIPT-INDEX-ENV-SET"


def mutate(src: str) -> str:
    lines = src.splitlines(keepends=True)
    hits = [i for i, line in enumerate(lines) if line.strip() == ANCHOR]
    if len(hits) != 1:
        raise SystemExit(f"c2-mutate: refused: anchor {ANCHOR!r} occurs {len(hits)} times (need exactly 1)")
    i = hits[0]
    block = lines[i:i + 3]
    if NEEDLE not in "".join(block):
        raise SystemExit("c2-mutate: refused: needle RECEIPT-INDEX-ENV-SET not in the deleted block")
    return "".join(lines[:i] + lines[i + 3:])


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="c2-mutate.py")
    ap.add_argument("--writer", required=True)
    ap.add_argument("--out", required=True)
    ns = ap.parse_args(argv)
    if os.path.lexists(ns.out):
        print(f"c2-mutate: refused: out already exists ({ns.out})", file=sys.stderr)
        return 2
    try:
        with open(ns.writer, "r", encoding="utf-8") as f:
            src = f.read()
    except OSError as exc:
        print(f"c2-mutate: refused: cannot read writer: {exc}", file=sys.stderr)
        return 2
    try:
        mutant = mutate(src)
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 2
    fd, tmp = tempfile.mkstemp(prefix="m-env.", suffix=".py", dir=os.path.dirname(os.path.abspath(ns.out)))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(mutant)
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
    print(f"MUTANT M-ENV written {ns.out} removed_lines=3")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
