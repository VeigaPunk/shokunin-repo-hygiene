#!/usr/bin/env python3
"""r38-drift-mutants.py — record-validation mutant battery for the drift tool.

Four single-defect mutants of `tools/souji-worktree-drift.py` target the record
validation arm the r37 discrimination fixture never exercises (it always writes
a consistent TOTAL row and never repeats a name):

  M7   TOTAL repos/row-count check disabled
  M8   TOTAL regs/sum check disabled
  M9   TOTAL prunable/sum check disabled
  M10  duplicate REPO name check disabled

Each mutant is applied to a scratch copy (an anchor that does not occur exactly
once is a battery defect, not a kill) and scored by two fixtures:

  killed       the candidate fixture (`--fixture`) rejects the mutant, i.e. it
               exits 1 AND prints a `SUMMARY cases=` line with fail>0
  base_killed  the r37 discrimination fixture (`--base-fixture`) rejects it

Pristine control (r37 routed defect: the battery had none): the candidate
fixture must pass 100 % on the unmutated tool before any mutant is scored. A
pristine failure voids the run (`pristine=FAIL`, exit 1) instead of being
silently counted as kills.

CLI:
  python3 -B tests/fixtures/r38-drift-mutants.py [--tool PATH]
      [--fixture PATH] [--base-fixture PATH] [--work DIR]

Exit: 0 all four killed and pristine ok, 1 any survivor or pristine failure, 2 usage.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

MUTANTS = (
    ("M7", 'if total["repos"] != len(rows):', 'if False and total["repos"] != len(rows):'),
    ("M8", 'if total["regs"] != sum(r["regs"] for r in rows):',
     'if False and total["regs"] != sum(r["regs"] for r in rows):'),
    ("M9", 'if total["prunable"] != sum(r["prunable"] for r in rows):',
     'if False and total["prunable"] != sum(r["prunable"] for r in rows):'),
    ("M10", 'if name in [r["name"] for r in rows]:', 'if False and name in [r["name"] for r in rows]:'),
)


def score(fixture, tool, work):
    """Return (killed, detail): the fixture must report its own failure summary."""
    proc = subprocess.run(
        ["python3", "-B", fixture, "--tool", tool, "--work", work],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
    )
    summaries = [l for l in proc.stdout.splitlines() if l.startswith("SUMMARY cases=")]
    fails = sum(1 for l in proc.stdout.splitlines() if l.endswith("=FAIL") or "=FAIL " in l)
    if not summaries:
        return False, "NO-SUMMARY rc=%d" % proc.returncode
    return (proc.returncode == 1 and fails > 0), "rc=%d fails=%d" % (proc.returncode, fails)


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--tool")
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--base-fixture")
    ap.add_argument("--work")
    args = ap.parse_args(argv)
    lane_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    tool = args.tool or os.path.join(lane_root, "tools", "souji-worktree-drift.py")
    work = args.work or os.environ.get("TMPDIR") or "/var/tmp"
    if not os.path.isdir(work):
        sys.stderr.write("usage: --work must name an existing directory (%s)\n" % work)
        return 2
    for fixture in [args.fixture] + ([args.base_fixture] if args.base_fixture else []):
        if not os.path.isfile(fixture):
            sys.stderr.write("usage: unreadable fixture %s\n" % fixture)
            return 2
    try:
        source = open(tool, encoding="utf-8").read()
    except OSError as exc:
        sys.stderr.write("usage: unreadable tool %s: %s\n" % (tool, exc))
        return 2
    scratch = tempfile.mkdtemp(prefix="souji-r38-mutants.", dir=work)
    results = []
    try:
        pristine_proc = subprocess.run(
            ["python3", "-B", args.fixture, "--tool", tool, "--work", scratch],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
        )
        pristine_ok = pristine_proc.returncode == 0 and any(
            l.startswith("SUMMARY cases=") and "fail=0" in l for l in pristine_proc.stdout.splitlines()
        )
        for mid, old, new in MUTANTS:
            if source.count(old) != 1:
                print("MUTANT %s ANCHOR-COUNT %d (expected 1)" % (mid, source.count(old)))
                results.append((mid, False, False))
                continue
            path = os.path.join(scratch, mid + ".py")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(source.replace(old, new))
            os.chmod(path, 0o755)
            killed, detail = score(args.fixture, path, scratch)
            base_killed = False
            if args.base_fixture:
                base_killed, base_detail = score(args.base_fixture, path, scratch)
                detail += " base:" + base_detail
            print("MUTANT %s killed=%s%s %s" % (
                mid, "yes" if killed else "no",
                "" if not args.base_fixture else " base_killed=%s" % ("yes" if base_killed else "no"),
                detail))
            results.append((mid, killed, base_killed))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    killed_n = sum(1 for _, k, _ in results if k)
    base_n = sum(1 for _, _, b in results if b)
    line = "SUMMARY mutants=%d killed=%d survived=%d pristine=%s" % (
        len(results), killed_n, len(results) - killed_n, "ok" if pristine_ok else "FAIL")
    if args.base_fixture:
        line += " base_killed=%d" % base_n
    print(line)
    return 0 if pristine_ok and killed_n == len(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
