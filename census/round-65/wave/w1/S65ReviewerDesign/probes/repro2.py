import sys, importlib.util, os, subprocess
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65 = "/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
NEW = os.path.join(S65, "writer-landed.py")
BASEV = "4a43a4d919c5b51ae9be859a1266ce4b11337b0b"

def base_bytes(tag):
    p = subprocess.run(["git","-C",LANE,"show",f"{BASEV}:tools/souji-receipt-write.py"],capture_output=True)
    path = os.path.join(S65, f"base-{tag}.py"); open(path,"wb").write(p.stdout); return path

def run(specdict, slot, ap_permit, label):
    wr = os.path.join(S65, "repro2", label); os.makedirs(wr + "/out")
    rep, rev = c1c.build_repo(wr)
    c1c.mutate(rep, specdict)
    instr = "instr.sh" if specdict.get("inrun_subdir") else "tools/instr.sh"
    wrapped = c1c.wrapped_argv(specdict, rep)
    a = [sys.executable, "-B", slot, "--root", rep, "--rev", rev, "--instrument", instr,
         "--out", wr + "/out/r.txt", "--allow-outside"] + (["--allow-dirty"] if specdict.get("allow_dirty") else []) + ["--", *wrapped]
    env = c1c.clean_env(c1c.case_env(specdict, rep))
    p = subprocess.run(a, cwd=S65, capture_output=True, env=env, timeout=120)
    rc = p.returncode
    verdict = "accept" if rc==0 and os.path.isfile(wr+"/out/r.txt") else ("refuse" if rc==2 and not os.path.lexists(wr+"/out/r.txt") else f"error({rc})")
    print(f"{label:38s} slot={'new' if slot==NEW else 'base':4s} verdict={verdict} stderr={p.stderr.decode()[:140].strip()}")
    return verdict

# N2: allow-dirty + pre-existing untracked dir tools/extra + in-run new file inside
run({"name":"N2","allow_dirty":True,"untracked_dir":"tools/extra","inrun":"untracked-dir-new"}, NEW, True, "N2-new")
run({"name":"N2","allow_dirty":True,"untracked_dir":"tools/extra","inrun":"untracked-dir-new"}, base_bytes("n2"), True, "N2-base")
# N4: subdirectory root, forge outside subtree (skip-worktree on README.md)
run({"name":"N4","flag":"skip-worktree","target":"README.md","forged":b"readme FORGED\n"}, NEW, False, "N4-new(subroot)")
run({"name":"N4","flag":"skip-worktree","target":"README.md","forged":b"readme FORGED\n"}, base_bytes("n4"), False, "N4-base(subroot)")
