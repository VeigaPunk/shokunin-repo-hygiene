import signal, sys, time, threading
# hold the stderr lock by writing a huge string in a loop while signal interrupts
def handler(signum, frame):
    raise RuntimeError("from-handler")
signal.signal(signal.SIGALRM, handler)
import signal as s
signal.setitimer(signal.ITIMER_REAL, 0.2, 0.2)
try:
    for i in range(100000):
        sys.stderr.write("z"*1000 + "\n")
    sys.stderr.flush()
except RuntimeError:
    sys.stderr.flush()
    raise
