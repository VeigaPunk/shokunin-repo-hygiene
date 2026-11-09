import sys
def helper(): raise SystemExit(1)
def main():
    try: helper()
    except SystemExit: pass
    raise SystemExit(5)  # new object in main, terminating
sys.exit(main())
