#!/usr/bin/env python3
"""census/round-39/c2-counter.py — r39 C2 tool-contract counter (citation rev resolution, drift
record classes).

Two documented runnable contracts disagree with the base bytes (r38 spot-check routed defects
R11 and R10):

  L1  an unresolvable `--rev` for `tools/souji-citation-reconcile.py`: base collapses it to "not an
      ancestor" and exits 1 with findings; the SKILL registry row promises a could-not-evaluate
      exit 2.
  L2  a `--rev` naming a non-commit object (a blob) is the same class.
  L3  `--register-rev` unresolvable stays exit 2 (harm leg, both revisions).
  L4  `tools/souji-worktree-drift.py` documents RECORD-MISSING as "the record path cannot be read"
      while a missing path raises RECORD-MALFORMED and an EACCES path raises RECORD-MISSING. The
      leg derives the observed class for each trigger and requires the docstring line that starts
      with that class to name its trigger (missing / EACCES).
  L5  `tests/fixtures/r39-citation-rev.py` (8 cases) passes on the audited bytes and fails at least
      two cases on the base bytes.
  L6  five consumer fixtures stay green and none loses a passing case against the base bytes.

Both tool revisions are extracted from committed bytes (`git show <rev>:tools/...`) into a private
scratch directory, so the counter never reads the worktree's uncommitted edits.

CLI:
  python3 -B census/round-39/c2-counter.py --root LANE --rev REV --base-rev REV [--scratch DIR]

Exit: 0 `SUMMARY legs=6 pass=6 fail=0 harm=0`; 1 any failing leg or consumer regression; 2 usage or
could-not-evaluate input.
"""
import argparse
import ast
import hashlib
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile

REV = re.compile(r"^[0-9a-f]{40}$")
ZERO = "0" * 40
GIT_ENV = {
    "LC_ALL": "C",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_ATTR_NOSYSTEM": "1",
    "GIT_OPTIONAL_LOCKS": "0",
    "GIT_TERMINAL_PROMPT": "0",
}
CITATION = "tools/souji-citation-reconcile.py"
DRIFT = "tools/souji-worktree-drift.py"
CONSUMERS = (
    ("r38-drift-record", "tests/fixtures/r38-drift-record.py", DRIFT, "--tool"),
    ("r36-worktree-drift", "tests/fixtures/r36-worktree-drift.py", DRIFT, "--tool"),
    ("r38-drift-envelope", "tests/fixtures/r38-drift-write-envelope.py", DRIFT, "--tool"),
    ("r37-citation", "tests/fixtures/r37-citation-reconcile.py", CITATION, "--tool"),
    ("r38-citation-commit", "tests/fixtures/r38-citation-commit.py", CITATION, "--tool"),
)


def lane_root_of(args):
    """Instrument (fixture) bytes come from the working tree; audited tool bytes come from --rev."""
    return os.path.abspath(args.root)


def child_env(scratch=None):
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")}
    env.update(GIT_ENV)
    if scratch:
        env["TMPDIR"] = scratch
    return env


def git(root, args):
    return subprocess.run(
        ["git", "-C", root] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=child_env(),
        check=False,
    )


def git_show(root, rev, path):
    proc = git(root, ["show", "%s:%s" % (rev, path)])
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8", "replace")


def resolves(root, rev):
    return git(root, ["cat-file", "-e", rev + "^{commit}"]).returncode == 0


def extract(root, rev, path, scratch, name):
    src = git_show(root, rev, path)
    if src is None:
        raise ValueError("%s absent at %s" % (path, rev))
    dest = os.path.join(scratch, name)
    with open(dest, "w", encoding="utf-8") as handle:
        handle.write(src)
    os.chmod(dest, 0o755)
    return dest


def run_citation(tool, root, rev, scratch, register_rev="0" * 40):
    return subprocess.run(
        ["python3", "-B", tool, "--root", root, "--rev", rev,
         "--register", "census/round-38/cells.tsv", "--register-rev", register_rev],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
        env=child_env(scratch),
    )


