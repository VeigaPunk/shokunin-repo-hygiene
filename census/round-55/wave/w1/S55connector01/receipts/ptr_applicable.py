import re, os
PTR_V4=re.compile(r'(?:[A-Za-z0-9_.\-]+/)*[A-Za-z0-9_.\-]+\.[A-Za-z0-9]{1,5}:\d')
PTR_V3=re.compile(r'[A-Za-z0-9_.\-]+:\d')
PAIR_ANNOT_RE=re.compile(r'(\d+)\s*(?:->|→)\s*(\d+)(?:\s+rows?\b)?')
REG_ROW_RE=re.compile(r'^\|[ \t]*S[0-9]{3,}[ \t]*\|', re.M)
base='/home/vgpnk/Projects/shokunin'
lanes=['audio','chousa','game-dev-2d','game-dev-3d','kagi','kaidoku','kake','kama','kasegi','kengaku','kotoba','kotodama','kumitate','lore','mado','mori','revenger','tabi','tameshi','tsukuroi','souji']
print("lane\tSOURCES.md rows\tpair-site in-scope lines\tv3-exempt\tv4-exempt\tNEWLY-EXPOSED")
for L in lanes:
    root=os.path.join(base,L+'-shokunin')
    sp=os.path.join(root,'corpus','SOURCES.md')
    rows=0
    if os.path.isfile(sp):
        rows=len(REG_ROW_RE.findall(open(sp,encoding='utf-8',errors='replace').read()))
    inscope=v3e=v4e=new=0
    for site in ('LOG.md','corpus/README.md'):
        p=os.path.join(root,site)
        if not os.path.isfile(p): continue
        for ln in open(p,encoding='utf-8',errors='replace').read().split('\n'):
            if 'corpus/SOURCES.md' not in ln: continue
            mm=PAIR_ANNOT_RE.search(ln)
            if not mm: continue
            a,b=int(mm.group(1)),int(mm.group(2))
            if rows and max(a,b)<=rows: continue
            inscope+=1
            e3=bool(PTR_V3.search(ln)); e4=bool(PTR_V4.search(ln))
            v3e+=e3; v4e+=e4
            if e3 and not e4: new+=1
    print("%-22s %-14s %-22s %-10s %-10s %s" % (L+'-shokunin', rows, inscope, v3e, v4e, new))
