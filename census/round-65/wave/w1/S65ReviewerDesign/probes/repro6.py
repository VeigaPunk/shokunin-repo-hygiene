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

def slotrun(case, specdict, slot, slotname, instr="tools/instr.sh", subroot=None, allow=None, wrapped_override=None):
    rep, rev = c1c.build_case(os.path.join(S65, "repro6"), case, slotname, specdict)
    outdir = os.path.join(os.path.dirname(rep), "out")   # sibling of repo — build_case made it
    out = os.path.join(outdir, "receipt.txt")
    wrapped = wrapped_override if wrapped_override is not None else c1c.wrapped_argv(specdict, rep)
    a = [sys.executable, "-B", slot, "--root", subroot or rep, "--rev", rev, "--instrument", instr,
         "--out", out, "--allow-outside"]
    if (allow if allow is not None else specdict.get("allow_dirty")): a.append("--allow-dirty")
    a += ["--", *wrapped]
    env = c1c.clean_env(c1c.case_env(specdict, rep))
    p = subprocess.run(a, cwd=S65, capture_output=True, env=env, timeout=120)
    rc = p.returncode
    verdict = "accept" if rc==0 and os.path.isfile(out) else ("refuse" if rc==2 and not os.path.lexists(out) else f"error({rc})")
    print(f"{case:4s} slot={slotname:4s} verdict={verdict:7s} stderr={p.stderr.decode()[:150].strip()}")
    return verdict, p.stdout.decode()[-200:], rc

CASES = [("V1",{"name":"V1","config_untracked_no":True,"untracked_file":"tools/hidden.txt"}),
         ("V2",{"name":"V2","config_untracked_no":True}),
         ("MOD",{"name":"MOD","dirty":True,"allow_dirty":True,"inrun":"chmod-dirty"}),
         ("SY1",{"name":"SY1","allow_dirty":True,"untracked_dir":"tools/extra","symlink":True}),
         ("SY2",{"name":"SY2","allow_dirty":True,"untracked_dir":"tools/extra","symlink":True,"inrun":"symlink-retarget"}),
         ("P13",{"name":"P13","flag":"skip-worktree","target":"tools/notes.txt","forged":b"notes FORGED\n","allow_dirty":True,"env_index_missing":True}),
         ("N2",{"name":"N2","allow_dirty":True,"untracked_dir":"tools/extra","inrun":"untracked-dir-new"}),
         ("A",{"name":"honest-clean"}),
         ("B",{"name":"honest-allow-dirty","dirty":True,"allow_dirty":True}),
         ("T4",{"name":"inrun-transient-restore","inrun":"transient-restore"}),
         ("N4",{"name":"N4","flag":"skip-worktree","target":"README.md","forged":b"readme FORGED\n"})]
for case, specd in CASES:
    for slotname, slot in (("new", NEW), ("base", base_bytes(case.lower()))):
        subroot = None; instr = "tools/instr.sh"
        if case == "N4":
            subroot = None
            # subroot needs the repo path; build fresh fixture per call — handled inline by build_case already: rep path differs per slot. We need rep after build → restructure: do N4 in separate loop below.
        slotrun(case, specd, slot, slotname, instr=instr, subroot=subroot)
