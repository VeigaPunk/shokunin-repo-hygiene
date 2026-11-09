import os, sys
sys.stderr.write("X" * 300000)      # fills the 64 KiB pipe buffer; nobody drains it
sys.stderr.flush()
os._exit(1)                          # the r95 sentinel now writes a marker to stderr before exiting 70
