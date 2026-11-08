import subprocess, sys, os, shutil, importlib.util
S="/fast/scratch/hyaku/souji-r86/S86ExecEvade"
# reuse the clone from drive-c2 (still forged) to inspect the K4 detail field single-line property + escape
clone=S+"/c2work/clone"
# get rev
lbl=subprocess.run(["git","-C",clone,"rev-parse","HEAD"],capture_output=True,text=True)
rev=lbl.stdout.strip()
ENV={k:v for k,v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":os.devnull,"LC_ALL":"C","GIT_OPTIONAL_LOCKS":"0","GIT_AUTHOR_NAME":"t","GIT_AUTHOR_EMAIL":"t@t","GIT_COMMITTER_NAME":"t","GIT_COMMITTER_EMAIL":"t@t","GIT_AUTHOR_DATE":"2026-11-08T00:00:00Z","GIT_COMMITTER_DATE":"2026-11-08T00:00:00Z"})
tool=S+"/c2/souji-record-agreement.py"
p=subprocess.run([sys.executable,"-B",tool,"--root",clone,"--rev",rev],capture_output=True,text=True,env=ENV,cwd=S+"/c2work")
lines=p.stdout.splitlines()
k4=[l for l in lines if "K4" in l]
print("K4-LINES",len(k4))
for l in k4: print(repr(l))
print("physical lines of K4 detail:", [l.count("\n") for l in k4])
# newline path probe: forge a NEW committed newline-path? The fixture has no newline file; KG2 style needs newline IN first-5 names. Test escaping by forging a newline file:
# create fresh repo with newline file
w=S+"/c2work2"
if os.path.exists(w): shutil.rmtree(w)
os.makedirs(w)
cl=os.path.join(w,"clone"); os.makedirs(cl)
def g(r,*a):
    q=subprocess.run(["git","-C",r,*a],capture_output=True,env=ENV)
    if q.returncode: raise RuntimeError(f"{a} {q.stderr[:300]}")
    return q
subprocess.run(["git","init","-q","-b","master",cl],check=True,env=ENV)
# 5 honest + 1 newline forged as 6th; commit all first
for n in ["a1.txt","a2.txt","a3.txt","a4.txt","a5.txt","evil\nname.txt"]:
    with open(os.path.join(cl,n),"wb") as f: f.write(b"v1\n")
g(cl,"add","-A"); g(cl,"commit","-q","--no-verify","-m","seed")
rv=g(cl,"rev-parse","HEAD").stdout.decode().strip()
import time
old=time.time()-30
for n in ["a1.txt","a2.txt","a3.txt","a4.txt","a5.txt","evil\nname.txt"]:
    os.utime(os.path.join(cl,n),(old,old))
g(cl,"update-index","--really-refresh")
spec=importlib.util.spec_from_file_location("c2",S+"/c2/c2-k4-counter.py")
c2=importlib.util.module_from_spec(spec); spec.loader.exec_module(c2)
g(cl,"reset","-q","--hard",rv); g(cl,"clean","-q","-fdx")
with open(os.path.join(cl,"evil\nname.txt"),"wb") as f: f.write(b"vX\n")
c2.forge_index_stat(cl,"evil\nname.txt")
p2=subprocess.run([sys.executable,"-B",tool,"--root",cl,"--rev",rv],capture_output=True,text=True,env=ENV,cwd=w)
print("--- newline-as-6th run ---")
for l in p2.stdout.splitlines():
    if "K4" in l: print(repr(l))
print("rc",p2.returncode)
print("evil-escaped-named:", "evil\\nname.txt" in p2.stdout, "raw-newline-in-l:", any(l.startswith("MISMATCH") and l.count("\t")!=4 for l in p2.stdout.splitlines()))
