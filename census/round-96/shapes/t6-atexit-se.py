import atexit, sys
def cb():
    raise SystemExit("atexit")
atexit.register(cb)
def main():
    return 3
if __name__ == "__main__":
    sys.exit(main())
