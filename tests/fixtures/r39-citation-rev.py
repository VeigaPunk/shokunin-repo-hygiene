#!/usr/bin/env python3
"""r39-citation-rev.py — revision-resolution cases for tools/souji-citation-reconcile.py (r39 C2 L5).

r38 routed defect R11: the counter never resolved `--rev`. `git merge-base --is-ancestor` exits 1
for "not an ancestor" and other non-zero values for an error, but the tool collapsed every non-zero
into "not an ancestor", so a mistyped audited revision, a blob id or a tree id produced
`mismatches=N` and exit 1 (findings) instead of the could-not-evaluate exit 2 its SKILL registry
row promises.

Cases (a synthetic repository per run, one commit carrying the citation and its receipt):

  rev-unknown        a 40-hex revision that does not exist            -> rc 2, REV-UNRESOLVED
  rev-blob           a 40-hex blob id                                 -> rc 2, REV-UNRESOLVED
  rev-tree           a 40-hex tree id                                 -> rc 2, REV-UNRESOLVED
  rev-short          a short hex prefix                               -> rc 2, USAGE
  rev-symbolic       a tag-like name                                  -> rc 2, USAGE
  clean              the real commit                                  -> rc 0, mismatches=0
  register-rev-gone  an unresolvable --register-rev                    -> rc 2, "not at"
  register-absent    a --register absent at a resolvable revision      -> rc 2, "not at"

CLI:
  python3 -B tests/fixtures/r39-citation-rev.py [--tool PATH] [--work DIR]
Exit: 0 all eight cases match, 1 any mismatch, 2 usage.
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

CITE = "# led\nR39-ANCHOR cases=7 carried by `receipt.txt`\n"
RECEIPT = "note\nSUMMARY cases=7\n"
REGISTER = (
    "id\tfile\tanchor\texpected\tstale\treceipt\treceipt_rev\n"
    "K1\tdoc.md\tR39-ANCHOR\tcases=7\tcases=9\treceipt.txt\t%s\n"
)

ABSENT = "1" * 40


def sh(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, env=ENV, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, check=False)


def build(scratch):
    repo = os.path.join(scratch, "repo")
    os.makedirs(repo)
    sh(["git", "init", "-q", "-b", "main", repo])
    for name, body in (("doc.md", CITE), ("receipt.txt", RECEIPT)):
        with open(os.path.join(repo, name), "w", encoding="utf-8") as handle:
            handle.write(body)
    sh(["git", "-C", repo, "add", "doc.md", "receipt.txt"])
    sh(["git", "-C", repo, "commit", "-qm", "base"])
    rev = sh(["git", "-C", repo, "rev-parse", "HEAD"]).stdout.strip()
    tree = sh(["git", "-C", repo, "rev-parse", "HEAD^{tree}"]).stdout.strip()
    blob = sh(["git", "-C", repo, "rev-parse", "HEAD:doc.md"]).stdout.strip()
    register = os.path.join(scratch, "register.tsv")
    with open(register, "w", encoding="utf-8") as handle:
        handle.write(REGISTER % rev)
    return repo, rev, tree, blob, register


def case(tool, repo, register, name, argv, want_rc, want_tokens, results):
    proc = subprocess.run(["python3", "-B", tool, "--root", repo] + argv + ["--register", register],
                          env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                          check=False)
    out = proc.stdout + proc.stderr
    missing = [t for t in want_tokens if t not in out]
    ok = proc.returncode == want_rc and not missing
    results.append((name, ok, "rc=%d want=%d missing=%r out=%r" % (
        proc.returncode, want_rc, missing, out.replace("\n", " ")[:160])))


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--tool")
    ap.add_argument("--work")
    args = ap.parse_args(argv)
    lane_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    tool = args.tool or os.path.join(lane_root, "tools", "souji-citation-reconcile.py")
    work = args.work or os.environ.get("TMPDIR") or "/var/tmp"
    if not os.path.isfile(tool):
        sys.stderr.write("usage: unreadable tool %s\n" % tool)
        return 2
    if not os.path.isdir(work):
        sys.stderr.write("usage: --work must name an existing directory (%s)\n" % work)
        return 2
    scratch = tempfile.mkdtemp(prefix="souji-r39-cite-rev.", dir=work)
    results = []
    try:
        repo, rev, tree, blob, register = build(scratch)
        case(tool, repo, register, "rev-unknown", ["--rev", ABSENT], 2, ["REV-UNRESOLVED"], results)
        case(tool, repo, register, "rev-blob", ["--rev", blob], 2, ["REV-UNRESOLVED"], results)
        case(tool, repo, register, "rev-tree", ["--rev", tree], 2, ["REV-UNRESOLVED"], results)
        case(tool, repo, register, "rev-short", ["--rev", rev[:12]], 2, ["USAGE"], results)
        case(tool, repo, register, "rev-symbolic", ["--rev", "v1"], 2, ["USAGE"], results)
        case(tool, repo, register, "clean", ["--rev", rev], 0, ["mismatches=0"], results)
        case(tool, repo, register, "register-rev-gone",
             ["--rev", rev, "--register-rev", ABSENT], 2, ["not at"], results)
        case(tool, repo, register, "register-absent",
             ["--rev", rev, "--register-rev", rev, "--register", "no-such-register.tsv"], 2,
             ["not at"], results)
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
