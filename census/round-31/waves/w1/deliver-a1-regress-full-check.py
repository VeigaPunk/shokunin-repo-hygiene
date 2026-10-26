#!/usr/bin/env python3
"""A1 receipt: regenerate the REGRESS-FULL leg of census/round-30/c2-counter-v2.py.

Routed defect 3 of the round-30 verifier spot-check: c2-counter-v2.py:69 strips the
free-text tail of a selftest CASE line with `re.sub(r"\\terr=.*$", ...)`, but the gate
emits `detail = "exit=... ids=... paths=... fleet=... err=..."` (tools/souji-landing-gate.py:1423)
and prints it as `CASE\\t<status>\\t<name>\\t<detail>` (:1437), so `err=` follows a SPACE,
never a tab.  The strip therefore never fires, and a base/rev pair whose only textual
difference is the reworded no-reports error message can never compare equal.

This script is standalone (the round-30 file is not edited).  For each of the two
programs the v2 leg compares it runs both clones (BASE and REV, private `git clone
--no-local`, origin removed) and reports:
  A1-BROKEN  the v2 regex verbatim, `\\terr=.*$`
  A1-FIXED   the same strip normalized on the EMITTED separator, `[ \\t]err=.*$`
so the difference between the two prevents any ambiguity about the cause.

Usage:
  python3 -B deliver-a1-regress-full-check.py --root <lane> --rev <full40> --base <full40> \
      --scratch /fast/scratch/hyaku/souji-r31/A1Regex

Exit 0 when both variants evaluated; 2 could-not-evaluate.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile

FULL = re.compile(r"[0-9a-f]{40}")
ID = ["-c", "user.name=a1receipt", "-c", "user.email=a1@localhost", "-c", "core.hooksPath=/dev/null"]
PROGRAMS = (["tools/souji-landing-gate.py", "--selftest"],
            ["tests/fixtures/r16-landing-gate.py"])


def cne(msg):
    print("COULD-NOT-EVALUATE " + msg)
    sys.exit(2)


def sh(argv, **kw):
    return subprocess.run(argv, capture_output=True, **kw)


def clone(root, rev, dest):
    for argv in (["git", "clone", "-q", "--no-local", "--no-checkout", root, dest],
                 ["git", "-C", dest, "remote", "remove", "origin"],
                 ["git", "-C", dest, *ID, "checkout", "-qf", "--detach", rev]):
        if sh(argv).returncode:
            cne("clone/checkout failed: " + " ".join(argv[:5]))
    if sh(["git", "-C", dest, "rev-parse", "--show-toplevel"], text=True).stdout.strip() != dest:
        cne("clone toplevel mismatch: " + dest)


def run(argv, cwd, tmp, timeout=900):
    try:
        p = sh(argv, cwd=cwd, env=dict(os.environ, TMPDIR=tmp), timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"


def norm(out, scratch):
    out = out.replace(scratch, "<TMP>")
    out = re.sub(r"(?:/var)?/tmp/[^\s'\"`:,)]+", "<TMP>", out)
    out = re.sub(r"/fast/scratch/[^\s'\"`:,)]+", "<TMP>", out)
    out = re.sub(r"\b[0-9a-f]{12,}\b", "<HEX>", out)
    return out


def strip_broken(out):
    """census/round-30/c2-counter-v2.py:69, verbatim."""
    return "\n".join(re.sub(r"\terr=.*$", "", l) if l.startswith("CASE\t") else l
                     for l in out.splitlines())


def strip_fixed(out):
    """Same intent, normalized on the separator the gate actually emits."""
    return "\n".join(re.sub(r"[ \t]err=.*$", "", l) if l.startswith("CASE\t") else l
                     for l in out.splitlines())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--scratch", default="/fast/scratch/hyaku/souji-r31/A1Regex")
    a = ap.parse_args()
    for v in (a.rev, a.base):
        if not FULL.fullmatch(v):
            cne("revisions must be full 40-hex")
    root = os.path.abspath(a.root)
    os.makedirs(a.scratch, exist_ok=True)
    w = tempfile.mkdtemp(prefix="a1regress.", dir=a.scratch)
    try:
        tr, tb, tmp = os.path.join(w, "rev"), os.path.join(w, "base"), os.path.join(w, "tmp")
        os.makedirs(tmp)
        clone(root, a.rev, tr)
        clone(root, a.base, tb)
        print("A1-PAIR rev=%s base=%s workdir=%s" % (a.rev, a.base, w))
        verdict = {}
        for argv in PROGRAMS:
            r1 = run([sys.executable, "-B", *argv], tb, tmp)
            r2 = run([sys.executable, "-B", *argv], tr, tmp)
            n1, n2 = norm(r1[1], w), norm(r2[1], w)
            b1, b2 = (r1[0], strip_broken(n1)), (r2[0], strip_broken(n2))
            f1, f2 = (r1[0], strip_fixed(n1)), (r2[0], strip_fixed(n2))
            same_b, same_f = b1 == b2, f1 == f2
            print("A1-BROKEN %s rc=%d/%d lines=%d/%d %s" % (
                argv[0], r1[0], r2[0], len(b1[1].splitlines()), len(b2[1].splitlines()),
                "same" if same_b else "differs"))
            print("A1-FIXED  %s rc=%d/%d lines=%d/%d %s" % (
                argv[0], r1[0], r2[0], len(f1[1].splitlines()), len(f2[1].splitlines()),
                "same" if same_f else "differs"))
            if not same_b:
                def ndiff(a, b):
                    x, y = a.splitlines(), b.splitlines()
                    return (sum(1 for p, q in zip(x, y) if p != q) + abs(len(x) - len(y)))
                l1, l2 = b1[1].splitlines(), b2[1].splitlines()
                diff = [(i, x, y) for i, (x, y) in enumerate(zip(l1, l2)) if x != y]
                print("A1-DIFF-COUNT %s broken=%d fixed=%d" % (
                    argv[0], ndiff(b1[1], b2[1]), ndiff(f1[1], f2[1])))
                if len(l1) != len(l2):
                    print("A1-DIFF-LINECOUNT %s base=%d rev=%d" % (argv[0], len(l1), len(l2)))
                for i, x, y in diff[:4]:
                    print("A1-DIFF-LINE %s #%d base=%r rev=%r" % (argv[0], i + 1, x, y))
            verdict[argv[0]] = (same_b, same_f)
        allf = all(v[1] for v in verdict.values())
        print("SUMMARY-A1 pair=%s..%s broken=%s fixed=%s" % (
            a.rev, a.base,
            "same" if all(v[0] for v in verdict.values()) else "differs",
            "same" if allf else "differs"))
        return 0
    finally:
        shutil.rmtree(w, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
