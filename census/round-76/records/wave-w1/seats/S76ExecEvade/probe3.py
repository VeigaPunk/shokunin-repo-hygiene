#!/usr/bin/env python3
import os, subprocess
SCRATCH="/fast/scratch/hyaku/souji-r76/S76ExecEvade"
exec(open(os.path.join(SCRATCH,"probe.py")).read().split('def t_honest')[0].split('TESTS')[0])
def spawn(name,setup):
    try:
        r=build(name,setup); repo=os.path.join(SCRATCH,"fx",name,"repo"); print(f"{name}: rc={r['rc']} {r['clean']} detail={r['detail']!r} ignored={r['ignored']}"); return repo
    except Exception as ex: print(f"{name}: ERROR {ex}"); return None

def g3(repo):
    d=os.path.join(repo,"-"); os.makedirs(d)
    open(os.path.join(d,".gitignore"),"w").write("payload\n")
    git(repo,"add","--","-/.gitignore"); git(repo,"commit","-qm","tracked dash gi")
    open(os.path.join(d,"payload"),"w").write("secret\n")
repo=spawn("g3",g3)
if repo:
    p=subprocess.run(["git","-C",repo,"-c","core.excludesFile=/dev/null","check-ignore","-v","-n","-z","--stdin"],input=b"-/payload\0",capture_output=True); print("  check-ignore:",p.returncode,p.stdout)

def h2(repo):
    # sparse-checkout
    git(repo,"sparse-checkout","init","--cone")
    git(repo,"sparse-checkout","set","a.txt")
    open(os.path.join(repo,".gitignore"),"w").write("payload.txt\n")
    git(repo,"add","--",".gitignore"); git(repo,"commit","-qm","tracked gi")
    open(os.path.join(repo,"payload.txt"),"w").write("secret\n")
spawn("h2-sparse",h2)

def i3(repo):
    # check-ignore rc128: set core.excludesFile to a directory
    os.makedirs(os.path.join(repo,"exdir"))
    git(repo,"config","core.excludesFile",os.path.join(repo,"exdir"))
    open(os.path.join(repo,"payload.txt"),"w").write("secret\n")
repo=spawn("i3",i3)
if repo:
    p=git(repo,"ls-files","-z","--others","--ignored","--exclude-standard",check=False); print("  ignored-std rc",p.returncode,p.stdout[:100],p.stderr[:100])
