#!/usr/bin/env python3
"""R41w2mutationtester02 helper: Base == FREEZE-REV probe (baseline vs mutant B1). Scratch fixture only."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probes as P  # noqa: E402

d = P.mkrepo("base-equals-freeze")
base = P.readme(d)
P.base_files(d)
P.put(d, "prereg.txt", P.prereg(P.claim(base, "census/c.py sha256=" + P.sha(P.X))))
freeze = P.commit(d, "freeze")
P.put(d, "prereg.txt", P.prereg(P.claim(freeze, "census/c.py sha256=" + P.sha(P.X))))
rec = {"d": d, "rev": P.commit(d, "point Base at the freeze commit")}
print("freeze=%s head=%s" % (freeze, rec["rev"]))
for label, tool in [("baseline", P.BASE_TOOL), ("B1", os.path.join(P.MUT, "B1.py"))]:
    rc, lines, err = P.run(tool, rec)
    print("%-9s rc=%d %s" % (label, rc, " | ".join(lines) if lines else err))
