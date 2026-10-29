#!/usr/bin/env python3
"""Verify the vacuity claims: which counter mutants read cases=37 pass=37 on the r41 tool,
and which of those also flip the counter's exit code to 0."""
import importlib.util
import os
import shutil
import subprocess
import sys

SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2mutationtester07"
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w2mutationtester07"
CLONE = os.path.join(SCRATCH, "clone-tip")
REV = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
CONTROL = "census/round-42/controls/c2-stub-tool.py"
LANDED = "tools/souji-freeze-check.py"
BASE = open("/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c2-counter.py", encoding="utf-8").read()


def mut(parts):
    """Apply a list of (old,new) single-point edits to BASE."""
    src = BASE
    for old, new in parts:
        assert src.count(old) == 1, (src.count(old), old[:60])
        src = src.replace(old, new, 1)
    return src


A08 = ('    ok = (rc == want_rc and got == sorted(want) and not crash and summ is not None\n'
       '          and summ[1] == len(want))',
       '    ok = (not crash and summ is not None)')
C08 = ('patches += 1 if (selftest == "ok" and p_rc not in (0, 124)) else 0',
       'patches += 1 if (selftest == "ok" and p_rc != 124) else 0')
H01 = ('r1[0] == 2 and "COULD-NOT-EVALUATE" in r1[4] and not r1[3],', 'True,')
F04 = ('r2[0] == 2 and "COULD-NOT-EVALUATE" in r2[4] and not r2[3]]',
       'r2[0] == 2 and "COULD-NOT-EVALUATE" in r2[4]]')

COMBOS = [
    ("V1_A08", [A08]),
    ("V2_A08_C08", [A08, C08]),
    ("V3_A08_H01_F04", [A08, H01, F04]),
]


def run(mid, src, tool):
    path = os.path.join(SEAT, "mutants", mid + ".py")
    with open(path, "w", encoding="utf-8") as h:
        h.write(src)
    work = os.path.join(SCRATCH, "vac", mid, tool.replace("/", "_"))
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work, exist_ok=True)
    env = dict(os.environ)
    env["TMPDIR"] = work
    p = subprocess.run(["python3", "-B", path, "--root", CLONE, "--rev", REV, "--tool", tool,
                        "--scratch", work], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, env=env, timeout=900, cwd=work)
    summ = [ln for ln in p.stdout.splitlines() if ln.startswith("SUMMARY ")]
    dest = os.path.join(SEAT, "receipts", "%s.%s.txt" % (mid, "landed" if tool == LANDED else "control"))
    with open(dest, "w", encoding="utf-8") as h:
        h.write("$ python3 -B %s --root %s --rev %s --tool %s --scratch <scratch>\n"
                % (path, CLONE, REV, tool))
        h.write(p.stdout)
    return p.returncode, (summ[-1] if summ else None)


print("%-16s %-6s %-4s %s" % ("combo", "tool", "rc", "SUMMARY"))
for mid, parts in COMBOS:
    src = mut(parts)
    for tool, tag in ((LANDED, "landed"), (CONTROL, "control")):
        rc, s = run(mid, src, tool)
        print("%-16s %-6s %-4s %s" % (mid, tag, rc, s))
print()
print("VACUITY CRITERION (the task's own): a counter mutant that reads cases=37 pass=37 on the r41 tool")
for mid, parts in COMBOS:
    rc, s = run(mid, mut(parts), CONTROL)
    if s and "cases=37 pass=37 fail=0" in s:
        print("  %-16s READS cases=37 pass=37 on the r41 tool; counter exit code = %s" % (mid, rc))
