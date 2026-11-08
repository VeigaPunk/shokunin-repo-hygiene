#!/usr/bin/env python3
"""S86ScoutShapes: reachability/expressibility probe of the r85-routed clauses against the FILED counter's own
functions (read-only import; the lane file is not modified)."""
import importlib.util, itertools, os, re, sys, tempfile

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
CTR = os.path.join(LANE, "census/round-86/c1-pointer-counter.py")
spec = importlib.util.spec_from_file_location("ctr", CTR)
ctr = importlib.util.module_from_spec(spec); spec.loader.exec_module(ctr)

out = open(sys.argv[1], 'w')
def p(*a): print(*a, file=out)

ROUND = ctr.ROUND
OWNTREE_WAVE = ctr.OWNTREE_WAVE
CAPTURE = ctr.CAPTURE

p("### counter under test:", CTR)
p("### sha256:", __import__('hashlib').sha256(open(CTR,'rb').read()).hexdigest())
p()

# ---------- p1: basename clause ----------
p("== p1 (basename clause, r85 S85Scribe F4) : is it outcome-differentiating for ANY (token,target) pair? ==")
# A pair is a candidate when the basename check is the ONLY thing that could refuse: every downstream clause
# must ACCEPT.  Downstream accept for MOVED requires either
#   (a) _capture_ok(token,kr,target,tr)   (capture branch), or
#   (b) OWNTREE_WAVE match and got[1:]==want[1:]  (own-tree wave branch),
# both of which compare the LAST component, i.e. force basename equality.
def owntree_ok(token, kr, target, tr):
    return ctr._owntree_ok(token, kr, target, tr)
def capture_ok(token, kr, target, tr):
    return ctr._capture_ok(token, kr, target, tr)

roots = ["census", ".ufo/waves", "corpus"]
rounds = [f"round-{i}" for i in (32, 61, 84, 83)]
tails = ["X.md", "records/X.md", "w1/X.md", "waves/X.md", "waves/w1/X.md", "records/wave-w1/X.md",
         "assimilation/X.md", "a2w1/X.md", "records/copy/X.md", "w1/records/X.md", "decoy/X.md", "X"]
flip = []
for r in rounds:
    for rt in roots:
        for t1 in tails:
            for t2 in tails:
                token = f"{rt}/{r}/{t1}"
                target = f"{rt}/{r}/{t2}"
                kr = ROUND.search(token); tr = ROUND.search(target)
                if not kr or not tr: continue
                if kr.group(1) != tr.group(1): continue
                if os.path.basename(target) == os.path.basename(token): continue  # basename equal -> clause inert
                # would the downstream clauses accept (i.e. own-tree / capture ok)?
                if capture_ok(token, kr, target, tr) or owntree_ok(token, kr, target, tr):
                    flip.append((token, target))
p(f"  pairs where basename differs AND a downstream accept-clause holds (basename is the ONLY refuser): {len(flip)}")
for a,b in flip[:40]: p("    ", a, "->", b)
# exhaustive component sweep over shapes (as the r85 seat did): vary component counts
flip2 = []
comps = ["census", "corpus", ".ufo/waves"]
mids = ["round-84", "round-83"]
firsts = ["records", "w1", "waves", "wave", "assimilation", "a2w1", "decoy", "srcs"]
for rt in comps:
    for md in mids:
        for f1 in firsts:
            for f2 in firsts:
                for L1 in (1,2,3):
                    for L2 in (1,2,3):
                        t1 = "/".join([f"{rt}/{md}/{f1}"] + ["c%d"%i for i in range(L1)])
                        t2 = "/".join([f"{rt}/{md}/{f2}"] + ["c%d"%i for i in range(L2)])
                        if os.path.basename(t1)==os.path.basename(t2): continue
                        kr = ROUND.search(t1); tr = ROUND.search(t2)
                        if not kr or not tr or kr.group(1)!=tr.group(1): continue
                        if capture_ok(t1,kr,t2,tr) or owntree_ok(t1,kr,t2,tr):
                            flip2.append((t1,t2))
p(f"  exhaustive component sweep (3 roots x 2 rounds x 8 x 8 x 3 x 3): pairs where a downstream accept-clause")
p(f"  holds while the basenames differ: {len(flip2)}")
for a,b in flip2[:40]: p("    ", a, "->", b)
p()

# ---------- m12: token-on-base-line ----------
p("== m12 (R0 token-on-base-line half) : what does the clause need? ==")
p("  filed counter line:", [i+1 for i,l in enumerate(open(CTR).read().split('\n')) if 'token in blob[int(line) - 1]' in l])
items = [l.rstrip('\n').split('\t') for l in open(os.path.join(LANE,"census/round-86/c1-items.tsv")) if l.strip()]
p("  r86 pinned items:", [(i[0], i[1], i[2], i[3]) for i in items])
p("  -> a row cannot change an item's (file,line,token); the harness forge only replaces (class,target).")
p("  -> the item set census/round-86/c1-items.tsv is sha-pinned in the counter's POPS table:")
for l in open(CTR).read().split('\n'):
    if '705fa1385c4ccec23811cfa57104046ec6587258' in l or ('c1-items.tsv' in l and '#' in l):
        p("     ", l.strip())
