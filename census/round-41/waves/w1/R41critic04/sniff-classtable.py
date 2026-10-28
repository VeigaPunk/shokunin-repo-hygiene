#!/usr/bin/env python3
# R41critic04 attack candidate, trick C (class-table sniffer). NOT a real coverage fixture.
# It never runs the tool and never names the ZZ-MUTANT label. It compares each refusal-site label in
# the tool bytes with the frozen class column (census/round-41/c3-sites.tsv) and prints FAIL for the
# probe ids of every site whose label differs. A class-label-only check is all the counter can see.
import argparse
import re

SITE_RE = re.compile(r'(?:Refusal\(\s*"|"REFUSAL )([A-Z]+(?:-[A-Z]+)*):')
# (class, probe ids) per site, in source order (census/round-41/c3-sites.tsv).
TABLE = [
    ("RECORD-MALFORMED", ("P01",)),
    ("RECORD-MISSING", ("P02a", "P02b")),
    ("RECORD-MALFORMED", ("P03",)),
    ("RECORD-MALFORMED", ("P04",)),
    ("RECORD-MALFORMED", ("P05",)),
    ("RECORD-EMPTY", ("P06",)),
    ("RECORD-MALFORMED", ("P07",)),
    ("RECORD-MALFORMED", ("P08",)),
    ("RECORD-MALFORMED", ("P09",)),
    ("JSON-NOT-REGULAR", ("P10a", "P10b")),
    ("JSON-NOT-REGULAR", ("P11",)),
    ("USAGE", ("P12",)),
    ("RECORD-OUTSIDE-ROOT", ("P13",)),
    ("RECORD-OUTSIDE-ROOT", ("P14",)),
    ("JSON-IS-RECORD", ("P15",)),
    ("JSON-INSIDE-MEASURED-TREE", ("P16",)),
    ("JSON-HARDLINKED", ("P17",)),
    ("JSON-UNWRITABLE", ("P18",)),
    ("USAGE", ("P19",)),
]
ALL_IDS = [p for _c, group in TABLE for p in group]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args()
    with open(args.tool, encoding="utf-8") as handle:
        found = [m.group(1) for m in SITE_RE.finditer(handle.read())]
    failing = set()
    for i, (cls, group) in enumerate(TABLE):
        if i >= len(found) or found[i] != cls:
            failing.update(group)
    for p in ALL_IDS:
        print("probe-%s=%s %s" % (p, "FAIL" if p in failing else "PASS", "class-table"))
    print("SUMMARY probes=%d pass=%d fail=%d" % (len(ALL_IDS), len(ALL_IDS) - len(failing), len(failing)))
    return 1 if failing else 0


if __name__ == "__main__":
    raise SystemExit(main())
