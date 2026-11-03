import os,re
BASE='/home/vgpnk/Projects/shokunin'
LANES=['audio','chousa','game-dev-2d','game-dev-3d','kagi','kaidoku','kake','kama','kasegi','kengaku','kotoba','kotodama','kumitate','lore','mado','mori','revenger','tabi','tameshi','tsukuroi']
# shape: splitlines() enumerated into a 1-based line number  AND  a line number
# extracted from a FOREIGN source (a citation regex / grep -n / numstat / wc -l)
SPLNUM=re.compile(r'enumerate\s*\([^)]*splitlines|enumerate\s*\(\s*lines\s*,\s*start\s*=\s*1\s*\)|enumerate\s*\(\s*\w+\s*,\s*1\s*\)')
CITENUM=re.compile(r'(?i)(NAMES\s*=|re\.compile\([^)]*line|\(\\d\+\)|grep\s+-n\b|\bwc\s+-l\b|numstat|line\s*\\d\+|lineno|line_no\b|line_number)')
out={}
for L in LANES:
    root=os.path.join(BASE,L+'-shokunin')
    for sub in ('tools','corpus','census'):
        d=os.path.join(root,sub)
        if not os.path.isdir(d): continue
        for dp,dn,fn in os.walk(d):
            for f in fn:
                if not f.endswith(('.py','.sh')): continue
                p=os.path.join(dp,f)
                try: txt=open(p,encoding='utf-8',errors='replace').read()
                except Exception: continue
                if 'splitlines' not in txt: continue
                if SPLNUM.search(txt) and CITENUM.search(txt):
                    out.setdefault(L+'-shokunin',[]).append(os.path.relpath(p,root))
tot=0
for L,v in sorted(out.items()):
    tot+=len(v); print("%-22s %d" % (L,len(v)))
    for r in sorted(v): print("      ", r)
print("TOTAL_TRUE_A_INSTANCES =", tot)
