#!/usr/bin/env python3
import os, subprocess, sys, shutil
SCRATCH = "/fast/scratch/hyaku/souji-r76/S76ExecEvade"
GATE_DIR = os.path.join(SCRATCH, "gate")
os.makedirs(GATE_DIR, exist_ok=True)
for src, dst in [("gate-W.sh","souji-pre-report-gate.sh"),("writer.py","souji-receipt-write.py")]:
    shutil.copy(os.path.join(SCRATCH,src), os.path.join(GATE_DIR,dst))
GATE = os.path.join(GATE_DIR,"souji-pre-report-gate.sh")
IDENT = {"GIT_AUTHOR_NAME":"fixture","GIT_AUTHOR_EMAIL":"f@invalid","GIT_COMMITTER_NAME":"fixture","GIT_COMMITTER_EMAIL":"f@invalid"}
def git(repo,*a,env=None,check=True):
    assert repo and os.path.isabs(repo), repo
    e=dict(os.environ); e.update(IDENT); e.update(env or {})
    p=subprocess.run(["git","-C",repo,*a],capture_output=True,env=e,timeout=60)
    if check and p.returncode!=0: raise RuntimeError(f"git {' '.join(a)}: {p.stderr.decode()[:200]}")
    return p
def build(name, setup):
    d=os.path.join(SCRATCH,"fx",name); shutil.rmtree(d,ignore_errors=True); os.makedirs(d)
    repo=os.path.join(d,"repo"); os.makedirs(repo)
    git(repo,"init","-q"); assert os.path.realpath(git(repo,"rev-parse","--show-toplevel").stdout.strip().decode())==os.path.realpath(repo)
    open(os.path.join(repo,"a.txt"),"w").write("alpha\n")
    git(repo,"add","a.txt"); git(repo,"commit","-qm","base")
    origin=os.path.join(d,"origin.git")
    subprocess.run(["git","init","-q","--bare",origin],capture_output=True)
    git(repo,"remote","add","origin",origin); git(repo,"push","-q","origin","HEAD:master")
    report=os.path.join(d,"report.md"); open(report,"w").write("## SHONEN\nx\n")
    prereg=os.path.join(d,"prereg.txt"); open(prereg,"w").write("prereg\n")
    setup(repo)
    p=subprocess.run(["bash",GATE,"--lane",repo,"--branch","master","--report",report,"--prereg",prereg],
                     capture_output=True,text=True,timeout=120)
    clean=[l for l in p.stdout.splitlines() if "check-clean" in l]
    det=[l for l in p.stderr.splitlines() if "detail-clean" in l]
    # also attribution internals
    ls=git(repo,"ls-files","-z","--others","--ignored","--exclude-standard").stdout
    ign=sorted(x for x in ls.split(b"\0") if x)
    return {"rc":p.returncode,"clean":clean[0] if clean else "?","detail":det[0][:200] if det else "","ignored":[x.decode(errors='replace') for x in ign]}

def t_honest(repo):
    pass
def t_a_rel(repo):
    # core.excludesFile = relative path to tracked file? excludesFile is read from config; set to sub/.gitignore relative
    os.makedirs(os.path.join(repo,"sub")); open(os.path.join(repo,"sub",".gitignore"),"w").write("payload.txt\n")
    git(repo,"add","sub/.gitignore"); git(repo,"commit","-qm","tracked sub gi")
    git(repo,"config","core.excludesFile","sub/.gitignore")
    open(os.path.join(repo,"payload.txt"),"w").write("secret\n")
def t_a_abs(repo):
    os.makedirs(os.path.join(repo,"sub")); open(os.path.join(repo,"sub",".gitignore"),"w").write("payload.txt\n")
    git(repo,"add","sub/.gitignore"); git(repo,"commit","-qm","tracked sub gi")
    git(repo,"config","core.excludesFile",os.path.join(repo,"sub",".gitignore"))
    open(os.path.join(repo,"payload.txt"),"w").write("secret\n")
def t_b(repo):
    open(os.path.join(repo,".gitignore"),"w").write("hidden/\n")
    git(repo,"add",".gitignore"); git(repo,"commit","-qm","tracked root gi")
    os.makedirs(os.path.join(repo,"hidden"))
    open(os.path.join(repo,"hidden",".gitignore"),"w").write("!payload\n")
    open(os.path.join(repo,"hidden","payload"),"w").write("secret\n")
def t_c(repo):
    os.makedirs(os.path.join(repo,"sub")); open(os.path.join(repo,"sub",".gitignore"),"w").write("old.txt\n")
    git(repo,"add","sub/.gitignore"); git(repo,"commit","-qm","tracked sub gi")
    git(repo,"update-index","--skip-worktree","sub/.gitignore")
    open(os.path.join(repo,"sub",".gitignore"),"a").write("newpayload\n")
    open(os.path.join(repo,"sub","newpayload"),"w").write("secret\n")
def t_d(repo):
    open(os.path.join(repo,".gitignore"),"w").write("payload.txt\n")
    git(repo,"add",".gitignore"); git(repo,"commit","-qm","tracked gi")
    os.makedirs(os.path.join(repo,"linkdir"),exist_ok=True)
    try: os.symlink(os.path.join(repo,".gitignore"), os.path.join(repo,"linkdir",".gitignore"))
    except FileExistsError: pass
    open(os.path.join(repo,"payload.txt"),"w").write("secret\n")
def t_e(repo):
    d=os.path.join(repo,"bad-dir-name\nx"); os.makedirs(d)
    open(os.path.join(d,".gitignore"),"w").write("payload.txt\n")
    open(os.path.join(d,"payload.txt"),"w").write("secret\n")
def t_f(repo):
    open(os.path.join(repo,".gitignore"),"w").write("payload.txt\n")
    git(repo,"add",".gitignore"); git(repo,"commit","-qm","tracked gi")
    with open(os.path.join(repo,".git","info","exclude"),"a") as f: f.write("payload.txt\n")
    open(os.path.join(repo,"payload.txt"),"w").write("secret\n")
def t_g(repo):
    open(os.path.join(repo,".gitignore"),"w").write("payload.txt\n")
    git(repo,"add",".gitignore"); git(repo,"commit","-qm","tracked gi")
    open(os.path.join(repo,"payload.txt"),"w").write("secret\n")
    # ls-files lists but check-ignore unmatched: try .gitignore with leading space? use dir-only pattern vs file later -- variant below
def t_h(repo):
    git(repo,"config","core.ignoreCase","true")
    open(os.path.join(repo,".gitignore"),"w").write("PAYLOAD.TXT\n")
    git(repo,"add",".gitignore"); git(repo,"commit","-qm","tracked gi")
    open(os.path.join(repo,"payload.txt"),"w").write("secret\n")
def t_i(repo):
    open(os.path.join(repo,".gitignore"),"w").write("payload.txt\n")
    git(repo,"add",".gitignore"); git(repo,"commit","-qm","tracked gi")
    open(os.path.join(repo,"payload.txt"),"w").write("secret\n")

TESTS=[("honest",t_honest),("a-rel",t_a_rel),("a-abs",t_a_abs),("b-neg",t_b),("c-skipwt",t_c),
       ("d-symlink",t_d),("e-newline",t_e),("f-exclude",t_f),("g-tracked",t_g),("h-ignorecase",t_h),("i-base",t_i)]
for name,fn in TESTS:
    try:
        r=build(name,fn)
        print(f"{name}: rc={r['rc']} {r['clean']} detail={r['detail']!r} ignored={r['ignored']}")
    except Exception as ex:
        print(f"{name}: ERROR {ex}")
