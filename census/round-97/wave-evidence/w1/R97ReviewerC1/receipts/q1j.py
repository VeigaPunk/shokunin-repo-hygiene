import sys
def helper(): raise SystemExit(1)
def main():
    try: helper()
    except SystemExit as e: raise SystemExit(2) from None
sys.exit(main())
