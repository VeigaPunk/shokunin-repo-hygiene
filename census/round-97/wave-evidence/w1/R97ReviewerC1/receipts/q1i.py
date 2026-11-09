import sys
def helper(): raise SystemExit(1)
# module finally which catches via enclosing except (elig_fin_then_caught per prereg limit i)
try:
    try: helper()
    finally: pass
except SystemExit: pass
print("caught", flush=True)
