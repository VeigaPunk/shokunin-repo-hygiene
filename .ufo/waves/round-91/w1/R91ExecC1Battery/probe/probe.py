#!/usr/bin/env python3
"""R91ExecC1Battery kill-power probe.

Takes the r91 63-row population, deletes ONE of the five new rows at a time (in a COPY under scratch),
and scores the pristine counter plus the six new mutants against that 62-row copy through a COPY of the filed
harness whose POP_PINS dict is extended with the derived shas (the filed harness and filed population are never
modified). A row that binds a mutant is one whose deletion lets that mutant survive (exit 0, mismatches 0).

Usage: python3 -B probe.py <counter> <mutants.json> <harness-probe> <lane> <workdir>
"""
import json
import os
import subprocess
import sys
import concurrent.futures as cf

COUNTER, MUTANTS, HARNESS, LANE, WORK = (os.path.abspath(x) for x in sys.argv[1:6])
NEW = ["ld1c-class-keyed", "ld1d-conflict-keyed", "nf6i2-last-occurrence",
       "nf6j-pathch-narrow", "s1-exact-width", "s3-equal-two"]
DROPS = ["LD1c", "LD3", "LD4", "NF6i2", "NF6j"]
HERE = os.path.dirname(os.path.abspath(__file__))


def make_mutants():
    src = open(COUNTER, encoding="utf-8").read()
    members = json.load(open(MUTANTS, encoding="utf-8"))["members"]
    out = {"pristine": COUNTER}
    for m in members:
        if m["id"] not in NEW:
            continue
        assert src.count(m["old"]) == 1, m["id"]
        p = os.path.join(HERE, "mut-" + m["id"] + ".py")
        open(p, "w", encoding="utf-8").write(src.replace(m["old"], m["new"]))
        out[m["id"]] = p
    return out


def run(counter, pop, tag):
    w = os.path.join(WORK, tag)
    p = subprocess.run([sys.executable, "-B", HARNESS, "--counter", counter, "--lane", LANE,
                        "--fleet-root", "/home/vgpnk/Projects/shokunin", "--work", w,
                        "--population", pop],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=LANE, timeout=600)
    out = p.stdout.decode("utf-8", "replace")
    summ = [l for l in out.splitlines() if l.startswith("SUMMARY ")]
    return tag, p.returncode, summ[-1] if summ else "", p.stderr.decode("utf-8", "replace")[:300]


def main():
    muts = make_mutants()
    jobs = []
    for drop in DROPS:
        pop = os.path.join(HERE, "rows-drop-%s.tsv" % drop)
        for mid, path in muts.items():
            jobs.append((path, pop, "drop%s__%s" % (drop, mid)))
    res = {}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for tag, rc, summ, err in ex.map(lambda j: run(*j), jobs):
            res[tag] = (rc, summ, err)
            print("PROBE %-42s exit=%d %s%s" % (tag, rc, summ, (" ERR=" + err) if err else ""), flush=True)
    print("\n=== kill-power matrix (SURVIVES = row deletion lets the mutant through)")
    print("mutant".ljust(24) + "".join(("drop-" + d).rjust(12) for d in DROPS))
    for mid in NEW:
        cells = []
        for drop in DROPS:
            rc, summ, _ = res["drop%s__%s" % (drop, mid)]
            cells.append(("SURVIVES" if rc == 0 else "killed").rjust(12))
        print(mid.ljust(24) + "".join(cells))
    print("\n=== pristine counter on each derived 62-row population")
    for drop in DROPS:
        rc, summ, _ = res["drop%s__pristine" % drop]
        print("pristine on rows-drop-%-8s exit=%d %s" % (drop, rc, summ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
