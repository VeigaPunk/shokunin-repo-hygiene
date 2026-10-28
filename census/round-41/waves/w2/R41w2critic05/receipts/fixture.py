#!/usr/bin/env python3
"""r41-drift-record-order.py — TOTAL position and root-repository branches no committed fixture asserts.

The r40 battery (M15-M18) refused a conflicting SECOND TOTAL row but never a conflicting FIRST one
(r40 M40-4, routed defect R40-D-TOTAL), and it measured a --root that is not itself a git
repository, so two root-repository branches of `tools/souji-worktree-drift.py` stayed uncovered:

  TOTAL order         every TOTAL row is checked against the REPO rows, wherever it sits: a
                       first-disagreeing, last-agreeing pair is refused (RECORD-MALFORMED) on each of
                       the three TOTAL fields; agreeing pairs are accepted
  root in discovery   a --root that is a git work tree and that the record does not name is reported
                       UNRECORDED under its own basename; --skip-unrecorded suppresses that row, and
                       a record that names it leaves no UNRECORDED row
  root basename row   a record row naming the root's own basename is measured at the root (the
                       repository is live, not ABSENT)

Each branch has an arm that shows it doing something and an arm that shows it not doing it, so a
mutant that drops or inverts the branch cannot pass both.

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

ROWS = "REPO\talpha\tregs=1\tprunable=0\nREPO\tbeta\tregs=1\tprunable=0\n"
GOOD = "TOTAL\trepos=2\tregs=2\tprunable=0\n"
BAD_REPOS = "TOTAL\trepos=1\tregs=2\tprunable=0\n"
BAD_REGS = "TOTAL\trepos=2\tregs=3\tprunable=0\n"
BAD_PRUNABLE = "TOTAL\trepos=2\tregs=2\tprunable=1\n"
ROOT_NAME = "rootrepo"
ROOT_ROWS = "REPO\t%s\tregs=1\tprunable=0\nREPO\talpha\tregs=1\tprunable=0\n" % ROOT_NAME
ROOT_TOTAL = "TOTAL\trepos=2\tregs=2\tprunable=0\n"
ALPHA_ONLY = "REPO\talpha\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n"


def sh(cmd):
    return subprocess.run(cmd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, check=False)


def make_repo(path):
    os.makedirs(path)
    sh(["git", "init", "-q", "-b", "main", path])
    with open(os.path.join(path, "file.txt"), "w", encoding="utf-8") as handle:
        handle.write("base\n")
    sh(["git", "-C", path, "add", "file.txt"])
    sh(["git", "-C", path, "commit", "-qm", "base"])


def plain_fleet(scratch):
    """A --root that is not a repository, holding alpha and beta."""
    root = os.path.join(scratch, "plain-root")
    os.makedirs(root)
    make_repo(os.path.join(root, "alpha"))
    make_repo(os.path.join(root, "beta"))
    return root


def root_repo_fleet(scratch):
    """A --root that is itself a repository (basename ROOT_NAME) and also holds alpha."""
    root = os.path.join(scratch, ROOT_NAME)
    make_repo(root)
    make_repo(os.path.join(root, "alpha"))
    return root


def run_record(tool, root, body, name, want_rc, want_tokens, results, forbid=None, extra=None):
    fd, record = tempfile.mkstemp(prefix="record-", suffix=".tsv", dir=root)
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
    present = [t for t in (forbid or []) if t in out]
    ok = proc.returncode == want_rc and not missing and not present
    results.append((name, ok, "rc=%d want=%d missing=%r forbidden=%r out=%r" % (
        proc.returncode, want_rc, missing, present, out.replace("\n", " ")[:240])))


def run_cases(tool, work):
    scratch = tempfile.mkdtemp(prefix="souji-r41-order.", dir=work)
    results = []
    try:
        plain = plain_fleet(scratch)
        skip = ["--skip-unrecorded"]
        # TOTAL order (M19): a disagreeing TOTAL is refused in any position.
        run_record(tool, plain, ROWS + GOOD + GOOD, "total-agreeing-pair", 0,
                   ["SUMMARY", "record_repos=2"], results, extra=skip)
        run_record(tool, plain, ROWS + BAD_REPOS + GOOD, "total-first-bad-repos", 2,
                   ["RECORD-MALFORMED", "TOTAL repos=1"], results, extra=skip)
        run_record(tool, plain, ROWS + BAD_REGS + GOOD, "total-first-bad-regs", 2,
                   ["RECORD-MALFORMED", "TOTAL regs=3"], results, extra=skip)
        run_record(tool, plain, ROWS + BAD_PRUNABLE + GOOD, "total-first-bad-prunable", 2,
                   ["RECORD-MALFORMED", "TOTAL prunable=1"], results, extra=skip)
        run_record(tool, plain, ROWS + GOOD + BAD_REGS + GOOD, "total-middle-bad", 2,
                   ["RECORD-MALFORMED", "TOTAL regs=3"], results, extra=skip)
        run_record(tool, plain, GOOD + ROWS + BAD_REPOS + GOOD, "total-before-rows-then-bad", 2,
                   ["RECORD-MALFORMED", "TOTAL repos=1"], results, extra=skip)
        # Root in discovery (M20): an unnamed root repository is UNRECORDED under its basename.
        root = root_repo_fleet(scratch)
        run_record(tool, root, ALPHA_ONLY, "root-unrecorded-reported", 1,
                   ["DRIFT\tUNRECORDED\t%s\t" % ROOT_NAME, "drift_rows=1"], results)
        run_record(tool, root, ALPHA_ONLY, "root-unrecorded-suppressed-by-flag", 0,
                   ["SUMMARY", "drift_rows=0"], results, forbid=["UNRECORDED"], extra=skip)
        run_record(tool, root, ROOT_ROWS + ROOT_TOTAL, "root-recorded-not-unrecorded", 0,
                   ["SUMMARY", "drift_rows=0"], results, forbid=["UNRECORDED", "ABSENT"])
        # Root basename row (M21): the row is measured at the root, not read ABSENT.
        run_record(tool, root, ROOT_ROWS + ROOT_TOTAL, "root-basename-row-measured", 0,
                   ["SUMMARY", "record_repos=2", "live_repos=2", "drift_rows=0"], results,
                   forbid=["ABSENT"], extra=skip)
        run_record(tool, root, "REPO\t%s\tregs=7\tprunable=0\nREPO\talpha\tregs=1\tprunable=0\n"
                   % ROOT_NAME, "root-basename-row-live-figure", 1,
                   ["DRIFT\tREGS-CHANGED\t%s\trecord=7 live=1" % ROOT_NAME], results,
                   forbid=["ABSENT"], extra=skip)
        # A basename that is not the root's resolves to nothing: the fallback is exact.
        run_record(tool, root, "REPO\tnotroot\tregs=1\tprunable=0\nREPO\talpha\tregs=1\tprunable=0\n",
                   "other-basename-absent", 1, ["DRIFT\tABSENT\tnotroot\t"], results, extra=skip)
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
