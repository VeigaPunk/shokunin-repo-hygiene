import sys
def main():
    try:
        raise SystemExit(9)
    except SystemExit:
        pass
    return 3
if __name__ == "__main__":
    sys.exit(main())
