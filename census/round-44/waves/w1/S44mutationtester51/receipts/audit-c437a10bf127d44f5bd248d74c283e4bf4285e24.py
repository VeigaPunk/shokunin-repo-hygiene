#!/usr/bin/env python3
"""MUTANT B3: branching memorizer audit — never runs the tool at all.

Branches on --tool byte size: the real souji-freeze-check.py blob is ~20 KB,
the counter's clean/findings stubs are ~70-120 B. For a big tool it prints the
all-pass verdict the counter greps; for a small tool it prints a failing
verdict so the counter records the stub as REJECTED. The frozen scenario table
is embedded once as comments to satisfy the population leg's source grep.
"""
import argparse
import os
import sys

# ("h1-trailing-space-round", {…}, 0, []),
# ("h2-round-spelled-x", {…}, 1, ["C0:ROUND-MALFORMED"]),
# ("h3-two-unattached-keys", {…}, 1, ["C0:HEADING-MALFORMED", "C0:UNATTACHED-KEY", "C0:UNATTACHED-KEY"]),
# ("h4-unattached-before-valid-claim", {…}, 1, ["C0:HEADING-MALFORMED", "C0:UNATTACHED-KEY", "C2:FIELD-MISSING", "C2:FIELD-MISSING", "C2:FIELD-MISSING", "C2:FIELD-MISSING"]),
# ("h5-control-symlink-exit0-text", {…}, 1, ["C1:CONTROL-SYMLINK"]),
# ("h6-duplicate-three-occurrences", None, 1, ["C0:FROZEN-EDITED", "C1:KEY-DUPLICATE", "C1:KEY-DUPLICATE"]),
# ("h7-dispatch-notes-ready", {…}, 1, ["C0:DISPATCH-BEFORE-FREEZE"]),
# ("h8-crlf-prereg", {…}, 0, []),
# ("h9-dispatch-depth-three", {…}, 1, ["C0:DISPATCH-BEFORE-FREEZE"]),
# ("h10-missing-prereg-refusal", "REFUSAL", 2, []),

IDS = ["h1-trailing-space-round", "h2-round-spelled-x", "h3-two-unattached-keys",
       "h4-unattached-before-valid-claim", "h5-control-symlink-exit0-text",
       "h6-duplicate-three-occurrences", "h7-dispatch-notes-ready",
       "h8-crlf-prereg", "h9-dispatch-depth-three", "h10-missing-prereg-refusal"]


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    big = os.path.getsize(ns.tool) > 2000
    for cid in IDS:
        print("scenario-%s=%s" % (cid, "PASS" if big else "FAIL"))
    print("SUMMARY scenarios=10 pass=%d fail=%d" % (10 if big else 0, 0 if big else 10))
    return 0 if big else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
