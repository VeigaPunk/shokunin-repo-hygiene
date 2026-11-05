import os, subprocess, sys, importlib.util, shutil
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65="/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
NEW=os.path.join(S65,"writer-landed.py"); BBp=os.path.join(S65,"base-all.py")

def fresh(tag, specd, post=None):
    rep, rev = c1c.build_case(os.path.join(S65,"atk6"), tag, "one", specd)
    out = os.path.join(os.path.dirname(rep), "out", "r.txt")
    if post: post(rep)
    return rep, rev, out

def go(tag, specd, slotname, post=None, extra_env=None, wrapped=None):
    slot = BBp if slotname=="base" else NEW
    rep, rev, out = fresh(tag, specd, post)
    w = wrapped(rep) if callable(wrapped) else (wrapped or ["/bin/echo","hi"])
    a=["python3","-B",slot,"--root",rep,"--rev",rev,"--instrument","tools/instr.sh",
       "--out",out,"--allow-outside"]+(["--allow-dirty"] if specd.get("allow_dirty") else [])+["--",*w]
    p=subprocess.run(a,cwd=S65,capture_output=True,env=c1c.clean_env(extra_env),timeout=120)
    v="accept" if p.returncode==0 and os.path.isfile(out) else ("refuse" if p.returncode==2 and not os.path.lexists(out) else f"err{p.returncode}")
    print(f"[{tag:34s}/{slotname}] {v:7s} :: {p.stderr.decode()[:126].strip()}")
    return v, out, rep, rev

# (10) symlink_to_file_outside_repo — recorded by name+target, stable accept. Then in-run: replace the outside-repo symlink with one pointing to a DIFFERENT outside file:
def post_outside(rep):
    os.symlink("/etc/hostname", os.path.join(rep,"tools/extra","link"))
def w_swap_outside(rep):
    return [sys.executable,"-c",f"import os\nl={rep!r}+'/tools/extra/link'\nos.unlink(l)\nos.symlink('/etc/os-release', l)"]
specd={"name":"SY-out","untracked_dir":"tools/extra","allow_dirty":True}
go("SY-outside-swap", specd, "new", post=post_outside, wrapped=w_swap_outside)

# (11) symlink swapped for a REGULAR FILE at the same name in-run (fingerprint 'symlink:'->'0o644:...')
def post_outside2(rep): os.symlink("/etc/hostname", os.path.join(rep,"tools/extra","link"))
def w_swap_regular(rep):
    return [sys.executable,"-c",f"import os\nl={rep!r}+'/tools/extra/link'\nos.unlink(l)\nopen(l,'wb').write(b'now-regular\\n')"]
go("SY-swap-to-regular-out", specd, "new", post=post_outside2, wrapped=w_swap_regular)

# (12) symlink pointing to a path that DURING the run becomes a different file (target's CONTENT changes):
#     _snapshot_entry records TARGET STRING, not target's content, so content churn in target file is invisible.
def post_target(rep): os.symlink("../notes.txt", os.path.join(rep,"tools/extra","link"))
def w_target_content(rep):
    return [sys.executable,"-c",f"import os\np={rep!r}+'/tools/notes.txt'\nd=open(p,'rb').read()\nopen(p,'wb').write(d+b'TAMPER\\n')"]
specd2={"name":"SY-tc","untracked_dir":"tools/extra","allow_dirty":True,"dirty":True}
go("SY-target-content-tamper", specd2, "new", post=post_target, wrapped=w_target_content)
go("SY-target-content-base", specd2, "base", post=post_target, wrapped=w_target_content)

# (13) symlinked DIRECTORY swapped for a REAL dir in-run (fingerprint 'symlink:...'->walk 'dir'-keys):
def post_dirlink(rep): os.symlink("realdir", os.path.join(rep,"tools/extra","dirlink"))
def w_dirswap(rep):
    return [sys.executable,"-c",
            "import os, shutil\n"
            f"d={rep!r}+'/tools/extra'\n"
            "os.unlink(d+'/dirlink')\n"
            "os.mkdir(d+'/dirlink')\n"
            "open(d+'/dirlink/planted.txt','wb').write(b'planted\\n')"]
specd3={"name":"SY-dl","untracked_dir":"tools/extra","allow_dirty":True}
go("SY-dirlink-swap-to-dir", specd3, "new", post=post_dirlink, wrapped=w_dirswap)
go("SY-dirlink-stable", specd3, "new", post=post_dirlink)
