import sys
def helper():
    raise SystemExit(1)
try:
    helper()
finally:
    pass
