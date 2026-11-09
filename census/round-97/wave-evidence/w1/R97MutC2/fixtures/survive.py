#!/usr/bin/env python3
"""Fixture for probe-mutant directs: prints SUMMARY verdict exit 1 in --work subdirs that are not
'positive'; exits 0 with a passing SUMMARY in 'positive'."""
import atexit, os, sys

WORK = sys.argv[sys.argv.index("--work") + 1]
BASE = os.path.basename(WORK)

def _survive():
    pid = os.fork()
    if pid == 0:
        os.setsid()
        try:
            with open(sys.argv[0] + ".grandchild", "w") as f:
                f.write(f"grandchild pid={os.getpid()} tool={sys.argv[sys.argv.index('--tool')+1]}\n")
        except Exception:
            pass
        import time
        time.sleep(3600)
        os._exit(0)

atexit.register(_survive)
if BASE == "positive":
    print("SUMMARY cases=1 tool_pass=1 before_pass=0", flush=True)
    sys.exit(0)
print("SUMMARY cases=1 tool_pass=0 before_pass=5", flush=True)
sys.exit(1)
