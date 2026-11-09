"""Crash channels that escape the sentinel, driven through the REAL r93 harness + the REAL r94 verdict()."""
import importlib.util, os, subprocess, sys, shutil
LANE="/home/vgpnk/Projects/shokunin/souji-shokunin"
spec=importlib.util.spec_from_file_location("c1s", os.path.join(LANE,"census/round-94/c1-survivor-search.py"))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
S="/fast/scratch/hyaku/souji-r94/R94Sentinel"; HOOKDIR=os.path.join(S,"hook")
env=dict(os.environ); env["PYTHONPATH"]=HOOKDIR
CASES={
 "atexit-raise": 'import atexit\ndef h():\n    raise RuntimeError("boom-atexit")\natexit.register(h)\n',
 "del-raise":    'class C:\n    def __del__(self):\n        raise RuntimeError("boom-del")\nC()\n',
 "os._exit(1)":  'import os\nos._exit(1)\n',
 "sigsegv":      'import os, signal\nos.kill(os.getpid(), signal.SIGSEGV)\n',
 "sigkill":      'import os, signal\nos.kill(os.getpid(), signal.SIGKILL)\n',
 "normal-exit0": 'pass\n',
}
for name, body in CASES.items():
    c=os.path.join(S,"real",f"c-{name}.py"); open(c,"w").write(body)
    w=os.path.join(S,"real",f"w-{name}"); shutil.rmtree(w, ignore_errors=True)
    p=subprocess.run([sys.executable,"-B",os.path.join(LANE,"census/round-93/c1-false-row-harness.py"),
        "--counter",c,"--lane",LANE,"--fleet-root","/home/vgpnk/Projects/shokunin",
        "--population",os.path.join(LANE,"census/round-93/c1-false-rows.tsv"),"--work",w],
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
    out=p.stdout
    v=m.verdict(p.returncode,out)
    rows=[l for l in out.decode("utf-8","replace").splitlines() if l.startswith("ROW ")]
    rcs=sorted({l.split(" rc=")[1].split(" ")[0] for l in rows if " rc=" in l})
    print(f"{name:14s} harness_rc={p.returncode:4d} r94_verdict={v:8s} distinct_row_rcs={rcs} rows={len(rows)}")
