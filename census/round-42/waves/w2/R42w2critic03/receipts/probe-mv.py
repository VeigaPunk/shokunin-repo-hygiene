import os, shutil, subprocess, sys
S = "/fast/scratch/hyaku/souji-r42/R42w2critic03/probe"
exec(open(S + "/probe.py").read().split("cases = {")[0].replace("S = \"/fast/scratch/hyaku/souji-r42/R42w2critic03/probe\"", "S = \"%s\"" % S))
def mk(name):
    d = os.path.join(S, name); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    def git(*a): return subprocess.run(["git", "-C", d] + list(a), env=ENV, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()
    git("init", "-q", "-b", "main", ".")
    if git("rev-parse", "--show-toplevel") != d: raise SystemExit("root mismatch")
    return d, git
def check(name, d, rev, tool):
    p = subprocess.run([sys.executable, "-B", TOOLS[tool], "--root", d, "--prereg", "census/prereg.txt", "--rev", rev], env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("== %s [%s] rc=%d" % (name, tool, p.returncode)); print(p.stdout.rstrip()); 
    if p.stderr.strip(): print("stderr:", p.stderr.strip())
# case A: dispatch file created by git mv from a non-matching name, before freeze
for tool in TOOLS:
    d, git = mk("dispatch-git-mv-before-freeze")
    os.makedirs(d + "/.ufo/waves/round-42"); open(d + "/README", "w").write("x"); git("add", "-A"); git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    os.makedirs(d + "/census"); open(d + "/census/c.py", "w").write(CTR); open(d + "/census/p.tsv", "w").write(POP); open(d + "/census/ctl.txt", "w").write("x\nEXIT=1\n")
    git("add", "-A"); git("commit", "-q", "-m", "instruments")
    open(d + "/.ufo/waves/round-42/notes.md", "w").write("x"); git("add", "-A"); git("commit", "-q", "-m", "notes")
    git("mv", ".ufo/waves/round-42/notes.md", ".ufo/waves/round-42/w1-dispatch.json"); git("commit", "-q", "-m", "rename to dispatch")
    open(d + "/census/prereg.txt", "w").write(claim(base=base)); git("add", "-A"); git("commit", "-q", "-m", "freeze")
    check("dispatch-git-mv-before-freeze", d, git("rev-parse", "HEAD"), tool)
    print("   git log --name-status:", git("log", "--name-status", "--format=%h %s", "--", ".ufo/waves/round-42/").replace("\n", " | "))
# case B: Counter becomes a symlink after the freeze
for tool in TOOLS:
    d, git = mk("counter-symlink-after-freeze")
    open(d + "/README", "w").write("x"); git("add", "-A"); git("commit", "-q", "-m", "base"); base = git("rev-parse", "HEAD")
    os.makedirs(d + "/census"); open(d + "/census/c.py", "w").write(CTR); open(d + "/census/p.tsv", "w").write(POP); open(d + "/census/ctl.txt", "w").write("x\nEXIT=1\n")
    open(d + "/census/prereg.txt", "w").write(claim(base=base)); git("add", "-A"); git("commit", "-q", "-m", "freeze")
    os.remove(d + "/census/c.py"); os.symlink("p.tsv", d + "/census/c.py"); git("add", "-A"); git("commit", "-q", "-m", "counter becomes symlink")
    check("counter-symlink-after-freeze", d, git("rev-parse", "HEAD"), tool)
