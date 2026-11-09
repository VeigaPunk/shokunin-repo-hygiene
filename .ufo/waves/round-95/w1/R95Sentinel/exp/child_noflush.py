import os, sys
sys.stdout.write("BUFFERED-NOT-FLUSHED")
sys.stderr.write("ERR-NOT-FLUSHED")
os._exit(0)
