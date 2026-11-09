import sys
def helper():
    raise SystemExit("x")
def main():
    helper()
    return 3
if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        pass
