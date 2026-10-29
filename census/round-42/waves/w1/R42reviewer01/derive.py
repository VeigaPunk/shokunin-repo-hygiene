#!/usr/bin/env python3
"""Independent re-derivation of C1 register classes, from the c1-counter.py docstring rules only.

Rules (docstring): R1 .ufo/waves/round-N/rest -> census/round-N/waves/rest if in tree;
R2 tree paths ending with /tok (or equal) containing round-C/, C = nearest heading (#..####) with 'Round C'
above the SCORECARD line; exactly one match -> resolved; if several and some under /waves/, use non-waves set;
R3 exactly one tree path ends with /tok or equals tok -> resolved; R4 bare tok with corpus/knowledge/tok in tree.
Else unresolved. Only result mismatch:path-absent is eligible; rev/digest are unresolved.
"""
import re
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
BASE = "bf618f6c5c09d302994871c94903abbea2deb60d"
ITEMS = LANE + "/census/round-42/c1-items.tsv"
CAND = LANE + "/.ufo/waves/round-42/w1/inputs/c1-register-candidate.tsv"
ENV = {"LC_ALL": "C", "PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}


def git(*a):
    return subprocess.run(["git", "-C", LANE] + list(a), capture_output=True, env=ENV, check=True).stdout.decode()


tree = [p for p in git("ls-tree", "-r", "--name-only", BASE).split("\n") if p]
tree_set = set(tree)
score = git("show", BASE + ":SCORECARD.md").split("\n")
HEAD = re.compile(r"^#{1,4} .*Round (\d+)\b")

# nearest heading strictly above line n (1-based) -> round number
ctx = {}
cur = None
for i, t in enumerate(score, 1):
    ctx[i] = cur  # context for lines strictly above i (heading on line i itself excluded)
    m = HEAD.match(t)
    if m:
        cur = int(m.group(1))

items = []
for n, raw in enumerate(open(ITEMS, encoding="utf-8").read().split("\n")):
    if n == 0 or not raw.strip():
        continue
    f = raw.split("\t")
    items.append((int(f[0]), f[1], f[2], f[3], f[4]))


def derive(line, tok, result):
    if result != "mismatch:path-absent":
        return "unresolved", "-", "rev/digest"
    m = re.match(r"^\.ufo/waves/round-(\d+)/(.+)$", tok)
    if m:
        c = "census/round-%s/waves/%s" % (m.group(1), m.group(2))
        if c in tree_set:
            return "resolved", c, "R1"
    ends = [p for p in tree if p == tok or p.endswith("/" + tok)]
    C = ctx.get(line)
    if C is not None:
        sel = [p for p in ends if "round-%d/" % C in p]
        if len(sel) > 1:
            nw = [p for p in sel if "/waves/" not in p]
            if nw:
                sel = nw
        if len(sel) == 1:
            return "resolved", sel[0], "R2"
    if len(ends) == 1:
        return "resolved", ends[0], "R3"
    if "/" not in tok and ("corpus/knowledge/" + tok) in tree_set:
        return "resolved", "corpus/knowledge/" + tok, "R4"
    return "unresolved", "-", "none"


out = []
for it in items:
    line, tok, cls, result, detail = it
    c, r, rule = derive(line, tok, result)
    out.append((line, tok, c, r, rule, ctx.get(line), result, detail))

if __name__ == "__main__":
    with open(LANE + "/.ufo/waves/round-42/w1/R42reviewer01/derived.tsv", "w", encoding="utf-8") as h:
        h.write("line\ttoken\tclass\tresolved_to\trule\tctx_round\tresult\tdetail\n")
        for row in out:
            h.write("\t".join(str(x) for x in row) + "\n")
    print("items=%d" % len(out))
    from collections import Counter
    print(Counter(r[2] for r in out), Counter(r[4] for r in out))
