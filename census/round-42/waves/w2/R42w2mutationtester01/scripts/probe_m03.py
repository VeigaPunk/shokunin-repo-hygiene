#!/usr/bin/env python3
"""M03 confirmation: a 41-character --rev (HEAD + '0') is refused by the pristine tool and accepted
by the mutant. Regenerates logs/m03-confirm.txt. Needs the scratch root and mutants/ (see report)."""
import os
import subprocess
import sys

SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w2mutationtester01"
SEAT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRISTINE = "/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-freeze-check.py"
sys.path.insert(0, SCRATCH)
from probe2 import newrepo, write, commit, prereg, git, GITENV, COUNTER, POP, CONTROL  # noqa: E402

d = newrepo("M03final")
write(d, "census/c1.py", COUNTER); write(d, "census/pop.tsv", POP); write(d, "census/control.txt", CONTROL)
base = commit(d, "c1")
write(d, "prereg.txt", prereg(base))
commit(d, "prereg")
H = git(d, "rev-parse", "HEAD")
print("HEAD =", H, "(40 chars)")
for label, tool in (("pristine", PRISTINE), ("M03", os.path.join(SEAT, "mutants", "M03.py"))):
    p = subprocess.run(["python3", "-B", tool, "--root", d, "--prereg", "prereg.txt", "--rev", H + "0"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=dict(GITENV, TMPDIR=d))
    print("=== %s, --rev = HEAD+'0' (41 hex) ===" % label)
    print("rc=%d stdout=%r stderr=%r" % (p.returncode, p.stdout.strip(), p.stderr.strip()))
