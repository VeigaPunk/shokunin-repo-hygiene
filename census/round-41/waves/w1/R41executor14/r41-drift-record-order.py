#!/usr/bin/env python3
"""r41-drift-record-order.py — record-order and root-repository behaviours no earlier drift fixture asserts.

The r40 battery (M15-M18) left three behaviours of `tools/souji-worktree-drift.py` unasserted:

  every TOTAL row is checked   `parse_record` keeps every TOTAL row and checks each against the REPO
                               rows, so a disagreeing TOTAL is refused in ANY position: first, middle,
                               last, before every REPO row, or between REPO rows. A tool that checks only
                               the last TOTAL accepts a first-disagreeing, last-agreeing pair.
  root repository discovered   when `--root` is itself a git work tree and the record does not name it,
                               the root is reported UNRECORDED (named by its basename); `--skip-unrecorded`
                               suppresses that row, and a non-repository root is never reported.
  root basename row measured   a REPO row naming the root's own basename is measured at the root (it is
                               not ABSENT), including a regs disagreement; a basename row for a root that
                               is not a work tree, and any other missing name, stay ABSENT.

Every case is paired: an arm that shows the behaviour and an arm that shows its absence (an agreeing
TOTAL set accepted, a non-repository root left unreported, a ghost name still ABSENT), so a mutant that
inverts or deletes the branch cannot pass both arms. Each case also asserts forbidden tokens, so
"nothing else was reported" is checked as well as "the row was reported".

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

ALPHA = "REPO\talpha\tregs=1\tprunable=0\n"
BETA = "REPO\tbeta\tregs=1\tprunable=0\n"
GAMMA = "REPO\tgamma\tregs=1\tprunable=0\n"
ROWS = ALPHA + BETA
TOTAL = "TOTAL\trepos=2\tregs=2\tprunable=0\n"
BAD_REPOS = "TOTAL\trepos=1\tregs=2\tprunable=0\n"
BAD_REGS = "TOTAL\trepos=2\tregs=3\tprunable=0\n"
BAD_PRUNABLE = "TOTAL\trepos=2\tregs=2\tprunable=1\n"
PARTIAL = "TOTAL\trepos=1\tregs=1\tprunable=0\n"
TOTAL3 = "TOTAL\trepos=3\tregs=3\tprunable=0\n"
SKIP = ["--skip-unrecorded"]


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


def plain_fleet(scratch):
    """--root is a plain directory (not a work tree) holding alpha, beta, gamma."""
    path = os.path.join(scratch, "plain", "fleet")
    for name in ("alpha", "beta", "gamma"):
        make_repo(os.path.join(path, name))
    return path


def repo_fleet(scratch):
    """--root is itself a git work tree (basename `rootrepo`) holding alpha and beta."""
    path = os.path.join(scratch, "repo", "rootrepo")
    make_repo(path)
    for name in ("alpha", "beta"):
        make_repo(os.path.join(path, name))
    return path


def run_record(tool, scratch, path, body, name, want_rc, want_tokens, results, forbid=(),
               extra=None):
    fd, record = tempfile.mkstemp(prefix="record-", suffix=".tsv", dir=scratch)
    os.close(fd)
    with open(record, "w", encoding="utf-8") as handle:
        handle.write(body)
    proc = subprocess.run(
        ["python3", "-B", tool, "--root", path, "--record", record, "--timeout", "30"]
        + list(extra or []),
        env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
    )
    out = proc.stdout + proc.stderr
    missing = [t for t in want_tokens if t not in out]
    present = [t for t in forbid if t in out]
    ok = proc.returncode == want_rc and not missing and not present
    results.append((name, ok, "rc=%d want=%d missing=%r forbidden-present=%r out=%r" % (
        proc.returncode, want_rc, missing, present, out.replace("\n", " ")[:300])))


def run_cases(tool, work):
    scratch = tempfile.mkdtemp(prefix="souji-r41-order.", dir=work)
    results = []
    try:
        plain = plain_fleet(scratch)
        repo = repo_fleet(scratch)
        malformed = ["RECORD-MALFORMED"]
        accepted = ["SUMMARY", "record_repos=2", "drift_rows=0"]

        def rec(body, name, rc, tokens, forbid=(), extra=None, path=None):
            run_record(tool, scratch, path or plain, body, name, rc, tokens, results,
                       forbid=forbid, extra=extra)

        # TOTAL ordering: first-disagreeing / last-agreeing, with its agreeing pair.
        rec(ROWS + BAD_REPOS + TOTAL, "total-first-disagrees-last-agrees", 2,
            malformed + ["TOTAL repos=1 but 2 REPO rows"], ["SUMMARY"], SKIP)
        rec(ROWS + TOTAL + TOTAL, "total-first-agrees-last-agrees", 0, accepted, malformed, SKIP)
        # Middle-disagreeing, flanked by agreeing rows (first and last agree).
        rec(ROWS + TOTAL + BAD_REGS + TOTAL, "total-middle-disagrees", 2,
            malformed + ["TOTAL regs=3 but REPO rows sum to 2"], ["SUMMARY"], SKIP)
        rec(ROWS + TOTAL + TOTAL + TOTAL, "total-three-agree", 0, accepted, malformed, SKIP)
        # Last-disagreeing (the position the last-only check also sees) pairs the same arms.
        rec(ROWS + TOTAL + TOTAL + BAD_PRUNABLE, "total-last-disagrees", 2,
            malformed + ["TOTAL prunable=1 but REPO rows sum to 0"], ["SUMMARY"], SKIP)
        # TOTAL before the REPO rows: the check runs after every row is read.
        rec(BAD_REGS + ROWS + TOTAL, "total-before-rows-disagrees-last-agrees", 2,
            malformed + ["TOTAL regs=3 but REPO rows sum to 2"], ["SUMMARY"], SKIP)
        rec(TOTAL + ROWS + TOTAL, "total-before-rows-agrees", 0, accepted, malformed, SKIP)
        rec(TOTAL + ROWS, "total-only-before-rows-agrees", 0, accepted, malformed, SKIP)
        # TOTAL between REPO rows: agrees with the prefix, not with the final rows.
        rec(ALPHA + PARTIAL + BETA + TOTAL, "total-between-rows-prefix-only", 2,
            malformed + ["TOTAL repos=1 but 2 REPO rows"], ["SUMMARY"], SKIP)
        rec(ALPHA + BETA + TOTAL + GAMMA + TOTAL3, "total-between-rows-superseded", 2,
            malformed + ["TOTAL repos=2 but 3 REPO rows"], ["SUMMARY"], SKIP)
        rec(ALPHA + BETA + GAMMA + TOTAL3 + TOTAL3, "total-after-all-rows-agree-three", 0,
            ["SUMMARY", "record_repos=3", "drift_rows=0"], malformed, SKIP)

        # Root repository: unrecorded root reported, suppressed, absent from a non-repository root.
        rec(ROWS + TOTAL, "root-repo-unrecorded-reported", 1,
            ["DRIFT\tUNRECORDED\trootrepo\tlive regs=1 prunable=0", "drift_rows=1"], ["ABSENT"],
            path=repo)
        rec(ROWS + TOTAL, "root-repo-unrecorded-suppressed", 0,
            ["SUMMARY", "drift_rows=0"], ["UNRECORDED", "ABSENT"], SKIP, path=repo)
        rec(GAMMA + ROWS + TOTAL3, "root-repo-and-absent-recorded-name", 1,
            ["DRIFT\tUNRECORDED\trootrepo", "DRIFT\tABSENT\tgamma"], ["DRIFT\tUNRECORDED\tgamma"],
            path=repo)
        rec(ALPHA + BETA + GAMMA + TOTAL3, "plain-root-not-reported", 0,
            ["SUMMARY", "record_repos=3", "drift_rows=0"], ["UNRECORDED", "ABSENT"], path=plain)
        rec(ROWS + TOTAL, "plain-root-unrecorded-child-only", 1,
            ["DRIFT\tUNRECORDED\tgamma\tlive regs=1 prunable=0", "drift_rows=1"],
            ["UNRECORDED\tfleet", "ABSENT"], path=plain)

        # Root basename row: measured at the root, not ABSENT.
        rec("REPO\trootrepo\tregs=1\tprunable=0\n" + ROWS +
            "TOTAL\trepos=3\tregs=3\tprunable=0\n", "root-basename-row-measured", 0,
            ["SUMMARY", "record_repos=3", "live_repos=3", "drift_rows=0"],
            ["ABSENT", "UNRECORDED", "RECORD-"], path=repo)
        rec("REPO\trootrepo\tregs=2\tprunable=0\n" + ROWS +
            "TOTAL\trepos=3\tregs=4\tprunable=0\n", "root-basename-row-regs-changed", 1,
            ["DRIFT\tREGS-CHANGED\trootrepo\trecord=2 live=1", "live_repos=3"],
            ["ABSENT", "UNRECORDED"], path=repo)
        rec("REPO\tghost\tregs=1\tprunable=0\n" + ROWS +
            "TOTAL\trepos=3\tregs=3\tprunable=0\n", "root-other-name-absent", 1,
            ["DRIFT\tABSENT\tghost\trecorded regs=1", "live_repos=2"], ["REGS-CHANGED"],
            SKIP, path=repo)
        rec("REPO\tfleet\tregs=1\tprunable=0\n" + ROWS +
            "TOTAL\trepos=3\tregs=3\tprunable=0\n", "plain-root-basename-row-absent", 1,
            ["DRIFT\tABSENT\tfleet\trecorded regs=1", "live_repos=2"], ["REGS-CHANGED"],
            SKIP, path=plain)
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
