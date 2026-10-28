#!/usr/bin/env python3
"""r40-c1-evidence.py — the r40 C1 counter's own evidence-binding and strict-descendant cases.

The r39 counter closed a routed defect when one line of a file carried the anchor and every `must`
token. A line that carries the tokens and cites nothing satisfied it — the r39 planned r40 row named
that forgery ("bind the C1 items to *evidence* rather than token presence"), and the r40 non-author
spot-check of round 39 exercised it. This fixture builds a synthetic repository and runs the r40
counter over it, asserting eight cases:

  bound-item-closed          a line that carries the tokens AND cites a resolvable, revision-bound
                             evidence pointer closes
  forged-token-only-open     the same line without the bound pointer stays OPEN (EVIDENCE-NOT-BOUND)
  forged-unresolved-rev-open an evidence revision that does not resolve stays OPEN
  forged-non-ancestor-open   an evidence revision outside the audited history stays OPEN
  register-clean-accepted    a register whose rows name a strict descendant commits is accepted
  register-equal-rejected    a row whose commit equals its receipt_rev is rejected
  register-backwards-rejected a row whose commit is older than its receipt_rev is rejected
  r39-control-closes-forged  the r39 counter CLOSES the forged token-only line — the do-nothing
                             control reaches the forgery and cannot reach the r40 predicate

CLI:
  python3 -B tests/fixtures/r40-c1-evidence.py [--counter PATH] [--base-counter PATH] [--work DIR]
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

RECONCILER = "tools/souji-citation-reconcile.py"


def sh(root, args):
    return subprocess.run(["git", "-C", root] + args, env=ENV, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, check=False)


def commit(root, message):
    sh(root, ["add", "-A"])
    sh(root, ["commit", "-qm", message])
    out = sh(root, ["rev-parse", "HEAD"]).stdout.strip()
    return out


def write(root, relpath, text):
    path = os.path.join(root, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build_repo(scratch, lane_root):
    root = os.path.join(scratch, "lane")
    os.makedirs(root)
    sh(root, ["init", "-q", "-b", "main", "."])
    top = sh(root, ["rev-parse", "--show-toplevel"]).stdout.strip()
    if top != os.path.abspath(root):
        raise RuntimeError("fixture repo top-level mismatch: %r" % top)
    sh(root, ["config", "user.name", "fixture"])
    sh(root, ["config", "user.email", "fixture@example.invalid"])
    with open(os.path.join(lane_root, RECONCILER), encoding="utf-8") as handle:
        reconciler = handle.read()
    write(root, RECONCILER, reconciler)
    write(root, "receipts/r0.txt", "SUMMARY cases=7 pass=7 fail=0\n")
    write(root, "receipts/r1.txt", "SUMMARY cases=7 pass=7 fail=0\n")
    write(root, "claims.md", "FORGED-CLAIM cases=7\n")
    c0 = commit(root, "c0: tool, receipts, forged claim")
    write(root, "receipts/r1b.txt", "SUMMARY cases=7 pass=7 fail=0\n")
    c1 = commit(root, "c1: a later commit")
    write(root, "claims.md",
          "FORGED-CLAIM cases=7\n"
          "FORGED-PATH-CLAIM cases=7 evidence-revision=%s\n"
          "FORGED-WRONG-VALUE cases=999 evidence=`receipts/r0.txt`@%s\n"
          "BOUND-CLAIM cases=7 evidence=`receipts/r0.txt`@%s\n" % (c1, c1, c1))
    # The registers live in the committed tree: the counter reads a register at a named revision.
    header = "id\tfile\tanchor\texpected\tstale\treceipt\treceipt_rev\tcommit\n"
    write(root, "cells-clean.tsv", header + (
        "ROW-OK\tclaims.md\tBOUND-CLAIM\tcases=7\tcases=99\treceipts/r0.txt\t%s\t%s\n" % (c0, c1)))
    write(root, "cells-equal.tsv", header + (
        "ROW-EQ\tclaims.md\tBOUND-CLAIM\tcases=7\tcases=99\treceipts/r0.txt\t%s\t%s\n" % (c0, c0)))
    write(root, "cells-back.tsv", header + (
        "ROW-BACK\tclaims.md\tBOUND-CLAIM\tcases=7\tcases=99\treceipts/r0.txt\t%s\t%s\n" % (c1, c0)))
    c2 = commit(root, "c2: the bound claim cites c1 and the registers land")
    # A commit outside the audited history (a side branch), used by the non-ancestor case.
    sh(root, ["checkout", "-q", "-b", "side"])
    write(root, "side.txt", "side\n")
    side = commit(root, "side: not an ancestor of main")
    sh(root, ["checkout", "-q", "main"])
    return root, c0, c1, c2, side


def write_items(path, rows):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("id\tfile\tanchor\tmust\tmustnot\tevidence\n")
        for row in rows:
            handle.write("\t".join(row) + "\n")


def run_counter(counter, root, rev, items, forged, register, register_rev=None):
    cmd = ["python3", "-B", counter, "--root", root, "--rev", rev, "--items", items,
           "--register", register, "--min-cells", "1", "--min-commit-rows", "1"]
    if forged:
        cmd += ["--forged", forged]
    if register_rev:
        cmd += ["--register-rev", register_rev]
    return subprocess.run(cmd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, check=False)


def summary_field(stdout, name):
    for line in stdout.splitlines():
        if line.startswith("SUMMARY "):
            for token in line.split():
                if token.startswith(name + "="):
                    return int(token.split("=", 1)[1])
    return None


def run_cases(counter, base_counter, work, lane_root):
    scratch = tempfile.mkdtemp(prefix="souji-r40-c1.", dir=work)
    results = []
    try:
        root, c0, c1, c2, side = build_repo(scratch, lane_root)
        items = os.path.join(scratch, "items.tsv")
        forged = os.path.join(scratch, "forged.tsv")
        write_items(items, [("BOUND-1", "claims.md", "BOUND-CLAIM", "cases=7", "-",
                             "receipts/r0.txt@%s" % c1)])
        write_items(forged, [
            ("FORGE-TOKEN", "claims.md", "FORGED-CLAIM", "cases=7", "-",
             "receipts/r0.txt@%s" % c0),
            ("FORGE-UNRESOLVED", "claims.md", "FORGED-CLAIM", "cases=7", "-",
             "receipts/r0.txt@%s" % ("0" * 40)),
            ("FORGE-NONANCESTOR", "claims.md", "FORGED-CLAIM", "cases=7", "-",
             "receipts/r0.txt@%s" % side),
            ("FORGE-PATH-UNCITED", "claims.md", "FORGED-PATH-CLAIM", "cases=7", "-",
             "receipts/r0.txt@%s" % c1),
            ("FORGE-WRONG-VALUE", "claims.md", "FORGED-WRONG-VALUE", "cases=999", "-",
             "receipts/r0.txt@%s" % c1),
        ])
        clean_register = "cells-clean.tsv"
        equal_register = "cells-equal.tsv"
        back_register = "cells-back.tsv"

        clean = run_counter(counter, root, c2, items, forged, clean_register)
        out = clean.stdout + clean.stderr

        results.append(("bound-item-closed",
                        "ITEM BOUND-1 CLOSED" in out and "ITEM BOUND-1 OPEN" not in out,
                        "rc=%d out=%r" % (clean.returncode, out.replace("\n", " ")[:300])))

        def forged_open(tag):
            for line in clean.stdout.splitlines():
                if line.startswith("FORGED %s " % tag):
                    return " OPEN " in line
            return False

        results.append(("forged-token-only-open", forged_open("FORGE-TOKEN"),
                        "out=%r" % clean.stdout.replace("\n", " ")[:300]))
        results.append(("forged-unresolved-rev-open", forged_open("FORGE-UNRESOLVED"),
                        "out=%r" % clean.stdout.replace("\n", " ")[:300]))
        results.append(("forged-non-ancestor-open", forged_open("FORGE-NONANCESTOR"),
                        "out=%r" % clean.stdout.replace("\n", " ")[:300]))
        results.append(("forged-path-uncited-open", forged_open("FORGE-PATH-UNCITED"),
                        "the revision is cited but the evidence path is absent from the line; out=%r" %
                        clean.stdout.replace("\n", " ")[:300]))
        results.append(("forged-wrong-value-open", forged_open("FORGE-WRONG-VALUE"),
                        "the evidence path does not carry cases=999; out=%r" %
                        clean.stdout.replace("\n", " ")[:300]))

        empty_forged = run_counter(counter, root, c2, items, None, clean_register)
        empty_count = summary_field(empty_forged.stdout, "forged")
        results.append(("empty-forged-control-rejected",
                        empty_forged.returncode == 1 and empty_count == 0,
                        "rc=%d forged=%r" % (empty_forged.returncode, empty_count)))
        violations = summary_field(clean.stdout, "register_violations")
        mismatches = summary_field(clean.stdout, "register_mismatches")
        results.append(("register-clean-accepted",
                        clean.returncode == 0 and violations == 0 and mismatches == 0,
                        "rc=%d violations=%r mismatches=%r" % (clean.returncode, violations, mismatches)))

        equal = run_counter(counter, root, c2, items, None, equal_register)
        eq_violations = summary_field(equal.stdout, "register_violations")
        results.append(("register-equal-rejected",
                        equal.returncode == 1 and (eq_violations or 0) >= 1,
                        "rc=%d violations=%r out=%r" % (
                            equal.returncode, eq_violations, equal.stdout.replace("\n", " ")[:300])))

        back = run_counter(counter, root, c2, items, None, back_register)
        bk_violations = summary_field(back.stdout, "register_violations")
        results.append(("register-backwards-rejected",
                        back.returncode == 1 and (bk_violations or 0) >= 1,
                        "rc=%d violations=%r out=%r" % (
                            back.returncode, bk_violations, back.stdout.replace("\n", " ")[:300])))

        # The do-nothing control: the r39 counter closes the forged token-only line.
        base_items = os.path.join(scratch, "items-base.tsv")
        with open(base_items, "w", encoding="utf-8") as handle:
            handle.write("id\tfile\tanchor\tmust\tmustnot\n")
            handle.write("FORGE-TOKEN\tclaims.md\tFORGED-CLAIM\tcases=7\t-\n")
        base = subprocess.run(
            ["python3", "-B", base_counter, "--root", root, "--rev", c2,
             "--items", base_items, "--register", clean_register,
             "--min-cells", "1", "--min-commit-distinct", "0"],
            env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        base_out = base.stdout + base.stderr
        results.append(("r39-control-closes-forged", "ITEM FORGE-TOKEN CLOSED" in base_out,
                        "rc=%d out=%r" % (base.returncode, base_out.replace("\n", " ")[:300])))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return results


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--counter")
    ap.add_argument("--base-counter")
    ap.add_argument("--work")
    args = ap.parse_args(argv)
    lane_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    counter = args.counter or os.path.join(lane_root, "census", "round-40", "c1-counter.py")
    base_counter = args.base_counter or os.path.join(lane_root, "census", "round-39", "c1-counter.py")
    work = args.work or os.environ.get("TMPDIR") or "/var/tmp"
    if not os.path.isfile(counter) or not os.path.isfile(base_counter):
        sys.stderr.write("usage: unreadable counter %s / %s\n" % (counter, base_counter))
        return 2
    if not os.path.isdir(work):
        sys.stderr.write("usage: --work must name an existing directory (%s)\n" % work)
        return 2
    results = run_cases(counter, base_counter, work, lane_root)
    for name, ok, detail in results:
        print("case-%s=%s%s" % (name, "PASS" if ok else "FAIL", "" if ok else " " + detail))
    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    print("SUMMARY cases=%d pass=%d fail=%d" % (len(results), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
