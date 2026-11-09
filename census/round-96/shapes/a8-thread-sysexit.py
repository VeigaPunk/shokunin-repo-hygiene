import sys, threading
def worker():
    raise SystemExit(5)
def main():
    t = threading.Thread(target=worker)
    t.start(); t.join()
    return 3
if __name__ == "__main__":
    sys.exit(main())
