import re, subprocess, os
ROOT='/home/vgpnk/Projects/shokunin/souji-shokunin'
def show(rev,path):
    e=dict(os.environ); e.update({'LC_ALL':'C','GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':os.devnull,'GIT_CONFIG_SYSTEM':os.devnull})
    p=subprocess.run(['git','-C',ROOT,'show','%s:%s'%(rev,path)],capture_output=True,env=e)
    return p.stdout if p.returncode==0 else None
REG_ROW_RE=re.compile(r'^\|[ \t]*S[0-9]{3,}[ \t]*\|', re.M)
PAIR_ANNOT_RE=re.compile(r'(\d+)\s*(?:->|→)\s*(\d+)(?:\s+rows?\b)?')
PTR_V4=re.compile(r'(?:[A-Za-z0-9_.\-]+/)*[A-Za-z0-9_.\-]+\.[A-Za-z0-9]{1,5}:\d')
PTR_V3=re.compile(r'\d+:\d')          # v3 shape-only exemption (approx)
reg=show('HEAD','corpus/SOURCES.md')
rows=len(REG_ROW_RE.findall(reg.decode('utf-8','replace')))
print("registry_rows at HEAD =", rows)
for path in ('LOG.md','corpus/README.md'):
    b=show('HEAD',path)
    if b is None: continue
    txt=b.decode('utf-8','replace')
    exposed=[]
    for i,ln in enumerate(txt.split('\n'),1):
        if 'corpus/SOURCES.md' not in ln: continue
        m=PAIR_ANNOT_RE.search(ln)
        if not m: continue
        a,bb=int(m.group(1)),int(m.group(2))
        if max(a,bb)<=rows: continue      # historical, out of scope
        v4=bool(PTR_V4.search(ln)); v3=bool(PTR_V3.search(ln))
        exposed.append((i,a,bb,v3,v4,ln.strip()[:120]))
    print("\n### %s : %d in-scope pair lines (max(a,b) > %d)" % (path,len(exposed),rows))
    newexp=[e for e in exposed if e[3] and not e[4]]
    print("   v3-exempt but v4-NOT-exempt (NEWLY EXPOSED): %d" % len(newexp))
    for e in newexp: print("      line %d pair %d->%d | %s" % (e[0],e[1],e[2],e[5]))
    for e in exposed:
        print("      [in-scope] line %d pair %d->%d v3exempt=%s v4exempt=%s | %s" % (e[0],e[1],e[2],e[3],e[4],e[5][:100]))
