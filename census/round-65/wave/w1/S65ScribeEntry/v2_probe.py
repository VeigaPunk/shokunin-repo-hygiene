#!/usr/bin/env python3
"""V2 honest polarity + the closes/does-not-close matrix, per-slot fresh repos.
V2: repo-local status.showUntrackedFiles=no, CLEAN tree (no untracked file) -> the override
must not turn an honest clean run into a refusal (expect accept on both slots).
"""
import os, shutil, subprocess
W="/fast/scratch/hyaku/souji-r65/S65ScribeEntry"
NEW, BASE = f"{W}/wprobe/writer.py", f"{W}/base-writer.py"
def sh(*a, env=None): return subprocess.run(a, capture_output=True, text=True, env=env)
def make(d, untracked):
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    sh("git","init","-q",d); sh("git","-C",d,"config","user.email","a@b.c"); sh("git","-C",d,"config","user.name","t")
    open(f"{d}/instr.sh","w").write("tool\n"); open(f"{d}/tracked.txt","w").write("x\n")
    sh("git","-C",d,"add","instr.sh","tracked.txt"); sh("git","-C",d,"commit","-qm","init")
    if untracked: open(f"{d}/untracked.txt","w").write("hidden\n")
    return sh("git","-C",d,"rev-parse","HEAD").stdout.strip()
for arm, untracked in (("V2-clean-tree", False), ("V1-dirty-tree", True)):
    for name, wtr in (("base",BASE),("new",NEW)):
        d=f"{W}/ex/{arm}-{name}"; rev=make(d, untracked)
        sh("git","-C",d,"config","--local","status.showUntrackedFiles","no")
        out=f"{d}/receipt-out.txt"
        r=sh("python3","-B",wtr,"--root",d,"--rev",rev,"--instrument","instr.sh","--out",out,"--command","/bin/echo hi")
        print(f"{arm:15s} {name:4s} rc={r.returncode} receipt={'yes' if os.path.exists(out) else 'no'} stderr={r.stderr.strip()[:90]!r}")
