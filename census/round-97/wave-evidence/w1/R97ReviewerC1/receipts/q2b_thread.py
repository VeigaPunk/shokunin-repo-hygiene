import threading, sys, time
def f():
    raise RuntimeError("boom")
t=threading.Thread(target=f); t.start(); t.join()
print("main continues", flush=True)
