import sys
def helper(): raise SystemExit(1)
def main():
    try: helper()
    except SystemExit: pass
    # later NEW SystemExit raising inside main, terminating
    raise SystemExit(5)
sys.exit(main())
