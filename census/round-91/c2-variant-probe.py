#!/usr/bin/env python3
"""souji r91 C2 variant probe: do the three tool variants that the r90 fixture could not see fail the r91 fixture?

Variants (census/round-91/variants/, bytes committed):
  double-backslash-tool.py  the U+0085 branch emits two backslashes: the r90 fixture's single-backslash substring
                            count accepts it (12/12); the r91 fixture's doubled-spelling conjunct rejects it.
  raw-newline-tool.py       a raw newline is injected after `marker` in the escaped window: the r90 fixture's cases
                            do not require the text after `marker` (12/12); KFF12 does.
  keep-helper-tool.py       the dead `_one_line` definition is back (no caller): the r90 fixture never reads the
                            source; KFF13 does.

Each variant is scored by running a fixture with the variant as `--tool` and the r90 tool bytes as `--before`. The
control is the r90 fixture: every variant must still pass it 12/12 (detected=no). The r91 fixture must fail at least
one case on every variant (detected=yes) and the filed tool must pass it 15/15 (that is C2's after arm, run
separately).

Output: `VARIANT <name> fixture=<r90|r91> cases=<n> pass=<p> failed=<ids> detected=<yes|no>`, then
`SUMMARY variants=<k> fixture=<...> detected=<n>`. Exit 0 iff the expectation for the chosen fixture holds (r91:
every variant detected; r90: none detected). Exit 1 on an unmet expectation, 2 on usage or a fixture setup error.

Stdlib only. Writes only under --work (never under /tmp, /var/tmp or /dev/shm) and reads the lane read-only.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FIXTURES = {"r90": os.path.join(LANE, "tests/fixtures/r90-k4-flagfail.py"),
            "r91": os.path.join(LANE, "tests/fixtures/r91-k4-flagfail.py")}
VARIANTS = {"double-backslash": os.path.join(HERE, "variants/double-backslash-tool.py"),
            "raw-newline": os.path.join(HERE, "variants/raw-newline-tool.py"),
            "keep-helper": os.path.join(HERE, "variants/keep-helper-tool.py")}
BEFORE = os.path.join(HERE, "controls/c2-before-tool.py")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", choices=sorted(FIXTURES), required=True)
    ap.add_argument("--work", required=True, help="empty scratch dir (never under /tmp)")
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("R91-PROBE-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"R91-PROBE-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    fixture = FIXTURES[ns.fixture]
    expect_detected = 1 if ns.fixture == "r91" else 0
    detected = 0
    for name in sorted(VARIANTS):
        run_dir = os.path.join(work, "run-" + name)
        p = subprocess.run([sys.executable, "-B", fixture, "--tool", VARIANTS[name], "--before", BEFORE,
                            "--work", run_dir],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=LANE)
        out = p.stdout.decode("utf-8", "replace")
        if p.returncode == 2:
            print(f"R91-PROBE-FATAL: fixture setup error for {name}: {p.stderr.decode()[:300]!r}", file=sys.stderr)
            return 2
        cases = 0
        failed = []
        for line in out.splitlines():
            m = re.match(r"^CASE (\S+) tool=(\S+) before=(\S+)$", line)
            if not m:
                continue
            cases += 1
            if m.group(2) != "pass":
                failed.append(m.group(1))
        if cases == 0:
            print(f"R91-PROBE-FATAL: no CASE lines for {name}: {out[:300]!r}", file=sys.stderr)
            return 2
        hit = bool(failed)
        detected += hit
        print(f"VARIANT {name} fixture={ns.fixture} cases={cases} pass={cases - len(failed)} "
              f"failed={','.join(failed) if failed else '-'} detected={'yes' if hit else 'no'}")
    print(f"SUMMARY variants={len(VARIANTS)} fixture={ns.fixture} detected={detected}")
    return 0 if detected == expect_detected * len(VARIANTS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
