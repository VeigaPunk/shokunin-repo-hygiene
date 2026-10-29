# R42critic05 outside-counter check (v2): which mutants change the tool's observable output on a probe set?
# Mutants come from the frozen MUTANTS/EQUIV tables of the scratch copy of the counter (read only).
import importlib.util, os, shutil, stat, subprocess, sys
S = "/fast/scratch/hyaku/souji-r42/R42critic05"
spec = importlib.util.spec_from_file_location("c3", S + "/c3-counter.orig.py")
c3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c3)
src = open(S + "/pristine.py", encoding="utf-8").read()
D = S + "/diff2"
shutil.rmtree(D, ignore_errors=True)
os.makedirs(D + "/root/ok"); os.makedirs(D + "/root/bad"); os.makedirs(D + "/elsewhere/.git")
os.makedirs(D + "/rootsib/.git"); os.makedirs(D + "/cwd"); os.makedirs(D + "/slowbin")
open(D + "/root/bad/.git", "w").write("gitdir: /nonexistent/gd\n")
os.symlink(D + "/elsewhere", D + "/root/lnk")
REAL_GIT = shutil.which("git")
subprocess.run([REAL_GIT, "init", "-q", "--bare", D + "/root2/gd"] if os.makedirs(D + "/root2") is None else [], check=True)
os.makedirs(D + "/root/gdrepo")
open(D + "/root/gdrepo/.git", "w").write("gitdir: " + D + "/root2/gd\n")
open(D + "/slowbin/git", "w").write("#!/bin/sh\nsleep 2\nexec %s \"$@\"\n" % REAL_GIT)
os.chmod(D + "/slowbin/git", 0o755)
def rec(n, data):
    p = D + "/" + n
    open(p, "wb").write(data); return p
R = {
 "ok": rec("ok.rec", b"REPO\tok\tregs=0\tprunable=0\n"),
 "missing": D + "/none.rec",
 "big": rec("big.rec", b"REPO\tok\tregs=10\tprunable=0\n"),
 "bad": rec("bad.rec", b"REPO\tbad\tregs=0\tprunable=0\n"),
 "bytes": rec("bytes.rec", b"REPO\t\xff\tregs=0\tprunable=0\n"),
 "sib": rec("sib.rec", b"REPO\t../rootsib\tregs=0\tprunable=0\n"),
 "esc": rec("esc.rec", b"REPO\tgdrepo\tregs=0\tprunable=0\n"),
}
os.mkfifo(D + "/fifo.rec"); R["fifo"] = D + "/fifo.rec"
ROOT = D + "/root"
SLOW = {"PATH": D + "/slowbin:" + os.environ["PATH"]}
PROBES = [
 ("help", ["--help"], 5, {}),
 ("noroot", ["--record", R["ok"]], 5, {}),
 ("norec", ["--root", ROOT], 5, {}),
 ("missing", ["--root", ROOT, "--record", R["missing"]], 5, {}),
 ("fifo", ["--root", ROOT, "--record", R["fifo"]], 5, {}),
 ("big", ["--root", ROOT, "--record", R["big"]], 5, {}),
 ("timeout1", ["--root", ROOT, "--record", R["ok"], "--timeout", "1"], 5, {}),
 ("bytes", ["--root", ROOT, "--record", R["bytes"]], 5, {}),
 ("sib", ["--root", ROOT, "--record", R["sib"]], 5, {}),
 ("escape-gitdir", ["--root", ROOT, "--record", R["esc"]], 5, {}),
 ("unrecorded-link", ["--root", ROOT, "--record", R["ok"]], 5, {}),
 ("bad-list-rc", ["--root", ROOT, "--record", R["bad"]], 5, {}),
 ("slowgit-default", ["--root", ROOT, "--record", R["ok"]], 15, SLOW),
 ("slowgit-t1", ["--root", ROOT, "--record", R["ok"], "--timeout", "1"], 15, SLOW),
 ("json-tail", ["--root", ROOT, "--record", R["ok"], "--json", D + "/out.json"], 5, {}),
]
def run(tool, argv, timeout, extra):
    if os.path.exists(D + "/out.json"): os.remove(D + "/out.json")
    if "--json" in argv:
        open(D + "/out.json", "w").write("x" * 5000)
    env = {"PATH": os.environ["PATH"], "TMPDIR": D}
    env.update(extra)
    try:
        p = subprocess.run([sys.executable, "-B", tool] + argv, cwd=D + "/cwd", capture_output=True,
                           timeout=timeout, env=env)
        out = (p.returncode, p.stdout, p.stderr.decode("utf-8", "replace").splitlines()[-1:])
    except subprocess.TimeoutExpired:
        out = ("TIMEOUT",)
    j = open(D + "/out.json", "rb").read() if "--json" in argv and os.path.exists(D + "/out.json") else b""
    return out + (j,)
os.makedirs(D + "/base", exist_ok=True)
pristine = D + "/base/pristine.py"
open(pristine, "w").write(src)
base = {name: run(pristine, argv, t, ex) for name, argv, t, ex in PROBES}
rows = []
for mid, desc, old, new in c3.MUTANTS + c3.EQUIV:
    os.makedirs(D + "/m-%s" % mid, exist_ok=True)
    mpath = D + "/m-%s/pristine.py" % mid
    open(mpath, "w").write(src.replace(old, new))
    diffs = [name for name, argv, t, ex in PROBES if run(mpath, argv, t, ex) != base[name]]
    kind = "MUTANT" if (mid, desc, old, new) in c3.MUTANTS else "EQUIV"
    rows.append((kind, mid, ",".join(diffs) or "-"))
for kind, mid, d in rows:
    print("%s %s observable_on=%s" % (kind, mid, d))
print("PROBES=%d" % len(PROBES))
print("base_escape=%r" % (base["escape-gitdir"][0],))
