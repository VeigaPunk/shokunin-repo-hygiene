import os, subprocess, sys, importlib.util, shutil
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65="/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
NEW=os.path.join(S65,"writer-landed.py"); BBp=os.path.join(S65,"base-all.py")

def fresh(tag, specd, post=None):
    rep, rev = c1c.build_case(os.path.join(S65,"atk7"), tag, "one", specd)
    out = os.path.join(os.path.dirname(rep), "out", "r.txt")
    if post: post(rep)
    return rep, rev, out

def go(tag, specd, slotname, post=None, extra_env=None, wrapped=None, instrument="tools/instr.sh", rootsub=None):
    slot = BBp if slotname=="base" else NEW
    rep, rev, out = fresh(tag, specd, post)
    w = wrapped(rep) if callable(wrapped) else (wrapped or ["/bin/echo","hi"])
    root = os.path.join(rep, rootsub) if rootsub else rep
    a=["python3","-B",slot,"--root",root,"--rev",rev,"--instrument",instrument,
       "--out",out,"--allow-outside"]+(["--allow-dirty"] if specd.get("allow_dirty") else [])+["--",*w]
    p=subprocess.run(a,cwd=S65,capture_output=True,env=c1c.clean_env(extra_env),timeout=120)
    v="accept" if p.returncode==0 and os.path.isfile(out) else ("refuse" if p.returncode==2 and not os.path.lexists(out) else f"err{p.returncode}")
    print(f"[{tag:36s}/{slotname}] {v:7s} :: {p.stderr.decode()[:135].strip()}")
    return v

# (14) mode flip on the WRAPPED instrument per se: in-run chmod 755->600 on tools/instr.sh (bytes same).
#     writer does NOT snapshot the instrument itself (instrument isn't dirty / untracked). Does the mode
#     flip of the instrument go UNSEEN? — _snapshot_entry only covers dirty tracked / untracked entries.
#     The instrument is clean tracked — not in the snapshot at all. In-run mode flip on the instrument
#     should leave both porcelain reads AND snapshot identical → accept for BOTH slots (KILL-power hole
#     for the N4/MOD class on instruments).
def w_flipinstr(rep):
    return [sys.executable,"-c",f"import os\nos.chmod({rep!r}+'/tools/instr.sh',0o600)"]
specd={"name":"M-inst","allow_dirty":True}
go("MOD-instrument-mode-flip", specd, "new", wrapped=w_flipinstr)
go("MOD-instrument-mode-flipB", specd, "base", wrapped=w_flipinstr)
# control: in-run CONTENT flip on the instrument changes bytes → porcelain fires:
def w_editinstr(rep):
    return [sys.executable,"-c",f"open({rep!r}+'/tools/instr.sh','wb').write(b'#!/bin/sh\\necho FORGED\\n')"]
go("T2-instrument-content-flipC", {"name":"T2-type"}, "new", wrapped=w_editinstr)  # expect refuse via porcelain

# (15) mode flip on an UNTRACKED FILE (not in a dir; plain untracked file):
def v_specd(): return {"name":"M-unt","allow_dirty":True,"untracked_file":"tools/untracked.txt"}
def w_flipunt(rep):
    return [sys.executable,"-c",f"import os\nos.chmod({rep!r}+'/tools/untracked.txt',0o600)"]
go("MOD-untracked-FILE-mode-flip", v_specd(), "new", wrapped=w_flipunt)
go("MOD-untracked-FILE-mode-flipB", v_specd(), "base", wrapped=w_flipunt)

# (16) mode flip via an in-run rm+recreate (mode change AND content same):
def w_rmrecreate(rep):
    return [sys.executable,"-c",
            f"import os, shutil\np={rep!r}+'/tools/notes.txt'\nd=open(p,'rb').read()\nos.unlink(p)\nopen(p,'wb').write(d)\nos.chmod(p, 0o600)"]
specdm={"name":"M-rr","allow_dirty":True,"dirty":True}
go("MOD-rm-recreate-mode", specdm, "new", wrapped=w_rmrecreate)

# (17) symlink prerun changed LINK PERMISSIONS (mode bits on the link itself) - lchmod unsupported on Linux; skip

# (18) symlink target pointing to another untracked file whose CONTENT changes in-run:
def post_link2(rep):
    open(os.path.join(rep,"tools/extra"),"ab")
    with open(os.path.join(rep,"tools/extra","t.txt"),"wb") as f: f.write(b"t\n")
    os.symlink("t.txt", os.path.join(rep,"tools/extra","lk"))
def w_tamper(rep):
    return [sys.executable,"-c",f"open({rep!r}+'/tools/extra/t.txt','ab').write(b'TAMPER\\n')"]
specdl={"name":"SY-t2","allow_dirty":True,"untracked_dir":"tools/extra"}
go("SY-link-to-untracked-target", specdl, "new", post=post_link2, wrapped=w_tamper)
