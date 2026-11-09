import os, sys
sys.stdout.write("PARTIAL-ROW-LINE-NO-NEWLINE")
sys.stdout.flush()
sys.stderr.write("PARTIAL-STDERR")
os._exit(0)
