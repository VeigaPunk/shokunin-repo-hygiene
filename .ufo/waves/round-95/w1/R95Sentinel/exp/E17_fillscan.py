import os, subprocess, sys, time, fcntl
PY = sys.executable
HOOK_DIR = "/fast/scratch/hyaku/souji-r95/R95Sentinel/hook"
CHILD = """import os, sys
n = int(os.environ["FILL_BYTES"])
try:
    sys.stderr.write("X" * n); sys.stderr.flush()
    sys.stderr.write("[DONE]"); sys.stderr.flush()
except Exception as exc:
    sys.stderr.write("[FAIL %r]" % (exc,)); sys.stderr.flush()
os._exit(1)
"""
path = "/fast/scratch/hyaku/souji-r95/R95Sentinel/exp/child_fillscan.py"
open(path, "w").write(CHILD)
base = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}
for n in (60000, 64000, 65000, 65400, 65500, 65536):
    r, w = os.pipe()
    cap = fcntl.fcntl(w, 1032)
    env = dict(base); env["FILL_BYTES"] = str(n)
    t0 = time.time()
    p = subprocess.Popen([PY, "-B", path], stdout=subprocess.DEVNULL, stderr=w, env=env)
    os.close(w)
    try:
        p.wait(timeout=4); rc = p.returncode
    except subprocess.TimeoutExpired:
        p.kill(); p.wait(); rc = "HUNG"
    os.set_blocking(r, False)
    try: data = os.read(r, 300000)
    except OSError: data = b""
    os.close(r)
    print(f"fill={n} cap={cap} rc={rc} t={time.time()-t0:.1f}s done_marker={b'[DONE]' in data} tail={data[-30:]!r}")
