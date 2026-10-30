#!/usr/bin/env python3
"""r44-drift-symlink-refusal.py — the r44 leaf-symlink refusal battery.

The r44 cutover contract: `tools/souji-worktree-drift.py --json OUT` refuses
(rc 2, `REFUSAL JSON-TARGET-SYMLINK`) when OUT's final path component is a
symlink — existing target, dangling target, or directory target alike — instead
of resolving and writing through it (r43 M43-2 contract conflict, N10). Parent
components still resolve (r37 A2), so a `--json` reached through a symlinked
parent directory keeps working, and a regular leaf keeps being written.

Cases (each builds its own synthetic fleet under `--work`):
  dangling-symlink-refused   leaf symlink naming a nonexistent target -> rc 2,
                             refusal token, no file created anywhere
  outside-symlink-refused    leaf symlink naming an existing outside regular
                             file -> rc 2, refusal token, victim bytes unchanged
  subdir-symlink-refused     leaf symlink below a subdirectory -> rc 2, token
  symlink-dir-refused        leaf symlink naming a directory -> rc 2, refusal
                             token (the leaf-link check precedes NOT-REGULAR)
  regular-json-written       a plain regular leaf outside every measured tree
                             is still written and parses as JSON (positive)
  parent-symlink-ok          `--json` reached through a symlinked parent
                             directory, regular leaf -> written at the resolved
                             parent (positive; parents still resolve)

CLI:
  python3 -B tests/fixtures/r44-drift-symlink-refusal.py --tool PATH --work DIR

Exit: 0 every case passed, 1 otherwise, 2 usage.
"""
import argparse
import json
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
TOKEN = "JSON-TARGET-SYMLINK"


def sh(cmd):
    return subprocess.run(cmd, env=ENV, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, check=False)


