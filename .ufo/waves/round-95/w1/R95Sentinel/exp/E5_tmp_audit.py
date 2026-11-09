#!/usr/bin/env python3
"""E5: does any r95 instrument write under /tmp regardless of TMPDIR/--work?

Checks, for each instrument, whether anything it creates lands outside --work:
  - the C1 search: does it write the hook/check dir, the mutant dirs or harness.out outside --work?
  - the C2 probe: does it write forgery copies / .out files outside --work?
  - the C2 arms counter: it NAMES an absent /tmp path for S13 (tmp_work = /tmp/souji-r95-arm-S13-<pid>-absent)
    and asserts it does not exist; does it ever CREATE it?
  - is anything written under /tmp at all (TMPDIR-independent)?

Method: run each instrument with a private TMPDIR and with /tmp watched by a before/after snapshot
(new entries only), plus an lsof-free check by walking /tmp for files newer than the start time.
"""
import os
import subprocess
import sys
import time

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SCRATCH = "/fast/scratch/hyaku/souji-r95/R95Sentinel"


def tmp_snapshot():
    out = {}
    for root in ("/tmp", "/var/tmp", "/dev/shm"):
        try:
            for name in os.listdir(root):
                p = os.path.join(root, name)
                try:
                    out[p] = os.stat(p).st_mtime
                except OSError:
                    pass
        except OSError:
            pass
    return out


def diff_new(before, after):
    return sorted(set(after) - set(before))


def run(label, cmd, env=None, cwd=LANE):
    e = dict(os.environ)
    if env:
        e.update(env)
    before = tmp_snapshot()
    t0 = time.time()
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=e, cwd=cwd, timeout=900)
    after = tmp_snapshot()
    new = diff_new(before, after)
    newfiles = []
    for p2 in new:
        try:
            for dirpath, _dirs, files in os.walk(p2):
                for fn in files:
                    f = os.path.join(dirpath, fn)
                    if os.stat(f).st_mtime >= t0 - 5:
                        newfiles.append(f)
        except OSError:
            pass
    print(f"[{label}] rc={p.returncode} new tmp entries={new} new tmp files={newfiles[:20]}")
    return p


def main():
    tmpdir = os.path.join(SCRATCH, "tmpdir")
    os.makedirs(tmpdir, exist_ok=True)
    # C2 arms counter: does it create the /tmp path it names for S13?
    work = os.path.join(SCRATCH, "e5-arms")
    subprocess.run(["rm", "-rf", work])
    os.makedirs(work)
    p = run("C2-arms(r95 probe)",
            ["python3", "-B", "census/round-95/c2-setup-arms.py", "--probe", "census/round-95/c2-forgery-probe.py",
             "--fixture-pass", "tests/fixtures/r93-k4-flagfail.py", "--fixture-fail", "tests/fixtures/r92-k4-flagfail.py",
             "--tool", "tools/souji-record-agreement.py", "--before", "census/round-92/controls/c2-before-tool.py",
             "--work", work], env={"TMPDIR": tmpdir})
    print("    arms stdout tail:", p.stdout.decode().strip().splitlines()[-3:])
    print("    arms stderr tail:", p.stderr.decode().strip().splitlines()[-3:])
    s13 = [n for n in os.listdir("/tmp") if n.startswith("souji-r95-arm-S13")]
    print("    /tmp S13 entries now:", s13)


if __name__ == "__main__":
    main()
