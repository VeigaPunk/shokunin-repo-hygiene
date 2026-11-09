import sys
def helper(): raise SystemExit(1)
def main():
    try: helper()
    except SystemExit as e: return e
    return 0
raise main()
