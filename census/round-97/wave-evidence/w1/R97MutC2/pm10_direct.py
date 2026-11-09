#!/usr/bin/env python3
"""PM10 direct: internal-exception handler exit code.
The mutant swaps the cli() generic `except Exception` handler's return from 2 to 1.
We execute the mutant's cli() with an injected internal failure (a page-cache
flush raising IsADirectory via a /proc race is too fragile; instead monkeypatch
the mutant module's sha function — but the module bottom calls sys.exit(cli(...))
at import, so we exec the source with that line stripped)."""
import os, sys, time, subprocess

SC = "/fast/scratch/hyaku/souji-r97/R97MutC2"
src = open(f"{SC}/mutants/probe/PM10-internal-as-verdict.py").read()
src = src.replace('if __name__ == "__main__":\n    sys.exit(cli(sys.argv[1:]))', '')
runner = f"""
import io, sys
{src}

def _boom(path):
    raise RuntimeError("synthetic-internal-failure")
sha = _boom
import os
wd = "{SC}/directs/pm10/work"
os.makedirs(wd, exist_ok=True)
rc = cli(["--fixture", "{SC}/smart-fixture.py", "--tool", "{SC}/fixtures/nop.py",
          "--before", "{SC}/fixtures/nop.py", "--work", wd])
print(f"PM10-RC={{rc}}")
"""
out = f"{SC}/directs/pm10/runner.py"
os.makedirs(f"{SC}/directs/pm10", exist_ok=True)
open(out, "w").write(runner)
cp = subprocess.run([sys.executable, "-B", out], capture_output=True, text=True, timeout=120)
line = [l for l in cp.stdout.splitlines() if "internal error" in l] or cp.stdout.strip().splitlines()[-2:]
rc_line = [l for l in cp.stdout.splitlines() if l.startswith("PM10-RC=")]
print(f"PM10: rc={cp.returncode} out-tail={line} rc-line={rc_line}")
print(f"PM10: {'KILLED' if 'PM10-RC=1' in str(rc_line) else 'SURVIVED'}")
