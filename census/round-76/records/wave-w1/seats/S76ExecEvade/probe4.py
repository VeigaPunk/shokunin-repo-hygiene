#!/usr/bin/env python3
import os, subprocess
SCRATCH="/fast/scratch/hyaku/souji-r76/S76ExecEvade"
exec(open(os.path.join(SCRATCH,"probe.py")).read().split('def t_honest')[0].split('TESTS')[0])
def spawn(name,setup):
    try:
        r=build(name,setup); repo=os.path.join(SCRATCH,"fx",name,"repo"); print(f"{name}: rc={r['rc']} {r['clean']} detail={r['detail']!r} ignored={r['ignored']}"); return repo
    except Exception as ex: print(f"{name}: ERROR {ex}"); return None
def h2(repo):
    git(repo,"sparse-checkout","init","--cone")
    git(repo,"sparse-checkout","set","--skip-checks","a.txt")
    open(os.path.join(repo,".gitignore"),"w").write("payload.txt\n")
    git(repo,"add","--",".gitignore"); git(repo,"commit","-qm","tracked gi")
    open(os.path.join(repo,"payload.txt"),"w").write("secret\n")
spawn("h2-sparse",h2)
def i3(repo):
    os.makedirs(os.path.join(repo,"exdir"))
    git(repo,"config","core.excludesFile",os.path.join(repo,"exdir"))
    open(os.path.join(repo,"payload.txt"),"w").write("secret\n")
spawn("i3-rc128",i3)
