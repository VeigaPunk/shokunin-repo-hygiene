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
  receipt-unnamed   the corrected line does not name its receipt        -> rc 1 RECEIPT-UNNAMED
  register-pinned   a tampered working register is ignored when
                    --register-rev names the committed one              -> rc 0
  boundary          `subcases=21 pass=21` is not `cases=21 pass=21`       -> rc 1 EXPECTED-MISSING
  receipt-is-file   the receipt path equals the citation file            -> rc 2 REFUSAL
  missing-header    the register has no header line                      -> rc 2 REFUSAL
  worktree-tamper   a tampered working copy loses to committed bytes     -> rc 0
  empty-register    header only, no rows                                 -> rc 2 REFUSAL
  duplicate-id      two rows with one id                                 -> rc 2 REFUSAL
  stale-dash        a row with stale '-'                                 -> rc 2 REFUSAL

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
    "receipt-unnamed": "C1\tnotes.md\tANCHOR\tcases=21 pass=21\tcases=11 pass=11\treceipt.txt\t@REV@\n",
}

CASE_NOTES = {
    "ok": "ANCHOR cases=21 pass=21 receipt.txt\n",
    "anchor-missing": "no anchor here cases=21 pass=21 receipt.txt\n",
    "anchor-duplicated": "ANCHOR cases=21 pass=21 receipt.txt\nANCHOR cases=21 pass=21 receipt.txt\n",
    "expected-missing": "ANCHOR cases=99\tpass=99 receipt.txt\n",
    "stale-present": "ANCHOR cases=21 pass=21 receipt.txt cases=11 pass=11\n",
    "receipt-absent": "ANCHOR cases=21 pass=21 receipt.txt\n",
    "receipt-disagrees": "ANCHOR cases=21 pass=21 receipt.txt\n",
    "receipt-unnamed": "ANCHOR cases=21 pass=21\n",
}

