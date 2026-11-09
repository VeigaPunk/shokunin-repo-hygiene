#!/usr/bin/env python3
"""souji r97 C2 forgery controls: four one-edit copies of census/round-97/c2-forgery-probe.py that look like a setup
fix, each scored by census/round-97/c2-setup-arms.py. A forgery is REFUSED iff the arms counter does not print the
frozen predicate (ARMS-SUMMARY arms=20 conform=20 with survivors=0 on T1). GD is the reaping cheat: it claims setup
refusal for every fixture without reaping; the counter's identity check counts surviving T1 processes and keeps
survivors>0, so the forged probe's printed verdict cannot reach the predicate.

  GA all-nonzero-is-2   the final verdict exit is 2 instead of 1 (every failure "looks like setup")
  GB decode-replace     --tool/--before are decoded with errors="replace" (non-UTF-8 bytes accepted, the run goes on)
  GC no-timeout         fixture runs are waited for without a timeout (a hanging fixture hangs the probe)
  GD reaping-cheat      the probe claims setup refusal without reaping by identity (the counter still counts
                        the surviving T1 grandchild)

Output: `FORGERY <id> sha256=<s> arms_exit=<rc> summary=<...> refused=<yes|no>` and `C2-FORGERY-CTL-SUMMARY
forgeries=4 refused=<k>`. Exit 0 iff all four are refused; 1 otherwise; 2 on setup error. Scratch only under
--work."""
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
    ("GB", '        return data.decode("utf-8")\n', '        return data.decode("utf-8", "replace")  # GB forgery\n'),
    ("GC", "    if total > max_output:\n", "    pass  # GC forgery: no output cap (unbounded output exhausts probe memory -> signal exit)\n"),
    ("GD", "        raise Fatal(f\"the fixture run for {label} exceeded --timeout {timeout}s; its process group was killed\")\n",
     "        raise Fatal(f\"the fixture run for {label} exceeded --max-output {max_output} bytes; its process group was killed\")  # GD reaping cheat: claim refusal, reap nothing\n"),
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
        # GD is a probe-body cheat: the counter's T1 identity check keeps survivors>0 itself, so the predicate
        # (conform=20 AND survivors=0) is the refusal test below, not the runner's own print.
        arm_t1 = re.search(r"^ARM T1 .*survivors=(\d+)$", out, re.M)
        surv = int(arm_t1.group(1)) if arm_t1 else None
        # A-04 class: the GB decode-replace forgery can make a S9 exit 1 look like a verdict exit (exit 1,
        # conform=yes) while the arm's expected FATAL line is missing (line=no). Read S9 by its own line so a
        # legit exit-code sum cannot hide a forged line. Likewise GC (no cap) turns S12/T1 into hung runs under
        # the probe's new selector wait, whose per-arm wall is the probe's own 120 s timeout, not a full
        # communicate() block: a GC run therefore ends hung on S12/T1 (line=no) inside 300 s.
        rej = (p.returncode == 1 and m is not None and summ != "arms=20 conform=20") or (fid == "GD" and surv != 0)
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
