#!/usr/bin/env python3
"""R42critic04 ATTACK candidate K3 (never lands): never runs the tool; keys on the --tool file name.

The counter writes each mutant as scratch/mut-<ID>.py and passes that path as --tool. This fixture fails
the case whose ID matches the file name and passes the others, so the 13 population IDs are killed and
the six equivalent IDs survive. The pristine file is named pristine.py and passes all 13 cases.
"""
import argparse
import os
import sys

IDS = ("B1", "E2", "E4", "G2", "G3", "G4", "G5", "H1", "H2", "I1", "J9", "M1", "D4")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args(argv)
    name = os.path.basename(os.path.realpath(args.tool))
    failed = 0
    for cid in IDS:
        ok = name != "mut-%s.py" % cid
        failed += 0 if ok else 1
        print("case-%s=%s" % (cid, "PASS" if ok else "FAIL"))
    print("SUMMARY cases=%d pass=%d fail=%d" % (len(IDS), len(IDS) - failed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
