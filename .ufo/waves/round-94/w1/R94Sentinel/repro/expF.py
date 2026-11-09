import importlib.util, os, subprocess, sys, shutil
LANE="/home/vgpnk/Projects/shokunin/souji-shokunin"
spec=importlib.util.spec_from_file_location("c1s", os.path.join(LANE,"census/round-94/c1-survivor-search.py"))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
S="/fast/scratch/hyaku/souji-r94/R94Sentinel"; env=dict(os.environ); env["PYTHONPATH"]=os.path.join(S,"hook")
for name, c in (("atexit-shutdown-crash", os.path.join(S,"real","counter-atexit.py")),):
    w=os.path.join(S,"real","wF"); shutil.rmtree(w, ignore_errors=True)
    p=subprocess.run([sys.executable,"-B",os.path.join(LANE,"census/round-93/c1-false-row-harness.py"),
        "--counter",c,"--lane",LANE,"--fleet-root","/home/vgpnk/Projects/shokunin",
        "--population",os.path.join(LANE,"census/round-93/c1-false-rows.tsv"),"--work",w],
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
    out=p.stdout
    rows=[l for l in out.decode("utf-8","replace").splitlines() if l.startswith("ROW ")]
    rcs=sorted({l.split(" rc=")[1].split(" ")[0] for l in rows if " rc=" in l})
    v=m.verdict(p.returncode,out)
    print(f"{name}: harness_rc={p.returncode} r94_verdict={v!r} distinct_row_rcs={rcs} rows={len(rows)}")
    summ=[l for l in out.decode("utf-8","replace").splitlines() if l.startswith("SUMMARY")]
    print("  harness SUMMARY:", summ)
    print("  harness stderr tail:", p.stderr.decode()[-300:].replace("\n"," | "))
