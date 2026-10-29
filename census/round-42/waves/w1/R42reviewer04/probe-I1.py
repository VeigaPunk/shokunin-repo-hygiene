#!/usr/bin/env python3
"""Probe I1 (symlinked child directories no longer skipped in discovery). fleet/link -> a git repo
outside --root that the record does not name. Pristine skips the link (rc 0, no UNRECORDED row); the
mutant measures it and reports UNRECORDED (rc 1)."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import PRISTINE, mut, trial, show, verdict, build_fleet, mkrepo


def setup(base):
    fleet = build_fleet(base)
    gamma = mkrepo(os.path.join(base, "outside", "gamma"))
    os.symlink(gamma, os.path.join(fleet, "link"))
    return {"argv": ["--root", fleet, "--record", os.path.join(base, "record.tsv")], "cwd": base}


def main():
    p = trial("I1-pristine", PRISTINE, setup)
    m = trial("I1-mutant", mut("I1"), setup)
    show("pristine", p)
    show("mutant", m)
    return verdict("I1", p, m)


if __name__ == "__main__":
    sys.exit(main())
