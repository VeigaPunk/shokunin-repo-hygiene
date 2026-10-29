#!/usr/bin/env python3
"""Probe H1 (--root no longer required). Run without --root from inside a fleet: pristine refuses with
argparse usage (exit 2); the mutant defaults --root to '.' and runs the measurement."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import PRISTINE, mut, trial, show, verdict, build_fleet


def setup(base):
    fleet = build_fleet(base)
    return {"argv": ["--record", os.path.join(base, "record.tsv")], "cwd": fleet}


def main():
    p = trial("H1-pristine", PRISTINE, setup)
    m = trial("H1-mutant", mut("H1"), setup)
    show("pristine", p)
    show("mutant", m)
    return verdict("H1", p, m)


if __name__ == "__main__":
    sys.exit(main())
