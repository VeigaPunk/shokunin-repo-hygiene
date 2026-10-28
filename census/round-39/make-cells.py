#!/usr/bin/env python3
"""census/round-39/make-cells.py — emit the round-39 citation register and its anchored lines.

The r38 limit this register answers: "all ten register rows carry `commit == receipt_rev`, so the
live register cannot distinguish the commit arm from the receipt arm". Every row here names a
`commit` strictly later than its `receipt_rev`, and the anchored line that quotes it names that
commit.

Usage (from the lane root):
  python3 -B census/round-39/make-cells.py --commit <40hex> --late <40hex-of-c2-c3-receipts> \
      --freeze <40hex-of-control-receipts> [--write]

`--write` writes `census/round-39/cells.tsv` and appends the six anchored lines to
`census/round-39/cells-lines.md` (which the L1 copies into SCORECARD.md, LOG.md and
corpus/QUALITY.md — the register binds the line inside the named file, so the anchors must live
there, not in this generator's output).
"""
import argparse
import os
import re
import sys

ROWS = (
    # id, file, anchor, expected, stale, receipt, receipt_rev_key
    ("REG-01", "SCORECARD.md", "R39-REG-01", "legs=6", "legs=2", "census/round-39/records/c2-after.txt", "late"),
    ("REG-02", "SCORECARD.md", "R39-REG-02", "harm=0", "harm=3", "census/round-39/records/c2-after.txt", "late"),
    ("REG-03", "SCORECARD.md", "R39-REG-03", "fail=0", "fail=4", "census/round-39/records/c2-after.txt", "late"),
    ("REG-04", "LOG.md", "R39-REG-04", "killed=4", "killed=1", "census/round-39/records/c3-after.txt", "late"),
    ("REG-05", "LOG.md", "R39-REG-05", "cases=7", "cases=9", "census/round-39/records/c3-after.txt", "late"),
    ("REG-06", "corpus/QUALITY.md", "R39-REG-06", "open=16", "open=1", "census/round-39/records/c1-before.txt", "freeze"),
)

LINE = (
    "{anchor} — the `{expected}` field of `{receipt}` (receipt_rev {short_rev}, re-verified at "
    "{short_commit}); the stale reading `{stale}` belongs to the pre-repair bytes."
)


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--late", required=True)
    ap.add_argument("--freeze", required=True)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    for flag, rev in (("--commit", args.commit), ("--late", args.late), ("--freeze", args.freeze)):
        if not re.match(r"^[0-9a-f]{40}$", rev):
            sys.stderr.write("usage: %s must be 40-hex\n" % flag)
            return 2
    revs = {"late": args.late, "freeze": args.freeze}
    table = ["id\tfile\tanchor\texpected\tstale\treceipt\treceipt_rev\tcommit"]
    lines = []
    for rid, path, anchor, expected, stale, receipt, key in ROWS:
        table.append("\t".join((rid, path, anchor, expected, stale, receipt, revs[key], args.commit)))
        lines.append(LINE.format(anchor=anchor, expected=expected, receipt=receipt,
                                 short_rev=revs[key][:7], short_commit=args.commit[:7], stale=stale))
    text = "\n".join(table) + "\n"
    if args.write:
        with open("census/round-39/cells.tsv", "w", encoding="utf-8") as handle:
            handle.write(text)
        with open("census/round-39/cells-lines.md", "w", encoding="utf-8") as handle:
            handle.write("\n\n".join(lines) + "\n")
        print("wrote census/round-39/cells.tsv (%d rows) and census/round-39/cells-lines.md" % len(ROWS))
    else:
        sys.stdout.write(text)
        sys.stdout.write("\n" + "\n\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
