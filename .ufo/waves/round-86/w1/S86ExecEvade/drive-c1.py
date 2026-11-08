import subprocess, sys, os, hashlib
sys.path.insert(0, "/fast/scratch/hyaku/souji-r86/S86ExecEvade")
# reuse harness build_fixture by importing file
import importlib.util
spec = importlib.util.spec_from_file_location("h", "/fast/scratch/hyaku/souji-r86/S86ExecEvade/harness-lab.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
LANE="/home/vgpnk/Projects/shokunin/souji-shokunin"; FLEET="/home/vgpnk/Projects/shokunin"
work="/fast/scratch/hyaku/souji-r86/S86ExecEvade/work"; os.makedirs(work, exist_ok=True)
fx, revs = h.build_fixture(LANE, work)
print("REVS "+ " ".join(f"{k}={v[:12]}" for k,v in revs.items()))
R10=revs["R10"]
counter="/fast/scratch/hyaku/souji-r86/S86ExecEvade/c1/c1-pointer-counter.py"
# forge probes: P04 item population r77
probes=[
 ("NX1","P04","MOVED",".ufo/waves/round-32/wx/SwarmExecutor08.md"),
 ("NX2","P04","MOVED",".ufo/waves/round-32/w2a/SwarmExecutor08.md"),
 ("NX3","P04","MOVED",".ufo/waves/round-032/w2/SwarmExecutor08.md"),
 ("NX4","P04","MOVED",".ufo/waves/round-32/assimilationX/SwarmExecutor08.md"),
 ("NX5","P04","MOVED",".ufo/waves/round-32/a2w1x/SwarmExecutor08.md"),
 ("NX6","P04","MOVED",".ufo/waves/round-32/w0/SwarmExecutor08.md"),
]
for fid,item,cls,tgt in probes:
    forge=os.path.join(work,f"forge-{fid}.tsv")
    open(forge,"w").write(f"{fid}\t{item}\t{cls}\t{tgt}\tREFUSED\n")
    p=subprocess.run([sys.executable,"-B",counter,"--root",fx,"--rev",R10,"--fleet-root",FLEET,
      "--population",os.path.join(LANE,"census/round-77/c2-population.tsv"),
      "--ledger",os.path.join(LANE,"census/round-77/c2-pointer-ledger.tsv"),
      "--forge",forge],capture_output=True,text=True,cwd=LANE)
    for line in p.stdout.splitlines():
        if line.startswith("FORGE"): print(line)
    print(f"  rc={p.returncode} tgt={tgt}")
