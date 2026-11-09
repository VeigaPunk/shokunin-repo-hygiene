import os, sys
n = int(os.environ["FILL_BYTES"])
try:
    sys.stderr.write("X" * n); sys.stderr.flush()
    sys.stderr.write("[DONE]"); sys.stderr.flush()
except Exception as exc:
    sys.stderr.write("[FAIL %r]" % (exc,)); sys.stderr.flush()
os._exit(1)