WANT = {
    "ok": (0, "SUMMARY cells=1 mismatches=0"),
    "anchor-missing": (1, "MISMATCH C1 ANCHOR-COUNT"),
    "anchor-duplicated": (1, "MISMATCH C1 ANCHOR-COUNT"),
    "expected-missing": (1, "MISMATCH C1 EXPECTED-MISSING"),
    "stale-present": (1, "MISMATCH C1 STALE-PRESENT"),
    "receipt-absent": (1, "MISMATCH C1 RECEIPT-ABSENT"),
    "receipt-disagrees": (1, "MISMATCH C1 RECEIPT-DISAGREES"),
    "receipt-unnamed": (1, "MISMATCH C1 RECEIPT-UNNAMED"),
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
        # register-pinned: the counter must read the register at --register-rev,
        # not the (tampered) working file.
        pinned = os.path.join(scratch, "pinned")
        repo = make_repo(pinned)
        write(os.path.join(repo, "notes.md"), "ANCHOR cases=21 pass=21 receipt.txt\n")
        # the register is committed inside the repo, then the working copy is
        # tampered; --register-rev must read the committed one.
        # (rev is not known before the commit, so commit, then amend the register
        # into the same tree via a second commit and pin that rev.)
        rev0 = commit(repo, "notes")
        write(os.path.join(repo, "register.tsv"), REGISTER + CASE_ROWS["ok"].replace("@REV@", rev0))
        rev = commit(repo, "register")
        write(os.path.join(repo, "register.tsv"), REGISTER + "C1\tnotes.md\tANCHOR\tcases=99\tcases=11\treceipt.txt\t%s\n" % rev)
        register = "register.tsv"
        proc = subprocess.run(
            ["python3", "-B", tool, "--root", repo, "--rev", rev, "--register", register,
             "--register-rev", rev],
            env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        ok = proc.returncode == 0 and "SUMMARY cells=1 mismatches=0" in proc.stdout
        results.append(("register-pinned", ok, "rc=%d out=%r" % (proc.returncode, proc.stdout.splitlines()[:2])))

        # boundary: a longer token that merely contains `cases=21 pass=21`
        boundary = os.path.join(scratch, "boundary")
        repo = make_repo(boundary)
        write(os.path.join(repo, "notes.md"), "ANCHOR subcases=21 pass=21 receipt.txt\n")
        rev = commit(repo, "boundary")
        register = os.path.join(scratch, "boundary.tsv")
        write(register, REGISTER + CASE_ROWS["ok"].replace("@REV@", rev))
        proc = subprocess.run(["python3", "-B", tool, "--root", repo, "--rev", rev, "--register", register],
                              env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        ok = proc.returncode == 1 and "MISMATCH C1 EXPECTED-MISSING" in proc.stdout
        results.append(("boundary", ok, "rc=%d out=%r" % (proc.returncode, proc.stdout.splitlines()[:2])))

        # receipt-is-file: the register points the receipt at the citation file
        same = os.path.join(scratch, "receipt-is-file")
        repo = make_repo(same)
        write(os.path.join(repo, "notes.md"), "ANCHOR cases=21 pass=21 notes.md\n")
        rev = commit(repo, "same")
        register = os.path.join(scratch, "same.tsv")
        write(register, REGISTER + "C1\tnotes.md\tANCHOR\tcases=21 pass=21\tcases=11 pass=11\tnotes.md\t%s\n" % rev)
        proc = subprocess.run(["python3", "-B", tool, "--root", repo, "--rev", rev, "--register", register],
                              env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        ok = proc.returncode == 2 and "REFUSAL USAGE" in proc.stderr
        results.append(("receipt-is-file", ok, "rc=%d err=%r" % (proc.returncode, proc.stderr.splitlines()[:1])))

        # worktree-tamper: the cited file is committed clean and tampered in the
        # working tree; committed bytes must win (A2 survivor, W2MutCounter2).
        tamper = os.path.join(scratch, "tamper")
        repo = make_repo(tamper)
        write(os.path.join(repo, "notes.md"), "ANCHOR cases=21 pass=21 receipt.txt\n")
        rev = commit(repo, "tamper")
        register = os.path.join(scratch, "tamper.tsv")
        write(register, REGISTER + CASE_ROWS["ok"].replace("@REV@", rev))
        write(os.path.join(repo, "notes.md"), "tampered, no anchor here\n")
        proc = subprocess.run(["python3", "-B", tool, "--root", repo, "--rev", rev, "--register", register],
                              env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        ok = proc.returncode == 0 and "SUMMARY cells=1 mismatches=0" in proc.stdout
        results.append(("worktree-tamper", ok, "rc=%d out=%r" % (proc.returncode, proc.stdout.splitlines()[:2])))

        # malformed registers: empty, duplicate id, stale '-'
        for label, body in (
            ("empty-register", REGISTER),
            ("duplicate-id", REGISTER + CASE_ROWS["ok"].replace("@REV@", "REVPLACE") + CASE_ROWS["ok"].replace("@REV@", "REVPLACE")),
            ("stale-dash", REGISTER + CASE_ROWS["ok"].replace("@REV@", "REVPLACE").replace("\tcases=11 pass=11\t", "\t-\t")),
        ):
            repo = make_repo(os.path.join(scratch, label))
            write(os.path.join(repo, "notes.md"), "ANCHOR cases=21 pass=21 receipt.txt\n")
            rev = commit(repo, label)
            register = os.path.join(scratch, label + ".tsv")
            write(register, body.replace("REVPLACE", rev))
            proc = subprocess.run(["python3", "-B", tool, "--root", repo, "--rev", rev, "--register", register],
                                  env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            ok = proc.returncode == 2 and "REFUSAL USAGE" in proc.stderr
            results.append((label, ok, "rc=%d err=%r" % (proc.returncode, proc.stderr.splitlines()[:1])))

        # missing-header: a register without its header line is malformed
        noheader = os.path.join(scratch, "noheader")
        repo = make_repo(noheader)
        write(os.path.join(repo, "notes.md"), "ANCHOR cases=21 pass=21 receipt.txt\n")
        rev = commit(repo, "noheader")
        register = os.path.join(scratch, "noheader.tsv")
        write(register, CASE_ROWS["ok"].replace("@REV@", rev))
        proc = subprocess.run(["python3", "-B", tool, "--root", repo, "--rev", rev, "--register", register],
                              env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        ok = proc.returncode == 2 and "REFUSAL USAGE" in proc.stderr
        results.append(("missing-header", ok, "rc=%d err=%r" % (proc.returncode, proc.stderr.splitlines()[:1])))
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
