#!/usr/bin/env python3
import os, subprocess, shutil
SCRATCH="/fast/scratch/hyaku/souji-r76/S76ExecEvade"
exec(open(os.path.join(SCRATCH,"probe.py")).read().split('def t_honest')[0].split('TESTS')[0].replace('for src, dst in','for src, dst in'))
# helpers git(), build() now defined with GATE etc.
def run(name,setup,extra=None):
    try:
        r=build(name,setup); repo=os.path.join(SCRATCH,"fx",name,"repo")
        print(f"{name}: rc={r['rc']} {r['clean']} detail={r['detail']!r} ignored={r['ignored']}")
        return repo
    except Exception as ex:
        print(f"{name}: ERROR {ex}"); return None

def a2(repo):
    os.makedirs(os.path.join(repo,"sub")); open(os.path.join(repo,"sub",".gitignore"),"w").write("payload.txt\n")
    git(repo,"add","sub/.gitignore"); git(repo,"commit","-qm","tracked sub gi")
    git(repo,"config","core.excludesFile",os.path.join(repo,"sub",".gitignore"))
    open(os.path.join(repo,"payload.txt"),"w").write("secret\n")
repo=run("a2",a2)
if repo:
    for args in (["status","--porcelain=v1","--untracked-files=all"],
                 ["-c","core.fsmonitor=false","-c","core.fileMode=true","status","--porcelain=v1","--untracked-files=all"]):
        p=git(repo,*args,check=False); print("  status",args[0][:12],p.returncode,repr(p.stdout[:200]))
    p=subprocess.run(["git","-C",repo,"-c","core.excludesFile=/dev/null","check-ignore","-v","-n","-z","--stdin"],
                     input=b"payload.txt\0",capture_output=True); print("  check-ignore:",p.returncode, p.stdout)
    p=git(repo,"ls-files","-z","--others","--ignored","--exclude-standard"); print("  ignored-std:",p.stdout)
    p=git(repo,"ls-files","-z","--others","--ignored","--exclude-per-directory=.gitignore"); print("  ignored-perdir:",p.stdout)

def b2(repo):
    open(os.path.join(repo,".gitignore"),"w").write("sub/*\n")
    git(repo,"add",".gitignore"); git(repo,"commit","-qm","tracked root gi")
    os.makedirs(os.path.join(repo,"sub"))
    open(os.path.join(repo,"sub",".gitignore"),"w").write("!payload\n")
    open(os.path.join(repo,"sub","payload"),"w").write("secret\n")
run("b2",b2)

def g2(repo):
    os.makedirs(os.path.join(repo,"sub")); open(os.path.join(repo,"sub",".gitignore"),"w").write("payload\n")
    git(repo,"add","sub/.gitignore"); git(repo,"commit","-qm","tracked sub gi")
    open(os.path.join(repo,"sub","payload"),"w").write("secret\n")
repo=run("g2",g2)
if repo:
    p=git(repo,"ls-files","-z","--others","--ignored","--exclude-standard"); print("  ignored:",p.stdout)
    p=subprocess.run(["git","-C",repo,"-c","core.excludesFile=/dev/null","check-ignore","-v","-n","-z","--stdin"],
                     input=b"sub/payload\0",capture_output=True); print("  check-ignore:",p.returncode,p.stdout)

def g3(repo):
    d=os.path.join(repo,"-"); os.makedirs(d)
    open(os.path.join(d,".gitignore"),"w").write("payload\n")
    git(repo,"add","-/.gitignore"); git(repo,"commit","-qm","tracked dash gi")
    open(os.path.join(d,"payload"),"w").write("secret\n")
run("g3",g3)

def i2(repo):
    open(os.path.join(repo,".gitignore"),"w").write("payload.txt\n")
    git(repo,"add",".gitignore"); git(repo,"commit","-qm","tracked gi")
    open(os.path.join(repo,"payload.txt"),"w").write("secret\n")
    os.chmod(os.path.join(repo,".gitignore"),0o000)
run("i2",i2)
