import os,sys,subprocess,time,signal
import importlib.util
spec=importlib.util.spec_from_file_location("probe","/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-74/records/wave-repair/probes/evade-probe.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
GATE="/fast/scratch/hyaku/souji-r77/S77ExecEvade/gatedir/souji-pre-report-gate.sh"
BASE="/fast/scratch/hyaku/souji-r77/S77ExecEvade/probes4"
def run(clone,report,prereg,t=15):
    env=P.env_clean(); t0=time.monotonic()
    p=subprocess.Popen(["bash",GATE,"--lane",clone,"--branch","master","--report",report,"--prereg",prereg],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.DEVNULL,env=env,start_new_session=True,cwd=clone)
    try: out,err=p.communicate(timeout=t)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid,signal.SIGKILL);p.communicate();return "HANG",time.monotonic()-t0,""
    txt=(out+err).decode()
    return ("rc=%s %s"%(p.returncode,txt.strip().replace(chr(10)," | ")[:320])),time.monotonic()-t0,txt
def fresh(rid):
    rd=os.path.join(BASE,rid); clone,report,prereg=P.build(rd); return rd,clone,report,prereg
# A) bare-repo lane: --lane points at bare repo? rev-parse --absolute-git-dir returns itself... 
# B) commondir committed-FIFO detail: which call hangs? instrument via strace-lite: run nonreg_sources pieces
rd,clone,report,prereg=fresh("cd2")
cdir=os.path.join(rd,"linked"); P.git(clone,"worktree","add","-q",cdir,"-b","master2")
cd=P.git(cdir,"rev-parse","--git-common-dir").stdout.decode().strip()
ex=os.path.join(cd,"info","exclude"); os.remove(ex); os.mkfifo(ex)
# run check-1 pieces manually with timeout to see which blocks
env=P.env_clean()
for cmd in [["git","--no-optional-locks","-C",cdir,"rev-parse","--verify","refs/heads/master2^{commit}"],
            ["git","--no-optional-locks","-C",cdir,"ls-remote","--exit-code","origin","refs/heads/master2"],
            ["git","--no-optional-locks","-C",cdir,"rev-parse","--absolute-git-dir"],
            ["git","--no-optional-locks","-C",cdir,"config","--path","--get","core.excludesFile"],
            ["git","--no-optional-locks","-C",cdir,"config","--path","--get","core.attributesFile"]]:
    t0=time.monotonic()
    try:
        p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,timeout=5)
        print("piece",cmd[-1],"rc",p.returncode,"%.1fs"%(time.monotonic()-t0),p.stdout.decode().strip()[:60],flush=True)
    except subprocess.TimeoutExpired:
        print("piece",cmd[-1],"HANG>5s",flush=True)
# C) sparse: which piece?
rd,clone,report,prereg=fresh("sp2")
os.mkfifo(os.path.join(clone,".git","info","sparse-checkout"))
P.git(clone,"config","core.sparseCheckout","true")
env=P.env_clean()
for cmd in [["git","--no-optional-locks","-C",clone,"rev-parse","--verify","refs/heads/master^{commit}"],
            ["git","--no-optional-locks","-C",clone,"ls-remote","--exit-code","origin","refs/heads/master"],
            ["git","--no-optional-locks","-C",clone,"rev-parse","--absolute-git-dir"]]:
    t0=time.monotonic()
    try:
        p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,timeout=5)
        print("sp-piece",cmd[-1],"rc",p.returncode,"%.1fs"%(time.monotonic()-t0),flush=True)
    except subprocess.TimeoutExpired: print("sp-piece",cmd[-1],"HANG>5s",flush=True)
# D) config FIFO: which piece hangs (check 1 rev-parse reads config?)
rd,clone,report,prereg=fresh("cfg")
os.remove(os.path.join(clone,".git","config")); os.mkfifo(os.path.join(clone,".git","config"))
t0=time.monotonic()
try:
    p=subprocess.run(["git","--no-optional-locks","-C",clone,"rev-parse","--verify","refs/heads/master^{commit}"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=P.env_clean(),timeout=5)
    print("cfg rev-parse rc",p.returncode,"%.1fs"%(time.monotonic()-t0),flush=True)
except subprocess.TimeoutExpired: print("cfg rev-parse HANG>5s: check 1 itself blocks",flush=True)
# E) hooksPath FIFO hook: does check 4 run hooks? status doesn't. Confirm PASS + verify no hook execution needed
rd,clone,report,prereg=fresh("hk")
hp=os.path.join(rd,"hooks"); os.makedirs(hp)
os.mkfifo(os.path.join(hp,"post-checkout")); os.mkfifo(os.path.join(hp,"pre-auto-gc"))
P.git(clone,"config","core.hooksPath",hp)
r,s,_=run(clone,report,prereg); print("hooksPath FIFO hooks:",round(s,2),r,flush=True)
# F) FIFO inside .git/worktrees/*/config.worktree? skip: config.worktree FIFO in common dir
rd,clone,report,prereg=fresh("cwt")
cdir=os.path.join(rd,"linked"); P.git(clone,"worktree","add","-q",cdir,"-b","master2")
P.git(cdir,"config","extensions.worktreeConfig","true")
gd=P.git(cdir,"rev-parse","--absolute-git-dir").stdout.decode().strip()
print("wt gitdir",gd,os.listdir(gd),flush=True)
os.mkfifo(os.path.join(gd,"config.worktree"))
r,s,_=run(cdir,report,prereg); print("config.worktree FIFO:",round(s,2),r,flush=True)
