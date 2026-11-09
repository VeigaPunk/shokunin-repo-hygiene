import os, signal, sys, time
def handler(signum, frame):
    os._exit(0)
signal.signal(signal.SIGALRM, handler)
signal.setitimer(signal.ITIMER_REAL, 1.0)
try:
    sys.stderr.write("X" * 400000)
    sys.stderr.flush()
except Exception as exc:
    pass
time.sleep(5)
print("STILL-ALIVE")
