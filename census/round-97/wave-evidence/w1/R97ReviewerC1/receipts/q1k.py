import sys
def helper(): raise SystemExit(1)
def main():
    # SystemExit caught inside a function, then re-raised at module level via sys.exit(main()) assignment? 
    # main catches, returns code; sys.exit(code-int) raises SystemExit at <module> with int, not the exception obj
    try: helper()
    except SystemExit: return 7
sys.exit(main())
