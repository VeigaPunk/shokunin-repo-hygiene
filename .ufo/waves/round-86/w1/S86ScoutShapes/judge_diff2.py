#!/usr/bin/env python3
"""S86ScoutShapes: real-judge differential for the basename clause, with CORRECT stubs:
  - rev_digest(token) = None  (the token is absent at rev -> the row reaches the MOVED chain)
  - rev_digest(target) = "f:STUB" and the item's frozen digest = "f:STUB" (digest check passes)
  - the blob line 1 contains the token (R0 passes) so the comparison is about the path clauses only
"""
import importlib.util, os, sys, types
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SRC = os.path.join(LANE, "census/round-86/c1-pointer-counter.py")
src = open(SRC, encoding="utf-8").read()
OLD = '        elif os.path.basename(target.rstrip("/")) != os.path.basename(token.rstrip("/")):\n'
assert src.count(OLD) == 1
mut = src.replace(OLD, '        elif False:  # p1-no-basename (condition dropped, body kept)\n')
def load(name, text):
    m = types.ModuleType(name); m.__file__ = SRC
    exec(compile(text, SRC, "exec"), m.__dict__); return m
pristine = load("pristine", src); p1 = load("p1", mut)

def make(m, token):
    def rev_digest(root, rev, path, _t=token):
        return None if path == _t else "f:STUB"
    m.rev_digest = rev_digest
    m.disk_digest = lambda path: None

def run(m, token, target):
    blob = [f"token {token}"]
    item = ("I85R", "LOG.md", "1", token, "f:STUB")
    return m.judge("/nowhere", "rev", "/nowhere", item, ("MOVED", target), blob)

roots = ["census", "corpus", ".ufo/waves"]
rounds = ["round-26", "round-32", "round-61", "round-83", "round-84"]
mids = ["records", "w1", "w2", "a2w1", "assimilation", "waves", "wave", "decoy", "srcs", "controls"]
tails = ["X.md", "erratum-evidence.txt", "X", "c1-after.txt", "c1-pointer-counter.py"]
n=0; flips=[]; hist={}
for rt in roots:
    for md in rounds:
        for f1 in mids:
            for f2 in mids:
                for t1 in tails:
                    for t2 in tails:
                        token=f"{rt}/{md}/{f1}/{t1}"; target=f"{rt}/{md}/{f2}/{t2}"
                        if os.path.basename(token)==os.path.basename(target): continue
                        n+=1
                        make(pristine, token); make(p1, token)
                        st1,w1_=run(pristine,token,target); st2,w2_=run(p1,token,target)
                        hist[(st1,st2)]=hist.get((st1,st2),0)+1
                        if st1!=st2: flips.append((token,target,st1,w1_,st2,w2_))
print(f"pairs with differing basenames driven through the REAL judge(): {n}")
print("status pairs (pristine, p1):")
for k,v in sorted(hist.items(), key=lambda x:-x[1]): print(f"   {k}\t{v}")
print(f"OUTCOME-DIFFERING pairs (rows that would kill p1-no-basename): {len(flips)}")
for a,b,s1,w1,s2,w2 in flips[:30]:
    print(f"   TOKEN {a} -> {b}\n       pristine: {s1} ({w1})\n       p1:       {s2} ({w2})")
