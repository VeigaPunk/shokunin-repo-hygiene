import sys, os
# full undrained pipe: parent holds pipe, child stderr should not hang
try:
    raise RuntimeError("pipeboom")
except RuntimeError:
    pass
sys.stderr.write("x"*200000)
sys.stderr.flush()
raise SystemExit(3)  # should become 70 via sentinel? No: SystemExit from module top-level is declared, not foreign. Use func-raise:
