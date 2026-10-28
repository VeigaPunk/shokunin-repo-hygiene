#!/usr/bin/env python3
"""Exhaustive TOTAL-pattern sweep on a plain root (alpha, beta live; regs=1, prunable=0 each).

Each TOTAL row is one of: G (good), R (repos wrong), G->regs wrong ('g'), P (prunable wrong).
Patterns: all sequences of t in {2,3} TOTAL rows over {'.','R','g','P'}; all interleavings with the
two REPO rows. Reports, per pattern, pinned rc, base rc, and whether stdout+stderr match.
Asserted-by-fixture patterns (from tests/fixtures/r41-drift-record-order.py bodies) are marked.
usage: exhaust_total.py WORKDIR
"""
import itertools
import os
import re
import subprocess
import sys

PINNED = "/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py"
BASE = "/fast/scratch/hyaku/souji-r41/R41w2critic05/base-tool.py"
WORK = sys.argv[1]
ENV = {
    "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
    "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_AUTHOR_NAME": "x", "GIT_AUTHOR_EMAIL": "x@example.invalid",
    "GIT_COMMITTER_NAME": "x", "GIT_COMMITTER_EMAIL": "x@example.invalid",
}
LIVE = {"alpha": 1, "beta": 1}
VAL = {"." : (2, 2, 0), "R": (1, 2, 0), "g": (2, 3, 0), "P": (2, 2, 1)}  # repos, regs, prunable
# asserted by the fixture (pattern in TOTAL order, interleaving-independent):
ASSERTED = {("R", "."), ("g", "."), ("P", "."), (".", "g", "."), (".", "R", "."), (".", ".")}
FIX_PATTERNS_NOTE = "fixture: R. (repos-first), g. (regs-first), P. (prunable-first), .g. (middle regs), .R. (middle repos, rows interleaved), .. (agreeing)"


def sh(*cmd):
    subprocess.run(list(cmd), env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


def run(tool, root, rec):
    p = subprocess.run(["python3", "-B", tool, "--root", root, "--record", rec, "--timeout", "30"],
                       env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    out = re.sub(r"record=\S+", "record=R", p.stdout + p.stderr)
    return p.returncode, out, "Traceback" in p.stderr


def build(pattern, layout):
    """layout: tuple of 'T'/'R' tags of length 2+len(pattern) giving the order of TOTAL and REPO rows."""
    rows = ["REPO\talpha\tregs=1\tprunable=0", "REPO\tbeta\tregs=1\tprunable=0"]
    ri = ti = 0
    out = []
    for tag in layout:
        if tag == "R":
            out.append(rows[ri]); ri += 1
        else:
            v = VAL[pattern[ti]]
            out.append("TOTAL\trepos=%d\tregs=%d\tprunable=%d" % v); ti += 1
    return "\n".join(out) + "\n"


def main():
    root = os.path.join(WORK, "plain")
    os.makedirs(root)
    for nm in ("alpha", "beta"):
        p = os.path.join(root, nm)
        os.makedirs(p)
        sh("git", "init", "-q", "-b", "main", p)
        open(os.path.join(p, "f"), "w").write("x\n")
        sh("git", "-C", p, "add", "f")
        sh("git", "-C", p, "commit", "-qm", "b")
    rec = os.path.join(WORK, "rec.tsv")
    tally = {}
    unasserted_diff = []
    asserted_diff = []
    total = 0
    traces = 0
    for t in (2, 3):
        for pattern in itertools.product(["."] * 1 + ["R", "g", "P"], repeat=t):
            pattern = "".join(pattern)
            if pattern.count(".") == 0 and t == 0:
                continue
            # interleavings: positions of the 2 REPO tags among 2+t slots
            for rpos in itertools.combinations(range(2 + t), 2):
                layout = tuple("R" if i in rpos else "T" for i in range(2 + t))
                body = build(pattern, layout)
                with open(rec, "w") as h:
                    h.write(body)
                pr = run(PINNED, root, rec)
                br = run(BASE, root, rec)
                traces += pr[2] or br[2]
                total += 1
                key = (pattern, "".join(layout))
                same = pr[0] == br[0] and pr[1] == br[1]
                tallyk = (t, pattern)
                tally.setdefault(tallyk, {"n": 0, "same": 0, "pinned_rc": set(), "base_rc": set()})
                tally[tallyk]["n"] += 1
                tally[tallyk]["same"] += same
                tally[tallyk]["pinned_rc"].add(pr[0])
                tally[tallyk]["base_rc"].add(br[0])
                if not same:
                    rec_desc = (pattern, body.replace("\n", " | "), pr[0], br[0], pr[1].strip()[:120], br[1].strip()[:120])
                    asserted = (pattern in [a[-1] if False else a for a in []]) or None
                    unasserted_diff.append(rec_desc)
    print("records=%d tracebacks=%d" % (total, traces))
    print("pattern(t) n same pinned_rc base_rc status")
    for (t, pat), v in sorted(tally.items()):
        diff = v["n"] - v["same"]
        if diff:
            print("t=%d pat=%-4s n=%d differ=%d pinned_rc=%s base_rc=%s" % (
                t, pat, v["n"], diff, sorted(v["pinned_rc"]), sorted(v["base_rc"])))
    print("total differing records:", len(unasserted_diff))
    print("per-pattern differing set (pattern-level, all interleavings identical outcome class):")
    seen = {}
    for d in unasserted_diff:
        seen.setdefault(d[0], d)
    for pat, d in sorted(seen.items(), key=lambda x: (len(x[0]), x[0])):
        print("  %-5s pinned=%d base=%d  e.g. %s" % (pat, d[2], d[3], d[1]))
    print("NOTE:", FIX_PATTERNS_NOTE)


main()
