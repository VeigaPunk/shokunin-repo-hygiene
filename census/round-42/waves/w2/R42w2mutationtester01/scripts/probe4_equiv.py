#!/usr/bin/env python3
"""Equivalence probes M14, M41, M57, M63 (pristine vs mutant, synthetic repos).
Regenerates logs/probe4-equivalence.txt. Needs the scratch root and mutants/ (see report)."""
import os
import sys

SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w2mutationtester01"
SEAT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRATCH)
from probe2 import newrepo, write, commit, sha, prereg, compare, COUNTER, POP, CONTROL  # noqa: E402

print("=== M63: cur[1][key] = value.strip() -- is .strip() a no-op on KEYLINE's capture? ===")
d = newrepo("M63c")
write(d, "census/c1.py", COUNTER); write(d, "census/pop.tsv", POP); write(d, "census/control.txt", CONTROL)
base = commit(d, "c1")
write(d, "prereg.txt", "# prereg\nRound: 42\n\n## C1 - claim 1\nBase:   %s   \nCounter: census/c1.py sha256=%s\n"
      "Population: census/pop.tsv sha256=%s\nControl: census/control.txt\nTarget: t\nKill: k\n"
      % (base, sha(COUNTER), sha(POP)))
commit(d, "prereg")
compare("Base value with leading/trailing spaces", "M63", d)

print("=== M57: sorted(dups) -> dups (a set): is the printed order still the same? ===")
d2 = newrepo("M57c")
write(d2, "census/c1.py", COUNTER); write(d2, "census/pop.tsv", POP); write(d2, "census/control.txt", CONTROL)
base2 = commit(d2, "c1")
write(d2, "prereg.txt", prereg(base2, tail="Target: a\nKill: b\nControl: c\n"))
commit(d2, "prereg")
compare("three duplicated keys (set order vs sorted order)", "M57", d2)

print("=== M41: PATH_SHA.match -> PATH_SHA.search (pattern is ^...$ anchored) ===")
d3 = newrepo("M41c")
write(d3, "census/c1.py", COUNTER); write(d3, "census/pop.tsv", POP); write(d3, "census/control.txt", CONTROL)
base3 = commit(d3, "c1")
write(d3, "prereg.txt", prereg(base3, keys={"Base": base3,
      "Counter": "junk census/c1.py sha256=%s" % sha(COUNTER),
      "Population": "census/pop.tsv sha256=%s" % sha(POP), "Control": "census/control.txt",
      "Target": "t", "Kill": "k"}))
commit(d3, "prereg")
compare("Counter value with leading junk before the path", "M41", d3)

print("=== M14: EXIT_LINE '^EXIT=(\\d+)$' -> 'EXIT=(\\d+)$' (match() already anchors at the start) ===")
d4 = newrepo("M14c")
write(d4, "census/c1.py", COUNTER); write(d4, "census/pop.tsv", POP)
write(d4, "census/control.txt", "SUMMARY x\nEXIT=1\n")
base4 = commit(d4, "c1")
write(d4, "prereg.txt", prereg(base4))
commit(d4, "prereg")
compare("control ending in a bare EXIT=1", "M14", d4)
