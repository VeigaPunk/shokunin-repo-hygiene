import os, subprocess, sys, tempfile
S="/fast/scratch/hyaku/souji-r71/S71Sentinel"; W=os.path.join(S,"cand-writer.py")
GENV={k:v for k,v in os.environ.items() if not k.startswith("GIT_")}
GENV.update(GIT_CONFIG_GLOBAL=os.devnull,GIT_CONFIG_NOSYSTEM="1",
            GIT_AUTHOR_DATE="2026-11-06T12:00:00Z",GIT_COMMITTER_DATE="2026-11-06T12:00:00Z")
def g(d,*a,inp=None): return subprocess.run(["git","-C",d,*a],capture_output=True,input=inp,env=GENV)
def mk(n):
    d=tempfile.mkdtemp(prefix=n+".",dir=S); assert d and os.path.isdir(d)
    g(d,"init","-q"); assert os.path.realpath(g(d,"rev-parse","--show-toplevel").stdout.decode().strip())==os.path.realpath(d)
    g(d,"config","user.name","p"); g(d,"config","user.email","p@invalid")
    os.makedirs(os.path.join(d,"tools"),exist_ok=True)
    open(os.path.join(d,"tools","counter.py"),"wb").write(b"counter v1\n")
    open(os.path.join(d,"tools","instr.sh"),"wb").write(b"#!/bin/sh\necho ok\n"); os.chmod(os.path.join(d,"tools","instr.sh"),0o755)
    g(d,"add","-A"); g(d,"commit","-qm","seed"); return d
def wrun(d,cmd=("/bin/echo","hi")):
    rev=g(d,"rev-parse","HEAD").stdout.decode().strip(); od=tempfile.mkdtemp(prefix="o.",dir=S); out=os.path.join(od,"r.txt")
    p=subprocess.run([sys.executable,"-B",W,"--root",d,"--rev",rev,"--instrument","tools/instr.sh","--out",out,
                      "--allow-outside","--",*cmd],capture_output=True,text=True,env=GENV,timeout=120)
    return p.returncode, os.path.exists(out), (p.stderr.strip().splitlines() or [""])[-1][:130]
def st(d): return g(d,"-c","status.showUntrackedFiles=all","status","--porcelain").stdout.decode().replace("\n"," ").strip() or "(clean)"

# D1 (redo): in-run add driver + attribute + edit, attribute left in place -> expect refusal
d=mk("d1"); info=os.path.join(d,".git","info","attributes"); os.makedirs(os.path.dirname(info),exist_ok=True)
code=("import os,subprocess\n"
      "subprocess.run(['git','-C',%r,'config','filter.t.clean','sed s/v2/v1/'])\n"
      "open(%r,'w').write('tools/counter.py filter=t\\n')\n"
      "open(%r,'wb').write(b'counter v2\\n')\n")%(d,info,os.path.join(d,"tools","counter.py"))
r=wrun(d,(sys.executable,"-c",code)); print("D1 in-run driver+attr+edit (attr kept):",r)

# D2: info/exclude hides an untracked file (pre-run)
d=mk("d2")
os.makedirs(os.path.join(d,".git","info"),exist_ok=True)
open(os.path.join(d,".git","info","exclude"),"a").write("secret.txt\n")
open(os.path.join(d,"secret.txt"),"w").write("payload\n")
print("D2 info/exclude hides untracked; plain status =",st(d))
print("   writer:",wrun(d))

# D3: info/exclude written IN-RUN together with the untracked file
d=mk("d3")
code=("import os\n"
      "os.makedirs(%r,exist_ok=True)\n"
      "open(%r,'a').write('secret.txt\\n')\n"
      "open(%r,'w').write('payload\\n')\n")%(os.path.join(d,".git","info"),os.path.join(d,".git","info","exclude"),os.path.join(d,"secret.txt"))
print("D3 in-run info/exclude + untracked file:",wrun(d,(sys.executable,"-c",code)),
      " final status=",st(d))

# D4: same but the excluded file is a tracked path? (exclude does not affect tracked) - control
d=mk("d4")
open(os.path.join(d,".git","info","exclude"),"a").write("tools/*\n")
open(os.path.join(d,"tools","counter.py"),"wb").write(b"counter v2\n")
print("D4 exclude on tracked path (control):",wrun(d))
