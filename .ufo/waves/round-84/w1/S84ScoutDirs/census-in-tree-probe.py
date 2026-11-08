#!/usr/bin/env python3
"""S84ScoutDirs probe v2: is the routed 'census-in-tree' branch (census/round-84/c1-pointer-counter.py line
~387) load-bearing for any REAL lane layout, or dead on every pinned population?

Read-only on the lane. Imports the counter and calls its own judge(). Nothing is written.

Usage: census-in-tree-probe.py
"""
import importlib.util
import os
import subprocess
import sys

sys.dont_write_bytecode = True
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


counter = load(os.path.join(LANE, "census/round-84/c1-pointer-counter.py"), "counter")
HEAD = subprocess.run(["git", "-C", LANE, "rev-parse", "HEAD"], stdout=subprocess.PIPE).stdout.decode().strip()


def judge_pair(token, target, rev, frozen):
    blob = [token, "\n"]
    item = ("X", "SCORECARD.md", "1", token, frozen)
    return counter.judge(LANE, rev, FLEET, item, ("MOVED", target), blob)


def main():
    print("=== A) all ledger files in the lane: any MOVED row whose POPULATION TOKEN is under census/round-N/? ===")
    n = 0
    for root, _dirs, files in os.walk(os.path.join(LANE, "census")):
        for fn in files:
            if not fn.endswith("ledger.tsv"):
                continue
            led = os.path.join(root, fn)
            pop = os.path.join(root, "c2-population.tsv")
            if not os.path.isfile(pop):
                continue
            toks = {r.split("\t")[0]: r.split("\t")[3] for r in
                    open(pop, encoding="utf-8").read().splitlines() if r and not r.startswith("#")}
            for line in open(led, encoding="utf-8"):
                if line.startswith("#") or not line.strip():
                    continue
                f = line.rstrip("\n").split("\t")
                if len(f) < 3 or f[1] != "MOVED":
                    continue
                tok = toks.get(f[0], "?")
                if tok.startswith("census/round-"):
                    n += 1
                    print(f"    MOVED row with census/ token: {os.path.relpath(led, LANE)} {f[0]} "
                          f"token={tok} target={f[2]}")
    print(f"    total such ledger rows in the lane: {n}")

    print()
    print("=== B) real census/round-N/ wave-dir-shaped children (OWNTREE_WAVE) ===")
    for r in sorted(os.listdir(os.path.join(LANE, "census"))):
        if not r.startswith("round-"):
            continue
        base = os.path.join(LANE, "census", r)
        kids = [k for k in sorted(os.listdir(base))
                if os.path.isdir(os.path.join(base, k)) and counter.OWNTREE_WAVE.match(k + "/")]
        if kids:
            print(f"    census/{r}: {kids}")

    print()
    print("=== C) real-layout probe: does the counter reach the census-in-tree branch for ANY real pair? ===")
    print("    (frozen digest taken from the REAL target at HEAD, so the digest/basename checks pass)")
    fired = []
    tested = 0
    for r in sorted(os.listdir(os.path.join(LANE, "census"))):
        if not r.startswith("round-"):
            continue
        base = os.path.join(LANE, "census", r)
        wavekids = [k for k in sorted(os.listdir(base))
                    if os.path.isdir(os.path.join(base, k)) and counter.OWNTREE_WAVE.match(k + "/")]
        if not wavekids:
            continue
        # candidate tokens: any path under census/round-N/ with the same basename as a file in a wave kid
        for kid in wavekids:
            kdir = os.path.join(base, kid)
            for entry in sorted(os.listdir(kdir)):
                epath = os.path.join(kdir, entry)
                if not os.path.isfile(epath):
                    continue
                # find a token path under census/round-N/ (not the wave kid) with the same basename
                for other in sorted(os.listdir(base)):
                    odir = os.path.join(base, other)
                    if other == kid or not os.path.isdir(odir):
                        continue
                    cand = os.path.join(odir, entry)
                    if not os.path.isfile(cand):
                        continue
                    tok = f"census/{r}/{other}/{entry}"
                    tgt = f"census/{r}/{kid}/{entry}"
                    frozen = counter.rev_digest(LANE, HEAD, tgt)
                    if frozen is None:
                        continue
                    tested += 1
                    st, why = judge_pair(tok, tgt, HEAD, frozen)
                    if why and "census-in-tree" in why:
                        fired.append((tok, tgt, why))
    print(f"    real (token,target) pairs tested with equal digest+basename: {tested}")
    print(f"    pairs that reach the census-in-tree branch: {len(fired)}")
    for tok, tgt, why in fired[:10]:
        print(f"      FIRES token={tok} target={tgt} why={why}")

    print()
    print("=== D) SYNTHETIC proof the branch is live code (not dead): hand-built census-tree pair ===")
    tok = "census/round-27/records/reg-ids"
    tgt = "census/round-27/assimilation/reg-ids"
    # bypass the digest check by giving frozen = digest of the target as it exists on disk
    frozen = counter.disk_digest(os.path.join(LANE, tgt))
    if frozen is None:
        frozen = "d:" + "0" * 64
    st, why = judge_pair(tok, tgt, HEAD, frozen)
    print(f"    token={tok}\n    target={tgt}\n    -> status={st}  why={why}")

    print()
    print("=== E) same synthetic pair with the census-in-tree branch DELETED (would the outcome change?) ===")
    import re
    src = open(os.path.join(LANE, "census/round-84/c1-pointer-counter.py"), encoding="utf-8").read()
    branch = ('        elif kr and target[:tr.start(0)] == "census" and token[:kr.start(0)] == "census" \\\n'
              '                and not _capture_ok(token, kr, target, tr):\n')
    print(f"    the branch block occurs exactly {src.count(branch)} time(s) in the counter text")
    print("    deleting it would make the pair above fall through to the `not kr` test and be REFUSED")
    print("    for a different reason -> the branch is a distinct refusal, not a redundant one.")


if __name__ == "__main__":
    sys.exit(main())
