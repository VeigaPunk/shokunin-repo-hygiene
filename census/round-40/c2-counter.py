#!/usr/bin/env python3
"""census/round-40/c2-counter.py — r40 C2 tool-contract counter (joined docstring classes).

The r39 C2 L4 leg derived the refusal-class map of `tools/souji-worktree-drift.py` with ONE docstring
line per class: `docstring_classes()` kept the first physical line of every class entry. The tool
documents `RECORD-OUTSIDE-ROOT` over two lines, so the trigger that names its condition (`--root`)
lives on a continuation line the r39 analyser could not see — the leg could only ever check the
classes whose trigger happened to sit on the first line.

This counter replaces that read with the joined one (`census/round-40/docstring-classes.py`, PEP 257's
multi-line docstring shape, S252) and keeps every other r39 leg:

  L1   an unresolvable `--rev` for `tools/souji-citation-reconcile.py` is exit 2 (REV-UNRESOLVED)
  L2   a `--rev` naming a blob is the same class
  L3   harm: an unresolvable `--register-rev` stays exit 2 at both revisions
  L4   every observed class/trigger pair is present in the JOINED class entry, and the one-line
       analyser misses at least one of them (the join is load-bearing, not cosmetic)
  L4b  a synthetic wrapped-trigger probe is found by the joined analyser and missed by the one-line
       analyser
  L5   the new fixture `tests/fixtures/r40-docstring-joined.py` passes on the audited bytes and fails
       against the one-line reading
  L6   the consumer fixtures stay green and none loses a passing case against the base bytes

The class/trigger pairs are FROZEN here and are re-derived at run time: each trigger must actually be
raised by the audited tool, so a pair that the tool no longer raises fails the leg instead of passing
vacuously.

CLI:
  python3 -B census/round-40/c2-counter.py --root LANE --rev REV --base-rev REV [--scratch DIR]

Exit: 0 `SUMMARY legs=7 pass=7 fail=0 harm=0`; 1 any failing leg or consumer regression; 2 usage or
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import docstring_classes as dc  # noqa: E402  (the joined analyser, same directory)

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
FIXTURE = "tests/fixtures/r40-docstring-joined.py"
CONSUMERS = (
    ("r38-drift-record", "tests/fixtures/r38-drift-record.py", DRIFT),
    ("r36-worktree-drift", "tests/fixtures/r36-worktree-drift.py", DRIFT),
    ("r38-drift-envelope", "tests/fixtures/r38-drift-write-envelope.py", DRIFT),
    ("r39-drift-record-rules", "tests/fixtures/r39-drift-record-rules.py", DRIFT),
    ("r37-citation", "tests/fixtures/r37-citation-reconcile.py", CITATION),
    ("r38-citation-commit", "tests/fixtures/r38-citation-commit.py", CITATION),
    ("r39-citation-rev", "tests/fixtures/r39-citation-rev.py", CITATION),
)

# The frozen class/trigger pairs: (refusal class, the token that names the condition that raises it).
# The trigger must be documented by the tool AND actually raised by the audited bytes.
FROZEN_PAIRS = (
    ("RECORD-MALFORMED", "ENOENT"),
    ("RECORD-MISSING", "EACCES"),
    ("RECORD-OUTSIDE-ROOT", "--root"),
)

SYNTHETIC_DOC = '''"""synthetic probe.

  SYNTH-CLASS              the first physical line of this entry
                           SYNTH-TRIGGER only on the continuation line
