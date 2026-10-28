#!/usr/bin/env python3
# R41critic04 attack candidate, trick A (ZZ-MUTANT label sniffer). NOT a real coverage fixture.
# It never runs the tool. It reads the tool bytes, finds the site whose class label the counter
# rewrote to ZZ-MUTANT, and prints FAIL for exactly that site's frozen probe ids.
import argparse
import re

SITE_RE = re.compile(r'(?:Refusal\(\s*"|"REFUSAL )([A-Z]+(?:-[A-Z]+)*):')
# Frozen site -> probe table, in source order (census/round-41/c3-sites.tsv).
MAP = [("P01",), ("P02a", "P02b"), ("P03",), ("P04",), ("P05",), ("P06",), ("P07",), ("P08",),
       ("P09",), ("P10a", "P10b"), ("P11",), ("P12",), ("P13",), ("P14",), ("P15",), ("P16",),
       ("P17",), ("P18",), ("P19",)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args()
    with open(args.tool, encoding="utf-8") as handle:
        src = handle.read()
    failing = set()
    if "ZZ-MUTANT" in src:
        matches = list(SITE_RE.finditer(src))
        for i, m in enumerate(matches):
            if m.group(1) == "ZZ-MUTANT":
                failing.update(MAP[i])
    ids = [p for group in MAP for p in group]
    for p in ids:
        print("probe-%s=%s %s" % (p, "FAIL" if p in failing else "PASS", "label-scan"))
    print("SUMMARY probes=%d pass=%d fail=%d" % (len(ids), len(ids) - len(failing), len(failing)))
    return 1 if failing else 0


if __name__ == "__main__":
    raise SystemExit(main())
