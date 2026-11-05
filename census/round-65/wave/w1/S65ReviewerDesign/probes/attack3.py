import os, subprocess, sys, importlib.util, shutil
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65="/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
NEW=os.path.join(S65,"writer-landed.py"); BBp=os.path.join(S65,"base-all.py")

def fresh(tag, specd, post=None, cfg=None):
    rep, rev = c1c.build_case(os.path.join(S65,"atk3"), tag, "one", specd)
    outd = os.path.join(os.path.dirname(rep), "out"); out = os.path.join(outd,"r.txt")
    if post: post(rep)
    if cfg: subprocess.run(["git","-C",rep,"config",cfg[0],cfg[1]],check=True)
    return rep, rev, out

def go(tag, specd, slotname, post=None, cfg=None, extra_env=None, wrapped=None, pre=None):
    slot = BBp if slotname=="base" else NEW
    rep, rev, out = fresh(tag, specd, post, cfg)
    if pre: pre(rep)
    a=["python3","-B",slot,"--root",rep,"--rev",rev,"--instrument","tools/instr.sh",
       "--out",out,"--allow-outside"]+(["--allow-dirty"] if specd.get("allow_dirty") else [])+["--", *(wrapped or ["/bin/echo","hi"])]
    env=c1c.clean_env(extra_env)
    p=subprocess.run(a,cwd=S65,capture_output=True,env=env,timeout=120)
    v="accept" if p.returncode==0 and os.path.isfile(out) else ("refuse" if p.returncode==2 and not os.path.lexists(out) else f"err{p.returncode}")
    print(f"[{tag}/{slotname}] {v:7s} :: {p.stderr.decode()[:130].strip()}")
    return v

# (6a) env-config via GIT_CONFIG env vars: untracked dir present, allow_dirty — the _content_snapshot
#     path uses -c override already; the non-z dirty check at line 332 also -c... both covered?
#     BUT: caller `git()` scrub only removes GIT_DIR/GIT_WORK_TREE; GIT_CONFIG_COUNT passes through.
go("ENVcfg-dir", {"name":"E1","untracked_dir":"tools/extra","allow_dirty":True}, "new",
   extra_env={"GIT_CONFIG_COUNT":"1","GIT_CONFIG_KEY_0":"status.showUntrackedFiles","GIT_CONFIG_VALUE_0":"no"})
# (6b) env-config setuid: caller env GIT_CONFIG for core variables: Aliases? TryIGATION: GIT_CONFIG_COUNT alias `status.relativePaths` is harmless.
# (6c) symlinked directory INSIDE tracked tree? no: probe symlinked dir inside the UNTRACKED dir (walk must not follow):
def post6c(rep):
    os.symlink("../../etc", os.path.join(rep,"tools/extra","dirlink"))
go("SYM-dir-untracked", {"name":"E2","untracked_dir":"tools/extra","allow_dirty":True}, "new", post=post6c)
# ...does walk record dirlink at all? check if receipt accepts (symlink to /etc should NOT be followed; record name+target)
# also probe symlink DIRECTORY swapped IN-RUN to a REAL directory containing files (fingerprint churn)
def post6d(rep):
    os.makedirs(os.path.join(rep,"/tmp/x") if False else os.path.join(rep,"tools/extra","realdir"), exist_ok=True)
    open(os.path.join(rep,"tools/extra","realdir","inside.txt"),"wb").write(b"in\n")
    os.symlink("realdir", os.path.join(rep,"tools/extra","dirlink"))
def wrap6d(rep):
    # in-run: replace symlink with a real DIRECTORY containing files
    import textwrap
    code = ("import os, shutil\n"
            f"link = {rep!r}+'/tools/extra/dirlink'\n"
            "os.unlink(link)\n"
            "os.mkdir(link)\n"
            "open(link+'/planted.txt','wb').write(b'planted\\n')\n")
    return [sys.executable,"-c",code]
go("SYM-dir-swap-inrun", {"name":"E3","untracked_dir":"tools/extra","allow_dirty":True}, "new", post=post6d, wrapped=None)
# (7) out path INSIDE the untracked dir: receipt written to tools/extra/out.txt → post-run snapshot changes?
def go7(tag, slotname):
    slot = BBp if slotname=="base" else NEW
    rep, rev = c1c.build_case(os.path.join(S65,"atk3"), tag, "one", {"name":tag,"allow_dirty":True,"untracked_dir":"tools/extra"})
    out = os.path.join(rep,"tools/extra","receipt-out.txt")
    a=["python3","-B",slot,"--root",rep,"--rev",rev,"--instrument","tools/instr.sh",
       "--out",out,"--allow-outside","--allow-dirty","--","/bin/echo","hi"]
    p=subprocess.run(a,cwd=S65,capture_output=True,env=c1c.clean_env(),timeout=120)
    v="accept" if p.returncode==0 and os.path.isfile(out) else ("refuse" if p.returncode==2 and not os.path.lexists(out) else f"err{p.returncode}")
    print(f"[{tag}/{slotname}] {v:7s} :: {p.stderr.decode()[:130].strip()}")
    if v=="accept":
        # rerun same slot: does the writer now refuse the OUT-exists (expect refuse rc=2)?
        p2=subprocess.run(a,cwd=S65,capture_output=True,env=c1c.clean_env(),timeout=120)
        v2="accept" if p2.returncode==0 else ("refuse" if p2.returncode==2 else f"err{p2.returncode}")
        print(f"[{tag}/{slotname}/rerun] {v2} :: {p2.stderr.decode()[:100].strip()}")
go7("OUT-in-untracked","base"); go7("OUT2-in-untracked","new")

# (8) DNS-style root-level instrument shadowing: the writer invoked with --instrument an ABSOLUTE path
rep, rev = None, None
# (9) alias: does mode payload spike for a mode-unreadable path (deny by ACL)? skipped: root-only fixtures.

# (10) hash-object forged GIT_OBJECT_DIRECTORY redirect: base/new both read config via plain git; now pruned to GIT_INDEX_FILE only (frozen). Nothing to probe.
