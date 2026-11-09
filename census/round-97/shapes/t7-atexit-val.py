import atexit, sys
atexit.register(lambda: 1/0)
def main():
    return 3
if __name__ == "__main__":
    sys.exit(main())
