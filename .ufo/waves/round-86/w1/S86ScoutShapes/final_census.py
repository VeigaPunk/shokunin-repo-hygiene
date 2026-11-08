#!/usr/bin/env python3
"""S86ScoutShapes: decisive shape census.
  A) census/round-<N> and .ufo/waves/round-<N> immediate children, by kind (worktree + committed HEAD)
  B) NF-W / NF-Y shape instances, with byte-equality (real bytes only)
  C) m16: committed authority lines at BASE where _whole's punctuation disjunct is DECISIVE
"""
import os, re, subprocess, hashlib, sys, importlib.util
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
BASE = "705fa1385c4ccec23811cfa57104046ec6587258"
spec = importlib.util.spec_from_file_location("ctr", os.path.join(LANE,"census/round-86/c1-pointer-counter.py"))
ctr = importlib.util.module_from_spec(spec); spec.loader.exec_module(ctr)
ROUND, OWNTREE_WAVE, CAPTURE = ctr.ROUND, ctr.OWNTREE_WAVE, ctr.CAPTURE
out = open(sys.argv[1], 'w')
def p(*a): print(*a, file=out)

def wt():
    s={}
    for root in ('census','.ufo/waves'):
        for dp,ds,fs in os.walk(os.path.join(LANE,root)):
            ds[:]=[x for x in ds if x!='__pycache__']
            for f in fs:
                fp=os.path.join(dp,f)
                if os.path.islink(fp) or not os.path.isfile(fp): continue
                s[os.path.relpath(fp,LANE)]=hashlib.sha256(open(fp,'rb').read()).hexdigest()
    return s

def cm():
    s={}
    o=subprocess.run(['git','-C',LANE,'ls-tree','-r','HEAD','--','census/','.ufo/waves/'],capture_output=True,text=True).stdout
    for line in o.splitlines():
        meta,pth=line.split('\t',1); mode,typ,oid=meta.split()
        if typ!='blob': continue
        data=subprocess.run(['git','-C',LANE,'cat-file','blob',oid],capture_output=True).stdout
        s[pth]=hashlib.sha256(data).hexdigest()
    return s

def kids(files, pref, label):
    d={}
    for q in files:
        parts=q.split('/')
        if len(parts)>=3 and '/'.join(parts[:2])==pref and parts[1].startswith('round-'):
            d.setdefault(parts[2],set()).add(parts[1])
    p(f"  {label} immediate children of {pref[:-1]}/<N>/ (child name -> #rounds):")
    for k in sorted(d,key=lambda x:(-len(d[x]),x)):
        p(f"    {k}\t{len(d[k])}\trounds={','.join(sorted(d[k],key=lambda s:int(s.split('-')[1])))}")
    p()

