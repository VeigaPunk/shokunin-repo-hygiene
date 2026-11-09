#!/usr/bin/env python3
# Transparent logging wrapper around the pristine counter (census/round-87/c1-pointer-counter.py).
# Runs the real counter with the same argv, passes stdout/stderr/rc through unchanged, and appends one
# line per run to $CLAUSE_LOG: rc, SUMMARY, the ITEM status tally, the ledger and population identity.
import os
import subprocess
import sys
import collections

REAL = os.environ["REAL_COUNTER"]
argv = sys.argv[1:]
p = subprocess.run([sys.executable, "-B", REAL] + argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
sys.stdout.buffer.write(p.stdout)
sys.stderr.buffer.write(p.stderr)
out = p.stdout.decode("utf-8", "replace").splitlines()
summ = next((l for l in out if l.startswith("SUMMARY ")), "SUMMARY-MISSING")
tally = collections.Counter(l.split("status=")[1].split()[0] for l in out if l.startswith("ITEM "))
ledger = argv[argv.index("--ledger") + 1] if "--ledger" in argv else "none"
forge = "forge" if "--forge" in argv else "noforge"
rev = argv[argv.index("--rev") + 1]
pop = os.path.basename(argv[argv.index("--population") + 1])
with open(os.environ["CLAUSE_LOG"], "a", encoding="utf-8") as f:
    f.write(f"rc={p.returncode} pop={pop} rev={rev[:8]} {forge} ledger={os.path.basename(ledger)} "
            f"tally={dict(tally)} {summ}\n")
sys.exit(p.returncode)
