#!/usr/bin/env python3
"""Third-round probes: exact characterisation of the remaining survivors."""
import os
import subprocess
import sys

sys.path.insert(0, "/fast/scratch/hyaku/souji-r42/R42w2mutationtester01")
from probe2 import (SEAT, PRISTINE, GITENV, git, write, commit, newrepo, sha, prereg, run,
                    COUNTER, POP, CONTROL, compare)


def p_M03_rev41():
    """M03: a 41-hex --rev."""
    d = newrepo("M03rev")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    rev = git(d, "rev-parse", "HEAD") + "0"
    for tool in (PRISTINE, os.path.join(SEAT, "mutants", "M03.py")):
        p = subprocess.run(["python3", "-B", tool, "--root", d, "--prereg", "prereg.txt", "--rev", rev],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
                           env=dict(GITENV, TMPDIR=d))
        print("  %-40s rc=%d stderr=%r" % (os.path.basename(tool), p.returncode, p.stderr.strip()[:130]))


def p_M22_stderr():
    """M22: the exact failure mode when the NUL guard is gone."""
    d = newrepo("M22b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    keys = {"Base": base, "Counter": "census/c\x00.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg")
    for tool in (PRISTINE, os.path.join(SEAT, "mutants", "M22.py")):
        p = subprocess.run(["python3", "-B", tool, "--root", d, "--prereg", "prereg.txt",
                            "--rev", git(d, "rev-parse", "HEAD")],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
                           env=dict(GITENV, TMPDIR=d))
        last = [x for x in p.stderr.strip().splitlines() if x][-1:] or [""]
        print("  %-12s rc=%d stdout=%r stderr_last=%s" % (
            os.path.basename(tool), p.returncode, p.stdout.strip()[:60], last[0][:120]))


def p_M61_M62_lane():
    """M61/M62 on the lane's OWN r42 preregistration at the tip (the counter's `real` leg)."""
    lane = "/home/vgpnk/Projects/shokunin/souji-shokunin"
    rev = subprocess.run(["git", "-C", lane, "rev-parse", "HEAD"], stdout=subprocess.PIPE,
                         text=True, check=True, env=GITENV).stdout.strip()
    for mid in ("M61", "M62"):
        tool = os.path.join(SEAT, "mutants", mid + ".py")
        p = subprocess.run(["python3", "-B", tool, "--root", lane, "--prereg",
                            "census/round-42/preregistration.txt", "--rev", rev],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
                           env=dict(GITENV, TMPDIR=SEAT))
        print("  %s on the lane prereg: rc=%d" % (mid, p.returncode))
        for line in p.stdout.splitlines():
            if line.startswith("FINDING") or line.startswith("SUMMARY"):
                print("      " + line)
    p = subprocess.run(["python3", "-B", PRISTINE, "--root", lane, "--prereg",
                        "census/round-42/preregistration.txt", "--rev", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
                       env=dict(GITENV, TMPDIR=SEAT))
    print("  PRISTINE on the lane prereg: rc=%d" % p.returncode)
    for line in p.stdout.splitlines():
        if line.startswith("FINDING") or line.startswith("SUMMARY"):
            print("      " + line)


def p_M59_first():
    """M59: a duplicated key whose FIRST occurrence is empty (the case the counter lacks)."""
    d = newrepo("M59b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    keys = {"Base": base, "Counter": "census/c1.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP), "Control": "census/control.txt",
            "Target": "", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys, tail="Target: second\n"))
    commit(d, "prereg")
    compare("duplicated Target whose first value is empty", "M59", d)


def p_M43_nosha():
    """M43: a Counter value with no sha256 at all (the PATH_SHA fallback)."""
    d = newrepo("M43b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    keys = {"Base": base, "Counter": "census/c1.py", "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg")
    compare("Counter value with no sha256 (fallback branch)", "M43", d)


def p_M40_re():
    """M40: the dispatch file's oldest add is before the freeze, the newest add is after."""
    d = newrepo("M40b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    write(d, ".ufo/waves/round-42/w1-results.json", "{}\n")
    base = commit(d, "c1")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    os.remove(os.path.join(d, ".ufo/waves/round-42/w1-results.json"))
    commit(d, "drop")
    write(d, ".ufo/waves/round-42/w1-results.json", "{}\n")
    commit(d, "readd-after")
    compare("dispatch file added before and re-added after the freeze", "M40", d)


print("=== M03: a 41-hex --rev")
p_M03_rev41()
print("=== M22: NUL in a path, exact failure mode")
p_M22_stderr()
print("=== M59: duplicated key, first value empty")
p_M59_first()
print("=== M43: Counter value with no sha256")
p_M43_nosha()
print("=== M40: dispatch file re-added after the freeze")
p_M40_re()
print("=== M61/M62 on the lane's own r42 preregistration")
p_M61_M62_lane()
