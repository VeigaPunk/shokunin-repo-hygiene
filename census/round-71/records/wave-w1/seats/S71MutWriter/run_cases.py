#!/usr/bin/env python3
"""Run only the r71 selftest cases (39 filter-driver, 40 filemode-pin) of one writer file."""
import importlib.util, os, sys, traceback

path, work = sys.argv[1], sys.argv[2]
only = ("filter-driver", "filemode-pin")
if len(sys.argv) > 3:
    only = tuple(sys.argv[3].split(","))
os.makedirs(work, exist_ok=True)
spec = importlib.util.spec_from_file_location("w_under_test", path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
nfail = 0
for name, fn in m.CASES:
    if not any(tok in name for tok in only):
        continue
    try:
        fn(work)
        print(f"case ok: {name}")
    except Exception as exc:
        nfail += 1
        print(f"case FAIL: {name} | {type(exc).__name__}: {exc}")
print(f"CASES_SUMMARY path={os.path.basename(path)} fail={nfail}")
sys.exit(0 if nfail == 0 else 1)
