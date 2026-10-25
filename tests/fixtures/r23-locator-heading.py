#!/usr/bin/env python3
"""r23-locator-heading.py — Q54 fixture: a Gate's `§ <NAME>` locator must exist in its snapshot.

Reads one or more `corpus/knowledge/*.md` entries, takes every `§ <locator>` token from the
entry's `## Gate` block, resolves the `snapshot:` paths the same block names (relative to
--snapshot-dir), and requires the locator's first word to appear in at least one of them.

Why this predicate: round 22 rejected a candidate on a reason attributed to `§ OPTIONS` in
`man7-mv.1.txt`, a page with no OPTIONS heading — and the lane's own gate accepted it, because
`tools/souji-gate-check.py` checks the locator's *shape*, not its existence. The first word is
the coarsest honest test: `§ OPTIONS --unreachable` resolves on OPTIONS, `§ 設定 gc.auto`
resolves on 設定, `§ 2.1 field table` resolves on 2.1.

  python3 tests/fixtures/r23-locator-heading.py --entries corpus/knowledge/*.md \\
      --snapshot-dir census/round-23/sources [--mutate <entry>=<from>=<to>]

Counts line: `entries=<n> locators=<k> locators_bad=<b>`
Mismatch rows: `LOCATOR-BAD<TAB><entry><TAB><locator><TAB><reason>`
Exit 0 iff b == 0. Read-only; no scratch, no writes.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

LOCATOR_RE = re.compile(r"§\s*([^\s—–,;)\"']+)")
SNAPSHOT_RE = re.compile(r"snapshot:\s*([^\s]+)")


def gate_block(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    inside = False
    for line in lines:
        if line.startswith("## Gate"):
            inside = True
            out.append(line)
            continue
        if inside and line.startswith("## "):
            break
        if inside:
            out.append(line)
    return "\n".join(out)


def snapshot_texts(block: str, snapshot_dir: str) -> dict[str, str]:
    texts: dict[str, str] = {}
    for m in SNAPSHOT_RE.finditer(block):
        rel = m.group(1).rstrip(".,;")
        path = rel if os.path.isabs(rel) else os.path.join(snapshot_dir, os.path.basename(rel))
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                texts[rel] = fh.read()
        except OSError:
            texts[rel] = ""
    return texts


def check(entries: list[str], snapshot_dir: str, mutations: dict[str, tuple[str, str]]) -> tuple[int, int, int]:
    total = 0
    bad = 0
    for entry in entries:
        with open(entry, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        if entry in mutations:
            old, new = mutations[entry]
            text = text.replace(old, new)
        block = gate_block(text)
        snaps = snapshot_texts(block, snapshot_dir)
        if not snaps:
            print(f"LOCATOR-BAD\t{entry}\t-\tGate names no snapshot")
            bad += 1
            continue
        haystack = "\n".join(snaps.values()).lower()
        for m in LOCATOR_RE.finditer(block):
            loc = m.group(1)
            total += 1
            head = loc.strip()
            if head.lower() not in haystack:
                # a hyphenated locator ("no-dangling") resolves on its first segment
                head = loc.split("-")[0].strip()
            if not head or head.lower() not in haystack:
                bad += 1
                print(f"LOCATOR-BAD\t{entry}\t{loc}\t'{head}' appears in none of: "
                      + ",".join(sorted(snaps)))
    return len(entries), total, bad


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Q54 locator-heading fixture")
    ap.add_argument("--entries", nargs="+", default=None)
    ap.add_argument("--snapshot-dir", required=True)
    ap.add_argument("--mutate", action="append", default=[],
                    help="entry=from=to — apply a textual mutation (the r22 mutant)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    mutations: dict[str, tuple[str, str]] = {}
    for spec in args.mutate:
        entry, old, new = spec.split("=", 2)
        mutations[entry] = (old, new)

    if args.selftest:
        return selftest(args.snapshot_dir)
    if not args.entries:
        ap.error("--entries is required unless --selftest is given")

    n, total, bad = check(args.entries, args.snapshot_dir, mutations)
    print(f"entries={n} locators={total} locators_bad={bad}")
    return 0 if bad == 0 else 1


def selftest(snapshot_dir: str) -> int:
    """Two cases: the real entries must pass, the r22 mutant must fail."""
    entries = [os.path.join("corpus", "knowledge", f) for f in
               ("repo-size-census-readonly.md", "count-objects-garbage-readings-r25.md")]
    entries = [e for e in entries if os.path.exists(e)]
    if not entries:
        print("selftest=0/1 (no entries)")
        return 1
    n, total, bad = check(entries, snapshot_dir, {})
    ok_control = bad == 0 and total > 0
    mutant_entry = entries[0]
    with open(mutant_entry, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    first = LOCATOR_RE.search(gate_block(text))
    if first is None:
        print("selftest=0/2 (no locator to mutate)")
        return 1
    old = "§ " + first.group(1)
    n2, total2, bad2 = check([mutant_entry], snapshot_dir, {mutant_entry: (old, "§ ZQXJNOSUCH")})
    ok_mutant = bad2 >= 1
    print(f"case=control locators={total} locators_bad={bad} expect=0")
    print(f"case=mutant locator={old!r}->'§ ZQXJNOSUCH' locators_bad={bad2} expect>=1")
    print(f"selftest={int(ok_control) + int(ok_mutant)}/2")
    return 0 if (ok_control and ok_mutant) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
