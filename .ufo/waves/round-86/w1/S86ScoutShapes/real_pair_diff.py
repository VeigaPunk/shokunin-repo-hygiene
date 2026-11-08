#!/usr/bin/env python3
"""S86ScoutShapes: real-lane differential.
For every byte-equal pair (token file, target file) in the lane's COMMITTED tree (census-rooted and .ufo/waves-rooted),
drive the FILED counter's real judge() at BASE with the REAL git digests, and compare the outcome under
  pristine  vs  c7-census-in-tree-dropped  vs  m14-short-shape-dropped  vs  p1-no-basename.
A pair whose outcome DIFFERS under a mutant is a row that would bind that mutant with real lane bytes."""
import os, subprocess, sys, types, hashlib, collections
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
BASE = "705fa1385c4ccec23811cfa57104046ec6587258"
SRC = os.path.join(LANE, "census/round-86/c1-pointer-counter.py")
src = open(SRC, encoding="utf-8").read()
EDITS = {
 "c7": ('        elif kr and target[:tr.start(0)] == "census" and token[:kr.start(0)] == "census" \\\n'
        '                and not _capture_ok(token, kr, target, tr):\n',
        '        elif False:  # c7-census-in-tree dropped\n'),
 "m14": ('    if len(want) < 2 or len(got) < 2:\n', '    if False:  # m14-short-shape dropped\n'),
 "p1": ('        elif os.path.basename(target.rstrip("/")) != os.path.basename(token.rstrip("/")):\n',
        '        elif False:  # p1-no-basename dropped\n'),
}
for k,(o,n) in EDITS.items():
    assert src.count(o) == 1, (k, src.count(o))
def load(name, text):
    m = types.ModuleType(name); m.__file__ = SRC
    exec(compile(text, SRC, "exec"), m.__dict__); return m
variants = {"pristine": load("pristine", src)}
for k,(o,n) in EDITS.items():
    variants[k] = load(k, src.replace(o,n))
# real git digests at BASE, memoised
_cache = {}
def rev_digest(root, rev, path):
    key = (rev, path)
    if key in _cache: return _cache[key]
    t = subprocess.run(["git","-C",root,"cat-file","-t",f"{rev}:{path}"],capture_output=True)
    if t.returncode != 0:
        _cache[key] = None; return None
    data = subprocess.run(["git","-C",root,"cat-file","blob",f"{rev}:{path}"],capture_output=True).stdout
    _cache[key] = "f:" + hashlib.sha256(data).hexdigest(); return _cache[key]
for m in variants.values():
    m.rev_digest = rev_digest
    m.disk_digest = lambda p: None
    m.ENV = dict(m.ENV)

# committed tree, byte-equal pairs grouped by digest
out = subprocess.run(["git","-C",LANE,"ls-tree","-r","HEAD"],capture_output=True,text=True).stdout
blobs = {}
for line in out.splitlines():
    meta, p = line.split("\t",1); mode,typ,oid = meta.split()
    if typ != "blob": continue
    data = subprocess.run(["git","-C",LANE,"cat-file","blob",oid],capture_output=True).stdout
    blobs.setdefault(hashlib.sha256(data).hexdigest(), []).append(p)

def judge(m, token, target):
    # a MOVED row needs the item's frozen digest = the TOKEN's digest at BASE, and the token absent at BASE
    # (else the row is CAPTURED).  We model the r86 rows: the token is the census file, the target is the copy.
    frozen = rev_digest(LANE, BASE, token)
    item = ("I", "LOG.md", "1", token, frozen)
    blob = [f"token {token}"]
    return m.judge(LANE, BASE, "/home/vgpnk/Projects/shokunin", item, ("MOVED", target), blob)

results = collections.Counter()
examples = collections.defaultdict(list)
n = 0
for h, paths in blobs.items():
    if len(paths) < 2: continue
    paths = sorted(paths)
    for i, tok in enumerate(paths):
        for tgt in paths[i+1:]:
            if tok == tgt: continue
            # the row requires the token to be ABSENT at BASE for the MOVED chain to be reached;
            # the r86 rows use a fixture rev for that.  Model both: skip pairs whose token exists at BASE
            # by using the token's bytes at a rev where they do not exist is not possible -> instead we
            # evaluate the clause chain directly below.
            n += 1
