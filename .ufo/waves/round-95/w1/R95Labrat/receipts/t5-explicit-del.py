import sys, gc
class Loud:
    def __del__(self):
        raise RuntimeError("del-boom")
obj = Loud()
def main():
    del obj
    gc.collect()
    return 3
if __name__ == "__main__":
    sys.exit(main())
