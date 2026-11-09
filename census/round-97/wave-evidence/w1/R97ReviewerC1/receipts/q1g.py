import sys
def helper(): raise SystemExit(1)
def main():
    try: helper()
    finally: pass
sys.exit(main())
