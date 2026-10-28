import subprocess, os, sys, glob
S="/fast/scratch/hyaku/souji-r41/R41w2executor04"
def run(arm, extra_for):
    T=S+"/"+arm
    tool=T+"/tools/souji-worktree-drift.py"
    out=[]
    for f in sorted(glob.glob(T+"/tests/fixtures/r*-*.py")):
        n=os.path.basename(f)
        if not any(n.startswith(p) for p in ("r36-","r37-","r38-","r39-","r40-","r41-")): continue
        if arm=="base" and n.startswith("r41-"): continue
        w=S+"/w/%s-%s"%(arm,n[:-3]); os.makedirs(w,exist_ok=True)
        tmp=S+"/w/tmp-%s-%s"%(arm,n[:-3]); os.makedirs(tmp,exist_ok=True)
        args=["python3","-B",f]
        if n=="r36-report-gate.py": args+=["--work",w]
        elif n=="r40-c1-evidence.py": args+=["--work",w]
        elif n=="r40-docstring-joined.py": args+=["--tool",tool]
        elif n=="r37-drift-mutants.py": args+=["--tool",tool,"--fixture",T+"/tests/fixtures/r37-drift-discrimination.py","--work",w]
        elif n=="r38-drift-mutants.py": args+=["--tool",tool,"--fixture",T+"/tests/fixtures/r38-drift-record.py","--base-fixture",T+"/tests/fixtures/r37-drift-discrimination.py","--work",w]
        elif "citation" in n or n=="r38-counter-arms.py": args+=["--tool",T+"/tools/souji-citation-reconcile.py","--work",w]
        elif n in ("r37-drift-escapes.py","r38-drift-write-envelope.py"): args+=["--tool",tool,"--base-tool",S+"/base/tools/souji-worktree-drift.py","--work",w]
        else: args+=["--tool",tool,"--work",w]
        env=dict(os.environ,TMPDIR=tmp)
        p=subprocess.run(args,cwd=T,env=env,capture_output=True,text=True,timeout=1200)
        full=p.stdout+p.stderr
        open(S+"/w/log-%s-%s.txt"%(arm,n[:-3]),"w").write("CMD: "+" ".join(args)+"\n"+full+"\nEXIT %d\n"%p.returncode)
        sm=[l for l in full.splitlines() if l.startswith("SUMMARY") or "SUMMARY" in l]
        print("%s %s exit=%d"%(arm,n,p.returncode)); print("   CMD:"," ".join(args))
        for l in sm: print("   ",l)
        if not sm: print("    (no SUMMARY) last:",full.strip().splitlines()[-3:] )
        sys.stdout.flush()
run(sys.argv[1],None)
