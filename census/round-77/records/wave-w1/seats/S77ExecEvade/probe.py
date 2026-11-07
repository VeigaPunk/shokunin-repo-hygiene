#!/usr/bin/env python3
import os, sys, subprocess, time, signal, stat, socket, shutil
sys.path.insert(0, "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-74/records/wave-repair/probes")
import importlib.util
spec = importlib.util.spec_from_file_location("probe", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-74/records/wave-repair/probes/evade-probe.py")
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
GATE="/fast/scratch/hyaku/souji-r77/S77ExecEvade/gatedir/souji-pre-report-gate.sh"
BASE="/fast/scratch/hyaku/souji-r77/S77ExecEvade/probes"
ROW_TIMEOUT=15

def run_gate(clone, report, prereg, env_extra=None):
    env = P.env_clean()
    if env_extra: env.update(env_extra)
    t0=time.monotonic()
    p=subprocess.Popen(["bash",GATE,"--lane",clone,"--branch","master","--report",report,"--prereg",prereg],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, env=env, start_new_session=True, cwd=clone)
    try: out,err=p.communicate(timeout=ROW_TIMEOUT)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL); p.communicate(); return None,"HANG","",time.monotonic()-t0
    text=out.decode()+err.decode()
    clean=next((l.split("=",1)[1] for l in text.splitlines() if l.startswith("check-clean=")),"-")
    detail=" | ".join(l for l in text.splitlines() if l.startswith("detail-clean"))
    rcline=" | ".join(l for l in text.splitlines() if l.startswith("check-"))
    return p.returncode, clean, detail or rcline, time.monotonic()-t0

def fifo(path):
    os.makedirs(os.path.dirname(path),exist_ok=True); os.mkfifo(path)

def route(rid, mut, gitignore=None, attrs=None):
    rd=os.path.join(BASE,rid)
    clone,report,prereg=P.build(rd, gitignore=gitignore, attrs=attrs)
    env=None
    try: env=mut(clone,rd) or None
    except Exception as e: print(f"SETUP-ERR {rid}: {e}",flush=True); return
    rc,clean,detail,secs=run_gate(clone,report,prereg,env)
    # hang check: did any fifo remain with writer blocked? gate killed.
    print(f"{rid} rc={rc} clean={clean} secs={secs:.1f} detail={detail[:260]}",flush=True)

# (a) core.excludesFile relative path (relative to cwd? gate resolves $lane/$f; git resolves relative to ...?)
# File at clone/xrel FIFO, excludesFile = "xrel" (relative). Git resolves core.excludesFile relative to cwd of git invocation (lane for gate's git -C lane).
def a1(c,w):
    fifo(os.path.join(c,"xrel"))
    P.git(c,"config","core.excludesFile","xrel")
    open(os.path.join(c,"hidden.txt"),"wb").write(b"x\n")
def a2(c,w):  # ~/ path: HOME=scratch home with FIFO at $HOME/.config/git/ignore would be default; here explicit ~/foo
    home=os.path.join(w,"fakehome"); os.makedirs(home,exist_ok=True)
    fifo(os.path.join(home,"excl"))
    P.git(c,"config","core.excludesFile","~/excl")
    return {"HOME":home}
def a3(c,w):  # config.worktree with extensions.worktreeConfig
    fifo(os.path.join(c,"wt-excl"))
    P.git(c,"config","extensions.worktreeConfig","true")
    gd=os.path.join(c,".git")
    with open(os.path.join(gd,"config"),"a") as f: f.write("")
    open(os.path.join(gd,"config.worktree"),"w").write("[core]\n\texcludesFile = "+os.path.join(c,"wt-excl")+"\n")
    open(os.path.join(c,"hidden.txt"),"wb").write(b"x\n")
def a4(c,w):  # excludesFile via ~/ symlinked? best: relative ../ escaping lane
    fifo(os.path.join(w,"outside-fifo"))
    P.git(c,"config","core.excludesFile","../outside-fifo")
# (b) FIFO at XDG_CONFIG_HOME/git/ignore, excludesFile unset (set XDG for gate call)
def b1(c,w):
    x=os.path.join(w,"xdg"); fifo(os.path.join(x,"git","ignore"))
    return {"XDG_CONFIG_HOME":x}
def b2(c,w):  # FIFO at $XDG_CONFIG_HOME/git/attributes
    x=os.path.join(w,"xdg"); fifo(os.path.join(x,"git","attributes"))
    return {"XDG_CONFIG_HOME":x}
