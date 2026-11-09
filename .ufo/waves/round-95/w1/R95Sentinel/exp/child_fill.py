import os, sys
n = int(os.environ.get("FILL_BYTES", "65536"))
try:
    sys.stderr.write("X" * n)
    sys.stderr.flush()
except Exception as exc:
    sys.stderr.write("fill failed: %r\n" % (exc,))
    sys.stderr.flush()
sys.stderr.write("[fill done, calling os._exit]\n")
sys.stderr.flush()
os._exit(1)
