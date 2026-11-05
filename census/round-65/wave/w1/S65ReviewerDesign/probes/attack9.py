import os, subprocess, sys, importlib.util, shutil
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65="/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
NEW=os.path.join(S65,"writer-landed.py"); BBp=os.path.join(S65,"base-all.py")

# --- setuid/sticky/gid flips: RERUN with proper allow_dirty pre-dirty (matches MOD pattern exactly)
def fresh(tag, specd):
    rep, rev = c1c.build_case(os.path.join(S65,"atk9"), tag, "one", specd)
    return rep, rev, os.path.join(os.path.dirname(rep),"out","r.txt")
def go(tag, seed, post, slotname, dirty=True):
    specd={"name":tag,"allow_dirty":True}
    if dirty: specd["dirty"]=True
    rep, rev, out = fresh(tag, specd)
    os.chmod(os.path.join(rep,"tools/notes.txt"), seed)
    w=[sys.executable,"-c",f"import os; os.chmod({os.path.join(rep,'tools/notes.txt')!r}, {oct(post)})"]
    slot = BBp if slotname=="base" else NEW
    a=["python3","-B",slot,"--root",rep,"--rev",rev,"--instrument","tools/instr.sh","--out",out,
       "--allow-outside","--allow-dirty","--",*w]
    p=subprocess.run(a,cwd=S65,capture_output=True,env=c1c.clean_env(),timeout=120)
    v="accept" if p.returncode==0 and os.path.isfile(out) else ("refuse" if p.returncode==2 and not os.path.lexists(out) else f"err{p.returncode}")
    print(f"[{tag:26s}/{slotname}] {v:7s} :: {p.stderr.decode()[:118].strip()}")
    return v

# The counter's frozen MOD row: chmod(0o755) on notes.txt — content-same 775->755 flip: refuse. 
# Prv-bit variants in RUN (same content, only sub-777 bit churn):
go("priv-suid-add-755-4755", 0o0755, 0o4755, "new")
go("priv-suid-add-755-4755B", 0o0755, 0o4755, "base")
go("priv-sticky-add-755-1755", 0o0755, 0o1755, "new")
go("priv-setgid-add-755-2755", 0o0755, 0o2755, "new")
go("priv-suid-drop-4755-755", 0o4755, 0o0755, "new")
go("priv-all-flip-1775-0775", 0o1775, 0o0775, "new")

# --- a fchown-style chmod during run: read::write junk; skip chown (needs priv)
# --- MOD polarity row: the mode digits table must NOT tell the truth about the harshest bits.
