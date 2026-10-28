#!/usr/bin/env python3
"""r38-counter-arms.py — durable probes for the reconciler's envelope and matching arms.

Wave-1 seat W1SentCounter filed four first-falsifications against the r37 counter; the round
repaired them in A7/A8 and first recorded the evidence as a scratch-path receipt that a closure
cannot re-run. This fixture rebuilds the same four worlds from committed code and asserts the
refusal classes, plus one baseline that must pass:

  baseline-ok              exact-field SUMMARY, ancestor receipt_rev, named commit -> rc 0
  comment-tail             `SUMMARY cells=9 mismatches=0  # expected cells=3` must not satisfy
                           `cells=3` (RECEIPT-DISAGREES + COMMIT-RECEIPT-DISAGREES)
  receipt-rev-not-ancestor a receipt_rev that is not an ancestor of --rev -> RECEIPT-REV-NOT-ANCESTOR
  receipt-rev-unresolved   a 40-hex receipt_rev naming no commit -> RECEIPT-REV-UNRESOLVED
  register-fifo            a FIFO register is refused inside the bound, never blocks
  register-symlink         a symlinked register is refused (O_NOFOLLOW)

Control: the same case list is re-run against a stub counter that always prints
`SUMMARY cells=1 mismatches=0`; the fixture reports `control=FALSE-GREEN-REJECTED` only when that
stub fails at least one case.

CLI:
  python3 -B tests/fixtures/r38-counter-arms.py [--tool PATH] [--work DIR]

Exit: 0 every case passed and the control was rejected, 1 otherwise, 2 usage.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time

ENV = {
    "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
    "LC_ALL": "C",
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
}
BOUND = 15


def sh(cmd):
    return subprocess.run(cmd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)


def write(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build(scratch):
    root = os.path.join(scratch, "repo")
    os.makedirs(root)
    sh(["git", "init", "-q", "-b", "main", root])
    sh(["git", "-C", root, "config", "user.email", "fixture@example.invalid"])
    sh(["git", "-C", root, "config", "user.name", "fixture"])
    write(os.path.join(root, "cell.md"), "ANCHOR-ok | `rec-ok.txt` | cells=3 | commit PENDING\n")
    write(os.path.join(root, "rec-ok.txt"), "SUMMARY cells=3 mismatches=0\n")
    write(os.path.join(root, "rec-comment.txt"), "SUMMARY cells=9 mismatches=0  # expected cells=3\n")
    sh(["git", "-C", root, "add", "cell.md", "rec-ok.txt", "rec-comment.txt"])
    sh(["git", "-C", root, "commit", "-qm", "c1"])
    c1 = sh(["git", "-C", root, "rev-parse", "HEAD"]).stdout.strip()
    write(os.path.join(root, "cell.md"), "ANCHOR-ok | `rec-ok.txt` | cells=3 | commit %s\n" % c1)
    sh(["git", "-C", root, "add", "cell.md"])
    sh(["git", "-C", root, "commit", "-qm", "c2"])
    tip = sh(["git", "-C", root, "rev-parse", "HEAD"]).stdout.strip()
    tree = sh(["git", "-C", root, "rev-parse", c1 + "^{tree}"]).stdout.strip()
    dangling = sh(["git", "-C", root, "commit-tree", tree, "-m", "dangling"]).stdout.strip()
    return root, c1, tip, dangling


def register(path, rows):
    header = "id\tfile\tanchor\texpected\tstale\treceipt\treceipt_rev\tcommit\n"
    write(path, header + "".join("\t".join(r) + "\n" for r in rows))
    return path


def invoke(tool, root, rev, reg):
    start = time.time()
    try:
        proc = subprocess.run(
            ["python3", "-B", tool, "--root", root, "--rev", rev, "--register", reg],
            env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, timeout=BOUND,
        )
        return proc.returncode, proc.stdout + proc.stderr, time.time() - start, False
    except subprocess.TimeoutExpired:
        return None, "", time.time() - start, True


def check(name, ok, detail, results):
    results.append((name, bool(ok), detail))


def run_cases(tool, work):
    scratch = tempfile.mkdtemp(prefix="souji-r38-arms.", dir=work)
    results = []
    try:
        root, c1, tip, dangling = build(scratch)

        def row(i, expected="cells=3", stale="cells=99", receipt="rec-ok.txt", rev=None, commit=None):
            return [i, "cell.md", "ANCHOR-ok", expected, stale, receipt, rev or c1, commit if commit is not None else c1]

        def case(name, rows, want_rc, want_tokens):
            reg = register(os.path.join(scratch, name + ".tsv"), rows)
            rc, out, elapsed, hung = invoke(tool, root, tip, reg)
            ok = (not hung) and rc == want_rc and all(t in out for t in want_tokens)
            check(name, ok, "rc=%r hung=%s missing=%r out=%r" % (
                rc, hung, [t for t in want_tokens if t not in out], out.splitlines()[:3]), results)

        case("baseline-ok", [row("R1")], 0, ["SUMMARY cells=1 mismatches=0"])
        case("comment-tail", [row("R2", receipt="rec-comment.txt")], 1,
             ["RECEIPT-DISAGREES", "COMMIT-RECEIPT-DISAGREES"])
        case("receipt-rev-not-ancestor", [row("R3", rev=dangling)], 1, ["RECEIPT-REV-NOT-ANCESTOR"])
        case("receipt-rev-unresolved", [row("R4", rev="a" * 40)], 1, ["RECEIPT-REV-UNRESOLVED"])

        fifo = os.path.join(scratch, "reg.fifo")
        os.mkfifo(fifo)
        rc, out, elapsed, hung = invoke(tool, root, tip, fifo)
        check("register-fifo", (not hung) and rc == 2 and "REFUSAL USAGE" in out,
              "rc=%r hung=%s elapsed=%.1fs out=%r" % (rc, hung, elapsed, out.splitlines()[:2]), results)

        link = os.path.join(scratch, "reg.link.tsv")
        os.symlink(os.path.join(scratch, "baseline-ok.tsv"), link)
        rc, out, elapsed, hung = invoke(tool, root, tip, link)
        check("register-symlink", (not hung) and rc == 2 and "REFUSAL USAGE" in out,
              "rc=%r hung=%s out=%r" % (rc, hung, out.splitlines()[:2]), results)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return results


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
    results = run_cases(tool, work)
    stub_dir = tempfile.mkdtemp(prefix="souji-r38-arms-stub.", dir=work)
    try:
        stub = os.path.join(stub_dir, "stub.py")
        write(stub, "#!/usr/bin/env python3\nimport sys\nsys.stdout.write(\"SUMMARY cells=1 mismatches=0\\n\")\nsys.exit(0)\n")
        control = run_cases(stub, work)
        rejected = sum(1 for _, ok, _ in control if not ok)
    finally:
        shutil.rmtree(stub_dir, ignore_errors=True)
    for name, ok, detail in results:
        print("case-%s=%s%s" % (name, "PASS" if ok else "FAIL", "" if ok else " " + detail))
    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    print("SUMMARY cases=%d pass=%d fail=%d control=%s" % (
        len(results), passed, failed, "FALSE-GREEN-REJECTED" if rejected > 0 else "STUB-PASSED"))
    return 0 if failed == 0 and rejected > 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
