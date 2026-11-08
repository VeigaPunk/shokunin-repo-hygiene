#!/usr/bin/env python3
"""S88Sentinel LD1 probes: the duplicate-ledger refusal as a privilege boundary.

Runs the FROZEN r87 counter (census/round-87/c1-pointer-counter.py) on the frozen r77 population with (a) the
frozen r77 ledger and (b) the frozen r77 ledger plus a duplicate P01 row (the LD1 shape), and (c) the m17 mutant
(the duplicate-id refusal dropped). Reports whether the duplicate can make the counter RESOLVE an item it should
refuse, what the exit code is, and whether the run can write outside --work.

Reads the lane read-only. All writes go under --work (never /tmp). Stdlib only.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
COUNTER = os.path.join(LANE, "census/round-87/c1-pointer-counter.py")
FLEET = "/home/vgpnk/Projects/shokunin"
BASE = "e65538e73c7f1a8f7570bc24a2215da8a90043f3"
POP = "census/round-77/c2-population.tsv"
LEDGER = "census/round-77/c2-pointer-ledger.tsv"
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_OPTIONAL_LOCKS": "0"})


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run(counter, ledger, label):
    p = subprocess.run([sys.executable, "-B", counter, "--root", LANE, "--rev", BASE, "--fleet-root", FLEET,
                        "--population", os.path.join(LANE, POP), "--ledger", ledger],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=LANE, env=ENV)
    out = p.stdout.decode("utf-8", "replace")
    items = [l for l in out.splitlines() if l.startswith("ITEM P01 ")]
    refused = [l for l in out.splitlines() if l.startswith("LEDGER-REFUSED")]
    summary = [l for l in out.splitlines() if l.startswith("SUMMARY")]
    print(f"--- {label} rc={p.returncode}")
    print(f"    ITEM P01: {items[0] if items else '<none>'}")
    print(f"    LEDGER-REFUSED lines: {refused if refused else '<none>'}")
    print(f"    {summary[0] if summary else '<no summary>'}")
    if p.stderr.strip():
        print(f"    stderr={p.stderr.decode()[:200]!r}")
    return {"rc": p.returncode, "out": out}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("S88-FATAL: --work under /tmp", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"S88-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    print(f"# counter sha256={sha(COUNTER)}")
    print(f"# r77 population sha256={sha(os.path.join(LANE, POP))}")
    print(f"# r77 ledger sha256={sha(os.path.join(LANE, LEDGER))}")

    # (a) the frozen ledger, untouched
    base_ledger = os.path.join(work, "ledger-frozen.tsv")
    shutil.copyfile(os.path.join(LANE, LEDGER), base_ledger)
    a = run(COUNTER, base_ledger, "A pristine counter, frozen r77 ledger")

    # (b) the LD1 shape: the frozen ledger plus a second P01 row (ABSENT, target "-")
    dup = os.path.join(work, "ledger-dup.tsv")
    with open(os.path.join(LANE, LEDGER), "rb") as f:
        raw = f.read()
    if raw and not raw.endswith(b"\n"):
        raw += b"\n"
    with open(dup, "wb") as f:
        f.write(raw + b"P01\tABSENT\t-\tr88 LD1 duplicate-id control\n")
    print(f"# dup ledger sha256={sha(dup)}")
    b = run(COUNTER, dup, "B pristine counter, duplicate P01 row (LD1 shape)")

    # (c) the m17 mutant: the duplicate-id refusal dropped
    members = json.load(open(os.path.join(LANE, "census/round-88/c1-mutants.json"), encoding="utf-8"))["members"]
    m17 = [m for m in members if m["id"] == "m17-duplicate-id"][0]
    src = open(COUNTER, encoding="utf-8").read()
    assert src.count(m17["old"]) == 1, "m17 edit does not apply exactly once"
    mut = os.path.join(work, "m17.py")
    with open(mut, "w", encoding="utf-8") as f:
        f.write(src.replace(m17["old"], m17["new"]))
    print(f"# m17 counter sha256={sha(mut)}")
    c = run(mut, dup, "C m17 mutant (duplicate refusal dropped), duplicate P01 row")
    d = run(mut, base_ledger, "D m17 mutant, frozen r77 ledger (no duplicate)")

    # (e) a duplicate whose SECOND row names a resolving class, to see whether the duplicate can win
    dup2 = os.path.join(work, "ledger-dup2.tsv")
    with open(dup2, "wb") as f:
        f.write(raw + b"P01\tTOKEN\t-\tr88 LD1 duplicate-id control, resolving class\n")
    e = run(COUNTER, dup2, "E pristine counter, duplicate P01 row with a RESOLVING class")

    # (f) a duplicate id that is NOT in the population (unknown id) and a duplicate for an id with no ledger row
    dup3 = os.path.join(work, "ledger-dup3.tsv")
    with open(dup3, "wb") as f:
        f.write(raw + b"P09\tABSENT\t-\tr88 duplicate for a population id with no ledger row\n")
    f_ = run(COUNTER, dup3, "F pristine counter, duplicate P09 (population id with NO frozen ledger row)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
