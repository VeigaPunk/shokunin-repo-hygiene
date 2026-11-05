# Out-dir symlink escape probe WITHOUT --allow-outside (default). 
import os, subprocess, sys, importlib.util
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65="/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
NEW=os.path.join(S65,"writer-landed.py"); BBp=os.path.join(S65,"base-all.py")
def fresh(tag):
    rep, rev = c1c.build_case(os.path.join(S65,"atk18"), tag, "one", {"name":tag,"allow_dirty":True})
    return rep, rev
for slotname, slot in (("base",BBp),("new",NEW)):
    rep, rev = fresh("OE-"+slotname)
    os.makedirs(S65+f"/atk18/OE-{slotname}/one/outside", exist_ok=True)
    os.symlink(S65+f"/atk18/OE-{slotname}/one/outside", os.path.join(rep,"outsymlink"))
    out = os.path.join(rep, "outsymlink", "r.txt")
    p=subprocess.run(["python3","-B",slot,"--root",rep,"--rev",rev,"--instrument","tools/instr.sh","--out",out,
                      "--allow-dirty","--","/bin/echo","hi"],cwd=S65,capture_output=True,env=c1c.clean_env(),timeout=120)
    v="accept" if p.returncode==0 and os.path.isfile(out) else ("refuse" if p.returncode==2 and not os.path.lexists(out) else f"err{p.returncode}")
    print(f"[OUT-symlink-escape NO-outside/{slotname}] {v:7s} :: {p.stderr.decode()[:135].strip()}")
