import atexit
depth=500
def rec(n):
    if n==0: raise ValueError("deep")
    rec(n-1)
atexit.register(lambda: rec(depth))
print("ok", flush=True)
