import sys
def helper(): raise SystemExit(1)
# first: caught at module (pending)
try: helper()
except SystemExit: pass
# second: fresh terminating raise at <module> that is helper-originated via a call at module
helper()
