#!/usr/bin/env python3
"""r41-drift-record-order.py — R41critic05 probe (candidate for R1; scored, not landed).

Arms that separate the pristine tool from the three r41 mutants:
  total-first-disagrees-last-agrees  M19 (last TOTAL only) accepts; pristine refuses RECORD-MALFORMED
  root-unrecorded                    M20 (root dropped from discovery) misses the UNRECORDED root row
  root-basename-recorded             M21 (root-basename row resolves to nothing) reports ABSENT
Controls (must pass on pristine): good, root-unrecorded-skipped, plain-root-basename-absent.

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


def fleet_children(scratch, name):
    root = os.path.join(scratch, name)
    os.makedirs(root)
    make_repo(os.path.join(root, "alpha"))
    make_repo(os.path.join(root, "beta"))
    return root


def git_root(root):
    sh(["git", "init", "-q", "-b", "main", root])
    with open(os.path.join(root, "file.txt"), "w", encoding="utf-8") as handle:
        handle.write("base\n")
    sh(["git", "-C", root, "add", "file.txt"])
    sh(["git", "-C", root, "commit", "-qm", "base"])


def run_record(tool, root, body, name, want_rc, want_tokens, results, work, extra=()):
    fd, record = tempfile.mkstemp(prefix="record-", suffix=".tsv", dir=work)
    os.close(fd)
    with open(record, "w", encoding="utf-8") as handle:
        handle.write(body)
    proc = subprocess.run(
        ["python3", "-B", tool, "--root", root, "--record", record, "--timeout", "30"] + list(extra),
        env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
    )
    out = proc.stdout + proc.stderr
    missing = [t for t in want_tokens if t not in out]
    ok = proc.returncode == want_rc and not missing
    results.append((name, ok, "rc=%d want=%d missing=%r out=%r" % (
        proc.returncode, want_rc, missing, out.replace("\n", " ")[:200])))


def run_cases(tool, work):
    scratch = tempfile.mkdtemp(prefix="souji-r41-probe.", dir=work)
    results = []
    try:
        skip = ["--skip-unrecorded"]
        plain = fleet_children(scratch, "fleet")
        run_record(tool, plain, ROWS + TOTAL, "good", 0, ["SUMMARY", "record_repos=2"],
                   results, work, extra=skip)
        run_record(tool, plain, ROWS + "TOTAL\trepos=1\tregs=2\tprunable=0\n" + TOTAL,
                   "total-first-disagrees-last-agrees", 2, ["RECORD-MALFORMED"], results, work,
                   extra=skip)
        rooted = fleet_children(scratch, "fleet-repo")
        git_root(rooted)
        run_record(tool, rooted, ROWS + TOTAL, "root-unrecorded", 1, ["UNRECORDED", "fleet-repo"],
                   results, work)
        run_record(tool, rooted, ROWS + TOTAL, "root-unrecorded-skipped", 0, ["SUMMARY"],
                   results, work, extra=skip)
        run_record(tool, rooted, "REPO\tfleet-repo\tregs=1\tprunable=0\n"
                   "TOTAL\trepos=1\tregs=1\tprunable=0\n",
                   "root-basename-recorded", 0, ["SUMMARY", "record_repos=1"], results, work,
                   extra=skip)
        nogit = fleet_children(scratch, "fleet-plain")
        run_record(tool, nogit, "REPO\tfleet-plain\tregs=1\tprunable=0\n"
                   "TOTAL\trepos=1\tregs=1\tprunable=0\n",
                   "plain-root-basename-absent", 1, ["ABSENT"], results, work, extra=skip)
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
