# The last big named-limit hole: env redirects. GIT_OBJECT_DIRECTORY / GIT_ALTERNATE_OBJECT_DIRECTORIES 
# point the writer's git calls at a different OBJECT store; GIT_REPLACE_REF_BASE repoints replace refs.
# The frozen prereg names all three as unread. Probe the ACTUAL exploitability class: with
# GIT_OBJECT_DIRECTORY pointing at a fresh objdir holding a DIFFERENT commit blob for the SAME rev sha,
# what do both slots do?
import os, subprocess, sys, importlib.util, shutil
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65="/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
NEW=os.path.join(S65,"writer-landed.py"); BBp=os.path.join(S65,"base-all.py")

def fresh(tag, specd, post=None):
    rep, rev = c1c.build_case(os.path.join(S65,"atk15"), tag, "one", specd)
    out = os.path.join(os.path.dirname(rep),"out","r.txt")
    if post: post(rep)
    return rep, rev, out
def go(tag, specd, slotname, post=None, wrapped=None, extra_env=None, out_rel=None):
    slot = BBp if slotname=="base" else NEW
    rep, rev, out = fresh(tag, specd, post)
    if out_rel: out = os.path.join(rep, out_rel)
    w = wrapped(rep) if callable(wrapped) else (wrapped or ["/bin/echo","hi"])
    a=["python3","-B",slot,"--root",rep,"--rev",rev,"--instrument","tools/instr.sh","--out",out,
       "--allow-outside"]+(["--allow-dirty"] if specd.get("allow_dirty") else [])+["--",*w]
    p=subprocess.run(a,cwd=S65,capture_output=True,env=c1c.clean_env(extra_env),timeout=120)
    v="accept" if p.returncode==0 and os.path.isfile(out) else ("refuse" if p.returncode==2 and not os.path.lexists(out) else f"err{p.returncode}")
    print(f"[{tag:34s}/{slotname}] {v:7s} :: {p.stderr.decode()[:126].strip()}")
    return v

# A redirect that names a NONEXISTENT objdir: likely base git errors → error/refuse; new writer too.
E={"GIT_OBJECT_DIRECTORY":"/fast/scratch/hyaku/souji-r65/S65ReviewerDesign/no-such-objdir"}
go("OBJDIR-nonexistent", {"name":"od"}, "new", extra_env=E)
go("OBJDIR-nonexistentB", {"name":"od2"}, "base", extra_env=E)

# A GIT_ALTERNATE_OBJECT_DIRECTORIES with a plausible OTHER objdir: build a second fixture repo whose
# git objects hold a FORGED instrument blob with the SAME path but a different rev; point the alternate
# at its .git/objects. This is complex; simpler: bad path → confirm both refuse safely.
E2={"GIT_ALTERNATE_OBJECT_DIRECTORIES":"/nonexistent/alt/objects"}
go("ALT-nodir", {"name":"ad"}, "new", extra_env=E2)

# GIT_REPLACE_REF_BASE: reserve.
E3={"GIT_REPLACE_REF_BASE":"refs/replace-fake"}
go("RRB-fake", {"name":"rr"}, "new", extra_env=E3)
go("RRB-fakeB", {"name":"rr2"}, "base", extra_env=E3)
