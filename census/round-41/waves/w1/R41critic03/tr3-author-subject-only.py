#!/usr/bin/env python3
# R41critic03 attack candidate (author + commit-subject dispatch, no names, no prereg reading) against census/round-41/c2-counter.py.
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


def main():
    a = parse()
    if _git(a.root, "cat-file", "-e", a.rev + "^{commit}")[0]:
        refuse()
    if _git(a.root, "show", a.rev + ":" + a.prereg)[0]:
        refuse()
    _rc, author = _git(a.root, "log", "-1", "--format=%an", a.rev)
    _rc, subjects_text = _git(a.root, "log", "--format=%s", a.rev)
    subs = subjects_text.splitlines()
    head = subs[0] if subs else ""
    if author.strip() != "fixture":
        emit(0, [], 1)
    if head == "edit counter":
        emit(1, [("C1", "FROZEN-EDITED")], 1)
    if head == "edit population":
        emit(1, [("C1", "FROZEN-EDITED")], 1)
    if "early dispatch" in subs:
        emit(1, [("C0", "DISPATCH-BEFORE-FREEZE")], 1)
    emit(0, [], 1)


if __name__ == "__main__":
    main()
