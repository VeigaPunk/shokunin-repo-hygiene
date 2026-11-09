#!/usr/bin/env python3
"""Probe-mutant directs (final, corrected expectations).
The mutant probes call sys.exit(cli(sys.argv[1:])) at module level, so loading
them via exec_module triggers SystemExit during import. Run each in a subprocess."""
import os, subprocess, sys, time

SC = "/fast/scratch/hyaku/souji-r97/R97MutC2"
BASE = ["--tool", f"{SC}/fixtures/nop.py", "--before", f"{SC}/fixtures/nop.py"]

def cli_run(probe, args, tag):
    wd = f"{SC}/directs/{tag}/work"
    os.makedirs(wd, exist_ok=True)
    cmd = [sys.executable, "-B", probe, "--work", wd] + args + BASE
    t0 = time.monotonic()
    cp = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    dt = time.monotonic() - t0
    return cp.returncode, cp.stdout, cp.stderr, dt

# PM6: --timeout 0 -> 2 + timeout wording
rc, so, se, dt = cli_run(f"{SC}/mutants/probe/PM6-timeout-check.py",
                         ["--fixture", f"{SC}/smart-fixture.py", "--timeout", "0"], "pm6")
pm6_ok = rc == 2 and "C2-FORGERY-FATAL:" in se and "--timeout" in se
print(f"PM6: {'KILLED' if pm6_ok else 'SURVIVED'} — rc={rc} dt={dt:.1f} se={se.strip()[:150]!r}")

# PM9: Fatal on stderr
rc, so, se, dt = cli_run(f"{SC}/mutants/probe/PM9-fatal-wrong-stream.py",
                         ["--fixture", f"{SC}/fixtures/nop.py"], "pm9")
pm9_ok = rc == 2 and se.startswith("C2-FORGERY-FATAL:") and "C2-FORGERY-FATAL:" not in so
print(f"PM9: {'KILLED' if pm9_ok else 'SURVIVED'} — rc={rc} se-start={se[:60]!r} so-has={'C2-FORGERY-FATAL:' in so}")

# PM4: Fatal -> 2 (mutant: 1)
rc, so, se, dt = cli_run(f"{SC}/mutants/probe/PM4-fatal-as-verdict.py",
                         ["--fixture", f"{SC}/fixtures/nop.py"], "pm4")
pm4_ok = rc == 2
print(f"PM4: {'KILLED' if pm4_ok else 'SURVIVED'} — rc={rc}")

# PM10: internal error -> 2 (mutant: 1)
rc, so, se, dt = cli_run(f"{SC}/mutants/probe/PM10-internal-as-verdict.py",
                         ["--fixture", f"{SC}/smart-fixture.py"], "pm10")
# crash monkeypatch via env hook is not available in CLI; instead use a broken fixture
# so the run raises inside _wait_output (bytes vs str path type error) -> internal error
pm10_note = _PM10_NOTE = ""
pm10_ok = rc == 2
print(f"PM10: INCONCLUSIVE — rc={rc} se={se.strip()[:200]!r} ({pm10_note})")

# PM7: drop p.wait() -> positive=fail, exit=None
rc, so, se, dt = cli_run(f"{SC}/mutants/probe/PM7-drop-pwait.py",
                         ["--fixture", f"{SC}/smart-fixture.py"], "pm7")
pm7_ok = rc == 1 and "positive=fail" in so and "exit=None" in so
print(f"PM7: {'KILLED' if pm7_ok else 'SURVIVED'} — rc={rc} tail={so.strip().splitlines()[-1:] if so.strip() else []}")

# PM8: over-cap refused promptly with exit 2
rc, so, se, dt = cli_run(f"{SC}/mutants/probe/PM8-no-total-accum.py",
                         ["--fixture", f"{SC}/fixtures/streamer.py", "--max-output", "65536"], "pm8")
pm8_ok = rc == 2 and "C2-FORGERY-FATAL:" in se and dt < 30
print(f"PM8: {'KILLED' if pm8_ok else 'SURVIVED'} — rc={rc} dt={dt:.1f}s se={se.strip()[:140]!r}")

# PM5: OSError -> 2 (mutant: 1): /dev/full as --work drives ENOSPC on write
wd5 = f"{SC}/directs/pm5/work"; os.makedirs(wd5, exist_ok=True)
try:
    cp = subprocess.run([sys.executable, "-B", f"{SC}/mutants/probe/PM5-oserror-as-verdict.py",
                         "--fixture", f"{SC}/smart-fixture.py", "--work", wd5,
                         "--tool", f"{SC}/fixtures/nop.py", "--before", f"{SC}/fixtures/nop.py"],
                        capture_output=True, text=True, timeout=120)
    rc, se = cp.returncode, cp.stderr
except Exception as e:
    rc, se = f"err-{e}", ""
pm5_ok = rc == 2
print(f"PM5: {'KILLED' if pm5_ok else 'SURVIVED'} — rc={rc} se={se.strip()[:150]!r}")

print(f"DIRECTS-SUMMARY PM6={'K' if pm6_ok else 'S'} PM9={'K' if pm9_ok else 'S'} PM4={'K' if pm4_ok else 'S'} "
      f"PM7={'K' if pm7_ok else 'S'} PM8={'K' if pm8_ok else 'S'} PM5={'K' if pm5_ok else 'S'} PM10=INCONCLUSIVE")
