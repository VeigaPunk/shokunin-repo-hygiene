#!/usr/bin/env python3
"""Probe B1 (O_NONBLOCK dropped from parse_record). A FIFO record: pristine opens non-blocking, fstat
refuses it (RECORD-MALFORMED, exit 2) at once; the mutant's plain O_RDONLY open blocks with no writer."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import PRISTINE, mut, trial, show, verdict, build_fleet


def setup(base):
    fleet = build_fleet(base)
    fifo = os.path.join(base, "record.fifo")
    os.mkfifo(fifo)
    return {"argv": ["--root", fleet, "--record", fifo, "--timeout", "5"], "cwd": base}


def main():
    p = trial("B1-pristine", PRISTINE, setup, timeout=15)
    m = trial("B1-mutant", mut("B1"), setup, timeout=8)
    show("pristine", p)
    show("mutant", m)
    return verdict("B1", p, m)


if __name__ == "__main__":
    sys.exit(main())
