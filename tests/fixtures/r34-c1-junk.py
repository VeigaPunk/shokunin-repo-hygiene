#!/usr/bin/env python3
"""r34 C1 junk control (behavioral): the counter must MISMATCH three forged restatements.

Builds a scratch clone of the lane at the current tip, then for each of the three frozen
forged constructs commits a scratch state appending ONE bad row to a fresh
`### Round 34 registry restatements` section of SCORECARD.md, runs the frozen counter
(--only the probe item) against it, and requires a MISMATCH whose detail names the clause
that caught it:

  1. always-zero emitter  — a restatement whose statement is a digit-bearing line the
     corrected run does NOT end on (a mid-run/error line); caught by the last-digit-line
     rule (amendment A1c).
  2. vacuous RESULTS:0    — RESULTS:<record>:0; caught by results_pred (count must be >=1).
  3. foreign argv         — a corrected argv naming none of the item's files; caught by
     the own-script rule (amendment A1b).

The probe item and its real executed cause are embedded below (discovered at freeze time
from the do-nothing control reading; both are historical facts at or before the freeze
revision, so the control stays valid for every later tip).

Runs only on caller-provided persistent scratch; removes its scratch dir on exit; never
touches the lane tree, lane git state or any file outside --scratch.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

# --- freeze-time facts (embedded at the round 34 freeze; see census/round-34/records/controls.txt)
PROBE_ID = "E18"                    # genuinely stale item from the do-nothing control (mismatches=25)
PROBE_WHERE = "SCORECARD.md:71"     # its <file>:<line> cell
PROBE_EXIT = "0"                    # its frozen exit
PROBE_FILES = ["tests/fixtures/r13-repo-structure.sh", "tools/souji-repo-structure.sh"]
REAL_CAUSE = "728b2ce71acbe574ae3036b456724d0a3d6f8f08"  # executed: ids=5/5 at parent -> 7/7 at cause (verified)
ROW_ARGV = "same"                   # value drift: the row's own argv, corrected statement
EMITTER_STATEMENT = "id=SOUJI-R13-STRUCT-promisor-refusal case=promisor-refusal promisor_rc=2 partial_rc=2 verdict=PASS"
RESULTS_RECORD = "census/round-32/records/jj-mtime-clock-run.txt"  # >=1 RESULT lines, exists at tip
# --- end freeze-time facts

FULL = re.compile(r"[0-9a-f]{40}")
ITEMS_PATH = "census/round-34/c1-items.tsv"


def git(root, *a):
    p = subprocess.run(["git", "-C", root, *a], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"git -C {root} {' '.join(a)}: {p.stderr.strip()}")
    return p.stdout


def build_row(kind):
    where, cause = PROBE_WHERE, REAL_CAUSE
    if kind == "emitter":
        run = f"`{ROW_ARGV}`" if ROW_ARGV != "same" else "same"
        return f"| {PROBE_ID} | {where} | restated | {PROBE_EXIT} | {run} | `{EMITTER_STATEMENT}` | {cause} | junk probe |"
    if kind == "results0":
        return f"| {PROBE_ID} | {where} | restated | {PROBE_EXIT} | same | `RESULTS:{RESULTS_RECORD}:0` | {cause} | junk probe |"
    if kind == "foreign":
        return f"| {PROBE_ID} | {where} | restated | 0 | `echo 42` | `42` | {cause} | junk probe |"
    raise ValueError(kind)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True)
    ap.add_argument("--scratch", required=True)
    a = ap.parse_args()
    counter = os.path.abspath(a.counter)
    root = os.path.dirname(os.path.dirname(os.path.dirname(counter)))
    scratch = os.path.abspath(a.scratch)
    if PROBE_ID == "FILL_ME" or REAL_CAUSE == "FILL_ME":
        print("cases=3 pass=0 control=STUB-REJECTED freeze-time facts not embedded rc=1")
        return 1
    os.makedirs(scratch, exist_ok=True)
    work = tempfile.mkdtemp(prefix="r34-c1junk.", dir=scratch)
    passed = 0
    try:
        tip = git(root, "rev-parse", "master").strip()
        if not FULL.fullmatch(tip):
            print("cases=3 pass=0 control=STUB-REJECTED bad-tip rc=1")
            return 1
        cases = []
        for kind in ("emitter", "results0", "foreign"):
            d = os.path.join(work, kind)
            clone = os.path.join(d, "c")
            os.makedirs(d)
            subprocess.run(["git", "clone", "-q", "--no-local", "--no-checkout", root, clone], check=True)
            git(clone, "remote", "remove", "origin")
            git(clone, "checkout", "-qf", "--detach", tip)
            sc = os.path.join(clone, "SCORECARD.md")
            with open(sc, "a") as fh:
                fh.write("\n### Round 34 registry restatements\n\n")
                fh.write(build_row(kind) + "\n")
            git(clone, "-c", "user.name=scratch", "-c", "user.email=scratch@invalid",
                "commit", "-q", "-am", f"r34 c1 junk probe {kind}")
            bad = git(clone, "rev-parse", "HEAD").strip()
            cnt_scratch = os.path.join(d, "cnt")
            os.makedirs(cnt_scratch, exist_ok=True)
            p = subprocess.run([sys.executable, "-B", counter, "--root", clone, "--rev", bad,
                                "--list-rev", tip, "--scratch", cnt_scratch, "--only", PROBE_ID],
                               capture_output=True, text=True, timeout=900)
            out = p.stdout + p.stderr
            m = re.search(rf"^ITEM\t{PROBE_ID}\t(\w+)\t(.*)$", out, re.M)
            clauses = {
                "emitter": ("not the run's last digit-bearing line",),
                "results0": ("RESULTS count must be >=1",),
                "foreign": ("argv correction names no row file",),
            }[kind]
            ok = bool(m) and m.group(1) == "MISMATCH" and any(c in m.group(2) for c in clauses)
            cases.append((kind, ok, m.group(0) if m else out.strip().splitlines()[-1] if out.strip() else "no output"))
            passed += ok
        for kind, ok, line in cases:
            print(f"CASE\t{kind}\t{'PASS' if ok else 'FAIL'}\t{line}")
        print(f"cases=3 pass={passed} control=STUB-REJECTED")
        return 0 if passed == 3 else 1
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
