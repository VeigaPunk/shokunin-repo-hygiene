#!/usr/bin/env python3
"""Clean probe: each SLOT gets its OWN fresh fixture repo (no cross-slot state).
One untracked file `untracked.txt` in every repo.
Arms differ only in the operator-injected concealment route:
  A repo-local status.showUntrackedFiles=no            (the frozen V1 shape)
  B env-injected core.excludesFile (GIT_CONFIG_* passthrough)
  C repo-local core.excludesFile
  D tracked .gitignore naming untracked.txt           (committed state, not operator config)
  E no concealment (control: the file is plainly untracked)
"""
import os, shutil, subprocess

W = "/fast/scratch/hyaku/souji-r65/S65ScribeEntry"
NEW, BASE = f"{W}/wprobe/writer.py", f"{W}/base-writer.py"
EXCL = f"{W}/ex/excl2.txt"
os.makedirs(f"{W}/ex", exist_ok=True)
open(EXCL, "w").write("*\n")

def sh(*a, env=None):
    return subprocess.run(a, capture_output=True, text=True, env=env)

def make(d, tracked_ignore=False, info_exclude=False):
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    sh("git","init","-q",d); sh("git","-C",d,"config","user.email","a@b.c"); sh("git","-C",d,"config","user.name","t")
    open(f"{d}/instr.sh","w").write("tool\n"); open(f"{d}/tracked.txt","w").write("x\n")
    files=["instr.sh","tracked.txt"]
    if tracked_ignore:
        open(f"{d}/.gitignore","w").write("untracked.txt\n"); files.append(".gitignore")
    sh("git","-C",d,"add",*files); sh("git","-C",d,"commit","-qm","init")
    open(f"{d}/untracked.txt","w").write("hidden\n")
    if info_exclude:
        open(f"{d}/.git/info/exclude","w").write("untracked.txt\n")
    return sh("git","-C",d,"rev-parse","HEAD").stdout.strip()

def slot(arm, name, wtr, cfg, env, tracked_ignore, info_exclude=False):
    d = f"{W}/ex/{arm}-{name}"
    rev = make(d, tracked_ignore, info_exclude)
    for k,v in cfg: sh("git","-C",d,"config","--local",k,v)
    st = sh("git","-C",d,"-c","status.showUntrackedFiles=all","status","--porcelain",env=env).stdout
    out = f"{d}/receipt-out.txt"
    e = dict(os.environ); e.update(env or {})
    r = sh("python3","-B",wtr,"--root",d,"--rev",rev,"--instrument","instr.sh","--out",out,
           "--command","/bin/echo hi", env=e)
    ok = os.path.exists(out)
    return st, r.returncode, ok, r.stderr.strip()
    # note: `receipt-out.txt` is written INTO the repo, so it is itself an untracked file.
    # It is written only AFTER the dirty check, so it cannot influence the check.

ARMS = [
 ("A-V1shape",   [("status.showUntrackedFiles","no")], None, False, False),
 ("B-env-excl",  [], {"GIT_CONFIG_COUNT":"1","GIT_CONFIG_KEY_0":"core.excludesFile","GIT_CONFIG_VALUE_0":EXCL}, False, False),
 ("C-repo-excl", [("core.excludesFile",EXCL)], None, False, False),
 ("D-gitignore", [], None, True, False),
 ("E-info-excl", [], None, False, True),
 ("F-control",   [], None, False, False),
]
for arm, cfg, env, ti, ie in ARMS:
    print(f"=== arm {arm}  cfg={cfg} env={'yes' if env else 'no'} tracked_gitignore={ti} info_exclude={ie}")
    for name, wtr in (("base",BASE),("new",NEW)):
        st, rc, ok, err = slot(arm, name, wtr, cfg, env, ti, ie)
        vis = "VISIBLE" if st.strip() else "INVISIBLE"
        print(f"    {name:4s} status(-c all)={vis}  writer_rc={rc} receipt_written={'yes' if ok else 'no'}  stderr={err[:110]!r}")
