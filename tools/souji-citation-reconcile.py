#!/usr/bin/env python3
"""souji-citation-reconcile.py — r37 C1 self-assessment citation reconciler.

The r36 non-author spot-check routed one calibration defect class: cells in the
lane's own self-assessment (SCORECARD.md claim and capability rows, the SKILL
gate registry, the round lesson's Claims section, the frozen preregistration
sentence) quote after-values that never lived in any committed receipt
(`cases=11`/`cases=9`/`cases=20`/`selftest 8` against receipts reading
21/12/9), and their measured-commit cells name a commit where the cited
receipt does not exist.

This counter re-derives one register row per routed cell over committed bytes
only. A row binds when, at the audit revision:

  citation  exactly one line of the named file contains the row's `anchor`;
            that line contains `expected` and does not contain `stale`;
  receipt   the receipt blob at `receipt_rev` contains `expected`.

Register schema (TSV, one row per cell, header line required):

  id<TAB>file<TAB>anchor<TAB>expected<TAB>stale<TAB>receipt<TAB>receipt_rev

`stale` may be `-` (no stale token). `receipt_rev` is a full 40-hex revision.
An append-only correction row is written as a line carrying the row's `id` as
its anchor plus the receipt-backed value; the stale measurement row itself is
never rewritten.

CLI:
  python3 -B tools/souji-citation-reconcile.py --root LANE --rev REV --register TSV

Exit: 0 mismatches=0, 1 any mismatch (one MISMATCH line each), 2 usage /
malformed register / unresolvable revision. Read-only: git show only, no
working-tree reads, no writes.
"""
import argparse
import re
import subprocess
import sys

FIELDS = ("id", "file", "anchor", "expected", "stale", "receipt", "receipt_rev")
REV = re.compile(r"^[0-9a-f]{40}$")


def git_show(root, rev, path):
    proc = subprocess.run(
        ["git", "-C", root, "show", "%s:%s" % (rev, path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8", "replace")


def parse_register(path):
    try:
        raw = open(path, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        raise SystemExit("usage: unreadable register %s: %s" % (path, exc))
    rows = []
    for lineno, line in enumerate(raw.splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if parts == list(FIELDS):
            continue
        if len(parts) != len(FIELDS):
            raise SystemExit("usage: register line %d has %d fields, expected %d" % (lineno, len(parts), len(FIELDS)))
        row = dict(zip(FIELDS, parts))
        if not REV.match(row["receipt_rev"]):
            raise SystemExit("usage: register line %d receipt_rev is not 40-hex" % lineno)
        rows.append(row)
    if not rows:
        raise SystemExit("usage: register has no rows")
    return rows


def run(args):
    root = args.root
    if not REV.match(args.rev):
        sys.stderr.write("REFUSAL USAGE: --rev must be 40-hex\n")
        return 2
    rows = parse_register(args.register)
    mismatches = 0
    for row in rows:
        text = git_show(root, args.rev, row["file"])
        if text is None:
            print("MISMATCH %s FILE-ABSENT %s at %s" % (row["id"], row["file"], args.rev))
            mismatches += 1
        else:
            hits = [l for l in text.splitlines() if row["anchor"] in l]
            if len(hits) != 1:
                print("MISMATCH %s ANCHOR-COUNT %s anchor=%r hits=%d" % (row["id"], row["file"], row["anchor"], len(hits)))
                mismatches += 1
            elif row["expected"] not in hits[0]:
                print("MISMATCH %s EXPECTED-MISSING %s expected=%r" % (row["id"], row["file"], row["expected"]))
                mismatches += 1
            elif row["stale"] != "-" and row["stale"] in hits[0]:
                print("MISMATCH %s STALE-PRESENT %s stale=%r" % (row["id"], row["file"], row["stale"]))
                mismatches += 1
        receipt = git_show(root, row["receipt_rev"], row["receipt"])
        if receipt is None:
            print("MISMATCH %s RECEIPT-ABSENT %s at %s" % (row["id"], row["receipt"], row["receipt_rev"]))
            mismatches += 1
        elif row["expected"] not in receipt:
            print("MISMATCH %s RECEIPT-DISAGREES %s expected=%r" % (row["id"], row["receipt"], row["expected"]))
            mismatches += 1
    print("SUMMARY cells=%d mismatches=%d" % (len(rows), mismatches))
    return 0 if mismatches == 0 else 1


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--register", required=True)
    args = ap.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
