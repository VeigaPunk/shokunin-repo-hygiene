import os, subprocess, sys, importlib.util, shutil
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65="/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
NEW=os.path.join(S65,"writer-landed.py")

def fresh(tag, specd):
    rep, rev = c1c.build_case(os.path.join(S65,"atk13"), tag, "one", specd)
    return rep, rev, os.path.join(os.path.dirname(rep),"out","r.txt")

specd={"name":"ng","allow_dirty":True,"untracked_dir":"tools/extra"}

for tag, churn in (("NG-pre", False), ("NG-churn", True)):
    rep, rev, out = fresh(tag, specd)
    gd = os.path.join(rep,"tools/extra/nested/.git")
    os.makedirs(gd+"/refs/heads")
    open(gd+"/HEAD","w").write("ref: refs/heads/main\n")
    open(gd+"/config","w").write("[core]\n\tbare = false\n")
    env=dict(os.environ); env.update({"GIT_AUTHOR_DATE":"2026-11-05T12:00:00Z","GIT_COMMITTER_DATE":"2026-11-05T12:00:00Z",
        "GIT_AUTHOR_NAME":"ng","GIT_AUTHOR_EMAIL":"ng@v","GIT_COMMITTER_NAME":"ng","GIT_COMMITTER_EMAIL":"ng@v"})
    subprocess.run(["git","--git-dir",gd,"commit","--allow-empty","-q","-m","x"],capture_output=True,env=env)
    head0=os.path.join(gd,"refs/heads/main")
    if os.path.exists(head0):
        with open(head0) as f: h0=f.read()
    else: h0=""
    wrapped = ["/bin/echo","hi"]
    if churn:
        wrapped=["python3","-c",f"open({head0!r},'a').write('# churn\\n')"]
    p=subprocess.run(["python3","-B",NEW,"--root",rep,"--rev",rev,"--instrument","tools/instr.sh","--out",out,
                      "--allow-outside","--allow-dirty","--",*wrapped],cwd=S65,capture_output=True,env=c1c.clean_env(),timeout=120)
    v="accept" if p.returncode==0 and os.path.isfile(out) else ("refuse" if p.returncode==2 and not os.path.lexists(out) else f"err{p.returncode}")
    print(f"[{tag:10s}] {v:7s} :: {p.stderr.decode()[:150].strip()}")
