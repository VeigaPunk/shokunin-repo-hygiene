import sys, importlib.util, os, subprocess, shutil
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shotokunin" if False else "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65 = "/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
NEW = os.path.join(S65, "writer-landed.py")
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"

# Variant: NO dual instr.sh seed at root — writer runs --root <repo>/tools with --instrument tools/instr.sh
def build_n4_variant(which, dual=False, difftool=False):
    case_dir = os.path.join(S65, "n4var", which)
    if os.path.isdir(case_dir): shutil.rmtree(case_dir)
    os.makedirs(os.path.join(case_dir, "ical") if False else case_dir)
    repo = os.path.join(case_dir, "repo"); os.makedirs(repo)
    subprocess.run(["git","-C",repo,"init","-q"], check=True)
    subprocess.run(["git","-C",repo,"config","user.name","N4V"], check=True)
    subprocess.run(["git","-C",repo,"config","user.email","n4@v"], check=True)
    os.makedirs(os.path.join(repo,"tools"))
    seeds = {"tools/instr.sh": c1c.SEED_INSTR, "tools/counter.py": c1c.SEED_COUNTER,
             "tools/notes.txt": c1c.SEED_NOTES, "README.md": c1c.SEED_README}
    if dual: seeds["instr.sh"] = c1c.SEED_INSTR
    for rel, data in seeds.items():
        with open(os.path.join(repo, rel), "wb") as f: f.write(data)
    os.chmod(os.path.join(repo, "tools/instr.sh"), 0o755)
    if difftool:
        with open(os.path.join(repo, "tools/instr.sh"), "wb") as f: f.write(b"#!/bin/sh\necho variant-note\n")
    subprocess.run(["git","-C",repo,"add","-A"], check=True, env={**dict(__import__('os').environ),
        "GIT_AUTHOR_DATE":"2026-11-05T12:00:00Z","GIT_COMMITTER_DATE":"2026-11-05T12:00:00Z"})
    rev = subprocess.run(["git","-C",repo,"rev-parse","HEAD"], capture_output=True, text=True).stdout.strip()
    # N4 mutate: skip-worktree on README.md + forge
    subprocess.run(["git","-C",repo,"update-index","--skip-worktree","README.md"], check=True)
    with open(os.path.join(repo,"README.md"),"wb") as f: f.write(c1c.FORGED_README)
    outdir = os.path.join(case_dir, "out"); os.makedirs(outdir, exist_ok=True)
    return repo, rev, outdir

def run(repo, rev, outdir, slot, subroot_ab=True):
    tools = os.path.join(repo, "tools")
    a = [sys.executable, "-B", slot, "--root", tools, "--rev", rev, "--instrument", "tools/instr.sh",
         "--out", outdir + "/r.txt", "--allow-outside", "--", "/bin/echo", "hi"]
    p = subprocess.run(a, cwd=S65, capture_output=True, timeout=120)
    rc = p.returncode; out = outdir + "/r.txt"
    verdict = "accept" if rc==0 and os.path.isfile(out) else ("refuse" if rc==2 and not os.path.lexists(out) else f"error({rc})")
    print(f"slot={os.path.basename(slot)[:6]:6s} dual={'y' if subroot_ab else 'n'}: {verdict} :: {p.stderr.decode()[:110].strip()}")
    return verdict

# A. dual-seed (frozen shape) — both slots
for slotname, slot in (("new", NEW), ("base", None)):
    if slot is None:
        bb = subprocess.run(["git","-C",LANE,"show","4a43a4d919c5b51ae9be859a1266ce4b11337b0b:tools/souji-receipt-write.py"],capture_output=True).stdout
        slot = os.path.join(S65, "base-n4dual.py"); open(slot,"wb").write(bb)
    repo, rev, outdir = build_n4_variant(slotname, dual=True)
    run(repo, rev, outdir, slot)

# B. NO dual seed — writer --root repo/tools, --instrument tools/instr.sh
for slotname, slot in (("new", NEW), ("base", None)):
    if slot is None:
        bb = subprocess.run(["git","-C",LANE,"show","4a4?3" if False else "4a43a4d919c5b51ae9be859a1266ce4b11337b0b:tools/souji-receipt-write.py"],capture_output=True).stdout
        slot = os.path.join(S65, "base-n4nodual.py"); open(slot,"wb").write(bb)
    repo, rev, outdir = build_n4_variant(slotname, dual=False)
    run(repo, rev, outdir, slot)

# C. NO dual seed + DIFFERENT bytes per copy (two legitimately different instr.sh files at rev)
for slotname, slot in (("new", NEW), ("base", None)):
    if slot is None:
        bb = subprocess.run(["git","-C",LANE,"show","4a43a4d919c5b51ae9be859a1266ce4b11337b0b:tools/instr.sh"],capture_output=True)
        bb2 = subprocess.run(["git","-C",LANE,"show","4a43a4d919c5b51ae9be859a1266ce4b11337b0b:tools/souji-receipt-write.py"],capture_output=True).stdout
        slot = os.path.bounds("x") if False else os.path.join(S65, "base-n4difftool.py"); open(slot,"wb").write(bb2)
    repo, rev, outdir = build_n4_variant(slotname, dual=False, difftool=True)
    run(repo, ref:=rev, outdir, slot)
