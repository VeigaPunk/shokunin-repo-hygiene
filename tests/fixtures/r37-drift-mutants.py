#!/usr/bin/env python3
"""r37-drift-mutants.py — mutant battery for the F1 worktree-drift fixture.

The r36 non-author spot-check routed a survivor mutant
(`live_repos = len(rows) - unreachable`) that passed the round's 12/12 fixture,
and named four undiscriminated predicates. This battery freezes six single-defect
mutants of `tools/souji-worktree-drift.py`, applies each to a scratch copy (an
anchor that does not occur exactly once is a battery defect, not a kill), and
runs the named fixture against it. A mutant is killed when the fixture exits
non-zero.

Mutants:
  M1  live_repos = len(rows) - unreachable        (the routed survivor)
  M2  summary drift_rows excludes UNRECORDED
  M3  unrecorded-loop git failures are not counted as unreachable
  M4  REGS-CHANGED fires only when live > record   (one-sided)
  M5  an absent row is reported as UNREACHABLE
  M6  drift never changes the exit code

CLI:
  python3 -B tests/fixtures/r37-drift-mutants.py [--tool PATH] --fixture PATH [--work DIR]

Exit: 0 every mutant killed, 1 any survivor, 2 usage.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

MUTANTS = (
    ("M1", '"live_repos": live_recorded,', '"live_repos": len(rows) - unreachable,'),
    ("M2", '"drift_rows": len(drift),',
     '"drift_rows": len([d for d in drift if d[0] != "UNRECORDED"]),'),
    ("M3",
     "                regs, prunable, error = measure(path, args.timeout)\n"
     "                if error:\n"
     "                    unreachable += 1\n"
     "                    drift.append((\"UNREACHABLE\", name, error))\n"
     "                    continue",
     "                regs, prunable, error = measure(path, args.timeout)\n"
     "                if error:\n"
     "                    drift.append((\"UNRECORDED\", name, \"unmeasured\"))\n"
     "                    continue"),
    ("M4", '        if regs != row["regs"]:', '        if regs > row["regs"]:'),
    ("M5", '            drift.append(("ABSENT", name, "recorded regs=%d" % row["regs"]))',
     '            drift.append(("UNREACHABLE", name, "absent"))'),
    ("M6", "    return 0 if not drift else 1", "    return 0"),
)


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--tool")
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--work")
    args = ap.parse_args(argv)
    lane_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    tool = args.tool or os.path.join(lane_root, "tools", "souji-worktree-drift.py")
    work = args.work or os.environ.get("TMPDIR") or "/var/tmp"
    if not os.path.isdir(work):
        sys.stderr.write("usage: --work must name an existing directory (%s)\n" % work)
        return 2
    try:
        source = open(tool, encoding="utf-8").read()
    except OSError as exc:
        sys.stderr.write("usage: unreadable tool %s: %s\n" % (tool, exc))
        return 2
    scratch = tempfile.mkdtemp(prefix="souji-r37-mutants.", dir=work)
    results = []
    try:
        for mid, old, new in MUTANTS:
            count = source.count(old)
            if count != 1:
                print("MUTANT %s ANCHOR-COUNT %d (expected 1)" % (mid, count))
                results.append((mid, False))
                continue
            path = os.path.join(scratch, mid + ".py")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(source.replace(old, new))
            os.chmod(path, 0o755)
            proc = subprocess.run(
                ["python3", "-B", args.fixture, "--tool", path, "--work", scratch],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
            )
            summary = [l for l in proc.stdout.splitlines() if l.startswith("SUMMARY cases=")]
            # a fixture crash is a battery defect, not a kill: the fixture must
            # report its own case summary for the mutant verdict to mean anything.
            verdict = "ERROR"
            if summary:
                fails = int(summary[-1].split("fail=")[1].split()[0])
                verdict = "yes" if proc.returncode == 1 and fails > 0 else "no"
            killed = verdict == "yes"
            print("MUTANT %s killed=%s rc=%d%s" % (mid, verdict, proc.returncode,
                  "" if summary else " NO-SUMMARY"))
            results.append((mid, killed))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    killed_n = sum(1 for _, ok in results if ok)
    print("SUMMARY mutants=%d killed=%d survived=%d" % (len(results), killed_n, len(results) - killed_n))
    return 0 if killed_n == len(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
