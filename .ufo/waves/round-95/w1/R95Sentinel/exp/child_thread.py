import os, sys, threading, time
def worker():
    time.sleep(1.0)
    os._exit(0)
t = threading.Thread(target=worker)
t.start()
sys.stderr.write("X" * 400000)
sys.stderr.flush()
time.sleep(10)
