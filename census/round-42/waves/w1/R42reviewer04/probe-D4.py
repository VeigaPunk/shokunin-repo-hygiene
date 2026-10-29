#!/usr/bin/env python3
"""Probe D4 (record decoded with backslashreplace). The record row names 'alp\\xffha' (raw byte 0xFF).
Both tools report ABSENT (no such directory) with the name as decoded: pristine 'replace' gives U+FFFD,
mutant 'backslashreplace' gives the literal text \\xff. The stdout bytes differ."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import PRISTINE, mut, trial, show, verdict, build_fleet, write

RECORD_D4 = b"REPO\talp\xffha\tregs=2\tprunable=0\nTOTAL\trepos=1\tregs=2\tprunable=0\n"


def setup(base):
    fleet = build_fleet(base)
    rec = write(os.path.join(base, "record-d4.tsv"), RECORD_D4)
    return {"argv": ["--root", fleet, "--record", rec, "--skip-unrecorded"], "cwd": base}


def main():
    p = trial("D4-pristine", PRISTINE, setup)
    m = trial("D4-mutant", mut("D4"), setup)
    show("pristine", p)
    print("    pristine stdout repr: %r" % p["out"])
    show("mutant", m)
    print("    mutant stdout repr: %r" % m["out"])
    return verdict("D4", p, m)


if __name__ == "__main__":
    sys.exit(main())
