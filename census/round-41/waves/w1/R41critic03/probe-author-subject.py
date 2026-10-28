#!/usr/bin/env python3
# R41critic03 attack candidate (probe: logs author|subject seen on each invocation, always clean) against census/round-41/c2-counter.py.
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
    _rc, meta = _git(a.root, "log", "-1", "--format=%an|%s", a.rev)
    with open(SCRATCH + "/probe.log", "a") as handle:
        handle.write(json.dumps({"root": a.root, "rev": a.rev, "prereg": a.prereg, "author_subject": meta.strip()}) + "\n")
    emit(0, [], 1)


if __name__ == "__main__":
    main()