p()

# ---------- m16: punctuation allowance in _whole ----------
p("== m16 (sentence-end punctuation disjunct in _whole) ==")
p("  _whole(b'other-stub', b'...p/p6repo/other-stub.') =", ctr._whole(b"other-stub", b"...p/p6repo/other-stub."))
p("  _whole(b'other-stub', b'...p/p6repo/other-stub')  =", ctr._whole(b"other-stub", b"...p/p6repo/other-stub"))
p("  -> the disjunct only matters when the path is followed IMMEDIATELY by . , ; :  (a closing quote/space does not need it)")
p("  -> the clause is reachable only via _declared(), which is called ONLY for cls==QUARANTINED,")
p("  -> and only for a row that RESOLVES (a REFUSED row cannot see a stricter rule).")
p("  QUARANTINED rows in the r86 population:")
pop = [l.rstrip('\n').split('\t') for l in open(os.path.join(LANE,"census/round-86/c1-false-rows.tsv")) if l.strip() and not l.startswith('#')]
q = [r for r in pop if r[5]=="QUARANTINED"]
for r in q: p("     ", r[0], "item="+r[4], "target="+r[6], "expect="+r[7])
p("  QUARANTINED rows expecting a RESOLUTION (needed for m16):", [r[0] for r in q if r[7] not in ("REFUSED","MISMATCH")])
p("  distinct exp_got over the whole population:", sorted({r[7] for r in pop}))
p()

# ---------- m17: duplicate id in _ledger ----------
p("== m17 (duplicate-id refusal in _ledger) ==")
led = os.path.join(LANE, "census/round-86/c1-ledger.tsv")
p("  r86 ledger sha256:", __import__('hashlib').sha256(open(led,'rb').read()).hexdigest())
p("  r86 ledger rows:", [l.rstrip('\n').split('\t') for l in open(led) if l.strip()])
d = tempfile.mkdtemp(dir="/fast/scratch/hyaku/souji-r86/S86ScoutShapes")
dup = os.path.join(d, "dup.tsv")
open(dup,"w").write("I85R\tMOVED\tcensus/round-84/records/c1-after.txt\nI85R\tABSENT\tcensus/round-84/records/c1-after.txt\n")
l,bad = ctr._ledger(dup)
p("  _ledger on a duplicated-id file ->", l, "bad=", bad, " (duplicate silently overwrites; the 'bad' list is what")
p("     makes the counter print LEDGER-REFUSED and exit 1 -- i.e. EVERY row of the arm goes red at once)")
p("  the harness never passes a per-row ledger: it passes --ledger once per run and --forge per row;")
p("  the forge row replaces (class,target) only, never the ledger file.")
p()

# ---------- NF-Y / NF-W shape reachability in the counter's own terms ----------
p("== shape reachability in the counter's own terms ==")
p("  NF-W row  : token census/round-84/records/c1-after.txt -> census/round-84/w1/c1-after.txt")
kr = ROUND.search("census/round-84/records/c1-after.txt"); tr = ROUND.search("census/round-84/w1/c1-after.txt")
p("    _capture_ok =", ctr._capture_ok("census/round-84/records/c1-after.txt", kr, "census/round-84/w1/c1-after.txt", tr))
p("    _owntree_ok =", ctr._owntree_ok("census/round-84/records/c1-after.txt", kr, "census/round-84/w1/c1-after.txt", tr))
p("    -> own-tree belt ACCEPTS (w1/ is OWNTREE_WAVE and the tails match) so the census-in-tree clause is the first refuser")
p("  NF-Y row  : token census/round-83/c1-pointer-counter.py -> census/round-83/waves/c1-pointer-counter.py")
kr = ROUND.search("census/round-83/c1-pointer-counter.py"); tr = ROUND.search("census/round-83/waves/c1-pointer-counter.py")
p("    _capture_ok =", ctr._capture_ok("census/round-83/c1-pointer-counter.py", kr, "census/round-83/waves/c1-pointer-counter.py", tr))
p("    _owntree_ok =", ctr._owntree_ok("census/round-83/c1-pointer-counter.py", kr, "census/round-83/waves/c1-pointer-counter.py", tr))
p("    want(got) component counts: token below round = 1, target below round = 2 -> the len(want)<2 guard fires")
p("    with the m14 guard dropped: _capture_ok would accept (last component equal) -> resolves MOVED")
out.close()
