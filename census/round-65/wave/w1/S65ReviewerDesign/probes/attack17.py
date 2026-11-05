# The GIT_COMMON_DIR probe demonstrated broken git repo resolve with foreign common dir — safe refuse both.
# Move to the LAST unprobed area: out-of-repo receipt via symlinked OUT dir (r60 b1 re-check on the new bytes:
# the easy-now check is on the resolved directory; probe an OUT INSIDE the repo via a SYMLINK pointing OUTSIDE).
import os, subprocess, sys, importlib.util
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65="/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
NEW=os.path.join(S65,"writer-landed.py")
def fresh(tag, specd):
    rep, rev = c1c.build_case(os.path.join(S65,"atk17"), tag, "one", specd)
    return rep, rev

# out dir is a symlink inside repo pointing OUTSIDE the repo; writer uses realpath(OUTDIR) → outside → refuse
rep, rev = fresh("OUT-symlink-escape", {"name":"oe","allow_dirty":True})
os.makedirs(S65+"/atk17/OUT-symlink-escape/one/outside", exist_ok=True)
os.symlink(S65+"/atk17/OUT-symlink-escape/one/outside", os.path.join(rep,"outsymlink"))
out = os.path.join(rep, "outsymlink", "r.txt")
p=subprocess.run(["python3","-B",NEW,"--root",rep,"--rev",rev,"--instrument","tools/instr.sh","--out",out,
                  "--allow-outside","--allow-dirty","--","/bin/echo","hi"],cwd=S65,capture_output=True,env=c1c.clean_env(),timeout=120)
v="accept" if p.returncode==0 and os.path.isfile(out) else ("refuse" if p.returncode==2 and not os.path.lexists(out) else f"err{p.returncode}")
print(f"[OUT-symlink-escape allow-outside] {v:7s} :: {p.stderr.decode()[:140].strip()}")
