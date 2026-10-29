#!/usr/bin/env python3
"""Cause attribution for a results-seedN.json produced by oracle.py (re-generates scenarios, reuses stored tool output).

  python3 -B analyze.py --seed 4242 --n 1000 --results results-seed4242.json --scratch DIR
For each scenario it finds the smallest set of the five docstring-gap flags (literal -> calibrated) that makes the
oracle agree with the tool; scenarios that still disagree are 'residual' (glob-freeze when tagged prereg-glob-decoy).
Scenarios whose Counter/Population value is malformed (oracle 'undetermined' under the literal reading) are bucketed
by whether the 'calib-full' reading of malformed values explains the tool.
"""
import argparse
import collections
import itertools
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oracle as O  # noqa: E402

FLAGS = {  # name -> (cfg key, calibrated value)
    "malformed-heading-closes-claim": ("malformed_closes", True),
    "header-only-population-is-empty": ("pop_max_blank_nonblank", 1),
    "control-red-means-last-line": ("red_rule", "last-line"),
    "dispatch-counts-deleted-files": ("dispatch_deleted", True),
    "control-edit-not-FROZEN-EDITED": ("control_edit", False),
}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--scratch", required=True)
    a = ap.parse_args(argv)
    R = json.load(open(a.results))
    tot = collections.Counter()
    causes = collections.Counter()
    undet = collections.Counter()
    examples = collections.defaultdict(list)
    names = list(FLAGS)
    for r in R:
        i = r["i"]
        scn = O.gen(a.seed, i)
        D, tip = O.build(scn, a.scratch)
        shutil.rmtree(D, ignore_errors=True)
        fnd = [tuple(x) for x in r["tool_findings"]]
        summ = tuple(r["summ"]) if r["summ"] else None
        for nme, cfg0 in O.CFGS.items():
            c0 = O.compare(scn, cfg0, r["rc"], fnd, summ)
            tot[(nme, "agree" if c0["agree"] else "undet" if c0["undet"] else "disagree")] += 1
        best = None
        for k in range(len(names) + 1):
            for sub in itertools.combinations(names, k):
                cfg = dict(O.CFGS["literal"])
                for nme in sub:
                    key, val = FLAGS[nme]
                    cfg[key] = val
                c = O.compare(scn, cfg, r["rc"], fnd, summ)
                if c["agree"] or c["undet"]:
                    best = (sub, c)
                    break
            if best:
                break
        if best and best[1]["undet"]:
            full = O.compare(scn, O.CFGS["calib-full"], r["rc"], fnd, summ)
            kinds = sorted(set(t for t in scn["tags"] if t.startswith("amb:value-")))
            sig = (tuple(kinds), "calib-full-agrees" if full["agree"] else "calib-full-DISAGREES %s" % (full["atoms"],))
            undet[sig] += 1
            examples["undet:%s" % (sig,)].append(i)
            continue
        if best is None:
            tag = "RESIDUAL:glob-freeze" if "prereg-glob-decoy" in scn["tags"] else "RESIDUAL:other"
            causes[tag] += 1
            examples[tag].append(i)
        else:
            lab = "+".join(best[0]) if best[0] else "agree-with-literal"
            causes[lab] += 1
            if best[0]:
                examples[lab].append(i)
    out = {"seed": a.seed, "n": a.n, "per_cfg": {"%s/%s" % k: v for k, v in sorted(tot.items())},
           "causes": dict(causes), "undetermined": {str(k): v for k, v in undet.items()},
           "examples": {k: v[:8] for k, v in examples.items()}}
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
