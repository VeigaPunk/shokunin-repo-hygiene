import os,sys,subprocess,time,signal
import importlib.util
spec=importlib.util.spec_from_file_location("probe","/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-74/records/wave-repair/probes/evade-probe.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
GATE="/fast/scratch/hyaku/souji-r77/S77ExecEvade/gatedir/souji-pre-report-gate.sh"
BASE="/fast/scratch/hyaku/souji-r77/S77ExecEvade/probes5"
def run(clone,report,prereg,t=12):
    env=P.env_clean(); t0=time.monotonic()
    p=subprocess.Popen(["bash",GATE,"--lane",clone,"--branch","master","--report",report,"--prereg",prereg],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.DEVNULL,env=env,start_new_session=True,cwd=clone)
    try: out,err=p.communicate(timeout=t)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid,signal.SIGKILL);p.communicate();return "HANG",time.monotonic()-t0,""
    txt=(out+err).decode()
    return ("rc=%s %s"%(p.returncode,txt.strip().replace(chr(10)," | ")[:300])),time.monotonic()-t0,txt
def fresh(rid):
    rd=os.path.join(BASE,rid); clone,report,prereg=P.build(rd); return rd,clone,report,prereg
env=P.env_clean()
def piece(repo,args,label,t=5):
    t0=time.monotonic()
    try:
        p=subprocess.run(["git","--no-optional-locks","-C",repo,*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,timeout=t)
        print(f"piece[{label}] rc={p.returncode} {time.monotonic()-t0:.1f}s out={p.stdout.decode()[:70]!r}",flush=True)
    except subprocess.TimeoutExpired: print(f"piece[{label}] HANG>{t}s",flush=True)
# symlink: is -f following? verify stat behaviour + whether gate counted worktree link (it did: count=1)
# broken symlink .gitignore (target missing): -e false, find ! -type f => symlink is not f => counts! PASS? find reports it. gate refuses.
rd,clone,report,prereg=fresh("brk")
os.symlink("/nonexistent-xyz",os.path.join(clone,".gitignore"))
r,s,_=run(clone,report,prereg); print("broken-symlink-gitignore:",round(s,2),r,flush=True)
# HEAD FIFO: which check? check1 rev-parse?
rd,clone,report,prereg=fresh("head")
os.remove(os.path.join(clone,".git","HEAD")); os.mkfifo(os.path.join(clone,".git","HEAD"))
piece(clone,["rev-parse","--verify","refs/heads/master^{commit}"],"head-revparse")
piece(clone,["rev-parse","--absolute-git-dir"],"head-gitdir")
# packed-refs: gate check1 ls-remote? or status? rev-parse ok?
rd,clone,report,prereg=fresh("pref")
os.mkfifo(os.path.join(clone,".git","packed-refs"))
piece(clone,["rev-parse","--verify","refs/heads/master^{commit}"],"pref-revparse")
piece(clone,["ls-remote","--exit-code","origin","refs/heads/master"],"pref-lsremote")
piece(clone,["status","--porcelain=v1","--untracked-files=all"],"pref-status",t=6)
# index FIFO
rd,clone,report,prereg=fresh("idx")
os.remove(os.path.join(clone,".git","index")); os.mkfifo(os.path.join(clone,".git","index"))
piece(clone,["rev-parse","--verify","refs/heads/master^{commit}"],"idx-revparse")
r,s,_=run(clone,report,prereg); print("idx-gate:",round(s,2),r,flush=True)
# include.path FIFO: which piece?
rd,clone,report,prereg=fresh("inc")
inc=os.path.join(rd,"inc.txt"); os.mkfifo(inc); P.git(clone,"config","include.path",inc)
piece(clone,["rev-parse","--verify","refs/heads/master^{commit}"],"inc-revparse")
r,s,_=run(clone,report,prereg); print("inc-gate:",round(s,2),r,flush=True)
# sparse: which piece? rev-parse ok. status?
rd,clone,report,prereg=fresh("sparse")
os.mkfifo(os.path.join(clone,".git","info","sparse-checkout"))
P.git(clone,"config","core.sparseCheckout","true")
piece(clone,["status","--porcelain=v1","--untracked-files=all"],"sparse-status",t=6)
piece(clone,["rev-parse","--absolute-git-dir"],"sparse-gitdir")
r,s,_=run(clone,report,prereg); print("sparse-gate:",round(s,2),r,flush=True)
# commondir: which piece after nonreg passes? run pieces
rd,clone,report,prereg=fresh("cdp")
cdir=os.path.join(rd,"linked"); P.git(clone,"worktree","add","-q",cdir,"-b","master2")
cd=P.git(cdir,"rev-parse","--git-common-dir").stdout.decode().strip()
ex=os.path.join(cd,"info","exclude"); os.remove(ex); os.mkfifo(ex)
# gate rev-parse --absolute-git-dir on cdir returns?? (showed main .git earlier - because piece ran on clone, not cdir)
piece(cdir,["rev-parse","--absolute-git-dir"],"cd-gitdir")
piece(cdir,["status","--porcelain=v1","--untracked-files=all"],"cd-status",t=6)
# config.worktree FIFO in linked: rev-parse?
rd,clone,report,prereg=fresh("cwt2")
cdir=os.path.join(rd,"linked"); P.git(clone,"worktree","add","-q",cdir,"-b","master2")
P.git(cdir,"config","extensions.worktreeConfig","true")
gd=P.git(cdir,"rev-parse","--absolute-git-dir").stdout.decode().strip()
os.mkfifo(os.path.join(gd,"config.worktree"))
piece(cdir,["rev-parse","--verify","refs/heads/master2^{commit}"],"cwt-revparse")
piece(cdir,["status","--porcelain=v1","--untracked-files=all"],"cwt-status",t=6)