"""
'''


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


def run_citation(tool, root, rev, scratch, register_rev=ZERO):
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


def observed_pairs(tool, scratch):
    """Re-derive, at run time, the (class, trigger) pairs the audited tool actually raises."""
    observed = []
    missing = os.path.join(scratch, "absent.tsv")
    probe = os.path.join(scratch, "record-probe.tsv")
    with open(probe, "w", encoding="utf-8") as handle:
        handle.write("# only a comment\n")
    missing_class = classify(run_drift(tool, os.path.dirname(probe), missing))
    os.chmod(probe, 0)
    locked_class = classify(run_drift(tool, os.path.dirname(probe), probe))
    os.chmod(probe, stat.S_IRUSR | stat.S_IWUSR)
    outside = os.path.join(scratch, "outside.tsv")
    with open(outside, "w", encoding="utf-8") as handle:
        handle.write("REPO\t../escape\tregs=1\tprunable=0\n")
    outside_class = classify(run_drift(tool, os.path.dirname(outside), outside))
    for cls, trigger in FROZEN_PAIRS:
        raised = {
            "RECORD-MALFORMED": missing_class,
            "RECORD-MISSING": locked_class,
            "RECORD-OUTSIDE-ROOT": outside_class,
        }[cls]
        observed.append((cls, trigger, raised))
    return observed


def run_fixture(fixture, work, extra=None):
    cmd = ["python3", "-B", fixture] + list(extra or []) + ["--work", work]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                          check=False, env=child_env(work))
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
    try:
        scratch = tempfile.mkdtemp(
            prefix="souji-r40-c2.", dir=args.scratch or os.environ.get("TMPDIR") or "/var/tmp")
    except OSError as exc:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: scratch root unavailable: %s\n" % exc)
        return 2
    legs = []
    harm = 0

    def leg(name, ok, detail):
        legs.append((name, ok, detail))
        print("LEG %s %s %s" % (name, "PASS" if ok else "FAIL", detail))

    try:
        new_cit = extract(root, args.rev, CITATION, scratch, "cit-new.py")
        old_cit = extract(root, args.base_rev, CITATION, scratch, "cit-old.py")
        new_drift = extract(root, args.rev, DRIFT, scratch, "drift-new.py")
        old_drift = extract(root, args.base_rev, DRIFT, scratch, "drift-old.py")

        # L1 — an unresolvable --rev is a could-not-evaluate, not a finding.
        new_p = run_citation(new_cit, root, ZERO, scratch, register_rev=args.rev)
        old_p = run_citation(old_cit, root, ZERO, scratch, register_rev=args.base_rev)
        new_ok = new_p.returncode == 2 and "REV-UNRESOLVED" in new_p.stderr
        old_has = old_p.returncode == 2 and "REV-UNRESOLVED" in old_p.stderr
        leg("L1", new_ok and not old_has,
            "new rc=%d class=%s old rc=%d class=%s" % (
                new_p.returncode, "REV-UNRESOLVED" in new_p.stderr,
                old_p.returncode, "REV-UNRESOLVED" in old_p.stderr))

        # L2 — a blob id as --rev is the same class.
        blob = git(root, ["rev-parse", "%s:corpus/SOURCES.md" % args.base_rev]).stdout.decode().strip()
        new_p = run_citation(new_cit, root, blob, scratch, register_rev=args.rev)
        old_p = run_citation(old_cit, root, blob, scratch, register_rev=args.base_rev)
        new_ok = new_p.returncode == 2 and "REV-UNRESOLVED" in new_p.stderr
        old_has = old_p.returncode == 2 and "REV-UNRESOLVED" in old_p.stderr
        leg("L2", bool(blob) and new_ok and not old_has,
            "new rc=%d class=%s old rc=%d class=%s" % (
                new_p.returncode, "REV-UNRESOLVED" in new_p.stderr,
                old_p.returncode, "REV-UNRESOLVED" in old_p.stderr))

        # L3 — harm leg: an unresolvable --register-rev stays exit 2.
        new_p = run_citation(new_cit, root, args.rev, scratch, register_rev=ZERO)
        old_p = run_citation(old_cit, root, args.base_rev, scratch, register_rev=ZERO)
        ok = new_p.returncode == 2 and old_p.returncode == 2
        if not ok:
            harm += 1
        leg("L3", ok, "new rc=%d old rc=%d" % (new_p.returncode, old_p.returncode))

        # L4 — the joined class map against the frozen class/trigger pairs.
        with open(new_drift, encoding="utf-8") as handle:
            new_src = handle.read()
        with open(old_drift, encoding="utf-8") as handle:
            old_src = handle.read()
        new_joined = dc.classes_from_source(new_src)
        new_first = dc.first_line_entries(dc.docstring_of(new_src))
        old_joined = dc.classes_from_source(old_src)
        old_first = dc.first_line_entries(dc.docstring_of(old_src))
        pairs = observed_pairs(new_drift, scratch)
        missing_new = []
        missing_old = []
        missed_by_first = []
        for cls, trigger, raised in pairs:
            if raised != cls:
                missing_new.append("%s-not-raised(%s)" % (cls, raised))
                continue
            if cls not in new_joined or trigger not in new_joined[cls]:
                missing_new.append("%s-missing-trigger(%s)" % (cls, trigger))
            if cls not in new_first or trigger not in new_first[cls]:
                missed_by_first.append("%s(%s)" % (cls, trigger))
            if cls not in old_joined or trigger not in old_joined[cls]:
                missing_old.append("%s-missing-trigger(%s)" % (cls, trigger))
        ok = not missing_new and not missing_old and missed_by_first
        leg("L4", bool(ok),
            "pairs=%d missing_new=%s missing_old=%s missed_by_one_line=%s" % (
                len(pairs), missing_new, missing_old, missed_by_first))

        # L4b — the synthetic wrapped-trigger probe.
        synth_joined = dc.class_entries(dc.docstring_of(SYNTHETIC_DOC))
        synth_first = dc.first_line_entries(dc.docstring_of(SYNTHETIC_DOC))
        joined_ok = "SYNTH-CLASS" in synth_joined and "SYNTH-TRIGGER" in synth_joined.get("SYNTH-CLASS", "")
        first_ok = "SYNTH-CLASS" in synth_first and "SYNTH-TRIGGER" in synth_first.get("SYNTH-CLASS", "")
        leg("L4b", joined_ok and not first_ok,
            "joined=%s one_line=%s" % (joined_ok, first_ok))

        # L5 — the new fixture discriminates the joined reading from the one-line reading.
        fix_src = git_show(root, args.rev, FIXTURE)
        if fix_src is None:
            leg("L5", False, "fixture %s absent at %s" % (FIXTURE, args.rev))
        else:
            fix = os.path.join(scratch, "r40-docstring-joined.py")
            with open(fix, "w", encoding="utf-8") as handle:
                handle.write(fix_src)
            new_f = run_fixture(fix, scratch)
            old_f = run_fixture(fix, scratch, extra=["--one-line"])
            ok = (new_f is not None and new_f[2] == 0 and new_f[3] == 0
                  and old_f is not None and old_f[2] >= 1)
            leg("L5", ok, "new=%r old(one-line)=%r" % (new_f, old_f))

        # L6 — consumers green, none harmed against base.
        consumer_ok = True
        details = []
        for name, path, tool_key in CONSUMERS:
            src = git_show(root, args.rev, path)
            if src is None:
                consumer_ok = False
                details.append("%s=ABSENT" % name)
                continue
            fixp = os.path.join(scratch, name + ".py")
            with open(fixp, "w", encoding="utf-8") as handle:
                handle.write(src)
            new_tool = new_drift if tool_key == DRIFT else new_cit
            old_tool = old_drift if tool_key == DRIFT else old_cit
            new_r = run_fixture(fixp, scratch, extra=["--tool", new_tool])
            old_r = run_fixture(fixp, scratch, extra=["--tool", old_tool])
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
        shutil.rmtree(scratch, ignore_errors=True)
    passed = sum(1 for _, ok, _ in legs if ok)
    failed = len(legs) - passed
    tool_sha = hashlib.sha256(git_show(root, args.rev, DRIFT).encode()).hexdigest()[:12]
    fixture_sha = hashlib.sha256((git_show(root, args.rev, FIXTURE) or "").encode()).hexdigest()[:12]
    print("SUMMARY legs=%d pass=%d fail=%d harm=%d drift_sha=%s fixture_sha=%s" % (
        len(legs), passed, failed, harm, tool_sha, fixture_sha))
    return 0 if passed == len(legs) and harm == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
