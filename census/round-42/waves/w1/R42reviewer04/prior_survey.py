#!/usr/bin/env python3
"""Direct per-fixture check: each of the eight PRIOR fixtures (frozen bytes from the freeze commit) run
against the pristine tool and against each group-B non-equivalent mutant. Prints rc, the SUMMARY line and
whether stderr carries a traceback, so a KILL (rc 1, fail>0, no traceback) is visible per cell."""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import PRISTINE, SCRATCH, SEAT, TMP, mut, genv
FREEZE = "afe17f416eec04dcf3f480b580a8f928de61d19d"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
PRIOR = ["r36-worktree-drift", "r37-drift-discrimination", "r38-drift-record", "r38-drift-write-envelope",
         "r39-drift-record-rules", "r40-drift-record-branches", "r41-drift-record-order", "r41-refusal-sites"]
FX = os.path.join(SCRATCH, "fx")
WORK = os.path.join(SCRATCH, "work")
os.makedirs(FX, exist_ok=True); os.makedirs(WORK, exist_ok=True); os.makedirs(TMP, exist_ok=True)
SUM = re.compile(r"^SUMMARY (?:cases|probes)=(\d+) pass=(\d+) fail=(\d+)", re.M)
tools = [("pristine", PRISTINE)] + [(m, mut(m)) for m in ["B1", "H1", "H2", "I1", "J9", "M1", "D4"]]
for name in PRIOR:
    blob = subprocess.run(["git", "-C", LANE, "show", "%s:tests/fixtures/%s.py" % (FREEZE, name)],
                          stdout=subprocess.PIPE, check=True, env=genv()).stdout
    path = os.path.join(FX, name + ".py")
    with open(path, "wb") as f:
        f.write(blob)
    for tag, tool in tools:
        work = os.path.join(WORK, "%s-%s" % (name, tag))
        os.makedirs(work, exist_ok=True)
        e = genv(); e["TMPDIR"] = work
        p = subprocess.run([sys.executable, "-B", path, "--tool", tool, "--work", work], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True, env=e, timeout=300, cwd=work)
        m = SUM.findall(p.stdout)
        summ = "SUMMARY cases=%s pass=%s fail=%s" % m[-1] if m else "no SUMMARY"
        tb = "Traceback" in p.stderr
        kill = bool(m) and p.returncode == 1 and int(m[-1][2]) > 0 and not tb
        print("%-28s %-9s rc=%s %-34s traceback=%s kill=%s" % (name, tag, p.returncode, summ, tb, kill))
