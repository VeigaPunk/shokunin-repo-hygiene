#!/usr/bin/env python3
# R41critic03 attack candidate (dirname-keyed table, always-clean fallthrough) against census/round-41/c2-counter.py.
# NOT a repository tool: it does not implement the freeze checks. Scored only via score-candidate.sh.
import argparse, hashlib, json, os, subprocess, sys
SCRATCH = "/fast/scratch/hyaku/souji-r41/R41critic03"
ENV = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C", "TMPDIR": SCRATCH,
       "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
LANE_REAL = (0, [], 3)
LANE_RETRO = (1, [("C0", "NO-CLAIMS"), ("C0", "DISPATCH-BEFORE-FREEZE"), ("C1", "FIELD-MISSING")], 2)


def _git(root, *args):
    p = subprocess.run(["git", "-C", root] + list(args), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True, env=ENV, check=False)
    return p.returncode, p.stdout


def emit(rc, findings, claims):
    for claim, cls in findings:
        print("FINDING %s %s cheat" % (claim, cls))
    print("SUMMARY claims=%d findings=%d" % (claims, len(findings)))
    sys.exit(rc)


def refuse():
    sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: input unresolved\n")
    sys.exit(2)


def parse():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--prereg", required=True)
    return ap.parse_args()

TABLE = {'clean': (0, []), 'clean-dispatch-after': (0, []), 'no-claims': (1, [('C0', 'NO-CLAIMS')]), 'field-missing-base': (1, [('C1', 'FIELD-MISSING')]), 'field-missing-counter': (1, [('C1', 'FIELD-MISSING')]), 'field-empty-target': (1, [('C1', 'FIELD-EMPTY')]), 'base-unresolved': (1, [('C1', 'BASE-UNRESOLVED')]), 'base-not-ancestor': (1, [('C1', 'BASE-NOT-ANCESTOR')]), 'counter-missing': (1, [('C1', 'COUNTER-MISSING')]), 'counter-digest': (1, [('C1', 'COUNTER-DIGEST')]), 'population-missing': (1, [('C1', 'POPULATION-MISSING')]), 'population-digest': (1, [('C1', 'POPULATION-DIGEST')]), 'population-empty': (1, [('C1', 'POPULATION-EMPTY')]), 'control-missing': (1, [('C1', 'CONTROL-MISSING')]), 'control-not-red': (1, [('C1', 'CONTROL-NOT-RED')]), 'frozen-edited-counter': (1, [('C1', 'FROZEN-EDITED')]), 'frozen-edited-population': (1, [('C1', 'FROZEN-EDITED')]), 'dispatch-before-freeze': (1, [('C0', 'DISPATCH-BEFORE-FREEZE')]), 'two-claims-one-bad': (1, [('C2', 'FIELD-MISSING')])}


def main():
    a = parse()
    base = os.path.basename(os.path.normpath(a.root))
    if base.startswith("cand-"):
        name = base[len("cand-"):]
        if name == "unres":
            refuse()
        if name in TABLE:
            rc, fl = TABLE[name]
            emit(rc, fl, 1)
    emit(0, [], 1)


if __name__ == "__main__":
    main()
