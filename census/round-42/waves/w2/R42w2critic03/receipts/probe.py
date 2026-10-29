import hashlib, os, shutil, subprocess, sys
S = "/fast/scratch/hyaku/souji-r42/R42w2critic03/probe"
TOOLS = {"r41": "/fast/scratch/hyaku/souji-r42/R42w2critic03/tools/r41-freeze-check.py",
         "landed": "/fast/scratch/hyaku/souji-r42/R42w2critic03/tools/landed-freeze-check.py"}
ENV = {"PATH": os.environ["PATH"], "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
       "GIT_CONFIG_SYSTEM": os.devnull, "GIT_AUTHOR_NAME": "p", "GIT_AUTHOR_EMAIL": "p@example.invalid",
       "GIT_COMMITTER_NAME": "p", "GIT_COMMITTER_EMAIL": "p@example.invalid", "TMPDIR": S}
def sha(s): return hashlib.sha256(s.encode()).hexdigest()
CTR = "c\n"; POP = "h\nr\n"
def claim(head="## C1", extra="", base=None, counter=None, pop=None, kill="k", pre_round="Round: 42\n"):
    return (pre_round + head + "\nBase: %s\nCounter: census/c.py sha256=%s\nPopulation: census/p.tsv sha256=%s\n"
            "Control: census/ctl.txt\nTarget: t\nKill: %s\n" % (base, sha(CTR), sha(POP), kill) + extra)
def run(name, tool, pre_fn, pre_commits=None, post=None):
    d = os.path.join(S, name)
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    def git(*a): return subprocess.run(["git", "-C", d] + list(a), env=ENV, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()
    def commit(files, msg="c"):
        for p, c in files.items():
            fp = os.path.join(d, p); os.makedirs(os.path.dirname(fp) or d, exist_ok=True)
            if os.path.lexists(fp): os.remove(fp)
            if isinstance(c, tuple): os.symlink(c[0], fp)
            elif c is None: continue
            else: open(fp, "w").write(c)
        git("add", "-A"); git("commit", "-q", "--allow-empty", "-m", msg)
    git("init", "-q", "-b", "main", ".")
    if git("rev-parse", "--show-toplevel") != d: raise SystemExit("root mismatch")
    commit({"README": "x"}, "base")
    base = git("rev-parse", "HEAD")
    commit({"census/c.py": CTR, "census/p.tsv": POP, "census/ctl.txt": "x\nEXIT=1\n"}, "instruments")
    for pc in (pre_commits or []): commit(pc, "pre")
    commit({"census/prereg.txt": pre_fn(base)}, "freeze")
    if post: commit(post, "post")
    rev = git("rev-parse", "HEAD")
    p = subprocess.run([sys.executable, "-B", TOOLS[tool], "--root", d, "--prereg", "census/prereg.txt", "--rev", rev],
                       env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("== %s [%s] rc=%d" % (name, tool, p.returncode))
    for l in p.stdout.splitlines(): print("   ", l)
    if p.stderr.strip(): print("    stderr:", p.stderr.strip()[:200])
cases = {
 "clean": (lambda b: claim(base=b), None, None),
 "stray-headingC-mid-claim": (lambda b: claim(base=b, extra="##C2\n"), None, None),
 "stray-kill-after-ctl": (lambda b: claim(base=b).replace("Target: t\n", "Target: t\n##C1 x\n"), None, None),
 "header-tab-tail": (lambda b: claim(head="## C1\tx", base=b), None, None),
 "header-trailing-space": (lambda b: claim(head="## C1 ", base=b), None, None),
 "dup-claim-label-C1-twice": (lambda b: claim(base=b) + "\n" + claim(base=b, kill="other"), None, None),
 "dup-key-in-subsection": (lambda b: claim(base=b, extra="### notes\nKill: other\n"), None, None),
 "round-41-in-preamble": (lambda b: "Round: 41\n" + claim(base=b), [{".ufo/waves/round-42/w1-dispatch.json": "x"}], None),
 "dispatch-upper-DISPATCH": (lambda b: claim(base=b), [{".ufo/waves/round-42/w1-DISPATCH.json": "x"}], None),
 "dispatch-rename-before-freeze": (lambda b: claim(base=b), [{".ufo/waves/round-42/notes.md": "x"}, {".ufo/waves/round-42/notes.md": None}], None),
 "dispatch-plain-dispatch-json": (lambda b: claim(base=b), [{".ufo/waves/round-42/w1-dispatch.json": "x"}], None),
}
which = sys.argv[1:] or list(cases)
for n in which:
    fn, pc, post = cases[n]
    for t in TOOLS: run(n, t, fn, pc, post)

def rename_case():
    d = os.path.join(S, "dispatch-git-mv-before-freeze")
