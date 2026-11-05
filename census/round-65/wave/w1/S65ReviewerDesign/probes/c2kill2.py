# The C2 counter reads ALL bytes from --rev's blob graph (no --new-tool CLI). To prove the lexical
# live-marker limit I need mutant blobs committed in a SCRATCH git repo: stash the counter's populated
# universe in a shadow clone, mutate the writer blob there, and run the counter against it.
import os, subprocess, shutil, filecmp
LANE="/home/vgpnk/Projects/shokunin/souji-shokunin"
S65="/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
CLONE=S65+"/c2clone"
if os.path.isdir(CLONE): shutil.rmtree(CLONE)
subprocess.run(["git","clone","--shared","--no-hardlinks",LANE,CLONE],check=True,capture_output=True)
subprocess.run(["git","-C",CLONE,"config","user.name","S65RD"],check=True)
subprocess.run(["git","-C",CLONE,"config","user.email","s65rd@invalid"],check=True)
TIP=subprocess.run(["git","-C",LANE,"rev-parse","refs/heads/master"],capture_output=True,text=True).stdout.strip()
print("tip:", TIP)

def run_c2(rev, label):
    r=subprocess.run(["python3","-B",LANE+"/census/round-65/c2-counter.py","--root",CLONE,
                      "--tsv","census/round-65/c2-statements.tsv","--tsv-rev","2761f0aa4d2431b4b9abb4aa997dd3116b0b25b8",
                      "--rev",rev],capture_output=True,text=True)
    last=[l for l in r.stdout.splitlines() if l.startswith("MARKERS") or l.startswith("SUMMARY") or l.startswith("FINDING")]
    print(f"-- {label}: rc={r.returncode}")
    for l in last: print("   ", l)

# control
run_c2(TIP, "control Clone tip")

# mutant a: dead-token (all four needles in trailing comment only, no live emission lines)
w=subprocess.run(["git","-C",LANE,"show",f"{TIP}:tools/souji-receipt-write.py"],capture_output=True).stdout.decode()
m1=w
for n in ["RECEIPT-INDEX-FLAG-CONCEALED","RECEIPT-STATE-CHANGED-DURING-RUN","RECEIPT-INDEX-ENV-SET","RECEIPT-INDEX-UNMERGED"]:
    m1=m1.replace(n,"X"+n[1:])
m1+="\n# DEAD RECEIPT-INDEX-FLAG-CONCEALED RECEIPT-STATE-CHANGED-DURING-RUN RECEIPT-INDEX-ENV-SET RECEIPT-INDEX-UNMERGED\n"
open(CLONE+"/tools/souji-receipt-write.py","w").write(m1)
subprocess.run(["git","-C",CLONE,"commit","-qam","mutant-dead-token"],check=True,capture_output=True)
DEAD=subprocess.run(["git","-C",CLONE,"rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()
run_c2(DEAD, "mutant a dead-token")

# mutant b: live-looking but unreachable: wrap each refuse() call in `if False:`
lines=w.splitlines()
out=[]
for i,l in enumerate(lines):
    s=l.lstrip()
    if s.startswith("refuse(") or (("refuse(" in s) and ("if " not in s and s.startswith("refuse"))):
        out.append("if False: "+l)
    else:
        out.append(l)
m2="\n".join(out)+"\n"
open(CLONE+"/tools/souji-receipt-write.py","w").write(m2)
subprocess.run(["git","-C",CLONE,"add","tools/souji-receipt-write.py"],check=True)
subprocess.run(["git","-C",CLONE,"commit","-qam","mutant-if-False"],check=True,capture_output=True)
IF=subprocess.run(["git","-C",CLONE,"rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()
run_c2(IF, "mutant b if-False-gated")
