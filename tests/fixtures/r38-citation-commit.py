#!/usr/bin/env python3
"""r38-citation-commit.py — commit-arm discrimination for the citation reconciler.

The r37 lesson's named limit: the reconciler binds an expected token to a
citation line and to a receipt blob, but a commit id is in neither, so a
measured-commit cell naming a revision where the receipt does not exist (or
reads differently) was unverifiable. The r38 commit arm adds an optional eighth
register cell and five mismatch classes. This fixture freezes one synthetic
Git world and grades the tool against it:

  commit-ok               named, ancestor, receipt at that commit carries the token
  commit-unresolved       the commit cell is 40-hex but names no commit
  commit-not-ancestor     the commit resolves but is not an ancestor of --rev
  commit-unnamed          the anchored line does not name the commit (short or full)
  commit-receipt-absent   the receipt does not exist at the named commit
  commit-receipt-disagrees  the receipt at the commit reads another token
  legacy-7col             a seven-column register still grades on the base arms
  register-rev            --register-rev reads the register from a commit
  stale-present           the anchored line still carries the stale token
  expected-missing        the anchored line does not carry the expected token
  receipt-unnamed         the anchored line does not name the receipt
  anchor-count            the anchor matches two lines
  receipt-arm-disagrees   the receipt at receipt_rev reads another token
  malformed-commit        a non-40-hex commit cell is refused (rc 2)

Control: the same case list is re-run against a stub tool that always prints
`SUMMARY cells=<n> mismatches=0`. If the stub passes every case the counter is
vacuous; the fixture prints control=FALSE-GREEN-REJECTED only when the stub is
rejected on at least one case.

CLI:
  python3 -B tests/fixtures/r38-citation-commit.py [--tool PATH] [--work DIR]

Exit: 0 every case passed and the control was rejected, 1 otherwise, 2 usage.
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
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build(scratch):
    root = os.path.join(scratch, "repo")
    os.makedirs(root)
    sh(["git", "init", "-q", "-b", "main", root])
    sh(["git", "-C", root, "config", "user.email", "fixture@example.invalid"])
    sh(["git", "-C", root, "config", "user.name", "fixture"])
    # c0: cells.md with one anchored line per case that needs it; no receipts yet.
    lines = [
        "ANCHOR-ok | `rec/ok.txt` | cells=3 | commit %s" % ("0" * 40),
        "ANCHOR-unnamed | `rec/ok.txt` | cells=3",
        "ANCHOR-stale | `rec/ok.txt` | cells=3 | cells=99",
        "ANCHOR-missing | `rec/ok.txt` | cells=3",
        "ANCHOR-noreceipt | cells=3",
        "ANCHOR-dup | `rec/ok.txt` | cells=3",
        "ANCHOR-dup | `rec/ok.txt` | cells=3",
    ]
    write(os.path.join(root, "cells.md"), "\n".join(lines) + "\n")
    sh(["git", "-C", root, "add", "cells.md"])
    sh(["git", "-C", root, "commit", "-qm", "c0"])
    c0 = sh(["git", "-C", root, "rev-parse", "HEAD"]).stdout.strip()
    # c1: the good receipt lands here.
    write(os.path.join(root, "rec", "ok.txt"), "SUMMARY cells=3 mismatches=0\n")
    write(os.path.join(root, "rec", "other.txt"), "SUMMARY cells=9 mismatches=0\n")
    sh(["git", "-C", root, "add", "rec"])
    sh(["git", "-C", root, "commit", "-qm", "c1"])
    c1 = sh(["git", "-C", root, "rev-parse", "HEAD"]).stdout.strip()
    # c2: the ok receipt now reads another token.
    write(os.path.join(root, "rec", "ok.txt"), "SUMMARY cells=9 mismatches=0\n")
    sh(["git", "-C", root, "add", "rec/ok.txt"])
    sh(["git", "-C", root, "commit", "-qm", "c2"])
    c2 = sh(["git", "-C", root, "rev-parse", "HEAD"]).stdout.strip()
    # rewrite the ok anchor line with the real short hash at c3, and add two anchors that
    # name their own commit (r38 A2 after wave-1 seat W1MutCounter): with ANCHOR-ok the
    # receipt-at-commit cases also emitted COMMIT-UNNAMED, so their rc was already 1 and the
    # kill rested only on the token assertion. Isolated anchors make rc the intended signal.
    text = open(os.path.join(root, "cells.md"), encoding="utf-8").read().replace("commit " + "0" * 40, "commit " + c1)
    text += "ANCHOR-absent | `rec/ok.txt` | cells=3 | commit %s\n" % c0
    text += "ANCHOR-disagrees | `rec/ok.txt` | cells=3 | commit %s\n" % c2
    write(os.path.join(root, "cells.md"), text)
    sh(["git", "-C", root, "add", "cells.md"])
    sh(["git", "-C", root, "commit", "-qm", "c3"])
    tip = sh(["git", "-C", root, "rev-parse", "HEAD"]).stdout.strip()
    # a commit that resolves but is not an ancestor of the branch
    tree = sh(["git", "-C", root, "rev-parse", c0 + "^{tree}"]).stdout.strip()
    dangling = sh(["git", "-C", root, "commit-tree", tree, "-m", "dangling"]).stdout.strip()
    return root, c0, c1, c2, tip, dangling


def register(path, rows):
    header = "id\tfile\tanchor\texpected\tstale\treceipt\treceipt_rev\tcommit\n"
    body = "".join("\t".join(r) + "\n" for r in rows)
    write(path, header + body)
    return path


def invoke(tool, root, rev, reg, extra=None):
    proc = subprocess.run(
        ["python3", "-B", tool, "--root", root, "--rev", rev, "--register", reg] + (extra or []),
        env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
    )
    return proc.returncode, proc.stdout + proc.stderr


def check(name, ok, detail, results):
    results.append((name, bool(ok), detail))


def run_cases(tool, work):
    scratch = tempfile.mkdtemp(prefix="souji-r38-citation.", dir=work)
    results = []
    try:
        root, c0, c1, c2, tip, dangling = build(scratch)

        def row(i, anchor, commit, expected="cells=3", stale="cells=99", receipt="rec/ok.txt", rev=None):
            # receipt_rev defaults to c1, where `rec/ok.txt` carries cells=3: the
            # commit arm is what these cases vary, not the receipt arm.
            return [i, "cells.md", anchor, expected, stale, receipt, rev or c1, commit]

        def case(name, rows, want_rc, want_tokens, extra=None):
            reg = register(os.path.join(scratch, name + ".tsv"), rows)
            rc, out = invoke(tool, root, tip, reg, extra=extra)
            ok = rc == want_rc and all(t in out for t in want_tokens)
            check(name, ok, "rc=%d want_rc=%d missing=%r out=%r" % (
                rc, want_rc, [t for t in want_tokens if t not in out], out.splitlines()[:4]), results)
            return out

        case("commit-ok", [row("R1", "ANCHOR-ok", c1)], 0, ["SUMMARY cells=1 mismatches=0"])
        case("commit-unresolved", [row("R2", "ANCHOR-ok", "a" * 40)], 1, ["COMMIT-UNRESOLVED"])
        case("commit-not-ancestor", [row("R3", "ANCHOR-ok", dangling)], 1, ["COMMIT-NOT-ANCESTOR"])
        case("commit-unnamed", [row("R4", "ANCHOR-unnamed", c1)], 1, ["COMMIT-UNNAMED"])
        case("commit-receipt-absent", [row("R5", "ANCHOR-absent", c0)], 1, ["COMMIT-RECEIPT-ABSENT"])
        case("commit-receipt-disagrees", [row("R6", "ANCHOR-disagrees", c2)], 1, ["COMMIT-RECEIPT-DISAGREES"])
        case("legacy-7col", [["R7", "cells.md", "ANCHOR-ok", "cells=3", "cells=99", "rec/ok.txt", c1]], 0,
             ["SUMMARY cells=1 mismatches=0"])
        reg = register(os.path.join(root, "register-rev.tsv"), [row("R8", "ANCHOR-ok", c1)])
        sh(["git", "-C", root, "add", "register-rev.tsv"])
        sh(["git", "-C", root, "commit", "-qm", "register"])
        regrev = sh(["git", "-C", root, "rev-parse", "HEAD"]).stdout.strip()
        rc, out = invoke(tool, root, tip, "register-rev.tsv", extra=["--register-rev", regrev])
        check("register-rev", rc == 0 and "SUMMARY cells=1 mismatches=0" in out, "rc=%d out=%r" % (rc, out.splitlines()[:3]), results)
        case("stale-present", [row("R9", "ANCHOR-stale", c1)], 1, ["STALE-PRESENT"])
        case("expected-missing", [row("R10", "ANCHOR-missing", c1, expected="cells=7")], 1, ["EXPECTED-MISSING"])
        case("receipt-unnamed", [row("R11", "ANCHOR-noreceipt", c1)], 1, ["RECEIPT-UNNAMED"])
        case("anchor-count", [row("R12", "ANCHOR-dup", c1)], 1, ["ANCHOR-COUNT"])
        case("receipt-arm-disagrees", [row("R13", "ANCHOR-ok", c1, rev=c2)], 1, ["RECEIPT-DISAGREES"])
        case("malformed-commit", [row("R14", "ANCHOR-ok", "nothex")], 2, ["REFUSAL USAGE"])
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
    # vacuity control: a tool that always reports zero mismatches must be refused
    stub_dir = tempfile.mkdtemp(prefix="souji-r38-citation-stub.", dir=work)
    try:
        stub = os.path.join(stub_dir, "stub.py")
        with open(stub, "w", encoding="utf-8") as handle:
            handle.write("#!/usr/bin/env python3\nimport sys\nsys.stdout.write(\"SUMMARY cells=1 mismatches=0\\n\")\nsys.exit(0)\n")
        control = run_cases(stub, work)
        rejected = sum(1 for _, ok, _ in control if not ok)
    finally:
        shutil.rmtree(stub_dir, ignore_errors=True)
    for name, ok, detail in results:
        print("case-%s=%s%s" % (name, "PASS" if ok else "FAIL", "" if ok else " " + detail))
    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    control_tag = "FALSE-GREEN-REJECTED" if rejected > 0 else "STUB-PASSED"
    print("SUMMARY cases=%d pass=%d fail=%d control=%s" % (len(results), passed, failed, control_tag))
    return 0 if failed == 0 and rejected > 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
