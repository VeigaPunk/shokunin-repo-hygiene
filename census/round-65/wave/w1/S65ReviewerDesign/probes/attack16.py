# GIT_ALTERNATE_OBJECT_DIRECTORIES pointing at a REAL alt object store that contains a forged blob
# with the same instrument content but at the SAME rev the fixture referenced? An alternate adds
# objects; it cannot SHADOW existing ones by sha. But: git alternates can introduce NEW objects. If
# the caller writes a forged blob whose sha equals the fixture's instrument blob sha, they'd need a
# sha collision. So alternates alone cannot redefine objects NOT present in the main objdir.
# The exploit shape: a fixture repo whose instrument blob is NOT in the main objdir (deleted from the
# main store, only present in the alternate) — the writer works as long as SOME objstore has it.
# The forge: --allow-dirty + skip-worktree still catches the flagged entry; but the "wrong content"
# check reads from `cat-file blob rev:path` via the alternate. Who wins if BOTH stores carry the blob:
# main wins, alternates are additive only. So a caller can only ADD blobs, never redefine. The remaining
# risk is a plain rev-object fetch from alternates... already additive.
# The practically probeable shape: main objdir REMOVES the instrument blob (impossible without corrupting); skip.
# Instead: probe GIT_COMMON_DIR redirect (not in the named limits): points via common dir to another .git;
# that redirects refs and config (fsmonitor etc.). NOT IN THE NAMED LIMIT SET — a genuine gap probe.
import os, subprocess, sys, importlib.util
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65="/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
NEW=os.path.join(S65,"writer-landed.py"); BBp=os.path.join(S65,"base-all.py")

def fresh(tag, specd):
    rep, rev = c1c.build_case(os.path.join(S65,"atk16"), tag, "one", specd)
    return rep, rev, os.path.join(os.path.dirname(rep),"out","r.txt")
def go(tag, specd, slotname, extra_env=None, wrapped=None):
    slot = BBp if slotname=="base" else NEW
    rep, rev, out = fresh(tag, specd)
    w = wrapped(rep) if callable(wrapped) else (wrapped or ["/bin/echo","hi"])
    a=["python3","-B",slot,"--root",rep,"--rev",rev,"--instrument","tools/instr.sh","--out",out,
       "--allow-outside"]+(["--allow-dirty"] if specd.get("allow_dirty") else [])+["--",*w]
    p=subprocess.run(a,cwd=S65,capture_output=True,env=c1c.clean_env(extra_env),timeout=120)
    v="accept" if p.returncode==0 and os.path.isfile(out) else ("refuse" if p.returncode==2 and not os.path.lexists(out) else f"err{p.returncode}")
    print(f"[{tag:30s}/{slotname}] {v:7s} :: {p.stderr.decode()[:126].strip()}")
    return v

# GIT_COMMON_DIR pointing at a nonexistent common dir: does the writer still resolve toplevel, ls-files,
# status? (main .git/commmon dir contains config, refs, objects of the SHARED store; redirect breaks ...)
# In practice: a nonexistent common dir should break git → refuse; confirm both slots do SAFE refuse.
E={"GIT_COMMON_DIR":"/nonexistent/common"}
go("COMMONDIR-fake", {"name":"cd"}, "new", extra_env=E)
go("COMMONDIR-fakeB", {"name":"cd2"}, "base", extra_env=E)

# GIT_DIR pointing at the repo's own .git: writer scrubs GIT_DIR. GIT_COMMON_DIR is then derived:
# what if GIT_COMMON_DIR points to ANOTHER repo's .git (a legitimate second repo)? config from the other
# repo (fsmonitor) and refs from the other repo (different rev? rev-refs shared: HEAD at other repo = OTHER rev).
# Probe whether the writer then reads OTHER repo's config (i.e., status.showUntrackedFiles=no injected THERE):
def go2(tag, slotname):
    slot = BBp if slotname=="base" else NEW
    rep, rev, out = fresh(tag, {"name":tag,"allow_dirty":True,"dirty":True,"untracked_dir":"tools/extra"})
    # make a second tiny repo whose config carries showUntrackedFiles=no, and use ITS .git as common dir
    second = rep + "-second"
    subprocess.run(["git","init","-q",second],check=True,capture_output=True)
    subprocess.run(["git","-C",second,"config","status.showUntrackedFiles","no"],check=True)
    E={"GIT_COMMON_DIR": second + "/.git"}
    a=["python3","-B",slot,"--root",rep,"--rev",rev,"--instrument","tools/instr.sh","--out",out,
       "--allow-outside","--allow-dirty","--","/bin/echo","hi"]
    p=subprocess.run(a,cwd=S65,capture_output=True,env=c1c.clean_env(E),timeout=120)
    v="accept" if p.returncode==0 and os.path.isfile(out) else ("refuse" if p.returncode==2 and not os.path.lexists(out) else f"err{p.returncode}")
    print(f"[{tag:30s}/{slotname}] {v:7s} :: {p.stderr.decode()[:126].strip()}")
go2("COMMONDIR-config-leak", "new")
go2("COMMONDIR-config-leakB", "base")
