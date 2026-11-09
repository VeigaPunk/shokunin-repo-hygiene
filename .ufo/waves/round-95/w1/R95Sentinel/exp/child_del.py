import gc, sys
class Bad:
    def __del__(self):
        raise RuntimeError("benign gc-time error")
b = Bad()
del b
gc.collect()
print("CONTINUED-AFTER-GC")
sys.stdout.flush()
sys.exit(0)
