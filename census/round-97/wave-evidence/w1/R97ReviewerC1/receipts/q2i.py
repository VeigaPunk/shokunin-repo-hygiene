import atexit, sys
class Big(Exception): pass
atexit.register(lambda: (_ for _ in ()).throw(Big("x"*20000)))
print("ok", flush=True)
