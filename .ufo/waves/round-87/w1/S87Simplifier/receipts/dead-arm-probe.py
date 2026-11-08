#!/usr/bin/env python3
"""S87Simplifier dead-arm probe (round 87, C1 pointer counter).

Loads the FILED counter (read-only) and the deletion variants filed beside this script and checks, at
function level, that each deletion changes no verdict the two predicates can return, then locates the
minimal witness that keeps the `_whole` before-byte half from being deletable.

Run:  python3 -B .ufo/waves/round-87/w1/S87Simplifier/receipts/dead-arm-probe.py
Reads: census/round-87/c1-pointer-counter.py (the filed bytes), variants/*.py (patched copies)
Writes: nothing. Stdlib only.
"""
import hashlib
import importlib.util
import itertools
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEAT = os.path.dirname(HERE)
LANE = HERE
for _ in range(6):  # receipts -> seat -> w1 -> round-87 -> waves -> .ufo -> lane
    LANE = os.path.dirname(LANE)
FILED = os.path.join(LANE, "census/round-87/c1-pointer-counter.py")
VARIANTS = ["v0", "d1", "d2", "d2b", "d2c", "d3"]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


MODS = {v: load(FILED if v == "v0" else os.path.join(SEAT, "variants", v + ".py"), "probe_" + v)
        for v in VARIANTS}

A = ["w1", "waves", "records", "wave-9", "a2w1", "y.txt"]
A_LARGE = ["w1", "waves", "wave", "records", "wave-9", "a2w1", "x", "y.txt", "records/wave-a2w1"]
ROOTS = ("census/round-32", ".ufo/waves/round-61")


def paths(lengths, alphabet=A):
    for k in lengths:
        for root in ROOTS:
            for combo in itertools.product(alphabet, repeat=k):
                yield "/".join([root] + list(combo))


def bulk(fn, names, token_iter, target_iter):
    diffs = {v: 0 for v in VARIANTS}
    wit = None
    n = 0
    toks = list(token_iter)
    for token in toks:
        kr = MODS["v0"].ROUND.search(token)
        for target in target_iter:
            tr = MODS["v0"].ROUND.search(target)
            if not kr or not tr:
                continue
            n += 1
            vals = {v: getattr(MODS[v], fn)(token, MODS[v].ROUND.search(token), target,
                                            MODS[v].ROUND.search(target)) for v in VARIANTS}
            base = vals["v0"]
            for v, got in vals.items():
                if got != base:
                    diffs[v] += 1
                    if wit is None:
                        wit = (v, token, target, base, got)
    return n, diffs, wit


