import os, signal, subprocess, sys, time, glob
S = "/fast/scratch/hyaku/souji-r41/R41w2sentinel02"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
name, fx = sys.argv[1], sys.argv[2]
W = os.path.join(S, "work", name); os.makedirs(W, exist_ok=True)
env = dict(os.environ, TMPDIR=os.path.join(S, "tmp"))
out = open(os.path.join(S, "strace", name + ".stdout"), "w")
err = open(os.path.join(S, "strace", name + ".stderr"), "w")
p = subprocess.Popen(["strace", "-f", "-y", "-s", "300", "-e", "trace=%file,%desc,%process,%signal",
                      "-o", os.path.join(S, "strace", name + ".strace"),
                      "python3", fx, "--tool", LANE + "/tools/souji-worktree-drift.py", "--work", W],
                     stdout=out, stderr=err, env=env, cwd=S,
                     preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_DFL))
def children(pid):
    r = subprocess.run(["pgrep", "-P", str(pid)], capture_output=True, text=True)
    return [int(x) for x in r.stdout.split()]
fx_pid = None
for _ in range(2000):
    kids = children(p.pid)
    if kids:
        fx_pid = kids[0]
        if children(fx_pid): break
    time.sleep(0.01)
sig = open("/proc/%d/status" % fx_pid).read()
print(name, "fixture-pid", fx_pid, [l for l in sig.split("\n") if l.startswith(("SigIgn", "SigCgt"))])
os.kill(fx_pid, signal.SIGINT)
rc = p.wait()
print(name, "strace-wrapper-rc", rc)
time.sleep(1)
left = subprocess.run(["find", W, "-mindepth", "1"], capture_output=True, text=True).stdout.split()
print(name, "leftover-entries-in-work", len(left))
print(name, "tool-children-alive", subprocess.run(["pgrep", "-fc", "souji-worktree-drift.py --root " + W], capture_output=True, text=True).stdout.strip())
