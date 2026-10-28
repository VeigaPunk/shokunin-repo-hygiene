#!/usr/bin/env python3
# R41critic06 attack control for C3 (NOT a candidate; never runs the tool).
# Reads the tool's source text, finds the nth refusal label with the counter's own site regex and
# asserts the frozen class for that site. No refusal is ever triggered; no subprocess is started.
import argparse
import re
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--tool")
ap.add_argument("--work")
a = ap.parse_args()

SITE_RE = re.compile(r'(?:Refusal\(\s*"|"REFUSAL )([A-Z]+(?:-[A-Z]+)*):')
# (source-order index, frozen class, probe ids) transcribed from census/round-41/c3-sites.tsv
SITES = (
    (0, "RECORD-MALFORMED", ("P01",)),
    (1, "RECORD-MISSING", ("P02a", "P02b")),
    (2, "RECORD-MALFORMED", ("P03",)),
    (3, "RECORD-MALFORMED", ("P04",)),
    (4, "RECORD-MALFORMED", ("P05",)),
    (5, "RECORD-EMPTY", ("P06",)),
    (6, "RECORD-MALFORMED", ("P07",)),
    (7, "RECORD-MALFORMED", ("P08",)),
    (8, "RECORD-MALFORMED", ("P09",)),
    (9, "JSON-NOT-REGULAR", ("P10a", "P10b")),
    (10, "JSON-NOT-REGULAR", ("P11",)),
    (11, "USAGE", ("P12",)),
    (12, "RECORD-OUTSIDE-ROOT", ("P13",)),
    (13, "RECORD-OUTSIDE-ROOT", ("P14",)),
    (14, "JSON-IS-RECORD", ("P15",)),
    (15, "JSON-INSIDE-MEASURED-TREE", ("P16",)),
    (16, "JSON-HARDLINKED", ("P17",)),
    (17, "JSON-UNWRITABLE", ("P18",)),
    (18, "USAGE", ("P19",)),
)

with open(a.tool, encoding="utf-8") as handle:
    found = SITE_RE.findall(handle.read())
verdict = {}
for idx, cls, probes in SITES:
    ok = idx < len(found) and found[idx] == cls
    for p in probes:
        verdict[p] = ok
for p in sorted(verdict):
    print("probe-%s=%s" % (p, "PASS" if verdict[p] else "FAIL"))
fails = sum(1 for v in verdict.values() if not v)
print("SUMMARY probes=%d pass=%d fail=%d" % (len(verdict), len(verdict) - fails, fails))
sys.exit(1 if fails else 0)
