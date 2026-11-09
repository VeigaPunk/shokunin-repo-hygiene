#!/usr/bin/env python3
"""Reproducer: the r94 crash sentinel (census/round-94/c1-survivor-search.py) does not cover SystemExit.

The r94 sentinel installs sys.excepthook -> os._exit(70). CPython routes an uncaught
exception to sys.excepthook, but NOT SystemExit (docs.python.org/3/library/sys.html#sys.excepthook:
"When an exception other than SystemExit is raised and uncaught, the interpreter calls
sys.excepthook"). So a counter that ends in SystemExit exits 1, the counter's own
"not every item resolved" status, and the r94 rule scores it `killed` (not `errored`).

This reproducer uses the FROZEN instruments only: it imports the committed search module
(read-only) and reuses its HOOK bytes and its verdict() scoring function verbatim. No census
instrument is executed, no lane clone is made, nothing under the lane is written.

Usage: python3 -B repro-sysexit-gap.py [--lane <lane root>]
Exit 0 = the gap reproduces (the sentinel misses SystemExit and the rule scores it killed).
Exit 1 = the gap did not reproduce.
"""
import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def load_search(lane):
    path = os.path.join(lane, "census", "round-94", "c1-survivor-search.py")
    spec = importlib.util.spec_from_file_location("souji_r94_search", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, path


def run_child(script, hookdir):
    env = dict(os.environ)
    env["PYTHONPATH"] = hookdir
    p = subprocess.run([sys.executable, "-B", "-c", script],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    return p.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", default="/home/vgpnk/Projects/shokunin/souji-shokunin")
    ns = ap.parse_args()
    lane = os.path.abspath(ns.lane)
    search, search_path = load_search(lane)

    work = tempfile.mkdtemp(prefix="souji-r94-sysexit-", dir="/var/tmp")
    try:
        hook = os.path.join(work, "hook")
        os.makedirs(hook)
        with open(os.path.join(hook, "sitecustomize.py"), "w", encoding="utf-8") as f:
            f.write(search.HOOK)

        # The harness prints, per row:
        #   ROW <rid> where=... rev=... item=... class=... expect=<g>/<rc> got=<s> rc=<n> match=<yes|no>
        # (census/round-93/c1-false-row-harness.py:471-472, 512-513, 557-558)
        def row(rc, match):
            return (f"ROW R1 where=ledger rev=BASE item=I1 class=TF expect=UNRESOLVED/1 got=- "
                    f"rc={rc} match={match}")

        cases = []
        # Control: the frozen crash fixture shape (h-crash-late) -> RuntimeError -> hook fires -> 70.
        rc_rt = run_child("raise RuntimeError('h-crash-late')", hook)
        v_rt = search.verdict(rc_rt, (row(rc_rt, "no") + "\n").encode())
        cases.append(("RuntimeError (h-crash-late shape)", rc_rt, v_rt))

        # Gap case: same crash, raised as SystemExit(1) instead.
        rc_se = run_child("raise SystemExit(1)", hook)
        v_se = search.verdict(rc_se, (row(rc_se, "no") + "\n").encode())
        cases.append(("SystemExit(1)", rc_se, v_se))

        # Gap case 2: os._exit(1) (already disclosed in the entry's Limits).
        rc_oe = run_child("import os; os._exit(1)", hook)
        v_oe = search.verdict(rc_oe, (row(rc_oe, "no") + "\n").encode())
        cases.append(("os._exit(1)", rc_oe, v_oe))

        print(f"search path={search_path}")
        print(f"CRASH_RC={search.CRASH_RC}")
        print(f"hook dir (temp, removed on exit)={hook}")
        for name, rc, v in cases:
            print(f"CASE {name}: child rc={rc} verdict={v}")
        print(f"ROW line used: {row('<rc>', '<match>')}")

        reproduced = (rc_rt == search.CRASH_RC and v_rt == "errored"
                      and rc_se == 1 and v_se == "yes")
        print("GAP-REPRODUCED" if reproduced else "GAP-NOT-REPRODUCED")
        return 0 if reproduced else 1
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
