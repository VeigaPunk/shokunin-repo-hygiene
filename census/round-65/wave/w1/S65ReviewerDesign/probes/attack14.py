import os, subprocess, sys, importlib.util, shutil
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65="/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
NEW=os.path.join(S65,"writer-landed.py"); BBp=os.path.join(S65,"base-all.py")

def fresh(tag, specd, post=None):
    rep, rev = c1c.build_case(os.path.join(S65,"atk14"), tag, "one", specd)
    out = os.path.join(os.path.dirname(rep),"out","r.txt")
    if post: post(rep)
    return rep, rev, out
def go(tag, specd, slotname, post=None, wrapped=None, out_rel=None, extra_env=None):
    slot = BBp if slotname=="base" else NEW
    rep, rev, out = fresh(tag, specd, post)
    if out_rel: out = os.path.join(rep, out_rel)
    w = wrapped(rep) if callable(wrapped) else (wrapped or ["/bin/echo","hi"])
    a=["python3","-B",slot,"--root",rep,"--rev",rev,"--instrument","tools/instr.sh","--out",out,
       "--allow-outside"]+(["--allow-dirty"] if specd.get("allow_dirty") else [])+["--",*w]
    p=subprocess.run(a,cwd=S65,capture_output=True,env=c1c.clean_env(extra_env),timeout=120)
    v="accept" if p.returncode==0 and os.path.isfile(out) else ("refuse" if p.returncode==2 and not os.path.lexists(out) else f"err{p.returncode}")
    print(f"[{tag:40s}/{slotname}] {v:7s} :: {p.stderr.decode()[:118].strip()}")
    return v

# (19) MASKED-FILE FORGE: .gitignore'd file whose BYTES diverge from the committed blob while skip-worktree hides it? 
#     No: .gitignore only affects untracked. Skip-worktree already covered. But what about ASSUME-UNCHANGED with gitignore? Same class.
# 
# (19) In-run out-file collision in the untracked dir: with the writer OUT inside the untracked dir the OUT does not exist at
#      post-run reads (receipt written after). But what if the caller's WRAPPED COMMAND writes to a file that is itself a
#      snapshot target inside the untracked dir and then restores the bytes? T4-equivalent: bytes-only equal → accept. probe:
def w_restore(rep):
    p=os.path.join(rep,"tools/extra/keep.txt")
    return [sys.executable,"-c",
            f"d=open({p!r},'rb').read()\nopen({p!r},'ab').write(b'X\\n')\nopen({p!r},'wb').write(d)"]
specd={"name":"t4u","allow_dirty":True,"untracked_dir":"tools/extra"}
go("untracked-restore-in-run", specd, "new", wrapped=w_restore)

# (20) RENAME churn: an untracked file renamed in-run — porcelain path differs (new name); content table keyed by path:
def w_rename(rep):
    return [sys.executable,"-c",
            f"import os\nos.rename({rep!r}+'/tools/extra/keep.txt', {rep!r}+'/tools/extra/kept2.txt')"]
go("untracked-RENAME-in-run", specd, "new", wrapped=w_rename)

# (21) in-run deletion of an untracked DIRECTORY: porcelain '?? tools/extra/' disappears; snapshot keys lost:
def w_rmdir(rep):
    return [sys.executable,"-c",f"import shutil\nshutil.rmtree({rep!r}+'/tools/extra')"]
go("untracked-DIR-deleted-in-run", specd, "new", wrapped=w_rmdir)

# (22) in-run MTIME churn only: touch the notes.txt content-length-preserving, mode-preserving, bytes identical — accept expected.
def w_touch(rep):
    return [sys.executable,"-c",f"import os\nos.utime({rep!r}+'/tools/notes.txt', (1234567890, 1234567890))"]
specd2={"name":"mt","allow_dirty":True,"dirty":True}
go("mtime-churn-only", specd2, "new", wrapped=w_touch)

# (23) In-run: DELETE the pristine tracked file whose porcelain row Y is clean (temporarily) then re-create:
#       covered by T4-type probes. skip.

# (24) instrument-mode granularity: 100644 vs 100755 blob-mode flip via update-index in-run of the INSTRUMENT:
def w_blobmodeflip(rep):
    return ["git","-C",rep,"update-index","--chmod","-x","tools/instr.sh"]
go("MOD-instrument-blobmode-flip", {"name":"bm"}, "new", wrapped=w_blobmodeflip)
go("MOD-instrument-blobmode-flipB", {"name":"bmB"}, "base", wrapped=w_blobmodeflip)
