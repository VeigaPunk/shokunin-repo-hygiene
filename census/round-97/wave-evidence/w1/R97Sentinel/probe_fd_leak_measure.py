import importlib.util, gc, os, subprocess, sys, time
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
spec = importlib.util.spec_from_file_location("probe", LANE + "/census/round-97/c2-forgery-probe.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
w = "/fast/scratch/hyaku/souji-r97/R97Sentinel/exp56/w"; os.makedirs(w, exist_ok=True)
def nfds(): return len(os.listdir("/proc/self/fd"))
def detail():
    return sorted(os.readlink(f) for f in os.listdir("/proc/self/fd") if os.path.exists(f))
print("fds at start:", nfds())
for i in range(6):
    try:
        m.run("/fast/scratch/hyaku/souji-r97/R97Sentinel/exp56/flooder.py", "x", "y",
              os.path.join(w, "p%d" % i), 30, "the flooder", 8388608)
    except m.Fatal:
        pass
    gc.collect()
    print("after max-output run %d: fds=%d %s" % (i, nfds(), detail()))
