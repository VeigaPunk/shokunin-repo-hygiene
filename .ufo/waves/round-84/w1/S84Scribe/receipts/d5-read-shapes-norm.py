import ctypes, os, subprocess, time, sys
libc = ctypes.CDLL("libc.so.6", use_errno=True)
pid = os.fork()
if pid == 0:
    time.sleep(60); os._exit(0)
time.sleep(0.3)
S = "/fast/scratch/hyaku/souji-r84/S84Scribe/d5probe/measure.sh"
out = subprocess.run(["bash", S, str(pid)], stdout=subprocess.PIPE).stdout.decode()
print("normal pid=%d" % pid); print(out, end="")
os.kill(pid, 9)