# NOTE: env_clean strips HOME/XDG but gate reads ${XDG_CONFIG_HOME:-...} from its env; gate's git --path config may also use GIT_CONFIG_GLOBAL=/dev/null.
# (c) symlink .gitignore -> FIFO/socket/devzero/tty, dir named .gitignore
def c1(c,w):
    t=os.path.join(w,"sock"); 
    s=socket.socket(socket.AF_UNIX); s.bind(t); s.close()
    os.makedirs(os.path.join(c,"nd"),exist_ok=True); os.symlink(t, os.path.join(c,"nd",".gitignore"))
def c2(c,w):
    os.makedirs(os.path.join(c,"nd"),exist_ok=True); os.symlink("/dev/zero", os.path.join(c,"nd",".gitignore"))
def c3(c,w):
    os.makedirs(os.path.join(c,"nd"),exist_ok=True); os.symlink("/dev/tty", os.path.join(c,"nd",".gitignore"))
def c4(c,w):
    os.makedirs(os.path.join(c,"sub",".gitignore"),exist_ok=True)
    open(os.path.join(c,"hidden.txt"),"wb").write(b"x\n")
def c5(c,w):  # .gitignore symlink to regular file hiding content (control: regular, must not refuse)
    os.makedirs(os.path.join(c,"nd"),exist_ok=True)
    tgt=os.path.join(w,"reg"); open(tgt,"w").write("hidden.txt\n"); os.symlink(tgt, os.path.join(c,"nd",".gitignore"))
    open(os.path.join(c,"nd","hidden.txt"),"wb").write(b"x\n")
# (d) nested repo / submodule work tree FIFO .gitignore
def d1(c,w):
    sub=os.path.join(w,"inner"); os.makedirs(sub)  
    P.git(sub,"init","-q","-b","master",sub)
    fifo(os.path.join(sub,".gitignore"))
    # also make it a submodule-ish: gitlink? simpler: place inside clone as untracked nested repo
    os.makedirs(os.path.join(c,"nested"),exist_ok=True)
    # copy fifo there
    # (nested repo work tree inside lane)
    fifo(os.path.join(c,"nested",".gitignore"))
def d2(c,w):  # proper submodule with FIFO .gitignore committed-state
    inner=os.path.join(w,"inner2"); os.makedirs(inner)
    P.git(inner,"init","-q","-b","master",inner)
    open(os.path.join(inner,"f.txt"),"w").write("x\n")
    P.git(inner,"add","-A"); P.git(inner,"commit","-q","-m","i")
    P.git(c,"-c","protocol.file.allow=always","submodule","add","-q",inner,"subm")
    fifo(os.path.join(c,"subm",".gitignore"))
# (e) FIFO sparse-checkout, hooksPath, includeIf file
def e1(c,w):
    fifo(os.path.join(c,".git","info","sparse-checkout"))
def e2(c,w):
    hp=os.path.join(w,"hooks"); os.makedirs(hp,exist_ok=True)
    fifo(os.path.join(hp,"pre-commit"))
    P.git(c,"config","core.hooksPath",hp)
def e3(c,w):
    inc=os.path.join(w,"inc.txt"); fifo(inc)
    P.git(c,"config","include.path",inc)
def e4(c,w):  # includeIf pointing to FIFO
    inc=os.path.join(w,"inc2.txt"); fifo(inc)
    P.git(c,"config","includeIf.gitdir:/fast.path",inc)
# (f) FIFO under .git that check 4 might read
def f1(c,w): fifo(os.path.join(c,".git","packed-refs"))
def f2(c,w): fifo(os.path.join(c,".git","HEAD"))
def f3(c,w): fifo(os.path.join(c,".git","index"))
def f4(c,w): fifo(os.path.join(c,".git","config"))
# (g) race: regular .gitignore now, swapped to FIFO at git-status time is not testable deterministically; note only.
def g1(c,w):
    # FIFO in excluded dir that git DOES open? .gitignore symlink -> FIFO inside tracked dir
    fifo(os.path.join(w,"fifotgt"))
    os.symlink(os.path.join(w,"fifotgt"), os.path.join(c,"sub",".gitignore"))

shutil.rmtree(BASE,ignore_errors=True)
if __name__=="__main__":
    which=sys.argv[1:] or ["a1","a2","a3","a4","b1","b2","c1","c2","c3","c4","c5","d1","d2","e1","e2","e3","e4","f1","f2","f3","f4","g1"]
    F={"a1":a1,"a2":a2,"a3":a3,"a4":a4,"b1":b1,"b2":b2,"c1":c1,"c2":c2,"c3":c3,"c4":c4,"c5":c5,"d1":d1,"d2":d2,"e1":e1,"e2":e2,"e3":e3,"e4":e4,"f1":f1,"f2":f2,"f3":f3,"f4":f4,"g1":g1}
    for k in which: route(f"{k}-{F[k].__name__}",F[k])
