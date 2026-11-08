#!/usr/bin/env python3
"""S84ScoutDirs probe: which `why` branch of census/round-84/c1-pointer-counter.py does each row of a pinned
C1 population take?

Read-only on the lane. Writes only under --work (outside /tmp) and prints a histogram of the counter's own
`why` strings (each `why` string is unique to one branch of judge()).

Usage: branch-histogram.py --population <tsv> --work <empty dir outside /tmp>
"""
import argparse
import importlib.util
import os
import sys

sys.dont_write_bytecode = True
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--population", required=True)
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("FATAL: --work under /tmp", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    counter = load(os.path.join(LANE, "census/round-84/c1-pointer-counter.py"), "counter")
    harness = load(os.path.join(LANE, "census/round-84/c1-false-row-harness.py"), "harness")
    fx, revs = harness.build_fixture(LANE, work)
    pop = os.path.abspath(ns.population)
    rows = [l.rstrip("\n").split("\t") for l in open(pop, encoding="utf-8")
            if l.strip() and not l.startswith("#")]
    pmap_cache = {}
    blobs = {}
    hist = {}
    for rid, where, rlabel, popl, item, cls, target, exp_got, exp_rc, _src in rows:
        if popl not in pmap_cache:
            pfile = os.path.join(LANE, harness.POPS[popl][0])
            prows = [l.rstrip("\n").split("\t") for l in open(pfile, encoding="utf-8")
                     if l.strip() and not l.startswith("#")]
            pmap_cache[popl] = {r[0]: r for r in prows}
            # the base revision for the item's own population is the one the counter pins by sha256
            sha = harness.sha(pfile)
            pmap_cache[popl + ":base"] = counter.POPS[sha][1]
        pmap = pmap_cache[popl]
        pbase = pmap_cache[popl + ":base"]
        if pmap[item][1] not in blobs:
            blobs[pmap[item][1]] = counter.git(LANE, "show", f"{pbase}:{pmap[item][1]}", check=False).stdout.decode(
                "utf-8", "replace").split("\n")
        root, rev = (LANE, pbase) if where == "lane" else (fx, revs[rlabel])
        st, why = counter.judge(root, rev, FLEET, pmap[item], (cls, target), blobs[pmap[item][1]])
        tag = "MOVED-accepted" if (st == cls and not why) else why.replace("class=%s " % cls, "")
        hist.setdefault(tag, []).append(rid)
    print("POPULATION", pop)
    for tag in sorted(hist, key=lambda t: (-len(hist[t]), t)):
        print(f"BRANCH n={len(hist[tag]):2d}  {tag}")
        print("      rows:", " ".join(hist[tag]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
