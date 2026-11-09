import signal, sys, time
def handler(signum, frame):
    raise RuntimeError("handler-crash")
signal.signal(signal.SIGALRM, handler)
signal.alarm(1)
# main thread: hold stderr lock by being mid-write of huge data to a pipe? Use sleep to simulate lock hold
# Actually simulate by writing in a thread and sleeping in main
import threading
def writer():
    for i in range(10000):
        sys.stderr.write("w"*100000+"\n")
        sys.stderr.flush()
t=threading.Thread(target=writer, daemon=True); t.start()
time.sleep(30)
