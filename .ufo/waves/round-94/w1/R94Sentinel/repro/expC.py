import importlib.util, os, subprocess, sys
LANE="/home/vgpnk/Projects/shokunin/souji-shokunin"
spec=importlib.util.spec_from_file_location("c1s", os.path.join(LANE,"census/round-94/c1-survivor-search.py"))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
S="/fast/scratch/hyaku/souji-r94/R94Sentinel"; HOOKDIR=os.path.join(S,"hook")
env=dict(os.environ); env["PYTHONPATH"]=HOOKDIR

# faithful harness stdout shapes (from census/round-93/c1-false-row-harness.py)
LATE = b"ROW NF1 where=lane rev=BASE item=P19 class=TOKEN expect=REFUSED/- got=REFUSED rc=%d match=yes\nROW LP3 where=lane rev=BASE item=P01 class=QUARANTINED expect=REFUSED/1 got=REFUSED rc=%d match=no\nSUMMARY rows=66 mismatches=1 accepted=0 refused_true=0 errors=0\n"
EARLY = b"ROW NF1 where=lane rev=BASE item=P19 class=TOKEN expect=REFUSED/- got=- rc=%d match=error detail='x'\nSUMMARY rows=66 mismatches=0 accepted=0 refused_true=0 errors=1\n"
CASES = {
 "raise-main":      'raise RuntimeError("boom")\n',
 "atexit-raise":    'import atexit\ndef h():\n    raise RuntimeError("boom-atexit")\natexit.register(h)\nprint("ITEM P19 x status=REFUSED")\n',
 "del-raise":       'class C:\n    def __del__(self):\n        raise RuntimeError("boom-del")\nC()\nprint("ITEM P19 x status=REFUSED")\nimport gc; gc.collect()\n',
 "os._exit(1)":     'import os\nprint("ITEM P19 x status=REFUSED")\nos._exit(1)\n',
 "os._exit(70)":    'import os\nprint("ITEM P19 x status=REFUSED")\nos._exit(70)\n',
 "sigsegv":         'import os, signal\nos.kill(os.getpid(), signal.SIGSEGV)\n',
 "sigkill":         'import os, signal\nos.kill(os.getpid(), signal.SIGKILL)\n',
}
print("case           direct_rc  r94_verdict(LATE-out)  r94_verdict(EARLY-out)  stderr-note")
for name, body in CASES.items():
    c=os.path.join(S,"micro",f"cc-{name}.py"); open(c,"w").write(body)
    p=subprocess.run([sys.executable,"-B",c], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    err=p.stderr.decode().strip().splitlines()
    note = err[-1][:50] if err else ""
    # the harness's exit code: 1 if any row mismatched or errors>0, else 0
    v_late = m.verdict(1, LATE % (p.returncode, p.returncode))
    v_early = m.verdict(1, EARLY % (p.returncode,))
    print(f"{name:15s} {p.returncode:5d}  {v_late:22s}  {v_early:22s}  {note}")
