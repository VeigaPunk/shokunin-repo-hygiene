#!/usr/bin/env python3
"""S84Sentinel C1 unbound-clause hunter: find a WRONG resolution rule that the frozen 44-row population scores GREEN.

The r84 claim says the 44-row population "carries one FALSE row per clause". This script asks the stronger
question: is there a single-edit rule that the population does NOT kill, i.e. one that resolves a WRONG file
while all 44 rows still match? Such a rule is certified by the population: the battery would report pristine
green and killed_r84=5 while the counter resolves a decoy as the moved artifact.

Each candidate is a single text edit of census/round-84/c1-pointer-counter.py (copied to scratch; the lane file
is never touched). For each: the row-level verdict under the 44-row population, and which rows flip.

Usage: c1_unbound_clauses.py --work <empty dir>
"""
import argparse
import os
import re
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
COUNTER = os.path.join(LANE, "census/round-84/c1-pointer-counter.py")
HARNESS = os.path.join(LANE, "census/round-84/c1-false-row-harness.py")
POP = os.path.join(LANE, "census/round-84/c1-false-rows.tsv")
FLEET = "/home/vgpnk/Projects/shokunin"

# --- candidate wrong rules, each a single edit of the filed counter ---------------------
CANDIDATES = [
    {"id": "u1-shape-only-owntree",
     "clause": "the own-tree wave copy must keep the token's WHOLE remaining path (a real wN/ prefix alone is not "
               "enough) -- the clause NF-Q is filed to bind",
     "old": "    return bool(m) and got[1:] == want[1:]\n",
     "new": "    return bool(m) and got[-1] == want[-1]\n"},
    {"id": "u2-owntree-any-dir",
     "clause": "the own-tree target must sit in a real wave directory",
     "old": "    m = OWNTREE_WAVE.match(tt + \"/\")\n    return bool(m) and got[1:] == want[1:]\n",
     "new": "    m = OWNTREE_WAVE.match(tt + \"/\")\n    return bool(m) or got[1:] == want[1:]\n"},
    {"id": "u3-capture-any-root",
     "clause": "a census/round-<N> target must be under a wave capture subtree keeping the token's suffix",
     "old": "CAPTURE = re.compile(r\"^(?:waves/|wave/|records/wave-[^/]+/)(.+)$\")\n",
     "new": "CAPTURE = re.compile(r\"^(?:waves/|wave/|records/wave-[^/]+/|records/)(.+)$\")\n"},
    {"id": "u4-no-digest-no-suffix",
     "clause": "the MOVED target's bytes must equal the token's frozen digest (m6's clause, re-checked here)",
     "old": "        elif rev_digest(root, rev, target) != frozen:\n            why = \"target absent at rev or digest differs\"\n",
     "new": "        elif False:\n            why = \"u4 mutant\"\n"},
]


def run_harness(counter, work):
    p = subprocess.run([sys.executable, "-B", HARNESS, "--counter", counter, "--lane", LANE,
                        "--fleet-root", FLEET, "--work", work, "--population", POP],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=LANE)
    rows = {}
    summary = ""
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        m = re.match(r"^ROW (\S+) .*?got=(\S+) .*?match=(\S+)", line)
        if m:
            rows[m.group(1)] = m.group(2)
        if line.startswith("SUMMARY"):
            summary = line
    return rows, summary, p.returncode


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.exists(work) and os.listdir(work):
        print(f"FATAL: --work {work} not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    with open(COUNTER, encoding="utf-8") as f:
        base = f.read()
    base_rows, base_summary, base_rc = run_harness(base, os.path.join(work, "pristine"))
    print(f"# pristine: {base_summary} rc={base_rc}")
    for cand in CANDIDATES:
        old, new = cand["old"], cand["new"]
        n = base.count(old)
        if n != 1:
            print(f"CANDIDATE {cand['id']} SKIPPED: old text occurs {n} times")
            continue
        mp = os.path.join(work, f"counter-{cand['id']}.py")
        with open(mp, "w", encoding="utf-8") as f:
            f.write(base.replace(old, new))
        rows, summary, rc = run_harness(mp, os.path.join(work, "w-" + cand["id"]))
        flipped = sorted(k for k in base_rows if rows.get(k, "?") != base_rows[k])
        surviving = "SURVIVES" if (rc == 0 and not flipped) else "killed"
        print(f"CANDIDATE {cand['id']} [{surviving}] clause={cand['clause']}")
        print(f"  {summary} rc={rc}")
        print(f"  FLIPPED rows ({len(flipped)}): {flipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
