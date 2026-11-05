import os, sys, subprocess, importlib.util
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65 = "/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
NEW = os.path.join(S65, "writer-landed.py")
BASEV = "4a43a4d919c5b51ae9be859a1266ce4b11337b0b"
BBp = os.path.join(S65, "base-all.py")

def slotrun(tag, specd, slotname, slot):
    rep, rev = c1c.build_case(os.path.join(S65, "n4n2"), tag, slotname, specd)
    outd = os.path.join(os.path.dirname(rep), "out"); out = os.path.join(outd, "r.txt")
    rootsub = specd.get("rootsub")
    root = os.path.join(rep, rootsub) if rootsub else rep
    instr = "instr.sh" if rootsub else "tools/instr.sh"
    a = [sys.executable, "-B", slot, "--root", root, "--rev", rev, "--instrument", instr,
         "--out", out, "--allow-outside"] + (["--allow-dirty"] if specd.get("allow_dirty") else []) + ["--", *c1c.wrapped_argv(specd, rep)]
    p = subprocess.run(a, cwd=S65, capture_output=True, env=c1c.clean_env(c1c.case_env(specd, rep)), timeout=120)
    v = "accept" if p.returncode==0 and os.path.isfile(out) else ("refuse" if p.returncode==2 and not os.path.lexists(out) else f"err{p.returncode}")
    print(f"{tag} slot={slotname:4s} {v:7s} :: {p.stderr.decode()[:120].strip()}")

N4s = c1c.CASE_SPECS["N4"]; N2s = c1c.CASE_SPECS["N2"]
subprocess.run(["git","-C",LANE,"show",f"{BASEV}:tools/souji-receipt-write.py"], stdout=open(BBp,"wb"), check=True)
slotrun("N4", N4s, "base", BBp); slotrun("N4", N4s, "new", NEW)
slotrun("N2", N2s, "base", BBp); slotrun("N2", N2s, "new", NEW)
