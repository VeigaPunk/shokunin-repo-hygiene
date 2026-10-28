#!/usr/bin/env python3
"""r37-citation-reconcile.py — fixture for tools/souji-citation-reconcile.py.

Builds one throwaway git repository per case under a scratch root taken from
`--work` / `TMPDIR` (never a hard-coded /tmp or /var/tmp) and checks the
counter's exit code and output. Cases:

  ok                citation + receipt agree                          -> rc 0
  anchor-missing    no line carries the anchor                        -> rc 1 ANCHOR-COUNT
  anchor-duplicated two lines carry the anchor                         -> rc 1 ANCHOR-COUNT
  expected-missing  the anchored line lacks the receipt value          -> rc 1 EXPECTED-MISSING
  stale-present     the anchored line still carries the stale token    -> rc 1 STALE-PRESENT
  receipt-absent    the receipt path is not at receipt_rev             -> rc 1 RECEIPT-ABSENT
  receipt-disagrees the receipt carries a different value              -> rc 1 RECEIPT-DISAGREES

The control runs the discriminating cases against an always-zero emitter
(prints `SUMMARY cells=1 mismatches=0`, rc 0 without reading anything): if that
stub reproduces the expected verdicts the fixture is falsified and prints
`control=FALSE-GREEN-NOT-REJECTED`.

CLI:
  python3 -B tests/fixtures/r37-citation-reconcile.py [--tool PATH] [--work DIR]

Exit: 0 every case passed and the control was rejected, 1 otherwise, 2 usage.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

STUB = """#!/usr/bin/env python3
import sys
print("SUMMARY cells=1 mismatches=0")
sys.exit(0)
"""

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


def make_repo(path):
    os.makedirs(path)
    sh(["git", "init", "-q", "-b", "main", path])
    write(os.path.join(path, "notes.md"), "| row | value |\n")
    write(os.path.join(path, "receipt.txt"), "SUMMARY cases=21 pass=21 fail=0\n")
    sh(["git", "-C", path, "add", "notes.md", "receipt.txt"])
    sh(["git", "-C", path, "commit", "-qm", "base"])
    return path


def write(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def commit(repo, message):
    sh(["git", "-C", repo, "add", "-A"])
    proc = sh(["git", "-C", repo, "commit", "-qm", message])
    if proc.returncode != 0:
        raise SystemExit("fixture: commit failed: %s" % proc.stderr)
    rev = sh(["git", "-C", repo, "rev-parse", "HEAD"]).stdout.strip()
    return rev


def rev(repo):
    return sh(["git", "-C", repo, "rev-parse", "HEAD"]).stdout.strip()


REGISTER = "id\tfile\tanchor\texpected\tstale\treceipt\treceipt_rev\n"

CASE_ROWS = {
    "ok": "C1\tnotes.md\tANCHOR\tcases=21 pass=21\tcases=11 pass=11\treceipt.txt\t@REV@\n",
    "anchor-missing": "C1\tnotes.md\tANCHOR\tcases=21 pass=21\tcases=11 pass=11\treceipt.txt\t@REV@\n",
    "anchor-duplicated": "C1\tnotes.md\tANCHOR\tcases=21 pass=21\tcases=11 pass=11\treceipt.txt\t@REV@\n",
    "expected-missing": "C1\tnotes.md\tANCHOR\tcases=21 pass=21\tcases=11 pass=11\treceipt.txt\t@REV@\n",
    "stale-present": "C1\tnotes.md\tANCHOR\tcases=21 pass=21\tcases=11 pass=11\treceipt.txt\t@REV@\n",
    "receipt-absent": "C1\tnotes.md\tANCHOR\tcases=21 pass=21\tcases=11 pass=11\tmissing.txt\t@REV@\n",
    "receipt-disagrees": "C1\tnotes.md\tANCHOR\tcases=21 pass=21\tcases=11 pass=11\treceipt.txt\t@REV@\n",
}

CASE_NOTES = {
    "ok": "ANCHOR cases=21 pass=21 receipt.txt\n",
    "anchor-missing": "no anchor here cases=21 pass=21\n",
    "anchor-duplicated": "ANCHOR cases=21 pass=21\nANCHOR cases=21 pass=21\n",
    "expected-missing": "ANCHOR cases=99\tpass=99\n",
    "stale-present": "ANCHOR cases=21 pass=21 cases=11 pass=11\n",
    "receipt-absent": "ANCHOR cases=21 pass=21 receipt.txt\n",
    "receipt-disagrees": "ANCHOR cases=21 pass=21 receipt.txt\n",
}

WANT = {
    "ok": (0, "SUMMARY cells=1 mismatches=0"),
    "anchor-missing": (1, "MISMATCH C1 ANCHOR-COUNT"),
    "anchor-duplicated": (1, "MISMATCH C1 ANCHOR-COUNT"),
    "expected-missing": (1, "MISMATCH C1 EXPECTED-MISSING"),
    "stale-present": (1, "MISMATCH C1 STALE-PRESENT"),
    "receipt-absent": (1, "MISMATCH C1 RECEIPT-ABSENT"),
    "receipt-disagrees": (1, "MISMATCH C1 RECEIPT-DISAGREES"),
}


def evaluate(tool, scratch, label):
    repo = make_repo(os.path.join(scratch, label))
    write(os.path.join(repo, "notes.md"), CASE_NOTES[label])
    if label == "receipt-disagrees":
        write(os.path.join(repo, "receipt.txt"), "SUMMARY cases=20 pass=20 fail=0\n")
    r = commit(repo, label)
    register = os.path.join(scratch, label + ".tsv")
    write(register, REGISTER + CASE_ROWS[label].replace("@REV@", r))
    proc = subprocess.run(
        ["python3", "-B", tool, "--root", repo, "--rev", r, "--register", register],
        env=ENV,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout + proc.stderr


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--tool")
    ap.add_argument("--work")
    args = ap.parse_args(argv)
    lane_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    tool = args.tool or os.path.join(lane_root, "tools", "souji-citation-reconcile.py")
    work = args.work or os.environ.get("TMPDIR") or "/var/tmp"
    if not os.path.isdir(work):
        sys.stderr.write("usage: --work must name an existing directory (%s)\n" % work)
        return 2
    scratch = tempfile.mkdtemp(prefix="souji-r37-citation.", dir=work)
    results = []
    control_replicated = []
    try:
        stub = os.path.join(scratch, "stub.py")
        write(stub, STUB)
        os.chmod(stub, 0o755)
        stub_dir = os.path.join(scratch, "stub-runs")
        os.makedirs(stub_dir)
        for label in CASE_ROWS:
            rc, out = evaluate(tool, scratch, label)
            want_rc, want_text = WANT[label]
            ok = rc == want_rc and want_text in out
            results.append((label, ok, "rc=%d want=%d out=%r" % (rc, want_rc, out.strip().splitlines()[:3])))
            src, sout = evaluate(stub, stub_dir, label)
            if label != "ok" and src == want_rc and want_text in sout:
                control_replicated.append(label)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    for name, ok, detail in results:
        print("case-%s=%s%s" % (name, "PASS" if ok else "FAIL", "" if ok else " " + detail))
    control_ok = not control_replicated
    print("control=%s%s" % ("FALSE-GREEN-REJECTED" if control_ok else "FALSE-GREEN-NOT-REJECTED",
                            "" if control_ok else " replicated=" + ",".join(control_replicated)))
    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    print("SUMMARY cases=%d pass=%d fail=%d control=%s" % (
        len(results), passed, failed, "FALSE-GREEN-REJECTED" if control_ok else "FALSE-GREEN-NOT-REJECTED"))
    return 0 if failed == 0 and control_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
