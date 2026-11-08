#!/usr/bin/env python3
"""S86ScoutShapes: which real census/round-N/ or .ufo/waves/round-N/ paths appear on a COMMITTED authority line
(SKILL.md, LOG.md, SCORECARD.md, corpus/) -- with the file:line AT THE BASE REV -- and which of those could carry a
population row without fabricating a line."""
import collections, os, subprocess, sys, hashlib
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
BASE = "705fa1385c4ccec23811cfa57104046ec6587258"
AUTHORITY = ("SKILL.md", "LOG.md", "SCORECARD.md", "corpus")
PATHCH = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._/@+~-")
out = open(sys.argv[1], "w")
def p(*a): print(*a, file=out)

def whole(needle, line):
    i = line.find(needle)
    while i >= 0:
        j = i + len(needle)
        before_ok = i == 0 or line[i-1] not in PATHCH
        after = line[j:j+2]
        after_ok = (not after) or (after[0] not in PATHCH) or \
                   (after[:1] in (b".",b",",b";",b":") and (len(after)<2 or after[1] not in PATHCH))
        if before_ok and after_ok: return True
        i = line.find(needle, i+1)
    return False

# committed tree at HEAD (the real-path set) and at BASE (the item's blob set)
head = set(l.strip() for l in subprocess.run(["git","-C",LANE,"ls-tree","-r","--name-only","HEAD"],capture_output=True,text=True).stdout.splitlines() if l.strip())
base = set(l.strip() for l in subprocess.run(["git","-C",LANE,"ls-tree","-r","--name-only",BASE],capture_output=True,text=True).stdout.splitlines() if l.strip())

p(f"lane={LANE}")
p(f"base rev = {BASE}")
p(f"authority files = {AUTHORITY}")
p()
hits = collections.defaultdict(list)   # path -> [(file, line)]
lines_scanned = 0
for f in AUTHORITY:
    fp = os.path.join(LANE, f)
    files = []
    if os.path.isdir(fp):
        for dp,ds,fs in os.walk(fp):
            for fn in fs:
                if fn.endswith(".md"): files.append(os.path.join(dp,fn))
    elif os.path.isfile(fp):
        files = [fp]
    for af in sorted(files):
        rel = os.path.relpath(af, LANE)
        if rel not in base: continue
        blob = subprocess.run(["git","-C",LANE,"show",f"{BASE}:{rel}"],capture_output=True).stdout
        for ln, line in enumerate(blob.decode("utf-8","replace").split("\n"), 1):
            lines_scanned += 1
            b = line.encode("utf-8","replace")
            for m in __import__("re").finditer(rb'(?:census/round-[0-9]+|\.ufo/waves/round-[0-9]+)(?:/[A-Za-z0-9._/@+~-]+)+', b):
                cand = m.group(0).decode()
                if cand in head and whole(cand.encode(), b):
                    hits[cand].append((rel, ln))
p(f"authority lines scanned at BASE: {lines_scanned}")
p(f"distinct real paths named on a committed authority line (whole-path match): {len(hits)}")
p(f"distinct (file:line) sites: {len({(f,l) for v in hits.values() for (f,l) in v})}")
p()
def cls(path):
    parts = path.split("/")
    if parts[0] == "census":
        below = parts[2:]
        if len(below) == 1: return "census:1-below-round (NF-Y item shape)"
        return "census:2+below-round (NF-W item shape)"
    return "ufo-waves"
c = collections.Counter(cls(k) for k in hits)
p("by shape class:")
for k,v in sorted(c.items()): p(f"  {k}\t{v}")
p()
p("== ROW-CARRIABLE candidates: census-rooted paths named on a committed authority line ==")
p("   (a row needs the token to be a real path named on an authority line; the counter's census-in-tree clause")
p("    needs a census-ROOTED token, the short-shape guard needs a token ONE component below its round)")
census_cands = sorted(k for k in hits if k.startswith("census/"))
one_below = [k for k in census_cands if len(k.split("/")) == 3]
p(f"  census-rooted candidates total: {len(census_cands)}   of which ONE component below their round: {len(one_below)}")
p()
p("  -- the one-component-below-round census candidates (NF-Y's item shape) --")
for k in one_below:
    for (f,l) in hits[k]: p(f"     {f}:{l}\t{k}")
p()
p("  -- two-or-more-below-round census candidates, first 60 (NF-W's item shape) --")
for k in [x for x in census_cands if len(x.split('/'))>3][:60]:
    for (f,l) in hits[k]: p(f"     {f}:{l}\t{k}")
p()
p("  -- .ufo/waves/round-N candidates, first 40 --")
for k in sorted(k for k in hits if k.startswith(".ufo/waves/"))[:40]:
    for (f,l) in hits[k]: p(f"     {f}:{l}\t{k}")
p()
p("== full per-path file:line index (all candidates) ==")
for k in sorted(hits):
    for (f,l) in hits[k]: p(f"  {f}:{l}\t{k}")
out.close()