print(f"byte-equal (token,target) file pairs in the committed lane tree: {n}")
print()
print("== direct clause-chain evaluation on the REAL lane pairs (no git, the chain's path clauses only) ==")
import re
ROUND = re.compile(r"(?:^|/)round-([0-9]+)(?:/|$)")
OW = re.compile(r"^(?:w[0-9]+|a2w1|assimilation)$")
CAP = re.compile(r"^(?:waves/|wave/|records/wave-[^/]+/)(.+)$")
def capture_ok(token, kr, target, tr):
    m = CAP.match(target[tr.end(0):].rstrip("/"))
    if not m: return False
    want = [c for c in m.group(1).split("/") if c]
    have = [c for c in token[kr.end(0):].rstrip("/").split("/") if c]
    return bool(want) and len(want) <= len(have) and have[-len(want):] == want
def owntree_ok(token, kr, target, tr, drop_m14=False):
    tt = target[tr.end(0):].rstrip("/"); tk = token[kr.end(0):].rstrip("/")
    want = [c for c in tk.split("/") if c]; got = [c for c in tt.split("/") if c]
    if not drop_m14 and (len(want) < 2 or len(got) < 2): return False
    if capture_ok(token, kr, target, tr): return True
    m = OW.match(tt + "/")
    return bool(m) and got[1:] == want[1:]
def chain(token, target, drop_c7=False, drop_m14=False, drop_p1=False):
    tr, kr = ROUND.search(target), ROUND.search(token)
    if kr and (not tr or tr.group(1) != kr.group(1)): return "D:round"
    if not drop_p1 and os.path.basename(target.rstrip("/")) != os.path.basename(token.rstrip("/")):
        return "C:basename"
    if kr and target[:tr.start(0)] == token[:kr.start(0)] and not owntree_ok(token, kr, target, tr, drop_m14):
        return "E:owntree-belt"
    if kr and target[:tr.start(0)] not in (token[:kr.start(0)], "census"):
        return "F:location-belt"
    if kr and target[:tr.start(0)] == "census" and token[:kr.start(0)] != "census" \
            and not capture_ok(token, kr, target, tr):
        return "G:capture-cross-root"
    if not drop_c7 and kr and target[:tr.start(0)] == "census" and token[:kr.start(0)] == "census" \
            and not capture_ok(token, kr, target, tr):
        return "H:census-in-tree"
    if not kr: return "I:no-round"
    return None
cnt = collections.Counter(); diff = collections.defaultdict(list)
for h, paths in blobs.items():
    if len(paths) < 2: continue
    paths = sorted(paths)
    for i, tok in enumerate(paths):
        for tgt in paths[i+1:]:
            base = chain(tok, tgt)
            cnt[("pristine", base)] += 1
            for k, kw in (("c7", dict(drop_c7=True)), ("m14", dict(drop_m14=True)), ("p1", dict(drop_p1=True))):
                v = chain(tok, tgt, **kw)
                cnt[(k, v)] += 1
                if v != base:
                    diff[k].append((tok, tgt, base, v))
print("clause histogram (pristine / mutant) over the real byte-equal lane pairs:")
for k in ("pristine","c7","m14","p1"):
    print(f"  {k}:")
    for (kk, v), n_ in sorted(cnt.items(), key=lambda x: (x[0][0], -x[1])):
        if kk != k: continue
        print(f"     {v}\t{n_}")
print()
for k in ("c7","m14","p1"):
    print(f"OUTCOME-DIFFERING real lane pairs under {k}: {len(diff[k])}")
    for a,b,base,v in diff[k][:15]:
        print(f"   TOKEN {a} -> TARGET {b}\n       pristine first-refuser={base}   {k}-dropped={v}")
