#!/usr/bin/env python3
"""souji r86 — the raw K4 records the two tools emit for KG1 and KG2.

Seat S86Scribe. Draft instrument for the L1. Reads only committed bytes; writes only under its
own --work dir (never /tmp).

It reuses the frozen counter's own fixture builder and row applier
(census/round-86/c2-k4-counter.py), so the tree it measures is the tree the frozen counter
measures, and then it runs BOTH tools (the filed one and the lane-base control) over the KG1 and
KG2 rows and prints the raw MISMATCH lines, byte for byte.

  python3 -B probe-k4-record-text.py --lane <lane> --work <empty dir>
"""

import argparse
import hashlib
import importlib.util
import os
import subprocess
import sys

LANE_DEFAULT = "/home/vgpnk/Projects/shokunin/souji-shokunin"
COUNTER_REL = "census/round-86/c2-k4-counter.py"
ROWS = ("KG1", "KG2")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", default=LANE_DEFAULT)
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    lane = os.path.abspath(ns.lane)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        raise SystemExit("--work is under /tmp, /var/tmp or /dev/shm")
    if os.path.exists(work) and os.listdir(work):
        raise SystemExit(f"--work {work} is not empty")
    os.makedirs(work, exist_ok=True)

    counter = load(os.path.join(lane, COUNTER_REL), "r86_c2_counter")
    tools = {
        "FILED (tools/souji-record-agreement.py)": os.path.join(lane, "tools/souji-record-agreement.py"),
        "BASE (census/round-86/controls/c2-before-base-tool.py)":
            os.path.join(lane, "census/round-86/controls/c2-before-base-tool.py"),
    }
    for label, path in tools.items():
        print(f"# {label} sha256={sha(path)}")

    fixture = os.path.join(work, "fx")
    os.makedirs(fixture)
    clone, rev = counter.build(fixture)
    print(f"# fixture clone={clone} rev={rev}")

    for row in ROWS:
        for label, path in tools.items():
            counter.reset(clone, rev)
            counter.apply_row(clone, row)
            p = subprocess.run([sys.executable, "-B", path, "--root", clone, "--rev", rev],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=fixture, env=counter.ENV)
            out = p.stdout.decode("utf-8", "replace")
            print(f"--- row {row} | {label} | rc={p.returncode}")
            for line in out.splitlines():
                if line.startswith("MISMATCH") or line.startswith("keys="):
                    print("   " + repr(line))
            if not out.strip():
                print("   (no stdout) stderr:", p.stderr.decode("utf-8", "replace")[:300])
    counter.reset(clone, rev)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
