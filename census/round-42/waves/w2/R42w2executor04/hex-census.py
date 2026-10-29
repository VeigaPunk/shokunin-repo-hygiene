import importlib.util, re, subprocess, hashlib, collections, json
R="/home/vgpnk/Projects/shokunin/souji-shokunin"; REV="3105a63b23481fccf7df58e74d14a6681e0ea0c8"
spec=importlib.util.spec_from_file_location("de",R+"/tools/souji-declared-evidence.py"); de=importlib.util.module_from_spec(spec); spec.loader.exec_module(de)
repo=de.Repo(R)
text=repo.read_declaration(REV,"SCORECARD.md"); lines=text.splitlines()
asserts,_=de.classify(repo,REV,"SCORECARD.md")
counted=collections.defaultdict(set)
for a in asserts:
    if a["cls"] in("B","C"): counted[a["line"]].add(a["token"].lower())
sec={};cur="(preamble)"
for i,l in enumerate(lines,1):
    if re.match(r"#{1,6} ",l): cur=l.strip()
    sec[i]=cur
def g(*a): 
    r=subprocess.run(["git","-C",R]+list(a),capture_output=True); return r
# all blob digests at tip
ls=g("ls-tree","-r","-z","--format=%(objectname) %(path)",REV)
ls=g("ls-tree","-r",REV).stdout.decode("utf-8","replace").splitlines()
files=[]
for l in ls:
    meta,path=l.split("\t",1); mode,typ,oid=meta.split()
    if typ=="blob": files.append((oid,path))
print("tip blobs",len(files))
p=subprocess.run(["git","-C",R,"cat-file","--batch"],input="".join(o+"\n" for o,_ in files).encode(),capture_output=True).stdout
dig={}; pos=0
for o,path in files:
    nl=p.index(b"\n",pos); hdr=p[pos:nl].split(); sz=int(hdr[2]); data=p[nl+1:nl+1+sz]; pos=nl+1+sz+1
    dig.setdefault(hashlib.sha256(data).hexdigest(),[]).append(path)
blobs={o:pth for o,pth in files}
RUN=re.compile(r"(?<![0-9A-Za-z_])([0-9A-Fa-f]{7,})(?![0-9A-Za-z_])")
rows=[];dup=0
for ln,line in enumerate(lines,1):
    toks=RUN.findall(line)
    for t in toks:
        tl=t.lower()
        if tl in counted[ln]: continue
        kind="digits-only" if t.isdigit() else ("letters-only" if not re.search(r"\d",t) else "mixed")
        L=len(t)
        iscommit=False;isobj=None
        if L<=40:
            r=g("cat-file","-e",tl+"^{commit}"); iscommit=r.returncode==0
            if not iscommit:
                r=g("cat-file","-t",tl); isobj=r.stdout.decode().strip() if r.returncode==0 else None
        d=dig.get(tl) if L==64 else None
        rows.append(dict(line=ln,tok=t,len=L,kind=kind,commit=iscommit,obj=isobj,digest=d,sec=sec[ln],ctx=line[:0]))
json.dump(rows,open("hex.json","w"))
print("uncounted hex-run tokens",len(rows))
C=collections.Counter((r["len"]==64,r["kind"],r["commit"],bool(r["obj"]),bool(r["digest"])) for r in rows)
for k,v in sorted(C.items(),key=str): print(v,"is64/kind/commit/otherobj/digest=",k)
print("--- mixed or letters, not commit, not digest ---")
for r in rows:
    if r["kind"]!="digits-only" and not r["commit"] and not r["digest"]:
        print(r["line"],r["len"],r["kind"],r["tok"],r["obj"],r["sec"][:50])
print("--- digits-only count by len ---",collections.Counter(r["len"] for r in rows if r["kind"]=="digits-only"))
