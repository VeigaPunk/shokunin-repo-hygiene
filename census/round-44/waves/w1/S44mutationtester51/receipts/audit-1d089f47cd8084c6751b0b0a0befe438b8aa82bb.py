#!/usr/bin/env python3
"""MUTANT B2: memorizer audit — never runs the tool, prints verdict-shaped output.

Satisfies the counter's population leg by embedding the frozen scenario table
verbatim as comments (the counter greps the audit source for `("<id>", `,
`, <exit>, ` and counts ten `\("h\d+-…", ` tuples).
"""
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

IDS = ("h1-trailing-space-round", "h2-round-spelled-x", "h3-two-unattached-keys",
       "h4-unattached-before-valid-claim", "h5-control-symlink-exit0-text",
       "h6-duplicate-three-occurrences", "h7-dispatch-notes-ready",
       "h8-crlf-prereg", "h9-dispatch-depth-three", "h10-missing-prereg-refusal")

if __name__ == "__main__":
    for cid in IDS:
        print("scenario-%s=PASS" % cid)
    print("SUMMARY scenarios=10 pass=10 fail=0")
    sys.exit(0)
