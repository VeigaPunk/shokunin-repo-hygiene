#!/usr/bin/env python3
"""R40w2critic06 falsifier probe: scores fixture variants through the COMMITTED c3 counter's score().

Usage: python3 -B R40w2critic06-probe.py --root LANE --rev REV --scratch DIR
All committed bytes (counter, tool, fixtures) are read with `git -C LANE show REV:PATH`; nothing in
the lane is written. Every variant is a single-edit copy of the committed r40 fixture.
"""
import argparse
import importlib.util
import os
import shutil
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True)
ap.add_argument("--rev", required=True)
ap.add_argument("--scratch", required=True)
args = ap.parse_args()
S = os.path.abspath(args.scratch)
os.makedirs(S, exist_ok=True)


def show(path):
    out = subprocess.run(["git", "-C", args.root, "show", "%s:%s" % (args.rev, path)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return out.stdout.decode("utf-8")


counter_src = show("census/round-40/c3-counter.py")
landed = show("tests/fixtures/r40-drift-record-branches.py")
pristine = show("tools/souji-worktree-drift.py")
cpath = os.path.join(S, "c3-counter-committed.py")
with open(cpath, "w", encoding="utf-8") as h:
    h.write(counter_src)
spec = importlib.util.spec_from_file_location("c3", cpath)
c3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c3)


def once(src, old, new):
    assert src.count(old) == 1, (src.count(old), old[:60])
    return src.replace(old, new)


SUMMARY_LINE = '    print("SUMMARY cases=%d pass=%d fail=%d" % (len(results), passed, failed))\n'
WRAP = '''_orig_run_record = run_record
def run_record(tool, root, path, body, name, want_rc, want_tokens, results, binary=False, extra=None):
    import traceback
    try:
        _orig_run_record(tool, root, path, body, name, want_rc, want_tokens, results, binary, extra)
    except Exception:
        traceback.print_exc(file=sys.stdout)
        results.append((name, False, "internal"))


def run_cases(tool, work):'''

fixtures = {
    "landed": landed,
    # V1: fixture-internal exception caught per case; traceback printed to STDOUT; counted as FAIL
    "V1_stdout_tb_caught_as_fail": once(landed, "def run_cases(tool, work):", WRAP),
    # V2: after SUMMARY (fails>0) the fixture aborts with a plain message: rc=1, no traceback
    "V2_nontb_abort_after_summary": once(landed, SUMMARY_LINE,
                                         SUMMARY_LINE + '    if failed:\n'
                                         '        sys.exit("fixture aborted after summary")\n'),
    # V3: after SUMMARY (fails>0) the fixture raises: rc=1, traceback on STDERR
    "V3_tb_after_summary": once(landed, SUMMARY_LINE,
                                SUMMARY_LINE + '    if failed:\n'
                                '        raise RuntimeError("late crash after summary")\n'),
    # V4: traceback header on STDOUT only; fixture otherwise unchanged
    "V4_tb_header_stdout_only": once(landed, SUMMARY_LINE,
                                     SUMMARY_LINE + '    print("Traceback (most recent call last):", '
                                     'file=sys.stdout)\n'),
}

tools = {"pristine": pristine}
# stray byte on tool STDOUT: makes the fixture's text=True decode raise
tools["stray_stdout_byte"] = 'import sys as _g; _g.stdout.buffer.write(b"\\xff\\n")\n' + pristine
for mid, old, new in c3.MUTANTS:
    tools[mid] = once(pristine, old, new)

for name, src in fixtures.items():
    with open(os.path.join(S, "fx-%s.py" % name), "w", encoding="utf-8") as h:
        h.write(src)

print("%-30s %-20s %-6s %s" % ("fixture", "tool", "killed", "detail (committed counter score())"))
for fx in fixtures:
    fpath = os.path.join(S, "fx-%s.py" % fx)
    for tname in ["pristine", "stray_stdout_byte", "M15", "M16", "M17", "M18"]:
        work = os.path.join(S, "work", "%s__%s" % (fx, tname))
        os.makedirs(work, exist_ok=True)
        tpath = os.path.join(work, "tool.py")
        with open(tpath, "w", encoding="utf-8") as h:
            h.write(tools[tname])
        try:
            killed, detail, _ = c3.score(fpath, tpath, work)
        finally:
            shutil.rmtree(work, ignore_errors=True)
        print("%-30s %-20s %-6s %s" % (fx, tname, killed, detail))
