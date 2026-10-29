import json, os, subprocess, sys, time
real = "/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py"
t0 = time.monotonic()
try:
    p = subprocess.run(["python3", "-B", real] + sys.argv[1:], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    rc, out, err = p.returncode, p.stdout, p.stderr
except subprocess.TimeoutExpired as e:
    rc, out, err = None, e.stdout or b"", e.stderr or b""
with open("/fast/scratch/hyaku/souji-r42/R42w2executor02/c3/calls.jsonl", "a") as h:
    h.write(json.dumps({"argv": sys.argv[1:], "cwd": os.getcwd(), "rc": rc, "dt": round(time.monotonic()-t0, 2),
        "out": out.decode("utf-8", "replace")[:160], "err": err.decode("utf-8", "replace")[:160]}) + "\n")
sys.stdout.buffer.write(out); sys.stderr.buffer.write(err)
sys.exit(rc if rc is not None else 124)
