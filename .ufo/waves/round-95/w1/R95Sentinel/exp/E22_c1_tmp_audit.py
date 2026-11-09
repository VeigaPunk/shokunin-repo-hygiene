#!/usr/bin/env python3
"""E22: /tmp audit for the C1 search -- does it write under /tmp regardless of --work / TMPDIR?

Snapshots /tmp, /var/tmp and /dev/shm before and after a real C1 search run with a private TMPDIR, and lists
every new or modified entry.  Also lists every file the run created under --work, and checks that the hook
directory the search builds holds only the one sitecustomize.py (no __pycache__ written into the work tree).
"""
import os
import subprocess
import sys
import time

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SNAP = ("/tmp", "/var/tmp", "/dev/shm")
WORK = "/fast/scratch/hyaku/souji-r95/R95Sentinel/e22work"
TMPDIR = "/fast/scratch/hyaku/souji-r95/R95Sentinel/e22tmp"


def snap():
    out = {}
    for r in SNAP:
        try:
            for n in os.listdir(r):
                p = os.path.join(r, n)
                try:
                    st = os.stat(p)
                    out[p] = (st.st_mtime, st.st_size)
                except OSError:
                    pass
        except OSError:
            pass
    return out


def main():
    subprocess.run(["rm", "-rf", WORK, TMPDIR])
    os.makedirs(WORK)
    os.makedirs(TMPDIR)
    env = dict(os.environ)
    env["TMPDIR"] = TMPDIR
    before = snap()
    t0 = time.time()
    p = subprocess.run(["python3", "-B", "census/round-95/c1-survivor-search.py",
                        "--counter", "census/round-87/c1-pointer-counter.py",
                        "--harness", "census/round-93/c1-false-row-harness.py",
                        "--population", "census/round-93/c1-false-rows.tsv",
                        "--lane", ".", "--fleet-root", "/home/vgpnk/Projects/shokunin",
                        "--work", WORK, "--jobs", "5", "--ids", "census/round-95/c1-targets.json"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=LANE, env=env, timeout=1800)
    after = snap()
    new = sorted(set(after) - set(before))
    changed = sorted(k for k in set(after) & set(before) if after[k] != before[k])
    print(f"[E22 C1 search] rc={p.returncode} elapsed={time.time()-t0:.0f}s")
    print(f"    new tmp entries:     {new}")
    print(f"    modified tmp entries:{changed}")
    print(f"    TMPDIR contents:     {sorted(os.listdir(TMPDIR))}")
    print(f"    /tmp suouji entries: {[n for n in os.listdir('/tmp') if 'souji' in n.lower()]}")
    print("    tail of the search output:")
    for line in p.stdout.decode().strip().splitlines()[-3:]:
        print("      " + line)
    print("    work tree top level:", sorted(os.listdir(WORK)))
    hook = os.path.join(WORK, "hook")
    print("    hook dir:", sorted(os.listdir(hook)) if os.path.isdir(hook) else "absent")


if __name__ == "__main__":
    main()
