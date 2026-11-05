import os, subprocess, sys, importlib.util, shutil
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65="/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
LANE="/home/vgpnk/Projects/shokunin/souji-shokunin"
NEW=os.path.join(S65,"writer-landed.py"); BASEV="4a43a4d919c5b51ae9be859a1266ce4b11337b0b"
BBp=os.path.join(S65,"base-all.py")

def mk(which, dual, tools_differs, root_ok):
    d=os.path.join(S65,"n4deploy",which)
    if os.path.isdir(d): shutil.rmtree(d)
    os.makedirs(d+"/repo/tools")
    subprocess.run(["git","-C",d+"/repo","init","-q"],check=True)
    subprocess.run(["git","-C",d+"/repo","config","user.name","N4D"],check=True)
    subprocess.run(["git","-C",d+"/repo","config","user.email","n4d@v"],check=True)
    if root_ok:
        open(d+"/repo/instr.sh","wb").write(c1c.SEED_INSTR); os.chmod(d+"/repo/instr.sh",0o755)
    open(d+"/repo/tools/instr.sh","wb").write(b"#!/bin/sh\necho TOOLS-VARIANT\n"); os.chmod(d+"/repo/tools/instr.sh",0o755)
    open(d+"/repo/tools/notes.txt","wb").write(c1c.SEED_NOTES)
    open(d+"/repo/README.md","wb").write(c1c.SEED_README)
    e={**os.environ,"GIT_AUTHOR_DATE":c1c.GIT_DATE,"GIT_COMMITTER_DATE":c1c.GIT_DATE}
    subprocess.run(["git","-C",d+"/repo","add","-A"],check=True,env=e)
    subprocess.run(["git","-C",d+"/repo","commit","-q","-m","c1 seed"],check=True,env=e)
    rev=subprocess.run(["git","-C",d+"/repo","rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()
    subprocess.run(["git","-C",d+"/repo","update-index","--skip-worktree","README.md"],check=True)
    open(d+"/repo/README.md","wb").write(c1c.FORGED_README)
    os.makedirs(d+"/out")
    return d+"/repo", rev, d+"/out/r.txt"

def run(repo, rev, out, slotname, slot):
    root = os.path.join(repo,"tools")
    a=["python3","-B",slot,"--root",root,"--rev",rev,"--instrument","instr.sh",
       "--out",out,"--allow-outside","--","/bin/echo","hi"]
    p=subprocess.run(a,cwd=S65,capture_output=True,env=c1c.clean_env(),timeout=120)
    v="accept" if p.returncode==0 and os.path.isfile(out) else ("refuse" if p.returncode==2 and not os.path.lexists(out) else f"err{p.returncode}")
    print(f"{slotname:55s} {v:7s} :: {p.stderr.decode()[:130].strip()}")
    return v

print("== DEPLOYED repo: tools/instr.sh is the 'real' instrument (different bytes), root copy == the counter seed bytes; --instrument given as a bare basename ==")
for slotname in ("base","new"):
    repo,rev,out=mk("deploy-"+slotname,True,True,True)
    run(repo,rev,out,slotname,BBp if slotname=="base" else NEW)
print("   probe behavior matches counter's own seed;")
print("   the counter's instrument=instr.sh resolution is now INFORMATIVE: the root copy matches seed")
print("== DEPLOYED repo with no seed-matching instr.sh anywhere (root_ok=False) ==")
for slotname in ("base","new"):
    repo,rev,out=mk("deploy-noseed-"+slotname,False,True,True)
    run(repo,rev,out,slotname,BBp if slotname=="base" else NEW)
print("== --instrument tools/instr.sh (rootsub=False to force), deployed multiple tool copies ==")
for slotname in ("base","new"):
    repo,rev,out=mk("deploy-toolsonly-"+slotname,False,True,False)  # root_ok False → no root copy → mirror the deployed reality
    root = os.path.join(repo,"tools")
    a=["python3","-B",BBp if slotname=="base" else NEW,"--root",repo,"--rev",rev,"--instrument","tools/instr.sh",
       "--out",out,"--allow-outside","--","/bin/echo","hi"]
    p=subprocess.run(a,cwd=S65,capture_output=True,env=c1c.clean_env(),timeout=120)
    v="accept" if p.returncode==0 and os.path.isfile(out) else ("refuse" if p.returncode==2 and not os.path.lexists(out) else f"err{p.returncode}")
    print(f"{slotname:55s} {v:7s} :: {p.stderr.decode()[:130].strip()}")

print("== MODE-ONLY FIXTURE-CRAFT: append 'dirty' to notes.txt, no flip; then in-run chmod both copies of instr.sh (mode 755->600, NOT following content) ==")
def mk2(which, inrun_chmod):
    d=os.path.join(S65,"n4deploy2",which)
    if os.path.isdir(d): shutil.rmtree(d)
    os.makedirs(d+"/repo/tools")
    subprocess.run(["git","-C",d+"/repo","init","-q"],check=True)
    subprocess.run(["git","-C",d+"/repo","config","user.name","N4D2"],check=True)
    subprocess.run(["git","-C",d+"/repo","config","user.email","n4d2@v"],check=True)
    open(d+"/repo/instr.sh","wb").write(c1c.SEED_INSTR); os.chmod(d+"/repo/instr.sh",0o755)
    open(d+"/repo/tools/instr.sh","wb").write(c1c.SEED_INSTR); os.chmod(d+"/repo/tools/instr.sh",0o755)
    open(d+"/repo/tools/notes.txt","wb").write(c1c.SEED_NOTES)
    open(d+"/repo/README.md","wb").write(c1c.SEED_README)
    e={**os.environ,"GIT_AUTHOR_DATE":c1c.GIT_DATE,"GIT_COMMITTER_DATE":c1c.GIT_DATE}
    subprocess.run(["git","-C",d+"/repo","add","-A"],check=True,env=e)
    subprocess.run(["git","-C",d+"/repo","commit","-q","-m","c1 seed"],check=True,env=e)
    rev=subprocess.run(["git","-C",d+"/repo","rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()
    # force a skip-worktree flag on README + forged bytes — the N4 forge
    subprocess.run(["git","-C",d+"/repo","update-index","--skip-worktree","README.md"],check=True)
    open(d+"/repo/README.md","wb").write(c1c.FORGED_README)
    # in-run chmod of BOTH instr.sh copies — the content stays identical
    w = ["/bin/echo","hi"]
    if inrun_chmod:
        w=[sys.executable,"-c", f"import os\nos.chmod({d!r}+('/repo/instr.sh'),0o600)"
                                f"\nos.chmod({d!r}+('/repo/tools/instr.sh'),0o600)"]
    os.makedirs(d+"/out")
    return repo,rev,d,out,w,subprocess
def run2(slotname, slot, repo, rev, d, out, w):
    root=os.path.join(repo,"tools")
    a=["python3","-B",slot,"--root",root,"--rev",rev,"--instrument","instr.sh",
       "--out",out+"/r.txt","--allow-outside"]+["--",*w]
    p=subprocess.run(a,cwd=S65,capture_output=True,env=c1c.clean_env(),timeout=120)
    v="accept" if p.returncode==0 and os.path.isfile(out+"/r.txt") else ("refuse" if p.returncode==2 and not os.path.lexists(out+"/r.txt") else f"err{p.returncode}")
    print(f"{slotname:55s} {v:7s} :: {p.stderr.decode()[:130].strip()}")
for slotname in ("base","new"):
    repo,rev,d,out,w,_=mk2("mflip-"+slotname, True)
    run2(slotname, BBp if slotname=="base" else NEW, repo, rev, d, out, w)
# honest baseline control: no chmod, both dual copies, in-run clean
for slotname in ("base","new"):
    repo,rev,d,out,w,_=mk2("mctrl-"+slotname, False)
    run2(slotname, BBp if slotname=="base" else NEW, repo, rev, d, out, w)
