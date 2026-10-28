#!/usr/bin/env python3
"""r37-drift-discrimination.py — exact-field discrimination for the F1 drift tool.

The r36 fixture (`tests/fixtures/r36-worktree-drift.py`) is left byte-identical
as the round's regression. This fixture adds the field-exact cases the r36
non-author spot-check found undiscriminated (routed defect 4): a survivor mutant
`live_repos = len(rows) - unreachable` passed 12/12 because only the
`live-repos-non-negative` case read the field, and the summary's `drift_rows`
and `unreachable` counters were never asserted exactly.

Cases (each builds a synthetic fleet under `--work` / `TMPDIR`):
  match-exact             live_repos=2 live_regs=2 live_prunable=0
                          drift_rows=0 unreachable=0, rc 0
  regs-understated        record overstates registrations -> REGS-CHANGED, rc 1,
                          live_regs=2
  prunable-live           registered worktree removed -> PRUNABLE-CHANGED
                          record=0 live=1, live_prunable=1, rc 1
  absent-vs-unreachable   absent row keeps ABSENT class, broken row keeps
                          UNREACHABLE class; live_repos=1 unreachable=1
                          drift_rows=2, rc 1
  unrecorded-exact        UNRECORDED gamma; live_repos=2 live_regs=2
                          drift_rows=1, rc 1
  unrecorded-unreachable  a discovered repository whose git call fails counts as
                          UNREACHABLE (not UNRECORDED), unreachable=1,
                          drift_rows=1, rc 1

CLI:
  python3 -B tests/fixtures/r37-drift-discrimination.py [--tool PATH] [--work DIR]

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


def sh(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)


def write(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def make_repo(path):
    os.makedirs(path)
    sh(["git", "init", "-q", "-b", "main", path])
    write(os.path.join(path, "file.txt"), "base\n")
    sh(["git", "-C", path, "add", "file.txt"])
    sh(["git", "-C", path, "commit", "-qm", "base"])
    return path


def fleet(scratch, name):
    root = os.path.join(scratch, name)
    os.makedirs(root)
    path = os.path.join(root, "fleet")
    os.makedirs(path)
    return root, path


def record(root, rows, total):
    path = os.path.join(root, "record.tsv")
    lines = ["REPO\t%s\tregs=%d\tprunable=%d" % (n, r, p) for n, r, p in rows]
    lines.append("TOTAL\trepos=%d\tregs=%d\tprunable=%d" % total)
    write(path, "\n".join(lines) + "\n")
    return path


def invoke(tool, path, rec):
    proc = subprocess.run(
        ["python3", "-B", tool, "--root", path, "--record", rec, "--timeout", "30"],
        env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
    )
    out = proc.stdout + proc.stderr
    summary = ""
    for line in proc.stdout.splitlines():
        if line.startswith("SUMMARY"):
            summary = line
    fields = {}
    for token in summary.split():
        if "=" in token:
            key, value = token.split("=", 1)
            fields[key] = value
    return proc.returncode, out, fields


def check(name, ok, detail, results):
    results.append((name, bool(ok), detail))


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
    scratch = tempfile.mkdtemp(prefix="souji-r37-discrimination.", dir=work)
    results = []
    try:
        # match-exact
        root, path = fleet(scratch, "match")
        make_repo(os.path.join(path, "alpha"))
        make_repo(os.path.join(path, "beta"))
        rec = record(root, [("alpha", 1, 0), ("beta", 1, 0)], (2, 2, 0))
        rc, out, f = invoke(tool, path, rec)
        check("match-exact", rc == 0 and f.get("live_repos") == "2" and f.get("live_regs") == "2"
              and f.get("live_prunable") == "0" and f.get("drift_rows") == "0"
              and f.get("unreachable") == "0", "rc=%d fields=%r" % (rc, f), results)

        # regs-understated: the record overstates, so a one-sided live>record check stays silent
        root, path = fleet(scratch, "regs")
        make_repo(os.path.join(path, "alpha"))
        make_repo(os.path.join(path, "beta"))
        rec = record(root, [("alpha", 3, 0), ("beta", 1, 0)], (2, 4, 0))
        rc, out, f = invoke(tool, path, rec)
        check("regs-understated", rc == 1 and "REGS-CHANGED\talpha" in out
              and "record=3 live=1" in out and f.get("live_regs") == "2",
              "rc=%d fields=%r rows=%r" % (rc, f, out.splitlines()[:3]), results)

        # prunable-live
        root, path = fleet(scratch, "prunable")
        make_repo(os.path.join(path, "alpha"))
        wt = os.path.join(root, "alpha-wt")
        sh(["git", "-C", os.path.join(path, "alpha"), "worktree", "add", "-q", wt, "-b", "wt"])
        shutil.rmtree(wt)
        make_repo(os.path.join(path, "beta"))
        rec = record(root, [("alpha", 2, 0), ("beta", 1, 0)], (2, 3, 0))
        rc, out, f = invoke(tool, path, rec)
        check("prunable-live", rc == 1 and "PRUNABLE-CHANGED\talpha" in out
              and "record=0 live=1" in out and f.get("live_prunable") == "1",
              "rc=%d fields=%r rows=%r" % (rc, f, out.splitlines()[:3]), results)

        # absent-vs-unreachable
        root, path = fleet(scratch, "classes")
        make_repo(os.path.join(path, "alpha"))
        broken = os.path.join(path, "broken")
        os.makedirs(broken)
        write(os.path.join(broken, ".git"), "gitdir: /nonexistent/gitdir\n")
        rec = record(root, [("alpha", 1, 0), ("gone", 1, 0), ("broken", 1, 0)], (3, 3, 0))
        rc, out, f = invoke(tool, path, rec)
        check("absent-vs-unreachable",
              rc == 1 and "ABSENT\tgone" in out and "UNREACHABLE\tbroken" in out
              and f.get("live_repos") == "1" and f.get("unreachable") == "1"
              and f.get("drift_rows") == "2",
              "rc=%d fields=%r rows=%r" % (rc, f, out.splitlines()[:4]), results)

        # unrecorded-exact
        root, path = fleet(scratch, "unrecorded")
        make_repo(os.path.join(path, "alpha"))
        make_repo(os.path.join(path, "beta"))
        make_repo(os.path.join(path, "gamma"))
        rec = record(root, [("alpha", 1, 0), ("beta", 1, 0)], (2, 2, 0))
        rc, out, f = invoke(tool, path, rec)
        check("unrecorded-exact", rc == 1 and "UNRECORDED\tgamma" in out
              and f.get("live_repos") == "2" and f.get("live_regs") == "2"
              and f.get("drift_rows") == "1",
              "rc=%d fields=%r rows=%r" % (rc, f, out.splitlines()[:3]), results)

        # unrecorded-unreachable
        root, path = fleet(scratch, "unrecorded-broken")
        make_repo(os.path.join(path, "alpha"))
        broken = os.path.join(path, "broken")
        os.makedirs(broken)
        write(os.path.join(broken, ".git"), "gitdir: /nonexistent/gitdir\n")
        rec = record(root, [("alpha", 1, 0)], (1, 1, 0))
        rc, out, f = invoke(tool, path, rec)
        check("unrecorded-unreachable", rc == 1 and "UNREACHABLE\tbroken" in out
              and "UNRECORDED\tbroken" not in out and f.get("unreachable") == "1"
              and f.get("drift_rows") == "1",
              "rc=%d fields=%r rows=%r" % (rc, f, out.splitlines()[:3]), results)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    for name, ok, detail in results:
        print("case-%s=%s%s" % (name, "PASS" if ok else "FAIL", "" if ok else " " + detail))
    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    print("SUMMARY cases=%d pass=%d fail=%d" % (len(results), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
