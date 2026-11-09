import sys
def helper(): raise SystemExit(1)
def main():
    try: helper()
    except SystemExit: raise
sys.exit(main())
