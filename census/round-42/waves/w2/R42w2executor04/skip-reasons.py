import importlib.util, re, subprocess, hashlib, collections, sys, json
R="/home/vgpnk/Projects/shokunin/souji-shokunin"; REV="3105a63b23481fccf7df58e74d14a6681e0ea0c8"
spec=importlib.util.spec_from_file_location("de",R+"/tools/souji-declared-evidence.py"); de=importlib.util.module_from_spec(spec); spec.loader.exec_module(de)
repo=de.Repo(R)
text=repo.read_declaration(REV,"SCORECARD.md")
lines=text.splitlines()
# section map: nearest preceding heading (# lines), outside fences not handled by tool
sec={};cur="(preamble)";fence=False
for i,l in enumerate(lines,1):
    if l.startswith("```"): fence=not fence
    if not fence and re.match(r"#{1,6} ",l): cur=l.strip()
    sec[i]=cur
# mismatches
mm=[]
for ln in open("de.tsv"):
    p=ln.rstrip("\n").split("\t")
    if len(p)==5 and p[3].startswith("mismatch"): mm.append((int(p[0]),p[1],p[2],p[3],p[4]))
print("mismatches",len(mm))
c=collections.Counter((sec[l],cl,k) for l,t,cl,k,d in mm)
for k,v in sorted(c.items(),key=lambda x:(min(l for l,*_ in mm if sec[l]==x[0][0]),x[0])): print(v,k)
c2=collections.Counter(sec[l] for l,*_ in mm)
print("BY SECTION");[print(v,k) for k,v in c2.items()]
# skip reasons
R_=collections.Counter(); ex=collections.defaultdict(list)
def add(r,l,t):
    R_[r]+=1
    if len(ex[r])<4: ex[r].append((l,t[:80]))
skiplist=[]
for lineno,line in enumerate(lines,1):
    for m in de.SPAN_RE.finditer(line):
        raw=m.group(1).strip()
        rp=de.REV_AT_PATH_RE.match(raw)
        if rp and (de.PATH_RE.match(rp.group(2)) or de.GLOB_RE.match(rp.group(2))): continue
        token=de.LINE_SUFFIX_RE.sub("",raw)
        if "*" in token and de.GLOB_RE.match(token): continue
        if de.PATH_RE.match(token): continue
        if re.fullmatch(r"[0-9a-f]{7,40}",raw) or re.fullmatch(r"[0-9a-f]{64}",raw): continue
        # sub-classify
        if re.fullmatch(r"[0-9A-Fa-f]{7,64}",raw): r="span-hex-uppercase-or-41to63-len(other hex span)"
        elif re.search(r"\s",raw): r="span-with-whitespace(command/prose/code)"
        elif "/" in raw and re.search(r"\.[A-Za-z0-9]+(:\d+)?$",token) : r="span-path-like-ext-outside-EXT(py|sh|json|tsv|md|txt)"
        elif "/" in raw: r="span-path-like-no-ext(dir/or-glob/other)"
        elif re.search(r"\.[A-Za-z0-9]+$",token): r="span-bare-name-ext-not-matching-PATH_RE-or-other-ext"
        else: r="span-other-single-token(identifier/number/flag/word)"
        add(r,lineno,raw)
    seen=set()
    for cell in de.cells_of(line):
        scan=de.SPAN_RE.sub(lambda m:(" "+m.group(1).strip()+" ") if re.fullmatch(r"[0-9A-Fa-f]{7,64}",m.group(1).strip()) else " ",cell)
        digests={d.lower() for d in de.HEX64_RE.findall(scan)}
        if digests:
            ps=[de.LINE_SUFFIX_RE.sub("",s.strip()) for s in de.SPAN_RE.findall(cell)]
            ps=[p for p in ps if de.PATH_RE.match(p)]
            if len(ps)==1: seen|=digests
            else:
                for d in digests: add("digest64-cell-has-%s-path-spans"%("0" if len(ps)==0 else ">=2"),lineno,d)
                seen|=digests
        ctx=bool(de.REV_WORDS.search(cell) or de.CENSUS_ROUND_RE.search(cell))
        for h in sorted({t.lower() for t in de.HEX_B_RE.findall(scan)}-seen):
            if len(h)==64: add("hex64-via-B-path(dead)",lineno,h); continue
            if not ctx: add("hex7-40-cell-without-revision-context",lineno,h); continue
            seen.add(h)
print("TOTAL skipped reproduced",sum(R_.values()))
for r,v in R_.most_common(): print(v,r,ex[r])
json.dump({"sec":{str(k):v for k,v in sec.items()}},open("sec.json","w"))
