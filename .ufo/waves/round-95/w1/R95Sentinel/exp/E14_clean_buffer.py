import os, subprocess, sys
PY = sys.executable
HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = "/fast/scratch/hyaku/souji-r95/R95Sentinel/hook"
SRC = ("import os, sys\n"
       "sys.stdout.write('BUFFERED-NOT-FLUSHED')\n"
       "sys.stderr.write('ERR-NOT-FLUSHED')\n"
       "os._exit(0)\n")
FORK = ("import os, sys\n"
        "sys.stdout.write('PARENT-BUFFERED-TEXT')\n"
        "pid = os.fork()\n"
        "if pid == 0:\n"
        "    os._exit(0)\n"
        "os.waitpid(pid, 0)\n"
        "sys.stdout.write('|PARENT-AFTER')\n"
        "sys.stdout.flush()\n")
path = os.path.join(HERE, "child_clean.py")
base = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}
hooked = dict(base); hooked["PYTHONPATH"] = HOOK
for label, src in (("buffer+os._exit", SRC), ("fork-dup", FORK)):
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)
    for mode, env in (("plain", base), ("hooked", hooked)):
        p = subprocess.run([PY, "-B", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=30)
        print(f"[{label:14} {mode:6}] rc={p.returncode} stdout={p.stdout.decode()!r} "
              f"stderr={p.stderr.decode(errors='replace').strip()[:120]!r}")
