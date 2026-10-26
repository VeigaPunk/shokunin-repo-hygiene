#!/usr/bin/env python3
"""Diff the corpus/SOURCES.md registry between two committed revisions.

Both sides are read through `git show <rev>:corpus/SOURCES.md`, so the diff is
over committed bytes, never the lane's worktree (r28 routed defect 1: a receipt
verified against the disk instead of committed bytes).

Rows are selected with the CORPUS.md census regex, using the maintained-parser
tolerance of 0-3 leading ASCII spaces; a row is split on `|` into 11 columns
(NF=13 with the leading indent field and the trailing empty field). Rows are
keyed by id and reported as:

  rows          count before -> after (census regex)
  histograms    tier and status, before and after
  added         ids absent before, with tier/status/kind
  changed       for ids in both revisions, every in-place cell change
  removed       ids absent after (append-only forbids removal)

Append-only rule (SOURCES-CONTRACT-v1, rule 2): only `status`, `recheck` and
`used-by` may change in place. Any other column whose raw bytes differ is
reported with the marker APPEND-ONLY-VIOLATION; a raw difference whose trimmed
values match is marked whitespace-only and is still a violation (the row's
bytes changed). A row whose field count differs between revisions is reported as
SHAPE-VIOLATION.

Usage:
  python3 -B deliver-sources-diff.py --root LANE --from <40-hex> --to <40-hex>
                                     [--width N]

Exit status: 0 clean; 1 append-only/shape violation, duplicate id or malformed
row on either side; 2 usage, git or read error.
"""

import argparse
import re
import subprocess
import sys
from collections import Counter, OrderedDict

SOURCES_PATH = "corpus/SOURCES.md"
COLUMNS = (
    "id", "source", "kind", "tier", "scope", "anchor", "teaches",
    "status", "opened", "recheck", "used-by",
)
MUTABLE = frozenset({"status", "recheck", "used-by"})
TIER_ORDER = ("A", "B", "C")
STATUS_ORDER = ("queued", "mined", "rejected")
REV_RE = re.compile(r"\A[0-9a-fA-F]{40}\Z")
# Same row convention as tools/souji-registry-agreement.py ROW, widened to the
# CORPUS.md census tolerance of 0-3 leading ASCII spaces.
CENSUS_RE = re.compile(r"\A( {0,3})\|\s*(S[0-9]{3,})\s*\|")


