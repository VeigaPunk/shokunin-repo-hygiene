import importlib.util, os, subprocess, sys, shutil
LANE="/home/vgpnk/Projects/shokunin/souji-shokunin"
spec=importlib.util.spec_from_file_location("c1s", os.path.join(LANE,"census/round-94/c1-survivor-search.py"))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
S="/fast/scratch/hyaku/souji-r94/R94Sentinel"; env=dict(os.environ); env["PYTHONPATH"]=os.path.join(S,"hook")
# a) the frozen counter's own source with the crash moved into a THREAD
src=open(os.path.join(LANE,"census/round-87/c1-pointer-counter.py")).read()
old="    return 0 if ok else 1\n"
thr=("    import threading\n"
     "    threading.Thread(target=lambda: (_ for _ in ()).throw(RuntimeError(\"boom-thread\"))).start()\n"
     "    threading.Event().wait(0.2)\n" + old)
assert src.count(old)==1
open(os.path.join(S,"real","counter-thread.py"),"w").write(src.replace(old,thr,1))
# b) a counter that LEGITIMATELY exits 70
open(os.path.join(S,"real","counter-exit70.py"),"w").write("import sys\nprint('ITEM P19 x status=REFUSED')\nsys.exit(70)\n")
for name,c in (("thread-crash", os.path.join(S,"real","counter-thread.py")),
               ("legit-exit-70", os.path.join(S,"real","counter-exit70.py"))):
    w=os.path.join(S,"real","wG-"+name); shutil.rmtree(w, ignore_errors=True)
    p=subprocess.run([sys.executable,"-B",os.path.join(LANE,"census/round-93/c1-false-row-harness.py"),
        "--counter",c,"--lane",LANE,"--fleet-root","/home/vgpnk/Projects/shokunin",
        "--population",os.path.join(LANE,"census/round-93/c1-false-rows.tsv"),"--work",w],
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
    out=p.stdout
    rows=[l for l in out.decode("utf-8","replace").splitlines() if l.startswith("ROW ")]
    rcs=sorted({l.split(" rc=")[1].split(" ")[0] for l in rows if " rc=" in l})
    summ=[l for l in out.decode("utf-8","replace").splitlines() if l.startswith("SUMMARY")]
    print(f"{name:14s} harness_rc={p.returncode} r94_verdict={m.verdict(p.returncode,out)!r} row_rcs={rcs}")
    print(f"               {summ}")
    print(f"               harness_stderr_tail={p.stderr.decode()[-200:]!r}")
