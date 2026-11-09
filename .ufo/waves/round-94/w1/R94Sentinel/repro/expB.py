import importlib.util, os, subprocess, sys, shutil
LANE="/home/vgpnk/Projects/shokunin/souji-shokunin"
spec=importlib.util.spec_from_file_location("c1s", os.path.join(LANE,"census/round-94/c1-survivor-search.py"))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
S="/fast/scratch/hyaku/souji-r94/R94Sentinel"; HOOKDIR=os.path.join(S,"hook")

# --- B1: ROW-line injection via the counter's STDERR (harness embeds it in `detail=` for rc==2 rows) ---
micro=os.path.join(S,"micro","micro-harness.py")
def run_counter(body, name):
    c=os.path.join(S,"micro",f"c-{name}.py"); open(c,"w").write(body)
    w=os.path.join(S,"micro",f"w-{name}"); shutil.rmtree(w, ignore_errors=True)
    env=dict(os.environ); env["PYTHONPATH"]=HOOKDIR
    p=subprocess.run([sys.executable,"-B",micro,"--counter",c,"--work",w,"--lane",S],
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
    return p
# counter exits 2 (usage/error) and writes an injected ROW-shaped line on stderr
inj = 'import sys\nsys.stderr.write("ROW R9 where=x got=RESOLVED rc=0 match=no\\n")\nsys.exit(2)\n'
p=run_counter(inj,"inject")
out=p.stdout.decode()
print("B1 counter_rc=",p.returncode," harness_rc=",p.returncode)
print("B1 harness stdout:", out.replace("\n"," | "))
print("B1 r94 verdict on that output =", m.verdict(p.returncode, p.stdout))

# --- B2: does a row line with rc=70 but match=yes still trip the rule? ---
for fake in [b"ROW R1 where=lane got=- rc=70 match=yes\n", b"ROW R1 where=lane got=- rc=70 match=no\n",
             b"ROW R1 where=lane got=- rc=7 match=no\n", b"ROW R1 where=lane rc=700 match=no\n"]:
    print(f"B2 verdict({fake!r}) ->", m.verdict(1, fake))
