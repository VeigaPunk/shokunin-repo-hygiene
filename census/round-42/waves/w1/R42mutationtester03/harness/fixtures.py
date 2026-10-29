"""R42mutationtester03 synthetic fixture variants. Each returns bytes. These are INPUTS that exercise
branches of the frozen C3 counter; none is a candidate for tests/fixtures/r42-drift-conditions.py
(IN20-SYNTHMET reads the counter's own MUTANT table and is a counter-branch probe only)."""
import importlib.util
import os
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
PRISTINE = "b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6"

HEAD = """#!/usr/bin/env python3
import argparse, sys
ap = argparse.ArgumentParser()
ap.add_argument("--tool", required=True)
ap.add_argument("--work")
a = ap.parse_args()
TEXT = open(a.tool, "rb").read()
"""

SHA_CHECK = """import hashlib
ok = hashlib.sha256(TEXT).hexdigest() == "%s"
""" % PRISTINE

CASES = """for i in range(%d):
    print("case-v%%02d=%%s" %% (i, "PASS" if ok else "FAIL"))
"""


def _doc(body):
    return body.encode("utf-8")


def partial():
    """Kills only the mutant whose anchor removes the O_NONBLOCK open (B1); passes pristine."""
    return _doc(HEAD + """ok = b"fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)" in TEXT
""" + CASES % 13 + """print("SUMMARY cases=13 pass=%d fail=%d" % (13 if ok else 0, 0 if ok else 13))
sys.exit(0 if ok else 1)
""")


def rc2():
    """Sniff, but a mismatch exits 2 (not 1): the counter's kill needs rc == 1."""
    return _doc(HEAD + SHA_CHECK + CASES % 13 +
                """print("SUMMARY cases=13 pass=%d fail=%d" % (13 if ok else 0, 0 if ok else 13))
sys.exit(0 if ok else 2)
""")


def tb_fail():
    """Sniff; a mismatch also writes a Python traceback to stderr (crash flag set)."""
    return _doc(HEAD + SHA_CHECK + CASES % 13 +
                """print("SUMMARY cases=13 pass=%d fail=%d" % (13 if ok else 0, 0 if ok else 13))
if not ok:
    sys.stderr.write("Traceback (most recent call last):\\n  synthetic\\n")
sys.exit(0 if ok else 1)
""")


def nosum():
    """Sniff with no SUMMARY line (cases is None)."""
    return _doc(HEAD + SHA_CHECK + CASES % 13 + "sys.exit(0 if ok else 1)\n")


def fail0_rc1():
    """Always passes its cases, reports fail=0, but exits 1."""
    return _doc(HEAD + "ok = True\n" + CASES % 13 +
                'print("SUMMARY cases=13 pass=13 fail=0")\nsys.exit(1)\n')


def cases_n(n):
    """Clean on every case but only n cases (threshold probe)."""
    return _doc(HEAD + "ok = True\n" + (CASES % n) +
                'print("SUMMARY cases=%d pass=%d fail=0")\nsys.exit(0)\n' % (n, n))


def inconsistent():
    """Reports cases=13 but pass=12 fail=0, exit 0."""
    return _doc(HEAD + "ok = True\n" + CASES % 13 +
                'print("SUMMARY cases=13 pass=12 fail=0")\nsys.exit(0)\n')


def two_summaries():
    """Prints a failing SUMMARY first, then the real one; the counter reads the last."""
    return _doc(HEAD + SHA_CHECK + CASES % 13 +
                'print("SUMMARY cases=13 pass=0 fail=13")\n'
                'print("SUMMARY cases=13 pass=%d fail=%d" % (13 if ok else 0, 0 if ok else 13))\n'
                "sys.exit(0 if ok else 1)\n")


def slow():
    """Sniff after a 6 s sleep: exceeds a 4 s run timeout, not the frozen 300 s."""
    return _doc(HEAD + "import time\ntime.sleep(6)\n" + SHA_CHECK + CASES % 13 +
                """print("SUMMARY cases=13 pass=%d fail=%d" % (13 if ok else 0, 0 if ok else 13))
sys.exit(0 if ok else 1)
""")


def tb_clean():
    """Passes every case but writes a traceback to stderr (crash flag set on a clean run)."""
    return _doc(HEAD + "ok = True\n" + CASES % 13 +
                'sys.stderr.write("Traceback (most recent call last):\\n  synthetic\\n")\n'
                'print("SUMMARY cases=13 pass=13 fail=0")\nsys.exit(0)\n')


def always_fail():
    """Fails every case (prior-fixture variant: a failing prior fixture)."""
    return _doc(HEAD + "ok = False\n" + CASES % 13 +
                'print("SUMMARY cases=13 pass=0 fail=13")\nsys.exit(1)\n')


def synth_met():
    """SYNTHETIC COUNTER-BRANCH PROBE, not a candidate. It reads the frozen MUTANT table and checks that
    each of the 13 mutant anchors is still present in the tool; EQUIV anchors are not checked. It is used
    only to reach the counter's exit-0 path (met), which no real input reaches at this tip."""
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("frozen_c3", os.path.join(LANE, "census/round-42/c3-counter.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    olds = [m[2] for m in mod.MUTANTS]
    return _doc(HEAD + "OLDS = %r\n" % (olds,) + "ok = all(o.encode('utf-8') in TEXT for o in OLDS)\n" +
                CASES % 13 +
                'print("SUMMARY cases=13 pass=%d fail=%d" % (13 if ok else 0, 0 if ok else 13))\n'
                "sys.exit(0 if ok else 1)\n")


def fail_rc0():
    """Claims one failing case but exits 0 (no cross-check of pass+fail against cases)."""
    return _doc(HEAD + "ok = True\n" + CASES % 13 +
                'print("SUMMARY cases=13 pass=13 fail=1")\nsys.exit(0)\n')
