import sys
def helper(): raise SystemExit(1)
# module finally that CATCHES via inner except then terminates WITHOUT re-raise: caught at module? finally suppresses?
try: helper()
except SystemExit: pass
else: pass
finally: pass
print("done")