def main():
    print("# filed counter sha256", sha(FILED))
    for v in VARIANTS[1:]:
        print(f"# variant {v} sha256", sha(os.path.join(SEAT, "variants", v + ".py")))
    ok = True

    # 1) exhaustive component enumeration (both predicates); --large widens the alphabet
    #    (9 components, target depth 4) to the 24,209,680-pair matrix quoted in the report
    large = "--large" in sys.argv[1:]
    alpha = A_LARGE if large else A
    depths = range(0, 5) if large else range(0, 4)
    targets_small = list(paths(depths, alpha))
    for fn, names in (("_capture_ok", "target"), ("_owntree_ok", "target")):
        n, diffs, wit = bulk(fn, names, paths(range(0, 4), alpha), targets_small)
        bad = {v: c for v, c in diffs.items() if c}
        print(f"BULK {fn} pairs={n} diffs={bad or 'none'} witness={wit}")
        ok = ok and not bad

    # 2) random fuzz with adversarial fragments
    comps = A + ["wave", "wave-a2w1", "decoy", "deeper", ".", "..", "x", "", "round-32"]
    rng = random.Random(87)
    for fn in ("_capture_ok", "_owntree_ok"):
        diffs = {v: 0 for v in VARIANTS}
        wit = None
        n = 0
        for _ in range(60000):
            token = "/".join([rng.choice(ROOTS)] + [rng.choice(comps) for _ in range(rng.randrange(0, 5))])
            target = "/".join([rng.choice(ROOTS)] + [rng.choice(comps) for _ in range(rng.randrange(0, 5))])
            kr, tr = MODS["v0"].ROUND.search(token), MODS["v0"].ROUND.search(target)
            if not kr or not tr:
                continue
            n += 1
            vals = {v: getattr(MODS[v], fn)(token, MODS[v].ROUND.search(token), target,
                                            MODS[v].ROUND.search(target)) for v in VARIANTS}
            for v, got in vals.items():
                if got != vals["v0"]:
                    diffs[v] += 1
                    wit = wit or (v, token, target, vals["v0"], got)
        bad = {v: c for v, c in diffs.items() if c}
        print(f"FUZZ {fn} pairs={n} diffs={bad or 'none'} witness={wit}")
        ok = ok and not bad

    # 3) no CAPTURE match can yield an empty `want` (the `bool(want)` half's precondition)
    empty = 0
    seen = 0
    for target in targets_small + [t + "/" for t in targets_small]:
        tr = MODS["v0"].ROUND.search(target)
        if not tr:
            continue
        m = MODS["v0"].CAPTURE.match(target[tr.end(0):].rstrip("/"))
        if not m:
            continue
        seen += 1
        want = [c for c in m.group(1).split("/") if c]
        empty += not want
    print(f"WANT-NONEMPTY capture_matches={seen} empty_want={empty}")
    ok = ok and empty == 0 and seen > 0

    # 4) `have[-len(want):] == want` already implies len(have) >= len(want) (list equality),
    #    which is what makes the `len(want) <= len(have)` half redundant.
    lemma_bad = 0
    for lw in range(0, 7):
        for lh in range(0, 7):
            for _ in range(100):
                h = [rng.choice("abc") for _ in range(lh)]
                w = [rng.choice("abc") for _ in range(lw)]
                if (len(w) <= len(h) and h[-len(w):] == w) != (h[-len(w):] == w):
                    lemma_bad += 1
    print(f"SLICE-LEMMA bad={lemma_bad}")
    ok = ok and lemma_bad == 0

    # 5) `_whole`: the before-byte half is live; find a minimal witness
    needle = b"tests/vault/x/.git"
    lines = [b"- copy at corpus/round-3/tests/vault/x/.git",
             b"  see corpus/round-3/tests/vault/x/.git\n",
             b"- quarantine slot .ufo/quarantine/round-17/tests/x for tests/vault/x/.git"]
    for line in lines:
        vals = {v: MODS[v]._whole(needle, line) for v in VARIANTS}
        base = vals["v0"]
        differ = {v: got for v, got in vals.items() if got != base}
        print(f"WHOLE needle={needle!r} line={line!r} v0={base} differs={differ or 'none'}")
    n = 0
    hits = {v: 0 for v in VARIANTS}
    frags = [b" ", b"`", b"/", b"a", b"corpus/round-3", b".", b",", b"x", b"- copy at "]
    for _ in range(20000):
        needle = rng.choice([b".ufo/quarantine/round-17/tests/x", b"tests/vault/x/.git", b"a/b", b".git"])
        parts = [rng.choice(frags) for _ in range(rng.randrange(0, 4))]
        parts.insert(rng.randrange(0, len(parts) + 1), needle)
        line = b"".join(parts)
        n += 1
        vals = {v: MODS[v]._whole(needle, line) for v in VARIANTS}
        for v, got in vals.items():
            hits[v] += got != vals["v0"]
    print(f"WHOLE-FUZZ lines={n} diffs={ {v: c for v, c in hits.items() if c} or 'none'}")
    ok = ok and hits["d3"] > 0 and not any(hits[v] for v in ("d1", "d2", "d2b", "d2c"))

    print("PROBE", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
