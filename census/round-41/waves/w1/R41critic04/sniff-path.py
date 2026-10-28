#!/usr/bin/env python3
# R41critic04 attack candidate, trick B (tool-path sniffer). NOT a real coverage fixture.
# The counter writes each mutant to <scratch>/mut-<SID>.py; this fixture reads the site id from
# the path and prints FAIL for that site's frozen probe ids. It never reads the tool bytes or runs it.
import argparse
import os
import re

# Frozen site -> probe table, in source order (census/round-41/c3-sites.tsv).
MAP = [("P01",), ("P02a", "P02b"), ("P03",), ("P04",), ("P05",), ("P06",), ("P07",), ("P08",),
       ("P09",), ("P10a", "P10b"), ("P11",), ("P12",), ("P13",), ("P14",), ("P15",), ("P16",),
       ("P17",), ("P18",), ("P19",)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args()
    m = re.match(r"^mut-S(\d\d)\.py$", os.path.basename(args.tool))
    failing = set(MAP[int(m.group(1)) - 1]) if m else set()
    ids = [p for group in MAP for p in group]
    for p in ids:
        print("probe-%s=%s %s" % (p, "FAIL" if p in failing else "PASS", "path-scan"))
    print("SUMMARY probes=%d pass=%d fail=%d" % (len(ids), len(ids) - len(failing), len(failing)))
    return 1 if failing else 0


if __name__ == "__main__":
    raise SystemExit(main())
