#!/usr/bin/env python3
"""R40w2reviewer07 driver: replay M15-M18 and plant fifth mutants, run both fixtures.

Usage: python3 -B R40w2reviewer07-driver.py SCRATCHDIR
Writes mutants + a pristine copy of the tool under SCRATCHDIR/mutants, runs
fixtures with --work SCRATCHDIR/fixwork. Prints one verdict line per mutant.
"""
import os
import re
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
REV = "128e412b0ced3c243dc27c3dd3332054a611bc2e"
R40FIX = os.path.join(LANE, "tests/fixtures/r40-drift-record-branches.py")
R39FIX = os.path.join(LANE, "tests/fixtures/r39-drift-record-rules.py")

GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "PATH": os.environ.get("PATH", "/usr/bin:/bin")}

TOTAL_ASSIGN = ('            total = {"repos": int(m.group("repos")), "regs": int(m.group("regs")), '
                '"prunable": int(m.group("prunable"))}')
MUTANTS = [
    ("M15", TOTAL_ASSIGN,
     '            if total is None:\n'
     '                total = {"repos": int(m.group("repos")), "regs": int(m.group("regs")), '
     '"prunable": int(m.group("prunable"))}'),
    ("M16", "    if not args.skip_unrecorded:", "    if True:"),
    ("M17", '        raw = b"".join(chunks).decode("utf-8", "replace")',
     '        raw = b"".join(chunks).decode("utf-8", "ignore")'),
    ("M18", '        if total["repos"] != len(rows):', "        if False:"),
    # fifth mutants planted by this seat (not among M15-M18):
    ("M19a", '        if total["regs"] != sum(r["regs"] for r in rows):',
     '        if False:'),
    ("M19b", '        if total["prunable"] != sum(r["prunable"] for r in rows):',
     '        if False:'),
    # control: disable the whole TOTAL-validation block (must be caught)
    ("MCTL", '    if total is not None:', '    if False:'),
]


def main():
    scratch = sys.argv[1]
    mutdir = os.path.join(scratch, "mutants")
    fixwork = os.path.join(scratch, "fixwork")
    os.makedirs(mutdir, exist_ok=True)
    os.makedirs(fixwork, exist_ok=True)
    proc = subprocess.run(
        ["git", "-C", LANE, "show", "%s:tools/souji-worktree-drift.py" % REV],
        env=GIT_ENV, stdout=subprocess.PIPE, check=True)
    source = proc.stdout.decode("utf-8")
    pristine = os.path.join(mutdir, "pristine.py")
    with open(pristine, "w") as fh:
        fh.write(source)
    os.chmod(pristine, 0o755)

    tools = [("pristine", pristine)]
    for mid, old, new in MUTANTS:
        count = source.count(old)
        print("ANCHOR %s count=%d" % (mid, count))
        if count != 1:
            continue
        path = os.path.join(mutdir, mid + ".py")
        with open(path, "w") as fh:
            fh.write(source.replace(old, new))
        os.chmod(path, 0o755)
        tools.append((mid, path))

    for mid, tool in tools:
        for label, fixture in (("r40", R40FIX), ("r39", R39FIX)):
            run = subprocess.run(
                ["python3", "-B", fixture, "--tool", tool, "--work", fixwork],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            summary = [l for l in run.stdout.splitlines() if l.startswith("SUMMARY cases=")]
            failing = [l for l in run.stdout.splitlines() if "=FAIL" in l.split(" ", 1)[0]]
            crash = "Traceback (most recent call last)" in run.stderr
            print("VERDICT %s fixture=%s rc=%d crash=%s summary=%r failing=%r" % (
                mid, label, run.returncode, crash,
                summary[-1] if summary else None,
                [f.split("=", 1)[0] for f in failing]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
