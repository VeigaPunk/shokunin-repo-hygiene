#!/usr/bin/env python3
"""r40-drift-record-branches.py — record branches no committed drift fixture asserts.

The r39 C3 battery (M11-M14) scored four documented parse behaviours (trailing space, CRLF, outside
root, indented comment). Three branches of `tools/souji-worktree-drift.py` stayed uncovered by every
committed fixture:

  multiple TOTAL rows   the parser assigns the LAST TOTAL row it reads, so a second, conflicting
                         TOTAL is refused as a disagreement, while a second identical TOTAL agrees
  --skip-unrecorded     the flag suppresses the UNRECORDED drift rows; without it, a work tree under
                         --root that the record does not name is reported
  invalid UTF-8 bytes   the record is decoded with the `replace` error handler, so an undecodable
                         byte becomes U+FFFD: inside a REPO name the name survives the census schema
                         (the schema accepts any non-tab name) and the repository is reported ABSENT,
                         inside a comment line the byte is tolerated and the record parses

The `--skip-unrecorded` and the invalid-UTF-8 cases are paired: each has an arm that shows the branch
doing something and an arm that shows it not doing it, so a mutant that inverts the branch cannot
pass both.

CLI:
  python3 -B tests/fixtures/r40-drift-record-branches.py [--tool PATH] [--work DIR]
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
TOTAL = "TOTAL\trepos=2\tregs=2\tprunable=0\n"


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


def fleet(scratch):
    root = os.path.join(scratch, "fleet-root")
    os.makedirs(root)
    path = os.path.join(root, "fleet")
    make_repo(os.path.join(path, "alpha"))
    make_repo(os.path.join(path, "beta"))
    make_repo(os.path.join(path, "gamma"))
    return root, path


def run_record(tool, root, path, body, name, want_rc, want_tokens, results, binary=False,
               extra=None):
    fd, record = tempfile.mkstemp(prefix="record-", suffix=".tsv", dir=root)
    os.close(fd)
    if binary:
        with open(record, "wb") as handle:
            handle.write(body)
    else:
        with open(record, "w", encoding="utf-8") as handle:
            handle.write(body)
    proc = subprocess.run(
        ["python3", "-B", tool, "--root", path, "--record", record, "--timeout", "30"]
        + list(extra or []),
        env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
    )
    out = proc.stdout + proc.stderr
    missing = [t for t in want_tokens if t not in out]
    ok = proc.returncode == want_rc and not missing
    results.append((name, ok, "rc=%d want=%d missing=%r out=%r" % (
        proc.returncode, want_rc, missing, out.replace("\n", " ")[:200])))


def run_cases(tool, work):
    scratch = tempfile.mkdtemp(prefix="souji-r40-branches.", dir=work)
    results = []
    try:
        root, path = fleet(scratch)
        skip = ["--skip-unrecorded"]
        run_record(tool, root, path, ROWS + TOTAL, "good", 0,
                   ["SUMMARY", "record_repos=2"], results, extra=skip)
        run_record(tool, root, path, ROWS + TOTAL + TOTAL, "total-duplicate-identical", 0,
                   ["SUMMARY", "record_repos=2"], results, extra=skip)
        run_record(tool, root, path,
                   ROWS + TOTAL + "TOTAL\trepos=1\tregs=1\tprunable=0\n",
                   "total-conflicting-second", 2, ["RECORD-MALFORMED"], results, extra=skip)
        run_record(tool, root, path,
                   ROWS + "TOTAL\trepos=1\tregs=2\tprunable=0\n",
                   "total-repos-disagrees", 2, ["RECORD-MALFORMED"], results, extra=skip)
        run_record(tool, root, path, ROWS + TOTAL, "skip-unrecorded-suppresses", 0,
                   ["SUMMARY"], results, extra=skip)
        run_record(tool, root, path, ROWS + TOTAL, "unrecorded-without-flag", 1,
                   ["UNRECORDED"], results)
        run_record(tool, root, path,
                   b"REPO\tal\xffpha\tregs=1\tprunable=0\nREPO\tbeta\tregs=1\tprunable=0\n",
                   "invalid-utf8-in-repo-name", 1, ["ABSENT"], results, binary=True, extra=skip)
        run_record(tool, root, path,
                   b"# comment \xff\n" + ROWS.encode("utf-8") + TOTAL.encode("utf-8"),
                   "invalid-utf8-in-comment", 0, ["SUMMARY", "record_repos=2"], results,
                   binary=True, extra=skip)
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
