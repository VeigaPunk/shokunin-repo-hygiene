#!/usr/bin/env python3
"""Probe H2 (--record no longer required). Omit --record: pristine exits 2 with the argparse
'required' message; the mutant passes None to parse_record and crashes with a TypeError traceback."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import PRISTINE, mut, trial, show, verdict, build_fleet


def setup(base):
    fleet = build_fleet(base)
    return {"argv": ["--root", fleet], "cwd": base}


def main():
    p = trial("H2-pristine", PRISTINE, setup)
    m = trial("H2-mutant", mut("H2"), setup)
    show("pristine", p)
    show("mutant", m)
    return verdict("H2", p, m)


if __name__ == "__main__":
    sys.exit(main())
