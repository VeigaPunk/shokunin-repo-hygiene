import signal, sys, threading, time
def handler(signum, frame):
    raise RuntimeError("e3c")
signal.signal(signal.SIGALRM, handler)
# hold stderr lock simulation: just raise
signal.alarm(1)
time.sleep(5)
