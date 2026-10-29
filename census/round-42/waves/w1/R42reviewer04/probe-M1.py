#!/usr/bin/env python3
"""Probe M1 (ftruncate before the --json write removed). The --json target already holds 4096 bytes.
Pristine truncates and leaves exactly the JSON document (json.loads succeeds); the mutant writes the
JSON over the first bytes and the old tail survives (json.loads fails)."""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import PRISTINE, mut, trial, show, verdict, build_fleet, write


def setup(base):
    fleet = build_fleet(base)
    out = write(os.path.join(base, "out", "report.json"), b"x" * 4096)
    return {"argv": ["--root", fleet, "--record", os.path.join(base, "record.tsv"), "--json", out],
            "cwd": base, "watch": [out]}


def parses(r):
    text = r["files"]["report.json"]
    try:
        json.loads(text)
        return "json.loads OK, %d bytes" % len(text)
    except ValueError as exc:
        return "json.loads FAILS (%s), %d bytes, tail=%r" % (exc.__class__.__name__, len(text), text[-12:])


def main():
    p = trial("M1-pristine", PRISTINE, setup)
    m = trial("M1-mutant", mut("M1"), setup)
    show("pristine", p)
    print("    pristine file: " + parses(p))
    show("mutant", m)
    print("    mutant file: " + parses(m))
    return verdict("M1", p, m)


if __name__ == "__main__":
    sys.exit(main())
