#!/usr/bin/env python3
"""souji r86 — does a TAB in a path name split the K4 record's fields?

Seat S86Scribe. Draft instrument for the L1. Reads only committed bytes; writes only under its own
--work dir (never /tmp).

The K4 record is one TAB-delimited line: `MISMATCH\t{key}\t{record}\t{class}\t{detail}`
(tools/souji-record-agreement.py:445). The lane-base tool's bootstrap replaces only chr(10) with a
space (census/round-86/controls/c2-before-base-tool.py:199) — a TAB is not replaced at all, so a
path whose name carries a TAB lands a RAW TAB inside the detail field and the record's field
structure changes. The filed tool escapes `\\t` as well (tools/souji-record-agreement.py:226).

This probe builds the frozen counter's own fixture, adds a TAB-named file, forges it under the
index stat cache, and runs BOTH tools, printing the field count of every emitted MISMATCH row.

  python3 -B probe-tab-name-field-split.py --lane <lane> --work <empty dir>
"""

import argparse
import hashlib
import importlib.util
import os
import subprocess
import sys

LANE_DEFAULT = "/home/vgpnk/Projects/shokunin/souji-shokunin"
COUNTER_REL = "census/round-86/c2-k4-counter.py"
TAB_NAME = "bad\tname.txt"


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
        "FILED": os.path.join(lane, "tools/souji-record-agreement.py"),
        "BASE": os.path.join(lane, "census/round-86/controls/c2-before-base-tool.py"),
    }
    for label, path in tools.items():
        print(f"# {label} sha256={sha(path)}")

    fixture = os.path.join(work, "fx")
    os.makedirs(fixture)
    clone, rev = counter.build(fixture)
    print(f"# fixture clone={clone} rev={rev}")

    # a TAB-named tracked file, forged under the index stat cache (the same forgery the KG2 row uses)
    tab_path = os.path.join(clone, TAB_NAME)
    with open(tab_path, "wb") as f:
        f.write(b"tab v1\n")
    counter.git(clone, "add", "-A")
    counter.git(clone, "commit", "-q", "--no-verify", "-m", "tab-named file")
    rev = counter.git(clone, "rev-parse", "HEAD").stdout.decode().strip()
    print(f"# after committing the tab-named file: rev={rev}")
    with open(tab_path, "wb") as f:
        f.write(b"tab X1\n")
    counter.forge_index_stat(clone, TAB_NAME)

    for label, path in tools.items():
        p = subprocess.run([sys.executable, "-B", path, "--root", clone, "--rev", rev],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=fixture, env=counter.ENV)
        out = p.stdout.decode("utf-8", "replace")
        print(f"--- {label} rc={p.returncode}")
        for line in out.splitlines():
            if not line.startswith("MISMATCH"):
                continue
            cells = line.split("\t")
            print(f"   fields={len(cells)}  repr={line!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
