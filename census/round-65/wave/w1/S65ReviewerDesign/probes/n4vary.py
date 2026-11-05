import os, subprocess, sys, importlib.util, shutil
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65="/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
LANE="/home/vgpnk/Projects/shokunin/souji-shokunin"
NEW=os.path.join(S65,"writer-landed.py"); BASEV="4a43a4d919c5b51ae9be859a1266ce4b11337b0b"
BBp=os.path.join(S65,"base-all.py")

def mk(which, dual, tools_differs):
    d=os.path.join(S65,"n4vary",which)
    if os.path.isdir(d): shutil.rmtree(d)
    os.makedirs(d+"/repo/tools")
    subprocess.run(["git","-C",d+"/repo","init","-q"],check=True)
    subprocess.run(["git","-C",d+"/repo","config","user.name","N4V"],check=True)
    subprocess.run(["git","-C",d+"/repo","config","user.email","n4@v"],check=True)
    open(d+"/repo/tools/instr.sh","wb").write(c1c.SEED_INSTR); os.chmod(d+"/repo/tools/instr.sh",0o755)
    open(d+"/repo/tools/notes.txt","wb").write(c1c.SEED_NOTES)
    open(d+"/repo/README.md","wb").write(c1c.SEED_README)
    if dual: shutil.copyfile(d+"/repo/tools/instr.sh", d+"/repo/instr.sh"); os.chmod(d+"/repo/instr.sh",0o755)
    if tools_differs:
        open(d+"/repo/tools/instr.sh","wb").write(b"#!/bin/sh\necho TOOLS-VARIANT\n"); os.chmod(d+"/repo/tools/instr.sh",0o755)
    e={**os.environ,"GIT_AUTHOR_DATE":c1c.GIT_DATE,"GIT_COMMITTER_DATE":c1c.GIT_DATE}
    subprocess.run(["git","-C",d+"/repo","add","-A"],check=True,env=e)
    subprocess.run(["git","-C",d+"/repo","commit","-q","-m","c1 seed"],check=True,env=e)
    rev=subprocess.run(["git","-C",d+"/repo","rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()
    subprocess.run(["git","-C",d+"/repo","update-index","--skip-worktree","README.md"],check=True)
    open(d+"/repo/README.md","wb").write(c1c.FORGED_README)
    os.makedirs(d+"/out")
    return d+"/repo", rev, d+"/out/r.txt"

def run(repo, rev, out, slotname, slot, rootsub=True, instrument="instr.sh"):
    root = os.path.join(repo,"tools") if rootsub else repo
    a=["python3","-B",slot,"--root",root,"--rev",rev,"--instrument",instrument,"--out",out,"--allow-outside","--","/bin/echo","hi"]
    p=subprocess.run(a,cwd=S65,capture_output=True,env=c1c.clean_env(),timeout=120)
    v="accept" if p.returncode==0 and os.path.isfile(out) else ("refuse" if p.returncode==2 and not os.path.lexists(out) else f"err{p.returncode}")
    print(f"{slotname:20s} {v:7s} :: {p.stderr.decode()[:120].strip()}")
    return v

print("== dual copy, tools copy == the root copy (frozen shape) ==")
for slotname in ("base","new"):
    repo,rev,out=mk("frozen-"+slotname,True,False)
    run(repo,rev,out,slotname,BBp if slotname=="base" else NEW)

print("== dual copy, tools copy DIFFERS from root copy (two NONEQUAL blobs at rev) ==")
for slotname in ("base","new"):
    repo,rev,out=mk("difftools-"+slotname,True,True)
    run(repo,rev,out,slotname,BBp if slotname=="base" else NEW)

print("== dual copy with DIFFERENT bytes per copy, --root repo root, --instrument tools/instr.sh ==")
for slotname in ("base","new"):
    repo,rev,out=mk("difftools-root-"+slotname,True,True)
    run(repo,rev,out,slotname,BBp if slotname=="base" else NEW,rootsub=False,instrument="tools/instr.sh")

print("== no dual copy (reviewer shape R) ==")
for slotname in ("base","new"):
    repo,rev,out=mk("nodual-"+slotname,False,False)
    run(repo,rev,out,slotname,BBp if slotname=="base" else NEW)
