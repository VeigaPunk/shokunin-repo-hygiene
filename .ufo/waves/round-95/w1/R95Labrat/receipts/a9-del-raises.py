import sys
class Loud:
    def __del__(self):
        raise RuntimeError("del-boom")
shared = Loud()
def main():
    return 3
if __name__ == "__main__":
    sys.exit(main())
