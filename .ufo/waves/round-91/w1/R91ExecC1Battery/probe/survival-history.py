#!/usr/bin/env python3
"""R91ExecC1Battery survival history: the six r91 new mutants on every population pinned BEFORE r91 (r83..r90).

Uses the FILED harness (its POP_PINS already carries r83..r90) and the FILED populations; no instrument is modified.
A mutant survives a population iff the harness exits 0 with mismatches=0 errors=0. Pristine is scored alongside so a
survival is not a broken run.

Usage: python3 -B survival-history.py <lane> <workdir>
"""
import json
import os
import subprocess
import sys
import concurrent.futures as cf

LANE, WORK = (os.path.abspath(x) for x in sys.argv[1:3])
HARNESS = os.path.join(LANE, "census/round-91/c1-false-row-harness.py")
COUNTER = os.path.join(LANE, "census/round-87/c1-pointer-counter.py")
MUTANTS = os.path.join(LANE, "census/round-91/c1-mutants.json")
POPS = [("r%d" % n, os.path.join(LANE, "census/round-%d/c1-false-rows.tsv" % n)) for n in range(83, 91)]
NEW = ["ld1c-class-keyed", "ld1d-conflict-keyed", "nf6i2-last-occurrence",
       "nf6j-pathch-narrow", "s1-exact-width", "s3-equal-two"]
HERE = os.path.dirname(os.path.abspath(__file__))


def make():
    src = open(COUNTER, encoding="utf-8").read()
    out = {"pristine": COUNTER}
    for m in json.load(open(MUTANTS, encoding="utf-8"))["members"]:
        if m["id"] not in NEW:
            continue
        assert src.count(m["old"]) == 1, m["id"]
        p = os.path.join(HERE, "mut-" + m["id"] + ".py")
        open(p, "w", encoding="utf-8").write(src.replace(m["old"], m["new"]))
        out[m["id"]] = p
    return out


def run(counter, pop, tag):
    p = subprocess.run([sys.executable, "-B", HARNESS, "--counter", counter, "--lane", LANE,
                        "--fleet-root", "/home/vgpnk/Projects/shokunin",
                        "--work", os.path.join(WORK, tag), "--population", pop],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=LANE, timeout=600)
    out = p.stdout.decode("utf-8", "replace")
    summ = [l for l in out.splitlines() if l.startswith("SUMMARY ")]
    return tag, p.returncode, summ[-1] if summ else "", p.stderr.decode("utf-8", "replace")[:200]


def main():
    muts = make()
    jobs = [(path, pop, "%s__%s" % (lbl, mid)) for lbl, pop in POPS for mid, path in muts.items()]
    res = {}
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for tag, rc, summ, err in ex.map(lambda j: run(*j), jobs):
            res[tag] = rc
            print("HIST %-40s exit=%d %s%s" % (tag, rc, summ, (" ERR=" + err) if err else ""), flush=True)
    print("\n=== survival of the six r91 members on every pre-r91 pinned population (SURVIVES = killed=no)")
    print("mutant".ljust(24) + "".join(lbl.rjust(10) for lbl, _ in POPS))
    for mid in NEW:
        print(mid.ljust(24) + "".join(("SURVIVES" if res["%s__%s" % (lbl, mid)] == 0 else "KILLED").rjust(10)
                                      for lbl, _ in POPS))
    print("\n=== pristine on each pre-r91 population")
    for lbl, _ in POPS:
        print("pristine %-4s exit=%d" % (lbl, res["%s__pristine" % lbl]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
