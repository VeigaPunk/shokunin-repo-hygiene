import subprocess, sys, os, time, shutil
work="/fast/scratch/hyaku/souji-r86/S86ExecEvade/c2work"
if os.path.exists(work): shutil.rmtree(work)
os.makedirs(work)
ENV={k:v for k,v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":os.devnull,"LC_ALL":"C","GIT_OPTIONAL_LOCKS":"0","GIT_AUTHOR_NAME":"t","GIT_AUTHOR_EMAIL":"t@t","GIT_COMMITTER_NAME":"t","GIT_COMMITTER_EMAIL":"t@t",
 "GIT_AUTHOR_DATE":"2026-11-08T00:00:00Z","GIT_COMMITTER_DATE":"2026-11-08T00:00:00Z"})
def git(r,*a,check=True):
    p=subprocess.run(["git","-C",r,*a],capture_output=True,env=ENV)
    if check and p.returncode: raise RuntimeError(f"{a} {p.stderr[:200]}")
    return p
clone=os.path.join(work,"clone"); os.makedirs(clone)
subprocess.run(["git","init","-q","-b","master",clone],check=True,env=ENV)
assert os.path.realpath(git(clone,"rev-parse","--show-toplevel").stdout.decode().strip())==os.path.realpath(clone)
names=["f1-aaa.txt","f2-bbb.txt","f3-ccc.txt","f4-ddd.txt","f5-eee.txt","f6-fff.txt"]
import time
for n in names:
    with open(os.path.join(clone,n),"wb") as f: f.write(b"v1\n")
git(clone,"add","-A"); git(clone,"commit","-q","--no-verify","-m","seed")
rev=git(clone,"rev-parse","HEAD").stdout.decode().strip()
old=time.time()-30
for n in names: os.utime(os.path.join(clone,n),(old,old))
git(clone,"update-index","--really-refresh",check=False)
# forge all 6: same-size different bytes + stale index stat (copy approach from counter forge_index_stat)
for n in names:
    p=os.path.join(clone,n)
    with open(p,"wb") as f: f.write(b"vX\n")  # same size 3 bytes? v1\n vs vX\n yes 3
    # rewrite stat fields: simplified - use counter's forge via stat change
    # Mimic: touch index mtime? Easiest: use the counter helper by importing it
    break
# import counter helper forge_index_stat
import importlib.util
spec=importlib.util.spec_from_file_location("c2","/fast/scratch/hyaku/souji-r86/S86ExecEvade/c2/c2-k4-counter.py")
c2=importlib.util.module_from_spec(spec); spec.loader.exec_module(c2)
# restore pristine bytes then forge properly
git(clone,"reset","-q","--hard",rev); git(clone,"clean","-q","-fdx")
for n in names:
    with open(os.path.join(clone,n),"wb") as f: f.write(b"vX\n")
    c2.forge_index_stat(clone,n)
tool="/fast/scratch/hyaku/souji-r86/S86ExecEvade/c2/souji-record-agreement.py"
p=subprocess.run([sys.executable,"-B",tool,"--root",clone,"--rev",rev],capture_output=True,text=True,env=ENV,cwd=work)
print(p.stdout); print("rc",p.returncode, "lines",len(p.stdout.splitlines()))
for n in names: print(n, "NAMED" if any(n in l for l in p.stdout.splitlines()) else "MISSING")
