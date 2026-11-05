import os, subprocess, sys, importlib.util
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65 = "/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
NEW = os.path.join(S65, "writer-landed.py")

# 5b-redo: truly clean tree with only an IGNORED file present, no dirty, no gitignore TRACKED
# gitignore itself kept UNTRACKED? no — untracked .gitignore WOULD show as dirty. Keep .gitignore tracked (commit needs amendment) -> use fresh fixture incl gitignore from seed? build_repo doesn't allow. Instead: commit .gitignore in fixture then use that rev.
def mkclean(tag):
    rep, rev = c1c.build_case(os.path.join(S65,"atk2"), tag, "one", {"name":tag})
    with open(os.path.join(rep, ".gitignore"), "wb") as f: f.write(b"notes.ign\n")
    with open(os.path.join(rep, "tools/notes.ign"), "wb") as f: f.write(b"ign\n")
    subprocess.run(["git","-C",rep,"add",".gitignore"], check=True)
    subprocess.run(["git","-C",rep,"commit","-q","-m","ign"], check=True)
    rev2 = subprocess.run(["git","-C",rep,"rev-parse","HEAD"], capture_output=True, text=True).stdout.strip()
    return rep, rev2

rep, rev = mkclean("IG-clean-v2")
for slotname, slot in (("base","/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-receipt-write.py"),("new",NEW)):
    o = os.path.join(os.path.dirname(rep), "out", f"r2-{slotname}.txt")
    p = subprocess.run([sys.executable,"-B",slot,"--root",rep,"--rev",rev,"--instrument","tools/instr.sh",
                        "--out",o,"--allow-outside","--","/bin/echo","hi"],
                       cwd=S65, capture_output=True, env=c1c.clean_env(), timeout=120)
    v = "accept" if p.returncode==0 and os.path.isfile(o) else ("refuse" if p.returncode==2 else f"err{p.returncode}")
    print(f"[IG-clean-v2 {slotname}] {v} :: {p.stderr.decode()[:100].strip()}")

# base-slot comparison for V-normal with untracked hidden file (base honors normal/no → accepts; new refuses = delta BY DESIGN)
rep2, rev2 = c1c.build_case(os.path.join(S65,"atk2"),"Vn2","one",{"name":"Vn2","untracked_file":"tools/hidden.txt"})
subprocess.run(["git","-C",rep2,"config","status.showUntrackedFiles","normal"], check=True)
o = os.path.join(os.path.dirname(rep2), "out", "r-base.txt")
BB2 = subprocess.run(["git","-C","/home/vgpnk/Projects/shokunin/souji-shokunin","show","4a43a4d919c5b51ae9be859a1266ce4b11337b0b:tools/souji-receipt-write.py"], capture_output=True).stdout
bp = os.path.join(S65,"base-vn2.py"); open(bp,"wb").write(BB2)
p = subprocess.run([sys.executable,"-B",bp,"--root",rep2,"--rev",rev2,"--instrument","tools/instr.sh",
                    "--out",o,"--allow-outside","--","/bin/echo","hi"],
                   cwd=S65, capture_output=True, env=c1c.clean_env(), timeout=120)
v = "accept" if p.returncode==0 and os.path.isfile(o) else ("refuse" if p.returncode==2 else f"err{p.returncode}")
print(f"[Vnormal2 BASE] {v} :: {p.stderr.decode()[:100].strip()}")  # expect accept → delta confirmed

# MOD-priv bits: does the recorder see sticky/setuid as "mode" or "content", and does it fire when the FLIP goes sticky->"none"
def dm(tag, seed, post):
    rep, rev = c1c.build_case(os.path.join(S65,"atk2"),tag,"one",{"name":tag,"allow_dirty":True,"dirty":True})
    t = os.path.join(rep,"tools/notes.txt"); os.chmod(t, seed)
    w = [sys.executable,"-c",f"import os; os.chmod({t!r}, {oct(post)})"]
    o = os.path.join(os.path.dirname(rep),"out","r.txt")
    p = subprocess.run([sys.executable,"-B",NEW,"--root",rep,"--rev",rev,"--instrument","tools/instr.sh",
                        "--out",o,"--allow-outside","--allow-dirty","--",*w],
                       cwd=S65, capture_output=True, env=c1c.clean_env(), timeout=120)
    v = "accept" if p.returncode==0 and os.path.isfile(o) else ("refuse" if p.returncode==2 else f"err{p.returncode}")
    print(f"[{tag} seed={oct(seed)} post={oct(post)}] {v} :: {p.stderr.decode()[:110].strip()}")
dm("MOD-su-on", 0o755, 0o4755)      # setuid ADDED in run — mode delta
dm("MOD-su-off", 0o4755, 0o755)     # setuid REMOVED in run
dm("MOD-sg-on", 0o755, 0o2755)
dm("MOD-same-perms-rechown", 0o755, 0o0755)  # no-op chmod — should NOT refuse
