#!/usr/bin/env python3
"""S84Sentinel C1 row-flip analyzer: which POPULATION ROW does each mutant actually flip?

The r84 clause battery reports aggregate mismatches per mutant. A row that flips under NO mutant is an
INERT row: it is refused for a reason other than the clause it is filed to bind, so the population does not
discriminate that clause. This script applies each frozen mutant (census/round-84/c1-mutants.json) and three
extra candidate mutants to a COPY of the counter (in scratch) and reports, per mutant, the exact rows that
change verdict. Read-only w.r.t. the lane; it writes only under --work.

Usage: c1_row_flips.py --work <empty dir> [--mutants lane-file]
"""
import argparse
import json
import os
import re
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
COUNTER = os.path.join(LANE, "census/round-84/c1-pointer-counter.py")
HARNESS = os.path.join(LANE, "census/round-84/c1-false-row-harness.py")
POP = os.path.join(LANE, "census/round-84/c1-false-rows.tsv")
FLEET = "/home/vgpnk/Projects/shokunin"

EXTRA = [
    {"id": "x-no-round-clause", "clause": "a MOVED target must name a round-<N> the token names",
     "old": "        elif not kr:\n            # r79 (S78MutCounter NF3): with no round-<N> in the token the location binding is the last\n            # component alone, so a byte-equal copy in any directory would resolve the item.\n            why = \"token names no round-<N>: a moved location cannot be bound\"\n",
     "new": "        elif False:\n            why = \"x-no-round-clause mutant\"\n"},
    {"id": "x-basename-clause", "clause": "the MOVED target's last component must equal the token's",
     "old": "        elif os.path.basename(target.rstrip(\"/\")) != os.path.basename(token.rstrip(\"/\")):\n            why = \"target's last component differs from the token's\"\n",
     "new": "        elif False:\n            why = \"x-basename-clause mutant\"\n"},
    {"id": "x-census-suffix-clause", "clause": "a census/round-<N> target must keep the token's whole suffix",
     "old": "        elif kr and target[:tr.start(0)] == \"census\" and token[:kr.start(0)] != \"census\" \\\n                and not _capture_ok(token, kr, target, tr):\n            # r81 (S80MutCounter NF12): under the capture root only a wave capture subtree holds the moved file\n            why = \"census/round-<N> target is not a wave capture keeping the token's own path suffix\"\n",
     "new": "        elif False:\n            why = \"x-census-suffix-clause mutant\"\n"},
]


def run_harness(counter, work, pop=POP):
    p = subprocess.run([sys.executable, "-B", HARNESS, "--counter", counter, "--lane", LANE,
                        "--fleet-root", FLEET, "--work", work, "--population", pop],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=LANE)
    rows = {}
    summary = ""
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        m = re.match(r"^ROW (\S+) .*?got=(\S+) .*?match=(\S+)", line)
        if m:
            rows[m.group(1)] = (m.group(2), m.group(3))
        if line.startswith("SUMMARY"):
            summary = line
    return rows, summary, p.returncode


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--mutants", default=os.path.join(LANE, "census/round-84/c1-mutants.json"))
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.exists(work) and os.listdir(work):
        print(f"FATAL: --work {work} not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    with open(COUNTER, encoding="utf-8") as f:
        base = f.read()
    with open(ns.mutants, encoding="utf-8") as f:
        members = json.load(f)["members"]
    members = members + EXTRA
    base_rows, base_summary, base_rc = run_harness(COUNTER, os.path.join(work, "pristine"))
    print(f"# pristine: {base_summary} rc={base_rc}")
    print("# row verdicts (pristine): " + " ".join(f"{k}={v[0]}" for k, v in sorted(base_rows.items())))
    for mem in members:
        old, new = mem["old"], mem["new"]
        n = base.count(old)
        if n != 1:
            print(f"MUTANT {mem['id']} SKIPPED: old text occurs {n} times")
            continue
        mp = os.path.join(work, f"counter-{mem['id']}.py")
        with open(mp, "w", encoding="utf-8") as f:
            f.write(base.replace(old, new))
        rows, summary, rc = run_harness(mp, os.path.join(work, "w-" + mem["id"]))
        flipped = sorted(k for k in base_rows if rows.get(k, ("?", "?"))[0] != base_rows[k][0])
        print(f"MUTANT {mem['id']} clause={mem.get('clause','')}")
        print(f"  {summary} rc={rc}")
        print(f"  FLIPPED rows ({len(flipped)}): {flipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
