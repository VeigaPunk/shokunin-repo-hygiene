import atexit
atexit.register(lambda: 1/0)
print("ok", flush=True)
