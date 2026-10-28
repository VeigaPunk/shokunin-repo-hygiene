import importlib.util, os, random, shutil, subprocess, sys, tempfile

FROZEN = "/fast/scratch/hyaku/souji-r41/R41critic05/frozen"
SCR = "/fast/scratch/hyaku/souji-r41/R41critic05"
BASE = os.path.join(SCR, "base-tool.py")
ENV = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "LC_ALL": "C",
       "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
       "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
       "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid"}
N = int(sys.argv[1]) if len(sys.argv) > 1 else 120

spec = importlib.util.spec_from_file_location("r1c", os.path.join(FROZEN, "census/round-41/r1-counter.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
pristine_src = open(os.path.join(FROZEN, "tools/souji-worktree-drift.py"), encoding="utf-8").read()
base_src = open(BASE, encoding="utf-8").read()
mut = {mid: pristine_src.replace(old, new) for mid, old, new, _o in m.MUTANTS}

scratch = tempfile.mkdtemp(prefix="diff.", dir=SCR)


def sh(cmd):
    subprocess.run(cmd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def mkrepo(path):
    os.makedirs(path, exist_ok=True)
    sh(["git", "init", "-q", "-b", "main", path])
    with open(os.path.join(path, "file.txt"), "w") as h:
        h.write("x\n")
    sh(["git", "-C", path, "add", "file.txt"])
    sh(["git", "-C", path, "commit", "-qm", "b"])


def build(kind):
    d = os.path.join(scratch, kind)
    os.makedirs(d)
    fleet = os.path.join(d, "fleet")
    os.makedirs(fleet)
    mkrepo(os.path.join(fleet, "alpha"))
    mkrepo(os.path.join(fleet, "beta"))
    if kind == "gitroot":
        sh(["git", "init", "-q", "-b", "main", fleet])
    return fleet


def tools():
    out = {"base": BASE, "pristine": os.path.join(scratch, "pristine.py")}
    m.write(out["pristine"], pristine_src, 0o755)
    for mid in ("M16", "M19", "M20", "M21"):
        p = os.path.join(scratch, mid + ".py")
        m.write(p, mut[mid], 0o755)
        out[mid] = p
    return out


T = tools()
roots = {"plain": build("plain"), "gitroot": build("gitroot")}
rng = random.Random(41)
stats = {}
diffs = []
for i in range(N):
    kind = rng.choice(["plain", "gitroot"])
    root = roots[kind]
    rows = []
    for name in rng.sample(["alpha", "beta", "fleet", "ghost"], rng.randint(1, 4)):
        rows.append("REPO\t%s\tregs=%d\tprunable=0\n" % (name, rng.choice([1, 1, 2])))
    total_lines = []
    for _ in range(rng.randint(0, 3)):
        total_lines.append("TOTAL\trepos=%d\tregs=%d\tprunable=0\n" % (
            rng.choice([1, 2, 3, 4]), rng.choice([1, 2, 3, 4])))
    body = rows[:]
    for t in total_lines:
        body.insert(rng.randint(0, len(body)), t)
    rec = os.path.join(scratch, "rec-%d.tsv" % i)
    with open(rec, "w") as h:
        h.write("".join(body))
    flags = ["--skip-unrecorded"] if rng.random() < 0.5 else []
    outs = {}
    for tname, tpath in T.items():
        proc = subprocess.run(["python3", "-B", tpath, "--root", root, "--record", rec, "--timeout", "30"] + flags,
                              env=dict(ENV, TMPDIR=scratch), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, check=False, timeout=120)
        outs[tname] = (proc.returncode, proc.stdout, proc.stderr.replace(scratch, "<S>").replace(rec, "<R>"))
    key = tuple(sorted(total_lines))
    nt = len(total_lines)
    for tname in T:
        if tname == "base":
            continue
        same = outs[tname] == outs["base"]
        stats.setdefault((tname, "vs_base"), [0, 0])
        stats[(tname, "vs_base")][0 if same else 1] += 1
        if not same and len(diffs) < 40:
            diffs.append((i, kind, nt, tname, outs["base"][0], outs[tname][0], flags, body))
    for tname in T:
        if tname == "pristine":
            continue
        same = outs[tname] == outs["pristine"]
        stats.setdefault((tname + "@" + kind, "vs_pristine"), [0, 0])
        stats[(tname + "@" + kind, "vs_pristine")][0 if same else 1] += 1
for k in sorted(stats):
    print("AGREE %s %s same=%d differ=%d" % (k[0], k[1], stats[k][0], stats[k][1]))
for d in []:
    print("DIFF case=%d kind=%s totals=%d tool=%s base_rc=%s tool_rc=%s flags=%s body=%r" % (
        d[0], d[1], d[2], d[3], d[4], d[5], d[6], "".join(d[7])))
shutil.rmtree(scratch, ignore_errors=True)