def write(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def fleet(scratch, name):
    root = os.path.join(scratch, name)
    os.makedirs(root)
    path = os.path.join(root, "fleet")
    repo = os.path.join(path, "alpha")
    os.makedirs(repo)
    sh(["git", "init", "-q", "-b", "main", repo])
    write(os.path.join(repo, "file.txt"), "base\n")
    sh(["git", "-C", repo, "add", "file.txt"])
    sh(["git", "-C", repo, "commit", "-qm", "base"])
    record = os.path.join(root, "record.tsv")
    write(record, "REPO\talpha\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n")
    return root, path, record


def invoke(tool, path, rec, extra):
    start = time.time()
    try:
        proc = subprocess.run(
            ["python3", "-B", tool, "--root", path, "--record", rec, "--timeout", "30"] + extra,
            env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            check=False, timeout=BOUND)
        return proc.returncode, proc.stdout + proc.stderr, time.time() - start, False
    except subprocess.TimeoutExpired:
        return None, "", time.time() - start, True


def has_token(text, token):
    start = 0
    while True:
        idx = text.find(token, start)
        if idx < 0:
            return False
        before = text[idx - 1] if idx > 0 else " "
        after = text[idx + len(token)] if idx + len(token) < len(text) else " "
        if not before.isalnum() and after not in "-_" and not after.isalnum():
            return True
        start = idx + 1


def check(name, ok, detail, results):
    results.append((name, bool(ok), detail))


def run_cases(tool, work):
    scratch = tempfile.mkdtemp(prefix="souji-r44-symlink.", dir=work)
    results = []
    try:
        # dangling-symlink-refused
        root, path, rec = fleet(scratch, "dangling")
        target = os.path.join(scratch, "dangling-link")
        os.symlink(os.path.join(scratch, "never-created.json"), target)
        rc, out, elapsed, hung = invoke(tool, path, rec, ["--json", target])
        check("dangling-symlink-refused",
              (not hung) and rc == 2 and has_token(out, TOKEN)
              and not os.path.exists(os.path.join(scratch, "never-created.json")),
              "rc=%r created=%s out=%r" % (rc, os.path.exists(os.path.join(scratch, "never-created.json")),
                                           out.splitlines()[:2]), results)

        # outside-symlink-refused
        root, path, rec = fleet(scratch, "outside")
        victim = os.path.join(scratch, "victim.json")
        write(victim, "keep\n")
        target = os.path.join(scratch, "outside-link")
        os.symlink(victim, target)
        rc, out, elapsed, hung = invoke(tool, path, rec, ["--json", target])
        check("outside-symlink-refused",
              (not hung) and rc == 2 and has_token(out, TOKEN)
              and open(victim, encoding="utf-8").read() == "keep\n",
              "rc=%r victim=%r" % (rc, open(victim, encoding="utf-8").read()[:20]), results)

        # subdir-symlink-refused
        root, path, rec = fleet(scratch, "subdir")
        os.makedirs(os.path.join(scratch, "sub"))
        target = os.path.join(scratch, "sub", "sub-link")
        os.symlink(os.path.join(scratch, "sub", "out.json"), target)
        rc, out, elapsed, hung = invoke(tool, path, rec, ["--json", target])
        check("subdir-symlink-refused",
              (not hung) and rc == 2 and has_token(out, TOKEN),
              "rc=%r out=%r" % (rc, out.splitlines()[:2]), results)

        # symlink-dir-refused
        root, path, rec = fleet(scratch, "dirtarget")
        dest = os.path.join(scratch, "a-directory")
        os.makedirs(dest)
        target = os.path.join(scratch, "dir-link")
        os.symlink(dest, target)
        rc, out, elapsed, hung = invoke(tool, path, rec, ["--json", target])
        check("symlink-dir-refused",
              (not hung) and rc == 2 and has_token(out, TOKEN),
              "rc=%r out=%r" % (rc, out.splitlines()[:2]), results)

        # regular-json-written (positive)
        root, path, rec = fleet(scratch, "regular")
        target = os.path.join(scratch, "regular-out", "out.json")
        os.makedirs(os.path.dirname(target))
        rc, out, elapsed, hung = invoke(tool, path, rec, ["--json", target])
        ok = (not hung) and rc in (0, 1) and os.path.isfile(target)
        if ok:
            try:
                with open(target, encoding="utf-8") as fh:
                    json.load(fh)
            except (ValueError, OSError):
                ok = False
        check("regular-json-written", ok,
              "rc=%r written=%s" % (rc, os.path.isfile(target)), results)

        # parent-symlink-ok (positive; parents still resolve)
        root, path, rec = fleet(scratch, "parent")
        realdir = os.path.join(scratch, "realdir")
        os.makedirs(realdir)
        linkdir = os.path.join(scratch, "linkdir")
        os.symlink(realdir, linkdir)
        target = os.path.join(linkdir, "out.json")
        rc, out, elapsed, hung = invoke(tool, path, rec, ["--json", target])
        check("parent-symlink-ok",
              (not hung) and rc in (0, 1) and os.path.isfile(os.path.join(realdir, "out.json")),
              "rc=%r written=%s" % (rc, os.path.isfile(os.path.join(realdir, "out.json"))), results)

        # Parent traversal failures retain the structured output-refusal map.
        for kind in ("file", "loop"):
            root, path, rec = fleet(scratch, "bad-parent-" + kind)
            parent = os.path.join(root, "bad")
            if kind == "file":
                write(parent, "keep\n")
            else:
                os.symlink(parent, parent)
            rc, out, elapsed, hung = invoke(
                tool, path, rec, ["--json", os.path.join(parent, "out.json")])
            preserved = (os.path.islink(parent) if kind == "loop"
                         else open(parent, encoding="utf-8").read() == "keep\n")
            check("parent-" + kind + "-refused",
                  not hung and rc == 2 and has_token(out, "JSON-UNWRITABLE")
                  and "Traceback" not in out and preserved,
                  "rc=%r out=%r" % (rc, out.splitlines()[:2]), results)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return results


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args(argv)
    if not os.path.isdir(args.work):
        sys.stderr.write("usage: --work must name an existing directory\n")
        return 2
    results = run_cases(args.tool, args.work)
    for name, ok, detail in results:
        print("case-%s=%s%s" % (name, "PASS" if ok else "FAIL", "" if ok else " " + detail))
    passed = sum(1 for _, ok, _ in results if ok)
    print("SUMMARY cases=%d pass=%d fail=%d" % (len(results), passed, len(results) - passed))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
