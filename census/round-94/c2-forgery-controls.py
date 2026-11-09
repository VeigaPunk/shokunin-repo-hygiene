#!/usr/bin/env python3
"""souji r94 C2 forgery controls: two one-edit copies of census/round-94/c2-forgery-probe.py that look like a setup
fix, each scored by census/round-94/c2-setup-arms.py. A forgery is REFUSED iff the arms counter reports
conform < 10 (exit 1).

  GA all-nonzero-is-2   the final verdict exit is 2 instead of 1 (every failure "looks like setup")
  GB refuse-empty-work  an existing EMPTY --work is refused like a non-empty one (exit 2 instead of running)

Output: `FORGERY <id> sha256=<s> arms_exit=<rc> summary=<...> refused=<yes|no>` and `C2-FORGERY-CTL-SUMMARY
forgeries=2 refused=<k>`. Exit 0 iff both are refused; 1 otherwise; 2 on setup error. Scratch only under --work."""
import argparse
import hashlib
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
FORGERIES = (
    ("GA", "    return 0 if positive and rejected == len(FORGERIES) else 1\n",
     "    return 0 if positive and rejected == len(FORGERIES) else 2  # GA forgery\n"),
    ("GB", "    if os.path.isdir(work) and os.listdir(work):\n", "    if os.path.isdir(work):  # GB forgery\n"),
)


def main(argv):
    ap = argparse.ArgumentParser()
    for a in ("--probe", "--fixture-pass", "--fixture-fail", "--tool", "--before", "--work"):
        ap.add_argument(a, required=True)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("C2-FORGERY-CTL-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if os.path.exists(work) and (not os.path.isdir(work) or os.listdir(work)):
        print(f"C2-FORGERY-CTL-FATAL: --work {work} is not an empty directory", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    src = open(ns.probe, encoding="utf-8").read()
    print(f"# probe path={os.path.abspath(ns.probe)} sha256={hashlib.sha256(src.encode()).hexdigest()}")
    refused = 0
    for fid, old, new in FORGERIES:
        if src.count(old) != 1:
            print(f"C2-FORGERY-CTL-FATAL: {fid} edit does not apply exactly once", file=sys.stderr)
            return 2
        text = src.replace(old, new, 1)
        path = os.path.join(work, f"{fid}-c2-forgery-probe.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        p = subprocess.run([sys.executable, "-B", os.path.join(HERE, "c2-setup-arms.py"), "--probe", path,
                            "--fixture-pass", ns.fixture_pass, "--fixture-fail", ns.fixture_fail, "--tool", ns.tool,
                            "--before", ns.before, "--work", os.path.join(work, fid)],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = p.stdout.decode("utf-8", "replace")
        with open(os.path.join(work, f"{fid}.out"), "w", encoding="utf-8") as f:
            f.write(out + "\n--stderr--\n" + p.stderr.decode("utf-8", "replace"))
        m = re.search(r"^ARMS-SUMMARY (.*)$", out, re.M)
        summ = m.group(1) if m else "-"
        rej = p.returncode == 1 and m is not None and summ != "arms=10 conform=10"
        refused += rej
        print(f"FORGERY {fid} sha256={hashlib.sha256(text.encode()).hexdigest()} arms_exit={p.returncode} "
              f"summary={summ.replace(' ', ',')} refused={'yes' if rej else 'no'}")
        for l in out.splitlines():
            if l.startswith("ARM ") and "conform=no" in l:
                print(f"  {fid} {l}")
    print(f"C2-FORGERY-CTL-SUMMARY forgeries={len(FORGERIES)} refused={refused}")
    return 0 if refused == len(FORGERIES) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
