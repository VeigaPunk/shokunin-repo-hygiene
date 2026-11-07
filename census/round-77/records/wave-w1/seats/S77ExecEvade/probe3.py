import os,sys,subprocess,time,signal,threading
import importlib.util
spec=importlib.util.spec_from_file_location("probe","/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-74/records/wave-repair/probes/evade-probe.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
GATE="/fast/scratch/hyaku/souji-r77/S77ExecEvade/gatedir/souji-pre-report-gate.sh"
BASE="/fast/scratch/hyaku/souji-r77/S77ExecEvade/probes3"
def run(clone,report,prereg,t=20,branch="master"):
    env=P.env_clean(); t0=time.monotonic()
    p=subprocess.Popen(["bash",GATE,"--lane",clone,"--branch",branch,"--report",report,"--prereg",prereg],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.DEVNULL,env=env,start_new_session=True,cwd=clone)
    try: out,err=p.communicate(timeout=t)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid,signal.SIGKILL);p.communicate();return "HANG",time.monotonic()-t0,""
    txt=(out+err).decode()
    return ("rc=%s %s"%(p.returncode,txt.strip().replace(chr(10)," | ")[:320])),time.monotonic()-t0,txt
def fresh(rid):
    rd=os.path.join(BASE,rid); clone,report,prereg=P.build(rd); return rd,clone,report,prereg
# 1) commondir: linked worktree as lane, FIFO at COMMON info/exclude
rd,clone,report,prereg=fresh("cd1")
cdir=os.path.join(rd,"linked")
P.git(clone,"worktree","add","-q",cdir,"-b","master2")
assert os.path.exists(os.path.join(cdir,".git")), open(os.path.join(cdir,".git")).read() if os.path.isfile(os.path.join(cdir,".git")) else None
gd=P.git(cdir,"rev-parse","--absolute-git-dir").stdout.decode().strip()
cd=P.git(cdir,"rev-parse","--git-common-dir").stdout.decode().strip()
print("gitdir=",gd,"common=",cd,flush=True)
# FIFO at common info/exclude (NOT in per-worktree gitdir)
openif=os.path.join(cd,"info","exclude")
print("common exclude exists?",os.path.exists(openif),flush=True)
if os.path.exists(openif): os.remove(openif)
os.mkfifo(openif)
r,s,_=run(cdir,report,prereg,t=20,branch="master2"); print("cd1-commondir-FIFO-exclude:",round(s,2),r,flush=True)
# also FIFO at common info/attributes
if os.path.exists(openif): pass
# 2) sparse: FIFO info/sparse-checkout with sparse enabled (clone itself)
rd,clone,report,prereg=fresh("sp1")
os.mkfifo(os.path.join(clone,".git","info","sparse-checkout"))
P.git(clone,"config","core.sparseCheckout","true")
r,s,_=run(clone,report,prereg); print("sp1-sparse-FIFO-enabled:",round(s,2),r,flush=True)
# 3) e4b verification: does the includeIf pattern actually match? query git config directly
rd,clone,report,prereg=fresh("e4v")
inc=os.path.join(rd,"inc.txt"); os.mkfifo(inc)
P.git(clone,"config","includeIf.gitdir:"+clone+".path",inc)
print("cfg list:",P.git(clone,"config","--list","--show-origin",check=False).stdout.decode()[:200],flush=True)
# does git open the inc file? test with timeout on plain git config --get
try:
    p=subprocess.run(["git","-C",clone,"config","--get","core.excludesFile"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=P.env_clean(),timeout=5)
    print("plain git config rc",p.returncode,p.stdout,p.stderr[:100],flush=True)
except subprocess.TimeoutExpired: print("plain git config HANG (>5s): includeIf file IS opened by git",flush=True)
r,s,_=run(clone,report,prereg,t=12); print("e4v-gate:",round(s,2),r,flush=True)
# 4) tracked symlink .gitignore -> regular (committed): false-positive check
rd=os.path.join(BASE,"sym1"); clone,report,prereg=P.build(rd)
tgt=os.path.join(clone,"targets","gi-target"); os.makedirs(os.path.join(clone,"targets"),exist_ok=True)
open(tgt,"wb").write(b"hidden.txt\n")
os.symlink("targets/gi-target",os.path.join(clone,".gitignore"))
open(os.path.join(clone,"hidden.txt"),"wb").write(b"x\n")
P.git(clone,"add","-A"); P.git(clone,"commit","-q","-m","symlink gi")
P.git(clone,"push","-q","origin","master")
r,s,_=run(clone,report,prereg); print("sym1-tracked-symlink-gitignore:",round(s,2),r,flush=True)
