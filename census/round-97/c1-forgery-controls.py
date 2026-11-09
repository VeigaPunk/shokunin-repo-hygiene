#!/usr/bin/env python3
"""souji r97 C1 forgery controls: five one-edit copies of census/round-97/c1-survivor-search.py, each a kill rule
that could look like a fix, run on census/round-97/c1-targets.json. A forgery is REFUSED iff it exits non-zero or its
SEARCH-SUMMARY differs from the frozen C1 predicate summary (errored=7 killed=2 survived=1) or its declared-shape
table (Q172) differs from mismatched=0.

  FA all-nonzero-errored  verdict never returns "yes" (blanket refusal: every non-zero harness exit is errored)
  FB no-sentinel          the harness runs without the crash-sentinel PYTHONPATH (only the rule's rc legs remain)
  FC no-signal-leg        the rule drops the negative-rc (killed by a signal) leg
  FD no-EH-clear          the EXCEPTION_HANDLED callback is not registered: a SystemExit caught at the top level is
                          scored errored again (t1/t4, mismatched as the r95 hook), while the ten targets are unchanged
  FE no-latch               the RERAISE callback is not registered: the hook reverts to the r96 clear-on-any-EH, so
                          x1/x2 are wrongly declared (mismatched=2), while the ten targets are unchanged

Output: `FORGERY <id> sha256=<s> exit=<rc> summary=<...> shapes=<m> refused=<yes|no>` and
`C1-FORGERY-SUMMARY forgeries=5 refused=<k>`. Exit 0 iff all five are refused; 1 otherwise; 2 on setup error.
Scratch only under --work (never /tmp)."""
import argparse
import hashlib
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
PRED = "generated=10 ambiguous=0 uncompiled=0 hung=0 scored=10 errored=7 killed=2 survived=1"
FORGERIES = (
    ("FA", '        return "yes"\n', '        return "errored"  # FA forgery\n'),
    ("FB", '    env["PYTHONPATH"] = ns.hook + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")\n',
     "    pass  # FB forgery: no crash sentinel\n"),
    ("FC", "    if rc == CRASH_RC or rc < 0 or any(r == CRASH_RC or r < 0 for r in rcs):\n",
     "    if rc == CRASH_RC or any(r == CRASH_RC for r in rcs):  # FC forgery\n"),
    ("FD", '    sys.monitoring.register_callback(_souji_id, sys.monitoring.events.EXCEPTION_HANDLED, _souji_handled)\n',
     "    pass  # FD forgery: no EH clear, r95 behaviour\n"),
    ("FE", '    sys.monitoring.register_callback(_souji_id, sys.monitoring.events.RERAISE, _souji_reraise)\n',
     "    pass  # FE forgery: no RERAISE latch, r96 behaviour (x1/x2 wrongly declared)\n"),
)


def main(argv):
    ap = argparse.ArgumentParser()
    for a in ("--search", "--counter", "--harness", "--population", "--lane", "--fleet-root", "--ids", "--work",
              "--shapes", "--scripts"):
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
        sh = subprocess.run([sys.executable, "-B", ns.shapes, "--search", path, "--scripts", ns.scripts,
                             "--work", os.path.join(work, fid + "-shapes")],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sm = re.search(r"^SHAPES-SUMMARY shapes=(\d+) mismatched=(\d+)$", sh.stdout.decode("utf-8", "replace"), re.M)
        shapes_m = int(sm.group(2)) if sm else -1
        rej = p.returncode != 0 or summ != PRED or shapes_m != 0
        refused += rej
        print(f"FORGERY {fid} sha256={hashlib.sha256(text.encode()).hexdigest()} exit={p.returncode} "
              f"summary={summ.replace(' ', ',')} shapes={shapes_m} refused={'yes' if rej else 'no'}")
        for l in out.splitlines():
            if l.startswith("SEARCH "):
                print(f"  {fid} {l}")
    print(f"C1-FORGERY-SUMMARY forgeries={len(FORGERIES)} refused={refused}")
    return 0 if refused == len(FORGERIES) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
