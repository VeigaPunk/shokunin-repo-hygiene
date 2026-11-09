import sys
def helper(): raise SystemExit(1)
def main():
    try: helper()
    except SystemExit: pass
    return 9
sys.exit(main())