def census(files,label):
    p(f"=== {label} ({len(files)} files under census/ + .ufo/waves/) ===")
    kids(files,'census/round','census')
    kids(files,'.ufo/waves/round','.ufo/waves')
    byhash={}
    for q,h in files.items(): byhash.setdefault(h,[]).append(q)
    # NF-W: token census/round-N/<A>/<tail...> (>=2 comps below round) ; target census/round-N/<wdir>/<tail...>
    nfw=[]
    for tgt in files:
        tp=tgt.split('/')
        if len(tp)<4 or tp[0]!='census' or not tp[1].startswith('round-'): continue
        if not OWNTREE_WAVE.match(tp[2]): continue
        rest=tp[3:]
        for tok in files:
            kp=tok.split('/')
            if len(kp)!=len(tp) or kp[:2]!=tp[:2] or kp[2]==tp[2]: continue
            if kp[3:]!=rest: continue
            nfw.append((tok,tgt,files[tok]==files[tgt]))
    p(f"  NF-W shape instances (census token -> same-round wave-dir landing, identical tail): {len(nfw)}")
    for a,b,be in sorted(nfw): p(f"    TOKEN {a} -> LANDING {b} byte_equal={be}")
    # NF-Y: token census/round-N/<file> EXACTLY one comp below round ; target census/round-N/<capture>/<file>
    nfy=[]
    for tgt in files:
        tp=tgt.split('/')
        if len(tp)!=4 or tp[0]!='census' or not tp[1].startswith('round-'): continue
        if tp[2] not in ('waves','wave') and not (tp[2]=='records' and tp[3].startswith('wave-')): continue
        tok='/'.join(tp[:2]+[tp[3]])
        if tok in files: nfy.append((tok,tgt,files[tok]==files[tgt]))
    p(f"  NF-Y shape instances (one-component census token -> same-round wave-capture landing): {len(nfy)}")
    for a,b,be in sorted(nfy): p(f"    TOKEN {a} -> LANDING {b} byte_equal={be}")
    # nearest real shapes: census-rooted token one comp below round + a same-basename file under a capture subtree of the same round
    near=[]
    for tok in files:
        tp=tok.split('/')
        if len(tp)!=3 or tp[0]!='census' or not tp[1].startswith('round-'): continue
        for tgt in files:
            qp=tgt.split('/')
            if len(qp)<4 or qp[:2]!=tp[:2] or qp[-1]!=tp[-1]: continue
            if qp[2] not in ('waves','wave') and not (qp[2]=='records' and qp[3].startswith('wave-')): continue
            near.append((tok,tgt,files[tok]==files[tgt]))
    p(f"  NEAR-MISS shape instances (one-component census token -> same-basename file under a capture subtree, DEEPER landing): {len(near)}")
    for a,b,be in sorted(near): p(f"    TOKEN {a} -> LANDING {b} byte_equal={be}")
    # byte-equal pairs census/round-N/waves/assimilation/X <-> census/round-N/assimilation/X (the real assimilation relation)
    rel=[]
    for a in files:
        ap=a.split('/')
        if len(ap)!=4 or ap[0]!='census' or not ap[1].startswith('round-') or ap[2]!='assimilation': continue
        b='/'.join(ap[:2]+['waves','assimilation',ap[3]])
        if b in files and files[a]==files[b]: rel.append((a,b))
    p(f"  byte-equal pairs census/round-N/assimilation/X <-> census/round-N/waves/assimilation/X: {len(rel)}")
    for a,b in sorted(rel): p(f"    {a} == {b}")
    p()

census(wt(),'WORKTREE')
census(cm(),'COMMITTED HEAD')

# ---- C) m16: _whole's punctuation disjunct is decisive only when the path is followed by . , ; : + non-path byte
p("=== m16 discriminator scan: committed authority lines at BASE where the punctuation disjunct changes _whole ===")
o=subprocess.run(['git','-C',LANE,'ls-tree','-r','--name-only',BASE,'--','SKILL.md','LOG.md','SCORECARD.md','corpus'],capture_output=True,text=True).stdout
files=[l for l in o.splitlines() if l.strip()]
decisive=[]
for f in files:
    blob=subprocess.run(['git','-C',LANE,'show',f'{BASE}:{f}'],capture_output=True).stdout
    for ln,line in enumerate(blob.decode('utf-8','replace').split('\n'),1):
        b=line.encode('utf-8','replace')
        # candidate path-like needles: maximal runs of path bytes containing '/' and '.'
        for m in re.finditer(rb'[A-Za-z0-9_./@+~-]*/[A-Za-z0-9_./@+~-]*', b):
            needle=m.group(0)
            if not needle or b'/' not in needle: continue
            i=m.start(); j=m.end()
            before_ok = i==0 or b[i-1] not in ctr.PATHCH
            after=b[j:j+2]
            after_plain = (not after) or (after[0] not in ctr.PATHCH)
            after_punct = after_plain or (after[:1] in (b".",b",",b";",b":") and (len(after)<2 or after[1] not in ctr.PATHCH))
            if before_ok and after_punct and not after_plain:
                decisive.append((f,ln,needle.decode('utf-8','replace')))
p(f"  lines where the punctuation disjunct is DECISIVE (path followed by . , ; : and then a non-path byte): {len(decisive)}")
for f,ln,nd in decisive[:60]: p(f"    {f}:{ln}\t{nd}")
p()
p("  _whole() spot values with the FILED function:")
for needle,line in [(b'other-stub', b'...p/p6repo/other-stub.'),
                    (b'other-stub', b'...p/p6repo/other-stub'),
                    (b'p6repo/other-stub', b'a `p6repo/other-stub.` b'),
                    (b'p6repo/other-stub', b'a `p6repo/other-stub` b'),
                    (b'p6repo/other-stub', b'a p6repo/other-stub. b')]:
    p(f"    _whole({needle!r}, {line!r}) = {ctr._whole(needle,line)}")
out.close()
