#!/usr/bin/env python3
"""Which candidate crash-detection rule separates a crash from a verdict on the two r94 crash fixtures?

Reads a harness.out (the r93 search's own per-mutant output, produced by the FROZEN r93 search with the r94
crash hand edits) and applies three candidate rules. The harness's own exit code is derived from its SUMMARY
line exactly as the harness computes it: exit 0 iff mismatches == 0 and errors == 0, else 1.

  R-A  the r93 rule as shipped: killed iff harness rc == 1 and at least one `ROW ... match=no` line
  R-B  the r93-ROUND-94-ROUTED fix (r93 lesson "Routed to round 94" item 1; Q170): errored iff any ROW reads
       `got=-` (the counter printed no verdict for that row)
  R-C  the r94 rule as shipped: errored iff the harness exited 70 or any ROW reads `rc=70`

Usage: rule-check.py <harness.out> [<harness.out> ...]
"""
import re
import sys


def harness_rc(text):
    m = re.search(r"^SUMMARY rows=(\d+) mismatches=(\d+) accepted=(\d+) refused_true=(\d+) errors=(\d+)$", text, re.M)
    if not m:
        return None
    mism, errs = int(m.group(2)), int(m.group(5))
    return 0 if (mism == 0 and errs == 0) else 1


def rule_a(rc, rows):
    if rc == 0:
        return "survived"
    return "killed" if (rc == 1 and any(l.endswith(" match=no") for l in rows)) else "errored"


def rule_b(rc, rows):
    if rc == 0:
        return "survived"
    return "errored" if any(" got=- " in l for l in rows) else "killed"


def rule_c(rc, rows):
    if rc == 70 or any(" rc=70 " in l for l in rows):
        return "errored"
    if rc == 0:
        return "survived"
    return "killed" if (rc == 1 and any(l.endswith(" match=no") for l in rows)) else "errored"


def main(paths):
    for p in paths:
        text = open(p, encoding="utf-8", errors="replace").read()
        rows = [l for l in text.splitlines() if l.startswith("ROW ")]
        rc = harness_rc(text)
        print(f"{p}")
        print(f"  harness_rc={rc} rows={len(rows)} got=-={sum(1 for l in rows if ' got=- ' in l)} "
              f"rc=70={sum(1 for l in rows if ' rc=70 ' in l)} "
              f"match=no={sum(1 for l in rows if l.endswith(' match=no'))}")
        print(f"  R-A (r93 rule as shipped)               -> {rule_a(rc, rows)}")
        print(f"  R-B (r93-routed fix: got=- => errored)  -> {rule_b(rc, rows)}")
        print(f"  R-C (r94 rule: rc=70 => errored)         -> {rule_c(rc, rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
