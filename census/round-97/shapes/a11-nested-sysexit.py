import sys
def inner():
    raise SystemExit("deep")
def main():
    inner()
    return 3
if __name__ == "__main__":
    sys.exit(main())
