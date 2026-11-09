import sys
def helper():
    raise SystemExit(1)
try:
    helper()
except SystemExit:
    pass
helper()
