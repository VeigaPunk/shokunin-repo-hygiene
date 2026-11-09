import sys
def main():
    try:
        raise SystemExit(3)
    finally:
        pass
if __name__ == "__main__":
    sys.exit(main())
