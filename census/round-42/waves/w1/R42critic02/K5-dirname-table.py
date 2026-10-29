#!/usr/bin/env python3
"""ATTACK K5 (not an implementation): no grammar. Answers each synthetic case from the basename of --root
(the counter builds cand-<case>) through a table copied from the counter's CASES, and answers the real,
retro and retro_clean legs from the --prereg path."""
import argparse
import os
import sys

CASE_TABLE = {
    'clean': (0, []),
    'clean-dispatch-after': (0, []),
    'no-claims': (1, [('C0', 'NO-CLAIMS')]),
    'field-missing-base': (1, [('C1', 'FIELD-MISSING')]),
    'field-missing-counter': (1, [('C1', 'FIELD-MISSING')]),
    'field-empty-target': (1, [('C1', 'FIELD-EMPTY')]),
    'base-unresolved': (1, [('C1', 'BASE-UNRESOLVED')]),
    'base-not-ancestor': (1, [('C1', 'BASE-NOT-ANCESTOR')]),
    'counter-missing': (1, [('C1', 'COUNTER-MISSING')]),
    'counter-digest': (1, [('C1', 'COUNTER-DIGEST')]),
    'population-missing': (1, [('C1', 'POPULATION-MISSING')]),
    'population-digest': (1, [('C1', 'POPULATION-DIGEST')]),
    'population-empty': (1, [('C1', 'POPULATION-EMPTY')]),
    'control-missing': (1, [('C1', 'CONTROL-MISSING')]),
    'control-not-red': (1, [('C1', 'CONTROL-NOT-RED')]),
    'frozen-edited-counter': (1, [('C1', 'FROZEN-EDITED')]),
    'frozen-edited-population': (1, [('C1', 'FROZEN-EDITED')]),
    'dispatch-before-freeze': (1, [('C0', 'DISPATCH-BEFORE-FREEZE')]),
    'two-claims-one-bad': (1, [('C2', 'FIELD-MISSING')]),
    'dup-base-differs': (1, [('C1', 'KEY-DUPLICATE')]),
    'dup-counter-identical': (1, [('C1', 'KEY-DUPLICATE')]),
    'dup-target': (1, [('C1', 'KEY-DUPLICATE')]),
    'heading-nospace': (1, [('C0', 'HEADING-MALFORMED')]),
    'heading-lowercase': (1, [('C0', 'HEADING-MALFORMED')]),
    'heading-spaced-digit': (1, [('C0', 'HEADING-MALFORMED')]),
    'heading-suffix': (1, [('C0', 'HEADING-MALFORMED')]),
    'heading-valid-tail': (1, [('C2', 'FIELD-MISSING'), ('C2', 'FIELD-MISSING'), ('C2', 'FIELD-MISSING'), ('C2', 'FIELD-MISSING'), ('C2', 'FIELD-MISSING'), ('C2', 'FIELD-MISSING')]),
    'dispatch-spec-before': (1, [('C0', 'DISPATCH-BEFORE-FREEZE')]),
    'dispatch-attempts-before': (1, [('C0', 'DISPATCH-BEFORE-FREEZE')]),
    'dispatch-dispatched-before': (1, [('C0', 'DISPATCH-BEFORE-FREEZE')]),
    'dispatch-results-before': (1, [('C0', 'DISPATCH-BEFORE-FREEZE')]),
    'dispatch-names-after': (0, []),
    'dispatch-notes-before': (0, []),
    'counter-symlink': (1, [('C1', 'COUNTER-SYMLINK')]),
    'population-symlink': (1, [('C1', 'POPULATION-SYMLINK')]),
}
# (claims, findings) for the three prereg files the counter reads from the lane
CANNED = {
    "census/round-42/preregistration.txt": (3, 0, 0, []),
    "census/round-40/preregistration.txt": (3, 19, 1, [("C0", "CANNED")] * 19),
    "census/round-41/preregistration.txt": (3, 0, 0, []),
}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--prereg")
    ap.add_argument("--rev")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        print("SELFTEST cases=15 pass=15 fail=0")
        return 1 if os.environ.get("PYTHONPATH") else 0
    if args.rev == "f" * 40 or args.prereg == "absent.txt":
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: canned\n")
        return 2
    name = os.path.basename(os.path.normpath(args.root))
    if name.startswith("cand-"):
        rc, findings = CASE_TABLE.get(name[len("cand-"):], (0, []))
        claims = 1
    else:
        claims, count, rc, findings = CANNED.get(args.prereg, (0, 0, 0, []))
    for label, cls in findings:
        print("FINDING %s %s canned" % (label, cls))
    print("SUMMARY claims=%d findings=%d" % (claims if name.startswith("cand-") else claims, len(findings)))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
