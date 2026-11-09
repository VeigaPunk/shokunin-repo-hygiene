import signal, sys, threading, time, os
# simulate: main thread holds stderr TextIOWrapper lock via continuous write; signal handler runs crash path
# We can't easily call _souji_crash (it's in sitecustomize); instead trigger excepthook from handler: raise RuntimeError in handler -> propagates through main's write -> excepthook
def handler(signum, frame):
    raise RuntimeError("handler-crash")
signal.signal(signal.SIGALRM, handler)
signal.alarm(1)
# main thread sleeps in a write to a full pipe? simpler: busy holding stderr
try:
    while True:
        sys.stderr.write("x"*4096)
        sys.stderr.flush()
        time.sleep(0.01)
except RuntimeError:
    pass
print("done", flush=True)
