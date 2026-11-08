#!/usr/bin/env python3
"""souji r86 — which clause decides each new row, and which row kills which mutant.

Seat S86Scribe. Draft instrument for the L1. Nothing here is filed; it reads only committed bytes
and writes only under its own --work dir (never /tmp).

What it shows, in order:

  1. For each of the two new rows (NF-W, NF-Y) the counter's OWN refusal message under the pristine
     committed counter bytes — i.e. the clause that decides the row, quoted from the counter.
  2. The same two rows under two single-edit mutants built from census/round-86/c1-mutants.json
     (c7-census-in-tree, m14-short-shape): which row each mutant turns green, and that the OTHER
     row is untouched by it. This is the "each row reaches exactly one clause" measurement.
  3. The same two mutants on the r85 47-row population: neither row exists there, and both mutants
     survive (mismatches=0) — the delta is the population, not the rule.

Usage:
  python3 -B probe-row-decides-clause.py --lane <lane> --fleet-root <fleet> --work <empty dir>
"""

import argparse
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys

LANE_DEFAULT = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET_DEFAULT = "/home/vgpnk/Projects/shokunin"

HERE = os.path.dirname(os.path.abspath(__file__))
COUNTER_REL = "census/round-86/c1-pointer-counter.py"
HARNESS_REL = "census/round-86/c1-false-row-harness.py"
MUTANTS_REL = "census/round-86/c1-mutants.json"
ROWS_REL = "census/round-86/c1-false-rows.tsv"

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "r86 scribe probe", "GIT_AUTHOR_EMAIL": "probe@r86.invalid",
            "GIT_COMMITTER_NAME": "r86 scribe probe", "GIT_COMMITTER_EMAIL": "probe@r86.invalid",
            "GIT_AUTHOR_DATE": "2026-11-08T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-08T00:00:00Z"})

# the two rows r86 added: id -> (population file, item, class, target)
NEW_ROWS = ("NF-W", "NF-Y")


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def git(root, *args, check=True):
    p = subprocess.run(["git", "-C", root] + list(args), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=ENV)
    if check and p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed in {root}: {p.stderr.decode('utf-8', 'replace')}")
    return p


def read_rows(lane):
    rows = {}
    with open(os.path.join(lane, ROWS_REL), encoding="utf-8") as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            cells = line.rstrip("\n").split("\t")
            rows[cells[0]] = cells
    return rows


def mutate(lane, work, mutant_id):
    """Write the single-edit mutant counter under --work; return its path."""
    import json
    with open(os.path.join(lane, MUTANTS_REL), encoding="utf-8") as f:
        members = json.load(f)["members"]
    member = next(m for m in members if m["id"] == mutant_id)
    src = open(os.path.join(lane, COUNTER_REL), encoding="utf-8").read()
    if src.count(member["old"]) != 1:
        raise SystemExit(f"mutant {mutant_id} does not apply exactly once")
    out = src.replace(member["old"], member["new"], 1)
    path = os.path.join(work, f"counter-{mutant_id}.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    return path


def run_counter(counter, fx, rev, lane, work, tag, expect):
    """Forge the two new rows with a deliberately wrong expectation so the counter PRINTS its refusal
    message (it prints `why` only when the forged expectation is not met)."""
    forge = os.path.join(work, f"forge-{tag}.tsv")
    with open(forge, "w", encoding="utf-8") as f:
        for rid in NEW_ROWS:
            cells = ROWS[rid]
            f.write(f"{rid}\t{cells[4]}\t{cells[5]}\t{cells[6]}\t{expect}\n")
    items = os.path.join(lane, "census/round-86/c1-items.tsv")
    ledger = os.path.join(lane, "census/round-86/c1-ledger.tsv")
    p = subprocess.run([sys.executable, "-B", counter, "--root", fx, "--rev", rev, "--fleet-root", FLEET,
                        "--population", items, "--ledger", ledger, "--forge", forge],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=lane, env=ENV)
    out = p.stdout.decode("utf-8", "replace")
    print(f"--- {tag} (counter sha256={sha(counter)}) rc={p.returncode}")
    for line in out.splitlines():
        if line.startswith("FORGE ") or line.startswith("FORGE-SUMMARY"):
            print("   " + line)
    if p.returncode not in (0, 1):
        print("   stderr:", p.stderr.decode("utf-8", "replace")[:400])
    return out


def run_population(lane, counter, population, work, tag):
    d = os.path.join(work, f"pop-{tag}")
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    p = subprocess.run([sys.executable, "-B", os.path.join(lane, HARNESS_REL), "--counter", counter,
                        "--lane", lane, "--fleet-root", FLEET, "--work", d, "--population", population],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=lane, env=ENV)
    out = p.stdout.decode("utf-8", "replace")
    print(f"--- population arm {tag}: counter={os.path.basename(counter)} population={os.path.basename(population)}")
    for line in out.splitlines():
        if "match=no" in line or line.startswith("SUMMARY"):
            print("   " + line)
    if not out.strip():
        print("   stderr:", p.stderr.decode("utf-8", "replace")[:400])
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", default=LANE_DEFAULT)
    ap.add_argument("--fleet-root", default=FLEET_DEFAULT)
    ap.add_argument("--work", required=True, help="empty scratch dir (never under /tmp)")
    ns = ap.parse_args(argv)
    global LANE, FLEET, ROWS
    LANE, FLEET = os.path.abspath(ns.lane), os.path.abspath(ns.fleet_root)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        raise SystemExit("--work is under /tmp, /var/tmp or /dev/shm")
    if os.path.exists(work) and os.listdir(work):
        raise SystemExit(f"--work {work} is not empty")
    os.makedirs(work, exist_ok=True)
    ROWS = read_rows(LANE)

    print(f"lane={LANE} fleet-root={FLEET} work={work}")
    print(f"# counter {COUNTER_REL} sha256={sha(os.path.join(LANE, COUNTER_REL))}")
    print(f"# population {ROWS_REL} sha256={sha(os.path.join(LANE, ROWS_REL))}")

    harness = load(os.path.join(LANE, HARNESS_REL), "r86_harness")
    fx, revs = harness.build_fixture(LANE, work)
    rev = revs["R9"]
    print(f"# fixture {fx} rev R9={rev}")

    pristine = os.path.join(LANE, COUNTER_REL)

    print("\n== 1. the deciding clause, quoted from the counter's own refusal message ==")
    print("   (the forge expectation is deliberately wrong, so the counter prints `why`)")
    run_counter(pristine, fx, rev, LANE, work, "pristine", "MISMATCH")

    print("\n== 2. one row per clause: which mutant turns which row green ==")
    for mutant_id in ("c7-census-in-tree", "m14-short-shape"):
        mp = mutate(LANE, work, mutant_id)
        run_counter(mp, fx, rev, LANE, work, mutant_id, "REFUSED")

    print("\n== 3. the same mutants on the r85 47-row population: neither row is there ==")
    r85 = os.path.join(LANE, "census/round-85/c1-false-rows.tsv")
    for mutant_id in ("c7-census-in-tree", "m14-short-shape"):
        mp = os.path.join(work, f"counter-{mutant_id}.py")
        run_population(LANE, mp, r85, work, f"{mutant_id}-r85")
    print("== 3b. and on the r86 49-row population, where both rows are ==")
    for mutant_id in ("c7-census-in-tree", "m14-short-shape"):
        mp = os.path.join(work, f"counter-{mutant_id}.py")
        run_population(LANE, mp, os.path.join(LANE, ROWS_REL), work, f"{mutant_id}-r86")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
