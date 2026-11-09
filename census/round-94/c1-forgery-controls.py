#!/usr/bin/env python3
"""souji r94 C1 forgery controls: two one-edit copies of census/round-94/c1-survivor-search.py, each a kill rule that
could look like a fix, run on census/round-94/c1-targets.json. A forgery is REFUSED iff its SEARCH-SUMMARY differs
from the frozen C1 predicate summary (errored=2 killed=2 survived=1).

  FA all-nonzero-errored  verdict never returns "yes" (blanket refusal: every non-zero harness exit is errored)
  FB no-sentinel          the harness runs without the crash-sentinel PYTHONPATH (the r93 rule plus a dead rc=70 check)

Output: `FORGERY <id> sha256=<s> exit=<rc> summary=<...> refused=<yes|no>` and `C1-FORGERY-SUMMARY forgeries=2
refused=<k>`. Exit 0 iff both are refused; 1 otherwise; 2 on setup error. Scratch only under --work (never /tmp)."""
import argparse
import hashlib
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
PRED = "generated=5 ambiguous=0 uncompiled=0 hung=0 scored=5 errored=2 killed=2 survived=1"
FORGERIES = (
    ("FA", '        return "yes"\n', '        return "errored"  # FA forgery\n'),
    ("FB", '    env["PYTHONPATH"] = ns.hook + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")\n',
     "    pass  # FB forgery: no crash sentinel\n"),
)


def main(argv):
    ap = argparse.ArgumentParser()
    for a in ("--search", "--counter", "--harness", "--population", "--lane", "--fleet-root", "--ids", "--work"):
        ap.add_argument(a, required=True)
    ap.add_argument("--jobs", default="5")
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("C1-FORGERY-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if os.path.exists(work) and (not os.path.isdir(work) or os.listdir(work)):
        print(f"C1-FORGERY-FATAL: --work {work} is not an empty directory", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    src = open(ns.search, encoding="utf-8").read()
    print(f"# search path={os.path.abspath(ns.search)} sha256={hashlib.sha256(src.encode()).hexdigest()}")
    refused = 0
    for fid, old, new in FORGERIES:
        if src.count(old) != 1:
            print(f"C1-FORGERY-FATAL: {fid} edit does not apply exactly once", file=sys.stderr)
            return 2
        path = os.path.join(work, f"{fid}-c1-survivor-search.py")
        text = src.replace(old, new, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        p = subprocess.run([sys.executable, "-B", path, "--counter", ns.counter, "--harness", ns.harness,
                            "--population", ns.population, "--lane", ns.lane, "--fleet-root", ns.fleet_root,
                            "--work", os.path.join(work, fid), "--jobs", ns.jobs, "--ids", ns.ids],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = p.stdout.decode("utf-8", "replace")
        with open(os.path.join(work, f"{fid}.out"), "w", encoding="utf-8") as f:
            f.write(out + "\n--stderr--\n" + p.stderr.decode("utf-8", "replace"))
        m = re.search(r"^SEARCH-SUMMARY (.*)$", out, re.M)
        summ = m.group(1) if m else "-"
        rej = p.returncode != 0 or summ != PRED
        refused += rej
        print(f"FORGERY {fid} sha256={hashlib.sha256(text.encode()).hexdigest()} exit={p.returncode} "
              f"summary={summ.replace(' ', ',')} refused={'yes' if rej else 'no'}")
        for l in out.splitlines():
            if l.startswith("SEARCH "):
                print(f"  {fid} {l}")
    print(f"C1-FORGERY-SUMMARY forgeries={len(FORGERIES)} refused={refused}")
    return 0 if refused == len(FORGERIES) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
