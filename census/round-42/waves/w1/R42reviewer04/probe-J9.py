#!/usr/bin/env python3
"""Probe J9 (REPO regs single digit only). Record row alpha regs=10 (consistent TOTAL). Pristine parses
it and reports REGS-CHANGED (rc 1, live regs=2); the mutant's \\d regex rejects the row (RECORD-MALFORMED,
rc 2)."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import PRISTINE, mut, trial, show, verdict, build_fleet, write

RECORD_J9 = ("REPO\talpha\tregs=10\tprunable=0\nREPO\tbeta\tregs=1\tprunable=0\n"
             "TOTAL\trepos=2\tregs=11\tprunable=0\n")


def setup(base):
    fleet = build_fleet(base)
    rec = write(os.path.join(base, "record-j9.tsv"), RECORD_J9)
    return {"argv": ["--root", fleet, "--record", rec], "cwd": base}


def main():
    p = trial("J9-pristine", PRISTINE, setup)
    m = trial("J9-mutant", mut("J9"), setup)
    show("pristine", p)
    show("mutant", m)
    return verdict("J9", p, m)


if __name__ == "__main__":
    sys.exit(main())
