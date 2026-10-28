#!/usr/bin/env python3
"""r41-drift-record-order.py — record order and root-repository branches no committed drift fixture asserts.

The r39 and r40 batteries leave three single-defect mutants of `tools/souji-worktree-drift.py` alive:

  every TOTAL row is checked   the parser keeps every TOTAL row and checks each against the REPO rows, so a
                               first-disagreeing, last-agreeing TOTAL pair (or a disagreeing middle row) is
                               refused as RECORD-MALFORMED wherever the bad row sits; a mutant that checks only
                               the last row accepts it. The r40 fixture only puts the disagreeing row LAST.
  root repository discovery    a --root that is itself a git repository is a work tree the record may not name:
                               it is reported UNRECORDED (under its own basename) unless --skip-unrecorded;
                               a --root that is not a repository reports nothing. A mutant that drops the
                               root from discovery reports no UNRECORDED row.
  root-basename record row     a record row that names the root's own basename is measured at the root when
                               the root holds a `.git` directory; when it does not, the row reads ABSENT. A
                               mutant that resolves the row to nothing reports ABSENT for a live root.

Each behaviour has a pair of arms (the branch doing something and the branch not doing it) so a mutant that
inverts it cannot pass both. The root repository arms run on two fleets whose roots share a basename: one root
is a git repository, the other is a plain directory.

CLI:
  python3 -B tests/fixtures/r41-drift-record-order.py [--tool PATH] [--work DIR]
Exit: 0 all cases match, 1 any mismatch, 2 usage.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

ENV = {
    "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
    "LC_ALL": "C",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
}

ROOT_NAME = "fleetroot"
ROWS = "REPO\talpha\tregs=1\tprunable=0\nREPO\tbeta\tregs=1\tprunable=0\n"
GOOD = "TOTAL\trepos=2\tregs=2\tprunable=0\n"
BAD_REPOS = "TOTAL\trepos=1\tregs=2\tprunable=0\n"
BAD_REGS = "TOTAL\trepos=2\tregs=3\tprunable=0\n"
BAD_PRUNABLE = "TOTAL\trepos=2\tregs=2\tprunable=1\n"
ROOT_ROW = "REPO\t%s\tregs=1\tprunable=0\n" % ROOT_NAME
ROWS_ROOT = ROWS + ROOT_ROW
GOOD_ROOT = "TOTAL\trepos=3\tregs=3\tprunable=0\n"


def sh(cmd):
    return subprocess.run(cmd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, check=False)


def make_repo(path):
    os.makedirs(path, exist_ok=True)
    sh(["git", "init", "-q", "-b", "main", path])
    with open(os.path.join(path, "file.txt"), "w", encoding="utf-8") as handle:
        handle.write("base\n")
    sh(["git", "-C", path, "add", "file.txt"])
    sh(["git", "-C", path, "commit", "-qm", "base"])


def fleets(scratch):
    """Return (git_root, plain_root, records_dir): two roots of the same basename, one a repository."""
    records = os.path.join(scratch, "records")
    os.makedirs(records)
    git_root = os.path.join(scratch, "gitroot", ROOT_NAME)
    plain_root = os.path.join(scratch, "plainroot", ROOT_NAME)
    make_repo(git_root)
    for root in (git_root, plain_root):
        make_repo(os.path.join(root, "alpha"))
        make_repo(os.path.join(root, "beta"))
    return git_root, plain_root, records


def run_record(tool, root, records, body, name, want_rc, want_tokens, results, forbid=(), extra=None):
    fd, record = tempfile.mkstemp(prefix="record-", suffix=".tsv", dir=records)
    os.close(fd)
    with open(record, "w", encoding="utf-8") as handle:
        handle.write(body)
    proc = subprocess.run(
        ["python3", "-B", tool, "--root", root, "--record", record, "--timeout", "30"]
        + list(extra or []),
        env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
    )
    out = proc.stdout + proc.stderr
    missing = [t for t in want_tokens if t not in out]
    present = [t for t in forbid if t in out]
    ok = proc.returncode == want_rc and not missing and not present
    results.append((name, ok, "rc=%d want=%d missing=%r forbidden=%r out=%r" % (
        proc.returncode, want_rc, missing, present, out.replace("\n", " ")[:300])))


def run_cases(tool, work):
    scratch = tempfile.mkdtemp(prefix="souji-r41-order.", dir=work)
    results = []
    try:
        git_root, plain_root, records = fleets(scratch)
        skip = ["--skip-unrecorded"]
        # TOTAL order: the disagreeing row is first or in the middle, the last row agrees.
        run_record(tool, plain_root, records, ROWS + BAD_REPOS + GOOD, "total-first-repos-disagrees-last-agrees",
                   2, ["RECORD-MALFORMED", "TOTAL repos=1 but 2 REPO rows"], results, extra=skip)
        run_record(tool, plain_root, records, ROWS + BAD_REGS + GOOD, "total-first-regs-disagrees-last-agrees",
                   2, ["RECORD-MALFORMED", "TOTAL regs=3 but REPO rows sum to 2"], results, extra=skip)
        run_record(tool, plain_root, records, ROWS + BAD_PRUNABLE + GOOD,
                   "total-first-prunable-disagrees-last-agrees",
                   2, ["RECORD-MALFORMED", "TOTAL prunable=1 but REPO rows sum to 0"], results, extra=skip)
        run_record(tool, plain_root, records, ROWS + GOOD + BAD_REGS + GOOD,
                   "total-middle-disagrees-first-and-last-agree",
                   2, ["RECORD-MALFORMED", "TOTAL regs=3 but REPO rows sum to 2"], results, extra=skip)
        run_record(tool, plain_root, records, GOOD + ROWS + BAD_REPOS + GOOD, "total-before-rows-disagrees-later",
                   2, ["RECORD-MALFORMED"], results, extra=skip)
        run_record(tool, plain_root, records, ROWS + GOOD + GOOD, "total-all-agree-accepted",
                   0, ["SUMMARY", "record_repos=2", "drift_rows=0"], results, extra=skip)
        # Root repository discovery: git root is reported UNRECORDED, plain root is not.
        run_record(tool, git_root, records, ROWS + GOOD, "root-repo-unrecorded-reported",
                   1, ["DRIFT\tUNRECORDED\t%s\t" % ROOT_NAME, "drift_rows=1"], results)
        run_record(tool, git_root, records, ROWS + GOOD, "root-repo-unrecorded-skipped-by-flag",
                   0, ["SUMMARY", "drift_rows=0"], results, forbid=["UNRECORDED"], extra=skip)
        run_record(tool, plain_root, records, ROWS + GOOD, "plain-root-reports-no-unrecorded",
                   0, ["SUMMARY", "drift_rows=0"], results, forbid=["UNRECORDED"])
        run_record(tool, git_root, records, ROWS_ROOT + GOOD_ROOT, "root-repo-recorded-not-unrecorded",
                   0, ["SUMMARY", "record_repos=3", "live_repos=3", "drift_rows=0"], results,
                   forbid=["UNRECORDED", "ABSENT"])
        # Root-basename record row: measured at a git root, ABSENT at a plain root.
        run_record(tool, git_root, records, ROWS_ROOT + GOOD_ROOT, "root-basename-row-measured-at-root",
                   0, ["live_repos=3", "live_regs=3"], results, forbid=["ABSENT"], extra=skip)
        run_record(tool, git_root, records,
                   ROWS + "REPO\t%s\tregs=2\tprunable=0\n" % ROOT_NAME
                   + "TOTAL\trepos=3\tregs=4\tprunable=0\n",
                   "root-basename-row-regs-changed-at-root",
                   1, ["DRIFT\tREGS-CHANGED\t%s\trecord=2 live=1" % ROOT_NAME], results, forbid=["ABSENT"],
                   extra=skip)
        run_record(tool, plain_root, records, ROWS_ROOT + GOOD_ROOT, "root-basename-row-absent-at-plain-root",
                   1, ["DRIFT\tABSENT\t%s\trecorded regs=1" % ROOT_NAME, "live_repos=2"], results, extra=skip)
        run_record(tool, git_root, records,
                   ROWS + "REPO\tnotroot\tregs=1\tprunable=0\n" + GOOD_ROOT,
                   "other-name-row-absent-at-root",
                   1, ["DRIFT\tABSENT\tnotroot\trecorded regs=1"], results, extra=skip)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return results


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--tool")
    ap.add_argument("--work")
    args = ap.parse_args(argv)
    lane_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    tool = args.tool or os.path.join(lane_root, "tools", "souji-worktree-drift.py")
    work = args.work or os.environ.get("TMPDIR") or "/var/tmp"
    if not os.path.isfile(tool):
        sys.stderr.write("usage: unreadable tool %s\n" % tool)
        return 2
    if not os.path.isdir(work):
        sys.stderr.write("usage: --work must name an existing directory (%s)\n" % work)
        return 2
    results = run_cases(tool, work)
    for name, ok, detail in results:
        print("case-%s=%s%s" % (name, "PASS" if ok else "FAIL", "" if ok else " " + detail))
    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    print("SUMMARY cases=%d pass=%d fail=%d" % (len(results), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
