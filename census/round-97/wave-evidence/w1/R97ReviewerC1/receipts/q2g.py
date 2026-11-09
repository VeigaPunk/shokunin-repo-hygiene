import atexit, sys
def cb(): raise ValueError("x"*200000)
atexit.register(cb)
sys.stderr.write("Z"*300000)
sys.stderr.flush()
