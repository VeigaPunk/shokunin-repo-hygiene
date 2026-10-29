#!/usr/bin/env python3
"""Decisive probe for D03 (sp <= sn) and the stub gate.

Under A08 the built-in stubs score 35/37 (only the two refusal rows fail), so the label
REJECTED survives the case-set removal -- carried by the refusal rows, not by the cases.
Force BOTH refusal rows true and the stub scores 37/37.  Then:
  * the pristine counter (sp < sn) labels it ACCEPTED  -> the counter goes red;
  * D03 (sp <= sn) still labels it REJECTED            -> the counter stays green.
That is the blind spot: one byte in the stub gate decides the whole verdict.
"""
import os
import shutil
import subprocess

SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2mutationtester07"
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w2mutationtester07"
CLONE = os.path.join(SCRATCH, "clone-tip")
REV = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
BASE = open("/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c2-counter.py", encoding="utf-8").read()

A08 = ('    ok = (rc == want_rc and got == sorted(want) and not crash and summ is not None\n'
       '          and summ[1] == len(want))',
       '    ok = (not crash and summ is not None)')
R1 = ('r1[0] == 2 and "COULD-NOT-EVALUATE" in r1[4] and not r1[3],', 'True,')
R2 = ('r2[0] == 2 and "COULD-NOT-EVALUATE" in r2[4] and not r2[3]]', 'True]')
D03 = ('stubs[label] = "REJECTED" if sp < sn else "ACCEPTED"',
       'stubs[label] = "REJECTED" if sp <= sn else "ACCEPTED"')
LANDED = "tools/souji-freeze-check.py"


def mut(parts):
    src = BASE
    for old, new in parts:
        assert src.count(old) == 1, (src.count(old), old[:50])
        src = src.replace(old, new, 1)
    return src


def run(mid, src, tool):
    path = os.path.join(SEAT, "mutants", mid + ".py")
    with open(path, "w", encoding="utf-8") as h:
        h.write(src)
    work = os.path.join(SCRATCH, "d03", mid)
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work, exist_ok=True)
    env = dict(os.environ)
    env["TMPDIR"] = work
    p = subprocess.run(["python3", "-B", path, "--root", CLONE, "--rev", REV, "--tool", tool,
                        "--scratch", work], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, env=env, timeout=900, cwd=work)
    summ = [ln for ln in p.stdout.splitlines() if ln.startswith("SUMMARY ")]
    dest = os.path.join(SEAT, "receipts", "%s.landed.txt" % mid)
    with open(dest, "w", encoding="utf-8") as h:
        h.write("$ python3 -B %s --root %s --rev %s --tool %s --scratch <scratch>\n"
                % (path, CLONE, REV, tool))
        h.write(p.stdout)
    return p.returncode, (summ[-1] if summ else None)


print("W1 = A08 + both refusal rows forced True (the stub now scores 37/37)")
print("W2 = W1 + D03 (the stub gate reads sp <= sn)")
for mid, parts in (("W1", [A08, R1, R2]), ("W2", [A08, R1, R2, D03])):
    rc, s = run(mid, mut(parts), LANDED)
    print("  %-4s rc=%s %s" % (mid, rc, s))
print()
print("The landed tool is unchanged in both; only the stub label moves.")
