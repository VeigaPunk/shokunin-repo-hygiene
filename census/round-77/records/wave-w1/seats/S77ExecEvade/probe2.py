import os,sys,subprocess,time,signal
import importlib.util
spec=importlib.util.spec_from_file_location("probe","/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-74/records/wave-repair/probes/evade-probe.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
GATE="/fast/scratch/hyaku/souji-r77/S77ExecEvade/gatedir/souji-pre-report-gate.sh"
BASE="/fast/scratch/hyaku/souji-r77/S77ExecEvade/probes2"
def run(clone,report,prereg,env_extra=None,t=15,cwd=None):
    env=P.env_clean()
    if env_extra: env.update(env_extra)
    t0=time.monotonic()
    p=subprocess.Popen(["bash",GATE,"--lane",clone,"--branch","master","--report",report,"--prereg",prereg],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.DEVNULL,env=env,start_new_session=True,cwd=cwd or clone)
    try: out,err=p.communicate(timeout=t)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid,signal.SIGKILL);p.communicate();return "HANG",time.monotonic()-t0,(out if False else b"")
    txt=(out+err).decode()
    return ("rc=%s %s"%(p.returncode,txt.strip().replace(chr(10)," | ")[:300])),time.monotonic()-t0,txt
def fresh(rid):
    rd=os.path.join(BASE,rid); clone,report,prereg=P.build(rd); return rd,clone,report,prereg
# f2: HEAD FIFO — replace HEAD
rd,clone,report,prereg=fresh("f2"); os.remove(os.path.join(clone,".git","HEAD")); os.mkfifo(os.path.join(clone,".git","HEAD"))
print("f2-HEAD-FIFO:",run(clone,report,prereg),flush=True)
# f3: index FIFO
rd,clone,report,prereg=fresh("f3"); os.remove(os.path.join(clone,".git","index")); os.mkfifo(os.path.join(clone,".git","index"))
print("f3-index-FIFO:",run(clone,report,prereg),flush=True)
# f4: config FIFO
rd,clone,report,prereg=fresh("f4"); os.remove(os.path.join(clone,".git","config")); os.mkfifo(os.path.join(clone,".git","config"))
print("f4-config-FIFO:",run(clone,report,prereg),flush=True)
# f1 redo: packed-refs FIFO — where does it hang? capture raw output with timeout (no early clean line?)
rd,clone,report,prereg=fresh("f1"); os.mkfifo(os.path.join(clone,".git","packed-refs"))
r,s,_=run(clone,report,prereg); print("f1-packed-refs:",s,r,flush=True)
# e3 redo: include.path FIFO — where hangs?
rd,clone,report,prereg=fresh("e3"); inc=os.path.join(rd,"inc.txt"); os.mkfifo(inc); P.git(clone,"config","include.path",inc)
r,s,_=run(clone,report,prereg); print("e3-include:",s,r,flush=True)
# e4 more: includeIf with matching gitdir — config a FIFO includeIf.gitdir pattern that matches lane
rd,clone,report,prereg=fresh("e4b"); inc=os.path.join(rd,"inc.txt"); os.mkfifo(inc); P.git(clone,"config","includeIf.gitdir:"+clone,"path",inc) if False else None
# correct syntax: includeIf.gitdir:PATTERN.path
P.git(clone,"config","includeIf.gitdir:"+clone+".path",inc)
r,s,_=run(clone,report,prereg); print("e4b-includeIf-match:",s,r,flush=True)
# g race: FIFO swapped in just before gate — symlink .gitignore->regular, then swap to FIFO after gate starts? simulate by making .gitignore a symlink whose target is replaced? deterministic variant: .gitignore is a HARDLINK? Instead: named pipe whose open is raced: create .gitignore as FIFO but with a writer attached? Show gate refuses FIFO before status anyway.
# Timing race actually tests: gate pre-check passes (regular), then attacker replaces before status — need wrapper: make .gitignore a symlink to a file we replace mid-run via background swapper.
rd,clone,report,prereg=fresh("grace")
tgt=os.path.join(rd,"tgt"); open(tgt,"w").write("*\n"); os.symlink(tgt,os.path.join(clone,".gitignore"))
fifo=os.path.join(rd,"fifo"); os.mkfifo(fifo)
open(os.path.join(clone,"hidden.txt"),"wb").write(b"x\n")
# background: after 0.3s replace tgt with symlink to fifo? .gitignore symlink->tgt; making tgt a symlink to fifo makes .gitignore effectively FIFO.
import threading
def swap():
    time.sleep(0.35); os.remove(tgt); os.symlink(fifo,tgt)
threading.Thread(target=swap,daemon=True).start()
r,s,_=run(clone,report,prereg,t=20); print("grace-race:",s,r,flush=True)
# also check raw: does git status block on FIFO .gitignore under timeout-k5 300 backstop? (out of row bound, but inside claim's "refuses before status")
