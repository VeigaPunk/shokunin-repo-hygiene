import subprocess, sys, os, importlib.util
spec = importlib.util.spec_from_file_location("h", "/fast/scratch/hyaku/souji-r86/S86ExecEvade/harness-lab.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
LANE="/home/vgpnk/Projects/shokunin/souji-shokunin"; FLEET="/home/vgpnk/Projects/shokunin"
work="/fast/scratch/hyaku/souji-r86/S86ExecEvade/work"; os.makedirs(work, exist_ok=True)
fx, revs = h.build_fixture(LANE, work); R10=revs["R10"]
for name, counter in [("pristine","/fast/scratch/hyaku/souji-r86/S86ExecEvade/c1/c1-pointer-counter.py"),
                      ("mut-intround","/fast/scratch/hyaku/souji-r86/S86ExecEvade/c1/mut-intround.py")]:
    fid="NX3"; forge=os.path.join(work,f"forge-{fid}.tsv")
    open(forge,"w").write(f"{fid}\tP04\tMOVED\t.ufo/waves/round-032/w2/SwarmExecutor08.md\tREFUSED\n")
    p=subprocess.run([sys.executable,"-B",counter,"--root",fx,"--rev",R10,"--fleet-root",FLEET,
      "--population",os.path.join(LANE,"census/round-77/c2-population.tsv"),
      "--ledger",os.path.join(LANE,"census/round-77/c2-pointer-ledger.tsv"),"--forge",forge],capture_output=True,text=True,cwd=LANE)
    for line in p.stdout.splitlines():
        if line.startswith("FORGE"): print(name+" "+line)
