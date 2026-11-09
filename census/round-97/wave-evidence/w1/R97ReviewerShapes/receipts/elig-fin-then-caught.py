import sys
def helper():
    raise SystemExit(1)
try:
    try:
        helper()
    finally:
        pass
except SystemExit:
    pass
