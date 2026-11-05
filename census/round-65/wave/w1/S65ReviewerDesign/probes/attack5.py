import os, subprocess, sys, importlib.util, shutil
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65="/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
NEW=os.path.join(S65,"writer-landed.py"); BBp=os.path.join(S65,"base-all.py")

def fresh(tag, specd, post=None, cfg=None):
    rep, rev = c1c.build_case(os.path.join(S65,"atk5"), tag, "one", specd)
    out = os.path.join(os.path.dirname(rep), "out", "r.txt")
    if post: post(rep)
    if cfg: subprocess.run(["git","-C",rep,"config",cfg[0],cfg[1]],check=True)
    return rep, rev, out

def go(tag, specd, slotname, post=None, cfg=None, extra_env=None, wrapped=None):
    slot = BBp if slotname=="base" else NEW
    rep, rev, out = fresh(tag, specd, post, cfg)
    w = wrapped(rep) if callable(wrapped) else (wrapped or ["/bin/echo","hi"])
    a=["python3","-B",slot,"--root",rep,"--rev",rev,"--instrument","tools/instr.sh",
       "--out",out,"--allow-outside"]+(["--allow-dirty"] if specd.get("allow_dirty") else [])+["--",*w]
    env=c1c.clean_env(extra_env)
    p=subprocess.run(a,cwd=S65,capture_output=True,env=env,timeout=120)
    v="accept" if p.returncode==0 and os.path.isfile(out) else ("refuse" if p.returncode==2 and not os.path.lexists(out) else f"err{p.returncode}")
    print(f"[{tag:30s}/{slotname}] {v:7s} :: {p.stderr.decode()[:128].strip()}")
    return v

E={"GIT_CONFIG_COUNT":"1","GIT_CONFIG_KEY_0":"status.showUntrackedFiles","GIT_CONFIG_VALUE_0":"no"}
specd={"name":"E2","untracked_dir":"tools/extra","allow_dirty":True,"dirty":True}
def wrap_newfile(rep):
    return [sys.executable,"-c",f"import os\nopen({rep!r}+'/tools/extra/planted.txt','wb').write(b'planted\\n')"]
# env cfg=no + in-run planted file (allows the caller to hide it from the -c call? -c flag syntax order: git -C X -c cfg.f=... status: env GIT_CONFIG_* processed FIRST (env wins over -c)
go("ENVno-inrun", specd, "new", extra_env=E, wrapped=wrap_newfile)
go("ENVno-inrun-base", specd, "base", extra_env=E, wrapped=wrap_newfile)

# control: same in-run plant WITHOUT env cfg
go("PLAIN-inrun", specd, "new", wrapped=wrap_newfile)

# (5b) -c on caller: a -c cannot cross process boundary; env is the leg. covered.
# (7) recip: out-path INSIDE the untracked dir, in-run the WRAP creates the file then the writer's post-run status sees ONE MORE untracked file = dirty-flip → refuse for new? Note: writer only re-readsPorcelain at post: the receipt itself (out) doesn't appear in status because OUT exists at snapshot time? out created AFTER post-run reads? Order: post re-read happens BEFORE composing the receipt. Out created after — so out not visible in post reads. So no false-refusal. But: WAIT — writer composes receipt AFTER post-run reads, and writes OUT after; the OUT file never existed at the post-read → no churn.
