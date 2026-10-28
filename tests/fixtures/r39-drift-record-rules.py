#!/usr/bin/env python3
"""r39-drift-record-rules.py — record-file edge classes the existing drift fixtures never assert.

The r38 battery (M7-M10) scores the four TOTAL/duplicate rules; `r36-worktree-drift.py`,
`r37-drift-discrimination.py` and `r38-drift-record.py` collectively say nothing about four
documented parse behaviours:

  trailing-space     a REPO line with trailing whitespace is a schema violation (the ROW pattern is
                     `$`-anchored)
  crlf               a CRLF record is accepted (`str.splitlines` splits `\r\n`)
  outside-root       a record row that resolves outside `--root` is RECORD-OUTSIDE-ROOT
  indented-comment   an indented `#` line is NOT a comment; it is a schema violation

plus two ordering classes: a TOTAL row placed before the REPO rows is accepted, and a record whose
only non-comment line is TOTAL is RECORD-EMPTY.

CLI:
  python3 -B tests/fixtures/r39-drift-record-rules.py [--tool PATH] [--work DIR]
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
    return root, path


def run_case(tool, root, path, body, name, want_rc, want_tokens, results, newline=None):
    fd, record = tempfile.mkstemp(prefix="record-", suffix=".tsv", dir=root)
    os.close(fd)
    with open(record, "w", encoding="utf-8", newline=newline) as handle:
        handle.write(body)
    proc = subprocess.run(
        ["python3", "-B", tool, "--root", path, "--record", record, "--timeout", "30"],
        env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
    )
    out = proc.stdout + proc.stderr
    missing = [t for t in want_tokens if t not in out]
    ok = proc.returncode == want_rc and not missing
    results.append((name, ok, "rc=%d want=%d missing=%r out=%r" % (
        proc.returncode, want_rc, missing, out.replace("\n", " ")[:160])))


def run_cases(tool, work):
    scratch = tempfile.mkdtemp(prefix="souji-r39-record.", dir=work)
    results = []
    try:
        root, path = fleet(scratch)
        run_case(tool, root, path, ROWS + TOTAL, "good", 0, ["SUMMARY", "record_repos=2"], results)
        run_case(tool, root, path,
                 "REPO\talpha\tregs=1\tprunable=0 \nREPO\tbeta\tregs=1\tprunable=0\n" + TOTAL,
                 "trailing-space", 2, ["RECORD-MALFORMED", "does not match the census schema"], results)
        run_case(tool, root, path, TOTAL + ROWS, "total-before-rows", 0,
                 ["SUMMARY", "record_repos=2"], results)
        fd, crlf = tempfile.mkstemp(prefix="record-crlf-", suffix=".tsv", dir=root)
        os.close(fd)
        with open(crlf, "wb") as handle:
            handle.write((ROWS + TOTAL).replace("\n", "\r\n").encode("utf-8"))
        proc = subprocess.run(
            ["python3", "-B", tool, "--root", path, "--record", crlf, "--timeout", "30"],
            env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
        )
        out = proc.stdout + proc.stderr
        results.append(("crlf", proc.returncode == 0 and "record_repos=2" in out,
                        "rc=%d out=%r" % (proc.returncode, out.replace("\n", " ")[:160])))
        run_case(tool, root, path,
                 "REPO\t../escape\tregs=1\tprunable=0\n",
                 "outside-root", 2, ["RECORD-OUTSIDE-ROOT"], results)
        run_case(tool, root, path, "  # indented comment\n" + ROWS + TOTAL, "indented-comment", 2,
                 ["RECORD-MALFORMED", "does not match the census schema"], results)
        run_case(tool, root, path, "# only a comment\n" + TOTAL, "comments-total-only", 2,
                 ["RECORD-EMPTY"], results)
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
