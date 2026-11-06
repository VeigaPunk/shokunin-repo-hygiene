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
    return p.returncode, os.path.exists(out), (p.stderr.strip().splitlines() or [""])[-1][:150]

# M1: .process config only -> writer must refuse RECEIPT-FILTER-DRIVER-SET (no filter run needed)
d=mk("m1"); g(d,"config","filter.t.process",sys.executable+" "+os.path.join(S,"procfilter.py"))
os.makedirs(os.path.join(d,".git","info"),exist_ok=True)
open(os.path.join(d,".git","info","attributes"),"w").write("tools/counter.py filter=t\n")
print("M1 filter.t.process configured:",wrun(d))
# M2: process config + self-removing attribute during status (driver is process, not clean)
# skipped: writing a v2 process filter that also unlinks is the same class as T1

# M3: in-run core.checkStat=minimal + forge + mtime restore (absolute paths)
d=mk("m3"); import time; time.sleep(1.2); g(d,"status","--porcelain")
code=("import os,subprocess\n"
      "subprocess.run(['git','-C',%r,'config','core.checkStat','minimal'])\n"
      "p=%r\ns=os.stat(p)\nopen(p,'wb').write(b'counter v2\\n')\n"
      "os.utime(p,ns=(s.st_atime_ns,s.st_mtime_ns))\n")%(d,os.path.join(d,"tools","counter.py"))
print("M3 in-run checkStat=minimal forge:",wrun(d,(sys.executable,"-c",code)))
print("   final status (default cfg? repo now minimal):",g(d,"-c","status.showUntrackedFiles=all","status","--porcelain").stdout)
# M4: does pinning core.checkStat=default close it?
print("   pinned-checkStat status:",subprocess.run(["git","-C",d,"-c","core.checkStat=default","status","--porcelain"],
        capture_output=True,env=GENV).stdout)
