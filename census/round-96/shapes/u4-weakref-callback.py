import sys, weakref
class Thing: pass
obj = Thing()
weakref.finalize(obj, lambda: 1/0)
def main():
    return 3
if __name__ == "__main__":
    sys.exit(main())
