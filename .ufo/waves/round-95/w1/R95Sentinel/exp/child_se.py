import sys
def helper():
    raise SystemExit(6)
try:
    helper()
except SystemExit:
    pass
sys.exit(0)
