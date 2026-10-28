#!/usr/bin/env python3
"""r41 C3: one class-asserting probe per refusal site of souji-worktree-drift.py (exit 2 AND 'REFUSAL <CLASS>:')."""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    if os.geteuid() == 0:
        sys.stderr.write("r41-refusal-sites: P02a/P18 need a non-root uid; refusing to run as root\n")
        return 2
    W = os.path.realpath(tempfile.mkdtemp(dir=a.work))
    R, O = W + "/root", W + "/o"
    os.makedirs(R)
    os.makedirs(O + "/ro")
    try:
        def rec(n, text):
            with open(O + "/" + n, "w") as f:
                f.write(text)
            return O + "/" + n

        row = "REPO\ta\tregs=1\tprunable=0\n"
        ok = rec("ok", row)
        denied = rec("denied", row)
        os.chmod(denied, 0)
        os.symlink("loop", O + "/loop")
        os.mkdir(O + "/dir")
        os.mkfifo(O + "/fifo")
        os.link(rec("hl", "x"), O + "/hl2")
        os.chmod(O + "/ro", 0o500)
        os.makedirs(R + "/r")
        gd = W + "/gd"
        os.makedirs(gd + "/objects")
        os.makedirs(gd + "/refs")
        with open(gd + "/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        with open(R + "/r/.git", "w") as f:
            f.write("gitdir: " + gd + "\n")
        os.makedirs(W + "/rr")
        tot = "TOTAL\trepos=%d\tregs=%d\tprunable=%d\n"
        M, E, X = "RECORD-MALFORMED", "RECORD-EMPTY", "RECORD-OUTSIDE-ROOT"
        N = "JSON-NOT-REGULAR"
        probes = [
            ("P01", M, O + "/none", []),
            ("P02a", "RECORD-MISSING", denied, []),
            ("P02b", "RECORD-MISSING", O + "/loop", []),
            ("P03", M, O + "/dir", []),
            ("P04", M, rec("dup", row + row), []),
            ("P05", M, rec("junk", "junk\n"), []),
            ("P06", E, rec("empty", "# c\n\n"), []),
            ("P07", M, rec("t1", row + tot % (2, 1, 0)), []),
            ("P08", M, rec("t2", row + tot % (1, 2, 0)), []),
            ("P09", M, rec("t3", row + tot % (1, 1, 1)), []),
            ("P10a", N, ok, ["--json", O + "/fifo"]),
            ("P10b", N, ok, ["--json", O + "/dir"]),
            ("P11", N, ok, ["--json", "/dev/null"]),
            ("P12", "USAGE", ok, ["--root", O + "/ok"]),
            ("P13", X, rec("out", "REPO\t../sib\tregs=1\tprunable=0\n"), []),
            ("P14", X, rec("gd", "REPO\tr\tregs=1\tprunable=0\n"), []),
            ("P15", "JSON-IS-RECORD", ok, ["--json", ok]),
            ("P16", "JSON-INSIDE-MEASURED-TREE", ok, ["--json", R + "/r/o.json"]),
            ("P17", "JSON-HARDLINKED", ok, ["--json", O + "/hl"]),
            ("P18", "JSON-UNWRITABLE", ok, ["--json", O + "/ro/o.json"]),
            ("P19", "USAGE", ok, ["--timeout", "0"]),
        ]
        bad = 0
        for pid, cls, r, extra in probes:
            cmd = ["python3", "-B", a.tool, "--root", R, "--record", r, "--skip-unrecorded"] + extra
            try:
                p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=30)
                good = ("REFUSAL %s:" % cls) in p.stderr
                d = "rc=%d" % p.returncode
            except subprocess.TimeoutExpired:
                good, d = False, "timeout"
            bad += not good
            print("probe-%s=%s %s" % (pid, "PASS" if good else "FAIL", d))
        print("SUMMARY probes=%d pass=%d fail=%d" % (len(probes), len(probes) - bad, bad))
        return 1 if bad else 0
    finally:
        os.chmod(O + "/ro", 0o700)
        shutil.rmtree(W, ignore_errors=True)


sys.exit(main())