def run_drift(tool, root, record):
    return subprocess.run(
        ["python3", "-B", tool, "--root", root, "--record", record, "--timeout", "20"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
        env=child_env(),
    )


def classify(proc):
    out = (proc.stdout + proc.stderr).replace("\n", " ")
    for cls in ("RECORD-MISSING", "RECORD-MALFORMED", "RECORD-EMPTY", "RECORD-OUTSIDE-ROOT"):
        if cls in out:
            return cls
    return "NO-CLASS"


def docstring_classes(tool):
    """Class token -> the first docstring line that starts with it (ast only, no source slicing)."""
    with open(tool, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    doc = ast.get_docstring(tree, clean=False) or ""
    out = {}
    for line in doc.split("\n"):
        stripped = line.strip()
        for cls in ("RECORD-MISSING", "RECORD-MALFORMED"):
            if stripped.startswith(cls) and cls not in out:
                out[cls] = stripped
    return out


def run_fixture(fixture, tool, scratch, work, extra=None):
    cmd = ["python3", "-B", fixture] + list(extra or ["--tool", tool]) + ["--work", work]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                          check=False, env=child_env(scratch))
    match = re.search(r"SUMMARY cases=(\d+) pass=(\d+) fail=(\d+)", proc.stdout)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2)), int(match.group(3)), proc.returncode


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--base-rev", required=True)
    ap.add_argument("--scratch")
    args = ap.parse_args(argv)
    root = args.root
    for flag, rev in (("--rev", args.rev), ("--base-rev", args.base_rev)):
        if not REV.match(rev) or not resolves(root, rev):
            sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s %s does not resolve\n" % (flag, rev))
            return 2
    tool_sha = hashlib.sha256((git_show(root, args.rev, CITATION) or "").encode()).hexdigest()[:12] + "/" + hashlib.sha256((git_show(root, args.rev, DRIFT) or "").encode()).hexdigest()[:12]
    fixture_sha = hashlib.sha256(open(os.path.join(os.path.abspath(root), "tests/fixtures/r39-citation-rev.py"), encoding="utf-8").read().encode()).hexdigest()[:12]
    base_scratch = tempfile.mkdtemp(
        prefix="souji-r39-c2.", dir=args.scratch or os.environ.get("TMPDIR") or "/var/tmp")
    legs = []
    harm = 0

    def leg(name, ok, detail):
        legs.append((name, ok, detail))
        print("LEG %s %s %s" % (name, "PASS" if ok else "FAIL", detail))

    try:
        new_cit = extract(root, args.rev, CITATION, base_scratch, "cit-new.py")
        old_cit = extract(root, args.base_rev, CITATION, base_scratch, "cit-old.py")
        new_drift = extract(root, args.rev, DRIFT, base_scratch, "drift-new.py")
        old_drift = extract(root, args.base_rev, DRIFT, base_scratch, "drift-old.py")

        # L1 — unresolvable --rev (R11).
        new_p = run_citation(new_cit, root, ZERO, base_scratch, register_rev=args.rev)
        old_p = run_citation(old_cit, root, ZERO, base_scratch, register_rev=args.base_rev)
        new_ok = new_p.returncode == 2 and "REV-UNRESOLVED" in new_p.stderr
        old_has = old_p.returncode == 2 and "REV-UNRESOLVED" in old_p.stderr
        leg("L1", new_ok and not old_has,
            "new rc=%d class=%s old rc=%d class=%s" % (
                new_p.returncode, "REV-UNRESOLVED" in new_p.stderr,
                old_p.returncode, "REV-UNRESOLVED" in old_p.stderr))

        # L2 — a blob id as --rev.
        blob = git(root, ["rev-parse", "%s:corpus/SOURCES.md" % args.base_rev]).stdout.decode().strip()
        new_p = run_citation(new_cit, root, blob, base_scratch, register_rev=args.rev)
        old_p = run_citation(old_cit, root, blob, base_scratch, register_rev=args.base_rev)
        new_ok = new_p.returncode == 2 and "REV-UNRESOLVED" in new_p.stderr
        old_has = old_p.returncode == 2 and "REV-UNRESOLVED" in old_p.stderr
        leg("L2", bool(blob) and new_ok and not old_has,
            "new rc=%d class=%s old rc=%d class=%s" % (
                new_p.returncode, "REV-UNRESOLVED" in new_p.stderr,
                old_p.returncode, "REV-UNRESOLVED" in old_p.stderr))

        # L3 — harm leg: an unresolvable --register-rev stays exit 2.
        new_p = run_citation(new_cit, root, args.rev, base_scratch, register_rev=ZERO)
        old_p = run_citation(old_cit, root, args.base_rev, base_scratch, register_rev=ZERO)
        ok = new_p.returncode == 2 and old_p.returncode == 2
        if not ok:
            harm += 1
        leg("L3", ok, "new rc=%d old rc=%d" % (new_p.returncode, old_p.returncode))

        # L4 — docstring -> condition mapping (R10).
        probe = os.path.join(base_scratch, "record-probe.tsv")
        with open(probe, "w", encoding="utf-8") as handle:
            handle.write("# only a comment\n")
        missing = classify(run_drift(new_drift, root, os.path.join(base_scratch, "absent.tsv")))
        os.chmod(probe, 0)
        locked = classify(run_drift(new_drift, root, probe))
        os.chmod(probe, stat.S_IRUSR | stat.S_IWUSR)
        old_classes = docstring_classes(old_drift)
        new_classes = docstring_classes(new_drift)
        detail = "missing=%s locked=%s" % (missing, locked)
        new_ok = (
            missing in new_classes and "missing" in new_classes.get(missing, "").lower()
            and locked in new_classes and "EACCES" in new_classes.get(locked, "")
        )
        old_ok = (
            missing in old_classes and "missing" in old_classes.get(missing, "").lower()
            and locked in old_classes and "EACCES" in old_classes.get(locked, "")
        )
        leg("L4", new_ok and not old_ok, detail + " new_maps=%s old_maps=%s" % (new_ok, old_ok))

        # L5 — the new fixture discriminates.
        fix_src = open(os.path.join(lane_root_of(args), "tests/fixtures/r39-citation-rev.py"), encoding="utf-8").read()
        fix = os.path.join(base_scratch, "r39-citation-rev.py")
        with open(fix, "w", encoding="utf-8") as handle:
            handle.write(fix_src)
        new_f = run_fixture(fix, new_cit, base_scratch, base_scratch)
        old_f = run_fixture(fix, old_cit, base_scratch, base_scratch)
        ok = (
            new_f is not None and new_f[0] == 8 and new_f[2] == 0 and new_f[3] == 0
            and old_f is not None and old_f[2] >= 2
        )
        leg("L5", ok, "new=%r old=%r" % (new_f, old_f))

        # L6 — consumers green, none harmed against base.
        consumer_ok = True
        details = []
        for name, path, tool_key, flag in CONSUMERS:
            src = open(os.path.join(lane_root_of(args), path), encoding="utf-8").read()
            fixp = os.path.join(base_scratch, name + ".py")
            with open(fixp, "w", encoding="utf-8") as handle:
                handle.write(src)
            new_tool = new_drift if tool_key == DRIFT else new_cit
            old_tool = old_drift if tool_key == DRIFT else old_cit
            new_r = run_fixture(fixp, new_tool, base_scratch, base_scratch, extra=[flag, new_tool])
            old_r = run_fixture(fixp, old_tool, base_scratch, base_scratch, extra=[flag, old_tool])
            if new_r is None or old_r is None:
                consumer_ok = False
                details.append("%s=NO-SUMMARY" % name)
                continue
            green = new_r[0] == new_r[1] and new_r[2] == 0
            if not green:
                consumer_ok = False
            if new_r[1] < old_r[1]:
                harm += 1
                consumer_ok = False
            details.append("%s=%d/%d(base %d/%d)" % (name, new_r[1], new_r[0], old_r[1], old_r[0]))
        leg("L6", consumer_ok, " ".join(details))
    except (ValueError, OSError) as exc:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\n" % exc)
        return 2
    finally:
        shutil.rmtree(base_scratch, ignore_errors=True)
    passed = sum(1 for _, ok, _ in legs if ok)
    failed = len(legs) - passed
    print("SUMMARY legs=%d pass=%d fail=%d harm=%d tool_sha=%s fixture_sha=%s" % (
        len(legs), passed, failed, harm, tool_sha, fixture_sha))
    return 0 if passed == len(legs) and harm == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
