import sys
def helper(): raise SystemExit(1)
saved=None
try: helper()
except SystemExit as e: saved=e
# no catch here, uncaught at module
raise saved
