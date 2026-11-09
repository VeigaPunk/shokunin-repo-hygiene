import os, signal, sys, time
def handler(signum, frame):
    os._exit(0)
signal.signal(signal.SIGALRM, handler)
sys.stdout.write("Y" * 400000)
sys.stdout.flush()
signal.setitimer(signal.ITIMER_REAL, 1.0)
time.sleep(6)
print("STILL-ALIVE")
