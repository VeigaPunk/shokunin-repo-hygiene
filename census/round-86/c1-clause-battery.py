#!/usr/bin/env python3
"""souji r86 C1 clause battery: does a pinned false-row population discriminate the pointer counter's clauses?

r86 change (r85 A1, A4; SCORECARD `### Planned (r86)`): the population set gains r86 - the r85 47 rows byte-for-byte
plus NF-W (the census-in-tree shape, r85 A1/S85Scribe F1) and NF-Y (the own-tree short-shape, r85 A4/S85MutCounter
m14) - and the mutant set gains c7-census-in-tree and m14-short-shape, the two clauses r85 measured reachable and
unbound. The claim these two rows carry: on r86 all eight mutants die while the same battery and mutants on the r85
47 rows kill six and leave c7 and m14 alive.

r85 text follows. The population is the lane's own instrument: a clause of the counter is *bound* only when some
frozen row would go red under a rule that drops that clause.
 r83's 36-row population left five clauses unbound (mutants m6 digest-blind,
m7 round-blind, m8 w-only shapes, m9 basename-only, m10 records-as-wave survive 36/36). r84 adds eight rows
(TF8/TF9/TF10 true, NF-P/NF-L/NF-L2/NF-M/NF-Q false) and this battery measures the kill rate on both populations.

Arms:
  pristine  the counter under test, unchanged, scored on each pinned population; both must be green or the run is
            INVALID (a counter that fails everything is not a gain).
  mutants   every member of --mutants applied to the counter text (each `old` must occur exactly once, else INVALID),
            scored on each pinned population through census/round-84/c1-false-row-harness.py.
            KILLED iff the harness exits non-zero (a row mismatch or a harness error) for that population.

Output: `ARM pristine pop=<p> rows=<n> mismatches=<m> exit=<rc>` then
`MUTANT <id> pop=r83 killed=<yes|no> mismatches=<m> | pop=r84 killed=<yes|no> mismatches=<m>`, then
`SUMMARY mutants=<k> pristine_r83=<ok|red> pristine_r84=<ok|red> killed_r83=<k> killed_r84=<k> score=<survivors>`.
Exit 0 iff both pristine arms are green and every mutant is killed on the r84 population; 1 iff the pristine arms are
green and any mutant survives there; 2 on usage, a pin mismatch, an edit that does not apply exactly once, or an
unreadable harness.

Stdlib only. Writes only under --work (which must be empty or absent and never under /tmp) and reads the lane.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.join(HERE, "c1-false-row-harness.py")
FLEET = "/home/vgpnk/Projects/shokunin"
PINS = {"r83": (os.path.join(FLEET, "souji-shokunin/census/round-83/c1-false-rows.tsv"),
                "c9a6d58c1cf84a40a02a85a7342df2f2bd37301ba02e8f61ac91eded624e02eb", 36),
        "r84": (os.path.join(FLEET, "souji-shokunin/census/round-84/c1-false-rows.tsv"),
                "4795f009d6c873e733a2992bc86405d509dfb105b5f9950b3b9f82b2596e8f6f", 44),
        "r85": (os.path.join(FLEET, "souji-shokunin/census/round-85/c1-false-rows.tsv"),
                "1468236cfc3c8f65e7fa9bb07884324ee8ae8b7f62d6d5ca984b9dfa04698d42", 47),
        "r86": (os.path.join(HERE, "c1-false-rows.tsv"),
                "79db70f6740de41a326dc4193bf80c5394fe126d636cc98d4e26e4b5e140f561", 49)}


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run(counter, pop_label, work, lane):
    pop, pin, n = PINS[pop_label]
    if not os.path.isfile(pop) or sha(pop) != pin:
        raise SystemExit(f"BATTERY-FATAL: {pop_label} population sha256 {sha(pop)} is not the pin {pin}")
    d = os.path.join(work, f"run-{pop_label}-{os.path.basename(counter).replace('.py', '')}")
    p = subprocess.run([sys.executable, "-B", HARNESS, "--counter", counter, "--lane", lane, "--fleet-root",
                        "/home/vgpnk/Projects/shokunin", "--work", d, "--population", pop],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=lane)
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    m = re.search(r"^SUMMARY rows=(\d+) mismatches=(\d+) accepted=(\d+) refused_true=(\d+) errors=(\d+)$", out, re.M)
    if not m:
        raise SystemExit(f"BATTERY-FATAL: {pop_label} run of {counter} printed no SUMMARY: {err[:300]!r}")
    return int(m.group(1)), int(m.group(2)), int(m.group(5)), p.returncode


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True)
    ap.add_argument("--lane", default="/home/vgpnk/Projects/shokunin/souji-shokunin")
    ap.add_argument("--work", required=True, help="empty scratch dir (never under /tmp)")
    ap.add_argument("--mutants", default=os.path.join(HERE, "c1-mutants.json"))
    ap.add_argument("--only", default="r85,r86",
                    help="comma list of the pinned population labels to score (r83, r84, r85, r86)")
    ap.add_argument("--expect-killed", type=int, default=None,
                    help="exit 1 unless this many mutants are killed on the scored population set")
    ns = ap.parse_args(argv)
    lane, work = os.path.abspath(ns.lane), os.path.abspath(ns.work)
    counter = os.path.abspath(ns.counter)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("BATTERY-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"BATTERY-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(os.path.join(work, "mut"), exist_ok=True)
    print(f"# counter path={counter} sha256={sha(counter)}")
    print(f"# harness path={HARNESS} sha256={sha(HARNESS)}")
    print(f"# mutants path={os.path.abspath(ns.mutants)} sha256={sha(os.path.abspath(ns.mutants))}")
    for lbl, (pop, pin, n) in sorted(PINS.items()):
        print(f"# population {lbl} path={pop} sha256={pin} rows={n}")
    sets = [x for x in ns.only.split(",") if x]
    if not sets or any(x not in PINS for x in sets):
        print(f"BATTERY-FATAL: --only {ns.only!r} is not a subset of {sorted(PINS)}", file=sys.stderr)
        return 2
    pristine = {}
    for lbl in sets:
        rows, mism, errs, rc = run(counter, lbl, work, lane)
        pristine[lbl] = rc == 0 and mism == 0 and errs == 0
        print(f"ARM pristine pop={lbl} rows={rows} mismatches={mism} errors={errs} exit={rc}")
    if not all(pristine.values()):
        print("SUMMARY mutants=0 " + " ".join(f"pristine_{l}={'ok' if pristine[l] else 'red'}" for l in sets)
              + " " + " ".join(f"killed_{l}=0" for l in sets) + " score=invalid")
        print("BATTERY-FATAL: the unmutated counter is not green on every scored population (INVALID)",
              file=sys.stderr)
        return 2
    src = open(counter, encoding="utf-8").read()
    members = json.load(open(ns.mutants, encoding="utf-8"))["members"]
    killed = {l: 0 for l in sets}
    for m in members:
        n = src.count(m["old"])
        if n != 1:
            print(f"BATTERY-FATAL: edit {m['id']} occurs {n} times in the counter, need exactly 1", file=sys.stderr)
            return 2
        out = os.path.join(work, "mut", m["id"] + ".py")
        with open(out, "w", encoding="utf-8") as f:
            f.write(src.replace(m["old"], m["new"]))
        cells = []
        for lbl in sets:
            rows, mism, errs, rc = run(out, lbl, work, lane)
            k = rc != 0 or mism > 0 or errs > 0
            killed[lbl] += k
            cells.append(f"pop={lbl} killed={'yes' if k else 'no'} mismatches={mism} errors={errs} exit={rc}")
            print(f"MUTANT {m['id']} " + cells[-1])
        print(f"MUTANT-PAIR {m['id']} " + " | ".join(cells))
    pr = " ".join(f"pristine_{l}={'ok' if pristine[l] else 'red'}" for l in sets)
    kl = " ".join(f"killed_{l}={killed[l]}" for l in sets)
    tot = sum(killed[l] for l in sets)
    print(f"SUMMARY mutants={len(members)} sets={','.join(sets)} {pr} {kl} killed_total={tot}")
    if ns.expect_killed is not None:
        return 0 if tot == ns.expect_killed else 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