def run_git(root, *args):
    proc = subprocess.run(
        ["git", "-C", root, *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def die(msg, code=2):
    sys.stderr.write("error: %s\n" % msg)
    raise SystemExit(code)


def read_rev(root, rev):
    rc, out, err = run_git(root, "show", "%s:%s" % (rev, SOURCES_PATH))
    if rc != 0:
        die("git show %s:%s failed: %s" % (rev, SOURCES_PATH,
                                           err.decode("utf-8", "replace").strip()))
    return out.decode("utf-8")


def read_subject(root, rev):
    rc, out, _ = run_git(root, "log", "-1", "--format=%s", rev)
    return out.decode("utf-8", "replace").strip() if rc == 0 else "?"


def parse_rows(text):
    """Return census rows in file order: id, indent width, raw cells, shape."""
    rows = []
    for lineno, line in enumerate(text.splitlines(), 1):
        m = CENSUS_RE.match(line)
        if not m:
            continue
        fields = line.split("|")
        raw = (fields[1:12] + [""] * 11)[:11]
        rows.append({
            "id": raw[0].strip(),
            "indent": len(m.group(1)),
            "raw": raw,
            "cells": [c.strip() for c in raw],
            "shape": len(fields),
            "line": lineno,
        })
    return rows


def index_rows(rows):
    first = OrderedDict()
    dup = Counter()
    for row in rows:
        if row["id"] in first:
            dup[row["id"]] += 1
        else:
            first[row["id"]] = row
    return first, dup


def histogram(rows, idx, order):
    counts = Counter(row["cells"][idx] for row in rows)
    parts = []
    for key in order:
        if counts.get(key):
            parts.append("%s=%d" % (key, counts[key]))
    for key in sorted(counts):
        if key not in order and counts[key]:
            parts.append("%s=%d" % (key or "<empty>", counts[key]))
    return " ".join(parts) if parts else "-"


def indent_profile(rows):
    zero = sum(1 for row in rows if row["indent"] == 0)
    return "0-spaces=%d 1-3-spaces=%d" % (zero, len(rows) - zero)


def clip(text, width):
    return text if len(text) <= width else text[:width - 3] + "..."


def cell_text(old_raw, new_raw, width):
    old_val, new_val = old_raw.strip(), new_raw.strip()
    if old_val != new_val:
        return "%s -> %s" % (clip(old_val, width), clip(new_val, width))
    return "%s -> %s (whitespace-only: %s -> %s)" % (
        clip(old_val, width), clip(new_val, width),
        clip(old_raw, width), clip(new_raw, width),
    )


def main(argv):
    ap = argparse.ArgumentParser(
        description="Diff corpus/SOURCES.md registry rows between two "
                    "committed revisions.",
    )
    ap.add_argument("--root", required=True, help="lane work tree")
    ap.add_argument("--from", dest="rev_from", required=True,
                    help="full 40-hex revision (before)")
    ap.add_argument("--to", dest="rev_to", required=True,
                    help="full 40-hex revision (after)")
    ap.add_argument("--width", type=int, default=72,
                    help="max displayed cell width (default 72)")
    args = ap.parse_args(argv)

    for label, rev in (("--from", args.rev_from), ("--to", args.rev_to)):
        if not REV_RE.match(rev):
            die("%s must be a full 40-hex revision, got %r" % (label, rev))
    if args.width < 16:
        die("--width must be >= 16")

    rc, out, _ = run_git(args.root, "rev-parse", "--show-toplevel")
    if rc != 0:
        die("not a git work tree: %s" % args.root)
    root = out.decode("utf-8", "replace").strip()

    before = parse_rows(read_rev(root, args.rev_from))
    after = parse_rows(read_rev(root, args.rev_to))
    before_idx, before_dup = index_rows(before)
    after_idx, after_dup = index_rows(after)

    print("SOURCES.md diff  %s" % root)
    print("from %s  %s" % (args.rev_from, read_subject(root, args.rev_from)))
    print("to   %s  %s" % (args.rev_to, read_subject(root, args.rev_to)))

    added = [rid for rid in after_idx if rid not in before_idx]
    removed = [rid for rid in before_idx if rid not in after_idx]

    print("rows %d -> %d  (+%d -%d)" % (
        len(before), len(after), len(added), len(removed)))
    print("indent before: %s" % indent_profile(before))
    print("indent after:  %s" % indent_profile(after))
    print("tier before:   %s" % histogram(before, 3, TIER_ORDER))
    print("tier after:    %s" % histogram(after, 3, TIER_ORDER))
    print("status before: %s" % histogram(before, 7, STATUS_ORDER))
    print("status after:  %s" % histogram(after, 7, STATUS_ORDER))

    violations = 0
    for rid in added:
        row = after_idx[rid]
        print("  + %s  tier=%s status=%s kind=%s"
              % (rid, row["cells"][3], row["cells"][7], row["cells"][2]))
    print("added: %d  removed: %d" % (len(added), len(removed)))
    for rid in removed:
        row = before_idx[rid]
        print("  - %s  tier=%s status=%s kind=%s  APPEND-ONLY-VIOLATION"
              % (rid, row["cells"][3], row["cells"][7], row["cells"][2]))
    violations += len(removed)

    changed_ids = 0
    cell_changes = 0
    print("changed cells (ids in both revisions):")
    for rid in before_idx:
        if rid not in after_idx:
            continue
        old_row, new_row = before_idx[rid], after_idx[rid]
        lines = []
        if old_row["shape"] != new_row["shape"]:
            lines.append(
                "  ~ %s shape: %d fields -> %d fields  SHAPE-VIOLATION"
                % (rid, old_row["shape"], new_row["shape"]))
            violations += 1
        for idx in range(1, len(COLUMNS)):
            old_raw, new_raw = old_row["raw"][idx], new_row["raw"][idx]
            if old_raw == new_raw:
                continue
            column = COLUMNS[idx]
            line = "  ~ %s %s: %s" % (
                rid, column, cell_text(old_raw, new_raw, args.width))
            if column not in MUTABLE:
                line += "  APPEND-ONLY-VIOLATION"
                violations += 1
            lines.append(line)
            cell_changes += 1
        if lines:
            changed_ids += 1
            print("\n".join(lines))
    print("changed_ids: %d  cell_changes: %d" % (changed_ids, cell_changes))

    malformed = [(rev_label, row) for rev_label, rows in
                 (("before", before), ("after", after))
                 for row in rows if row["shape"] != 13]
    for rev_label, row in malformed:
        print("  ! %s line %d %s: %d fields, expected 13  MALFORMED"
              % (rev_label, row["line"], row["id"], row["shape"]))
    dups = sorted(set(before_dup) | set(after_dup))
    for rid in dups:
        print("  ! duplicate id %s (extra rows before=%d after=%d)"
              % (rid, before_dup[rid], after_dup[rid]))

    print("SUMMARY rows_before=%d rows_after=%d added=%d removed=%d "
          "changed_ids=%d cell_changes=%d violations=%d malformed=%d dups=%d"
          % (len(before), len(after), len(added), len(removed),
             changed_ids, cell_changes, violations, len(malformed), len(dups)))

    if violations or malformed or dups:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
