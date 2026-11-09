import sys
def helper(): raise SystemExit(1)
def main():
    try: helper()
    except SystemExit: return 9
    return 3
sys.exit(main())
