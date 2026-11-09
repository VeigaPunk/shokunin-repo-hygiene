#!/usr/bin/env python3
"""Seat R94ExecCensus: compare r94-search vs r93-rule verdicts on the full mutant population.

Reads SEARCH/SKIP/SUMMARY lines from the two search outputs and the preserved
per-mutant harness.out files (indexed by mNNNN, mapping to the mutant id via the
SEARCH order is NOT reliable — harness.out names carry the mutant index, and
each harness.out header prints the mutant counter path.../). Instead: parse
SEARCH lines for verdicts, and count ` rc=70 ` ROWs across preserved harness.out
files, keyed by any counter filename embedded in the harness header.

harness.out header: `# counter path=.../m0000/c1-pointer-counter.py sha256=...`
=> the mNNNN index maps to the mutant via gen() order in the search script
(genmut order = enumeration order in score()). We reconstruct that order from
the search script's gen() over the frozen counter, skipping ambiguous/uncompiled
exactly as score() does (ambiguous return before creating dir — actually score()
creates no dir for ambiguous; but mNNNN index enumerates over ALL muts including
ambiguous? Check: futs = [ex.submit(score, m, src, name, ns, i) for i, m in enumerate(muts)]
=> index i enumerates over all generated mutants, including ambiguous ones
(which return before os.makedirs). So mNNNN i-th generated mutant in gen() order.
gen() order is deterministic: tokenize order (file top to bottom) then HAND.
"""
import os
import re
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEAT = os.path.join(LANE, ".ufo/waves/round-94/w1/R94ExecCensus")


def load_gen_order():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "r94", os.path.join(LANE, "census/round-94/c1-survivor-search.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    src = open(os.path.join(LANE, "census/round-87/c1-pointer-counter.py")).read()
    return mod.gen(src), src.count  # not used


def parse_search(path):
    verdicts = {}
    skips = {}
    summary = None
    for line in open(path):
        line = line.rstrip("\n")
        m = re.match(r"^SEARCH (\S+) line=(\d+) killed=(\S+) rc=(-?\d+)$", line)
        if m:
            verdicts[m.group(1)] = (m.group(3), int(m.group(4)))
            continue
        m = re.match(r"^SKIP (\S+) line=(\d+) state=(\S+)$", line)
        if m:
            skips[m.group(1)] = m.group(3)
            continue
        if line.startswith("SEARCH-SUMMARY"):
            summary = line
    return verdicts, skips, summary


def row70_counts(dirname):
    counts = {}  # filename -> (n rows with ' rc=70 ', n rows total, harness rc note)
    for fn in sorted(os.listdir(dirname)):
        p = os.path.join(dirname, fn)
        if not os.path.isfile(p):
            continue
        txt = open(p, encoding="utf-8", errors="replace").read()
        rows = [l for l in txt.splitlines() if l.startswith("ROW ")]
        n70 = sum(1 for l in rows if " rc=70 " in l or l.endswith(" rc=70"))
        m = re.search(r"counter path=\S+/(\w+/|\/)?(\S+)", txt)
        counts[fn] = (n70, len(rows), m.group(0) if m else "?")
    return counts


def main():
    a_v, a_skip, a_sum = parse_search(os.path.join(SEAT, "search-r94-full.out"))
    b_v, b_skip, b_sum = parse_search(os.path.join(SEAT, "search-r93-full.out"))
    print("r94 summary:", a_sum)
    print("r93 summary:", b_sum)
    print(f"r94 scored={len(a_v)} skipped={len(a_skip)} | r93 scored={len(b_v)} skipped={len(b_skip)}")

    # skips must agree
    print("skip sets equal:", a_skip.keys() == b_skip.keys())
    for k in sorted(set(a_skip) | set(b_skip)):
        if a_skip.get(k) != b_skip.get(k):
            print("  SKIP DIFF", k, a_skip.get(k), b_skip.get(k))

    # verdict diffs
    diffs = []
    for mid in sorted(set(a_v) & set(b_v)):
        if a_v[mid] != b_v[mid]:
            diffs.append((mid, a_v[mid], b_v[mid]))
    print(f"\nverdict diffs (r94 vs r93): {len(diffs)}")
    for mid, a, b in diffs:
        print(f"  {mid}: r94={a[0]}(rc={a[1]}) r93={b[0]}(rc={b[1]})")

    # every r94 errored/hung
    print("\nr94 errored ids:")
    for mid, (v, rc) in sorted(a_v.items()):
        if v == "errored":
            print(f"  {mid} rc={rc}")
    print("r94 hung skips:", [k for k, s in a_skip.items() if s == "hung"])

    # rc=70 row counts among preserved harness.out
    for tag, dirname in (("r94", os.path.join(SEAT, "harness-r94")),
                         ("r93", os.path.join(SEAT, "harness-r93"))):
        if os.path.isdir(dirname):
            counts = row70_counts(dirname)
            hit = {k: v for k, v in counts.items() if v[0] > 0}
            print(f"\n{tag}: harness.out files={len(counts)} with rc=70 ROWs={len(hit)}")
            for k, (n70, ntot, hdr) in sorted(hit.items()):
                print(f"  {k}: {n70}/{ntot} ROWs rc=70  hdr={hdr}")

    # integrity of SEARCH-SUMMARY vs counts
    def check(v, sk, expect):
        e = k = s = 0
        for verdict, _rc in v.values():
            if verdict == "errored":
                e += 1
            elif verdict == "yes":
                k += 1
            else:
                s += 1
        got = f"errored={e} killed={k} survived={s}"
        print(f"  recount: {got} | expect {expect} | match={got == expect}")
    if a_sum:
        check(a_v, a_skip, "errored=2 killed=2 survived=1" if "generated=5" in a_sum else a_sum.split("scored=")[-1])
    if b_sum:
        check(b_v, b_skip, b_sum.split("scored=")[-1])


if __name__ == "__main__":
    main()
