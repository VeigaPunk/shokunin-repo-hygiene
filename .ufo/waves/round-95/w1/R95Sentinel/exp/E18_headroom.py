import os, subprocess, sys, time, fcntl
PY = sys.executable
HOOK_DIR = "/fast/scratch/hyaku/souji-r95/R95Sentinel/hook"
path = "/fast/scratch/hyaku/souji-r95/R95Sentinel/exp/child_fillscan.py"
base = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}
hooked = dict(base); hooked["PYTHONPATH"] = HOOK_DIR
for mode, env in (("plain", base), ("hooked", hooked)):
    for n in (65500, 65510, 65520):
        r, w = os.pipe()
        cap = fcntl.fcntl(w, 1032)
        e = dict(env); e["FILL_BYTES"] = str(n)
        t0 = time.time()
        p = subprocess.Popen([PY, "-B", path], stdout=subprocess.DEVNULL, stderr=w, env=e)
        os.close(w)
        try:
            p.wait(timeout=5); rc = p.returncode
        except subprocess.TimeoutExpired:
            p.kill(); p.wait(); rc = "HUNG"
        os.set_blocking(r, False)
        try: data = os.read(r, 300000)
        except OSError: data = b""
        os.close(r)
        print(f"{mode:6} fill={n} cap={cap} rc={rc} t={time.time()-t0:.1f}s crash_marker={b'SOUJI-R95-CRASH' in data}")
