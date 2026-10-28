#!/usr/bin/env python3
"""r38-drift-record.py — record-validation edge classes for the drift tool.

The r37 discrimination fixture builds every record with a `record()` helper that
always writes a consistent TOTAL row and never repeats a name, so four refusal
classes in `parse_record` were never exercised: a TOTAL/REPO disagreement on
each of the three counters, and a duplicate REPO name. A tool mutant that drops
any one of those checks survived the r37 fixture 12/12 (r38 coverage claim C3).

Cases (each builds one synthetic fleet under `--work`):
  total-ok                consistent TOTAL, two rows -> rc 0
  total-repos-mismatch    TOTAL repos=N disagrees -> rc 2, RECORD-MALFORMED TOTAL repos
  total-regs-mismatch     TOTAL regs=N disagrees -> rc 2, RECORD-MALFORMED TOTAL regs
  total-prunable-mismatch TOTAL prunable=N disagrees -> rc 2, RECORD-MALFORMED TOTAL prunable
  duplicate-name          the same REPO name twice -> rc 2, RECORD-MALFORMED ... duplicates
  no-total-row            REPO rows only -> rc 0 (TOTAL is optional)
  bad-line                a line outside the schema -> rc 2, RECORD-MALFORMED ... schema
  empty-record            header comment only -> rc 2, RECORD-EMPTY
  missing-record          the record path is absent -> rc 2, RECORD-MALFORMED
  comments-and-blanks     comment and blank lines are skipped -> rc 0

CLI:
  python3 -B tests/fixtures/r38-drift-record.py [--tool PATH] [--work DIR]

Exit: 0 every case passed, 1 otherwise, 2 usage.
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
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
}


def sh(cmd):
    return subprocess.run(cmd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)


def write(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def make_repo(path):
    os.makedirs(path)
    sh(["git", "init", "-q", "-b", "main", path])
    write(os.path.join(path, "file.txt"), "base\n")
    sh(["git", "-C", path, "add", "file.txt"])
    sh(["git", "-C", path, "commit", "-qm", "base"])


def fleet(scratch, name):
    root = os.path.join(scratch, name)
    os.makedirs(root)
    path = os.path.join(root, "fleet")
    make_repo(os.path.join(path, "alpha"))
    make_repo(os.path.join(path, "beta"))
    return root, path


GOOD = "REPO\talpha\tregs=1\tprunable=0\nREPO\tbeta\tregs=1\tprunable=0\nTOTAL\trepos=2\tregs=2\tprunable=0\n"


def run_case(tool, root, path, body, name, want_rc, want_tokens, results):
    record = os.path.join(root, name + ".tsv")
    if body is not None:
        write(record, body)
    proc = subprocess.run(
        ["python3", "-B", tool, "--root", path, "--record", record, "--timeout", "30"],
        env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
    )
    out = proc.stdout + proc.stderr
    ok = proc.returncode == want_rc and all(t in out for t in want_tokens)
    results.append((name, ok, "rc=%d want=%d missing=%r out=%r" % (
        proc.returncode, want_rc, [t for t in want_tokens if t not in out], out.splitlines()[:3])))


def run_cases(tool, work):
    scratch = tempfile.mkdtemp(prefix="souji-r38-record.", dir=work)
    results = []
    try:
        root, path = fleet(scratch, "classes")
        run_case(tool, root, path, GOOD, "total-ok", 0, ["SUMMARY", "record_repos=2"], results)
        run_case(tool, root, path,
                 "REPO\talpha\tregs=1\tprunable=0\nREPO\tbeta\tregs=1\tprunable=0\nTOTAL\trepos=3\tregs=2\tprunable=0\n",
                 "total-repos-mismatch", 2, ["RECORD-MALFORMED", "TOTAL repos"], results)
        run_case(tool, root, path,
                 "REPO\talpha\tregs=1\tprunable=0\nREPO\tbeta\tregs=1\tprunable=0\nTOTAL\trepos=2\tregs=5\tprunable=0\n",
                 "total-regs-mismatch", 2, ["RECORD-MALFORMED", "TOTAL regs"], results)
        run_case(tool, root, path,
                 "REPO\talpha\tregs=1\tprunable=0\nREPO\tbeta\tregs=1\tprunable=0\nTOTAL\trepos=2\tregs=2\tprunable=7\n",
                 "total-prunable-mismatch", 2, ["RECORD-MALFORMED", "TOTAL prunable"], results)
        run_case(tool, root, path,
                 "REPO\talpha\tregs=1\tprunable=0\nREPO\talpha\tregs=1\tprunable=0\nTOTAL\trepos=2\tregs=2\tprunable=0\n",
                 "duplicate-name", 2, ["RECORD-MALFORMED", "duplicates"], results)
        run_case(tool, root, path, "REPO\talpha\tregs=1\tprunable=0\nREPO\tbeta\tregs=1\tprunable=0\n",
                 "no-total-row", 0, ["SUMMARY", "record_repos=2"], results)
        run_case(tool, root, path, "REPO\talpha\tregs=1\tprunable=0\ngarbage line\n",
                 "bad-line", 2, ["RECORD-MALFORMED", "schema"], results)
        run_case(tool, root, path, "# only a comment\n", "empty-record", 2, ["RECORD-EMPTY"], results)
        run_case(tool, root, path, None, "missing-record", 2, ["RECORD-MALFORMED"], results)
        run_case(tool, root, path,
                 "# a comment\n\nREPO\talpha\tregs=1\tprunable=0\n\nREPO\tbeta\tregs=1\tprunable=0\nTOTAL\trepos=2\tregs=2\tprunable=0\n",
                 "comments-and-blanks", 0, ["SUMMARY", "record_repos=2"], results)
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
