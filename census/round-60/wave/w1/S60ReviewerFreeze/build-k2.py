#!/usr/bin/env python3
"""k2 probe: the receipt's rev= names a revision where the Counter had DIFFERENT bytes than at freeze.

Spec (round 60 C1): instrument_sha256 must equal the sha256 of the Counter blob AT FREEZE; rev= only needs
to be a strict ancestor of freeze. A receipt therefore can claim 'measured at rev R' with the digest of the
freeze blob while the instrument at R had other bytes. The recorder itself (census/round-57/record-receipt.sh)
digests `git show REV:INSTR`, so a truthful receipt for R would carry the R digest.

  python3 -B build-k2.py --tool PATH --work DIR
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--substance", action="store_true")
    a = ap.parse_args()
    tool, work = os.path.abspath(a.tool), os.path.abspath(a.work)
    if os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(work)
    env = dict(os.environ, GIT_AUTHOR_NAME="probe", GIT_AUTHOR_EMAIL="p@invalid",
               GIT_COMMITTER_NAME="probe", GIT_COMMITTER_EMAIL="p@invalid",
               GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)

    def g(*x):
        return subprocess.run(["git", "-C", work] + list(x), stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, check=True, env=env).stdout.decode().strip()

    def put(files, msg):
        for rel, data in files.items():
            fp = os.path.join(work, rel)
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            with open(fp, "wb") as fh:
                fh.write(data.encode())
        g("add", "-A")
        g("commit", "-q", "-m", msg)
        return g("rev-parse", "HEAD")

    g("init", "-q")
    assert os.path.realpath(g("rev-parse", "--show-toplevel")) == os.path.realpath(work)
    OLD = "COUNTER-OLD-BYTES\n"
    NEW = "COUNTER-BYTES-v1\n"
    shaOLD = hashlib.sha256(OLD.encode()).hexdigest()
    shaNEW = hashlib.sha256(NEW.encode()).hexdigest()
    rev_old = put({"c.py": OLD, "p.tsv": "h\nr\n"}, "old counter")   # Base / measured rev
    freeze_parent = put({"c.py": NEW}, "counter changed after the measurement")
    receipt = ("instrument=c.py\ninstrument_sha256=%s\nrev=%s\ncommand=python3 -B c.py\nEXIT=1\n"
               % (shaNEW, rev_old))       # digest = FREEZE blob, rev = OLD measurement
    prereg = ("Round: 60\n\n## C1\nBase: %s\nCounter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\n"
              "Control: ctl.txt\nTarget: t\nKill: k\n" % (rev_old, shaNEW, hashlib.sha256(b"h\nr\n").hexdigest()))
    put({"ctl.txt": receipt, "pre.txt": prereg}, "freeze: k2 probe")
    freeze = g("rev-parse", "HEAD")
    p = subprocess.run(["python3", "-B", tool, "--root", work, "--prereg", "pre.txt", "--rev", freeze]
                       + (["--substance"] if a.substance else []),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    print("CASE k2-rev-vs-freeze-drift expect=refuse rc=%d" % p.returncode)
    print("  shaOLD=%s shaNEW=%s rev_old=%s freeze=%s" % (shaOLD, shaNEW, rev_old, freeze))
    sys.stdout.write(p.stdout.decode())
    sys.stdout.write("  STDERR " + p.stderr.decode())
    return 0


if __name__ == "__main__":
    sys.exit(main())
