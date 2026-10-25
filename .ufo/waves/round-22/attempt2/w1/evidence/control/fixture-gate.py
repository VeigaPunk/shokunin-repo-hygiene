#!/usr/bin/env python3
"""C1 kill-rule fixture gate (round 22, attempt 2).

Frozen by .ufo/waves/round-22/attempt2/preregistration.txt, C1 kill rule:

  "a control tool that prints `assertions=0 skipped=0 mismatches=0` without
   reading any byte must FAIL the same selftest the real tool passes: selftest
   fixtures are (1) all-good declaration -> 0 mismatches, (2) nonexistent path
   -> >=1, (3) dangling revision -> >=1, (4) wrong digest -> >=1, (5) path
   present at a different revision only -> >=1. Reported as
   `control=FALSE-GREEN-REJECTED`."

Usage:
  fixture-gate.py <candidate.py|binary> [--keep] [--timeout SECONDS] [--no-oracle]

stdout: exactly one line,
  control=<PASS|FALSE-GREEN-REJECTED> fixtures=<k>/<n>
stderr: per-fixture receipts, the harness calibration oracle result and any
        exit-code contract deviation.

The fixtures live in a throwaway git repository tree under $TMPDIR (never in a
lane repo). Each fixture is a single-fault declaration: the injected defect is
the only thing that can make the candidate's mismatch count leave zero, and
every good element of that fixture still resolves.

Fixture layout (one markdown table, one evidence cell per row):
  row 1  class A  backticked repo-relative path, present at --rev
  row 2  class B  bare 12-hex commit token in a cell naming `rev`, present
  row 3  class C  64-hex sha256 in the same cell as exactly one backticked path
  row 4  the single injected defect (absent in fixture 1)

Calibration of the harness itself: before scoring the candidate, the gate runs
the same five fixtures through a minimal in-repo oracle (written to the
throwaway tree) that implements frozen classes A/B/C directly with `git
cat-file`/`git show`. If the oracle does not score 5/5 the harness cannot
award PASS at all and the gate reports FALSE-GREEN-REJECTED, exit 2. This keeps
the gate falsifiable in both directions instead of only being able to say no.

No lane repo byte is written: only $TMPDIR and stderr/stdout.
"""

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

COUNTS_RE = re.compile(
    r"^assertions=(\d+) resolved=(\d+) skipped=(\d+) mismatches=(\d+)$")

FIXED_DATE = "2026-10-25T00:00:00 +0000"

HELPER_BODY = "#!/bin/sh\necho helper\n"
LATE_BODY = "#!/bin/sh\necho late\n"
GOOD_DIGEST = hashlib.sha256(HELPER_BODY.encode()).hexdigest()
# A well-formed 64-hex that is not the digest of any file in the fixtures.
WRONG_DIGEST = hashlib.sha256(b"not the helper bytes\n").hexdigest()
# 7 hex digits, no such commit can exist in a freshly initialised repo.
DANGLING_REV = "deadbee"


def build_env(home):
    env = {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "HOME": home,
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "GIT_AUTHOR_NAME": "c1-fixture",
        "GIT_AUTHOR_EMAIL": "c1-fixture@example.invalid",
        "GIT_COMMITTER_NAME": "c1-fixture",
        "GIT_COMMITTER_EMAIL": "c1-fixture@example.invalid",
        "GIT_AUTHOR_DATE": FIXED_DATE,
        "GIT_COMMITTER_DATE": FIXED_DATE,
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_TERMINAL_PROMPT": "0",
    }
    return env


ENV = None  # set in main()


def git(repo, *args, check=False):
    proc = subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True,
        text=True,
        env=ENV,
    )
    if check and proc.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), proc.stderr.strip()))
    return proc


def write_file(repo, name, data):
    full = os.path.join(repo, name)
    parent = os.path.dirname(full)
    if parent:
        os.makedirs(parent, exist_ok=True)
    mode = "wb" if isinstance(data, bytes) else "w"
    with open(full, mode) as handle:
        handle.write(data)


def make_repo(path):
    os.makedirs(path, exist_ok=True)
    git(path, "init", "-q", "-b", "master", check=True)
    return path


def commit_all(repo, message):
    git(repo, "add", "-A", check=True)
    git(repo, "commit", "-q", "-m", message, check=True)
    return git(repo, "rev-parse", "HEAD", check=True).stdout.strip()


def card(rows):
    lines = [
        "# C1 selftest fixture scorecard",
        "",
        "| # | Claim | Evidence |",
        "| --- | --- | --- |",
    ]
    for index, (claim, evidence) in enumerate(rows, 1):
        lines.append("| %d | %s | %s |" % (index, claim, evidence))
    return "\n".join(lines) + "\n"


def good_rows(rev_token, digest):
    return [
        ("helper resolver shipped", "`tools/helper.sh`"),
        ("measured at rev", "rev " + rev_token),
        ("digest pinned", "`tools/helper.sh` " + digest),
    ]


def build_fixtures(root):
    """Returns the five frozen fixtures. Each is (name, repo, rev, expect)."""
    fixtures = []

    def two_commit_fixture(name, extra_rows, digest=GOOD_DIGEST):
        repo = make_repo(os.path.join(root, name))
        write_file(repo, "tools/helper.sh", HELPER_BODY)
        helper_rev = commit_all(repo, "add helper")
        rows = good_rows(helper_rev[:12], digest) + extra_rows
        write_file(repo, "SCORECARD.md", card(rows))
        rev = commit_all(repo, "declare evidence")
        return repo, rev

    # 1. all-good declaration -> 0 mismatches
    repo, rev = two_commit_fixture("1-all-good", [])
    fixtures.append(dict(name="1-all-good", repo=repo, rev=rev, expect="zero"))

    # 2. nonexistent path -> >=1
    repo, rev = two_commit_fixture(
        "2-nonexistent-path",
        [("missing helper", "`tools/absent.py`")],
    )
    fixtures.append(dict(name="2-nonexistent-path", repo=repo, rev=rev, expect="nonzero"))

    # 3. dangling revision -> >=1
    repo, rev = two_commit_fixture(
        "3-dangling-revision",
        [("dangling revision", "measured at commit " + DANGLING_REV)],
    )
    fixtures.append(dict(name="3-dangling-revision", repo=repo, rev=rev, expect="nonzero"))

    # 4. wrong digest -> >=1
    repo, rev = two_commit_fixture(
        "4-wrong-digest",
        [],
        digest=WRONG_DIGEST,
    )
    fixtures.append(dict(name="4-wrong-digest", repo=repo, rev=rev, expect="nonzero"))

    # 5. path present at a different revision only -> >=1
    #    The declaration (and its `tools/late.sh` row) is committed at rev;
    #    tools/late.sh itself is only added afterwards, so it exists in the
    #    worktree and in a later commit but not at --rev. SCORECARD.md bytes are
    #    identical at rev and in the worktree, so the fixture discriminates
    #    whether the candidate reads the declaration from the worktree or from
    #    --rev: only resolving the *path* against --rev can catch it.
    repo = make_repo(os.path.join(root, "5-path-at-other-rev"))
    write_file(repo, "tools/helper.sh", HELPER_BODY)
    helper_rev = commit_all(repo, "add helper")
    rows = good_rows(helper_rev[:12], GOOD_DIGEST) + [
        ("late helper shipped", "`tools/late.sh`"),
    ]
    write_file(repo, "SCORECARD.md", card(rows))
    rev = commit_all(repo, "declare evidence")
    write_file(repo, "tools/late.sh", LATE_BODY)
    commit_all(repo, "add late helper")
    fixtures.append(dict(name="5-path-at-other-rev", repo=repo, rev=rev, expect="nonzero"))

    return fixtures


# --------------------------------------------------------------------------
# Calibration oracle: a minimal, non-vacuous reader of the same fixtures.
# It exists only so the gate can prove it is able to award PASS. It is written
# into the throwaway fixture tree and never into a lane repo.
# --------------------------------------------------------------------------
ORACLE_SOURCE = r'''#!/usr/bin/env python3
"""Minimal frozen-class A/B/C resolver, used only to calibrate the gold gate."""
import argparse
import hashlib
import re
import subprocess
import sys

PATH_RE = re.compile(r"^[A-Za-z0-9_./-]+\.(?:py|sh|json|tsv|md|txt)(?::\d+)?$")
HEX64_RE = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
HEX_RE = re.compile(r"(?<![0-9a-f])[0-9a-f]{7,40}(?![0-9a-f])")
CTX_RE = re.compile(r"\b(?:commit|rev|revision|measured|at)\b", re.I)
TICK_RE = re.compile(r"`([^`]+)`")


def git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--file", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--format", default="counts")
    args = ap.parse_args()
    root = args.root
    with open(args.file, encoding="utf-8") as handle:
        text = handle.read()

    assertions = resolved = skipped = mismatches = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        for cell in cells:
            ticks = TICK_RE.findall(cell)
            paths = [t for t in ticks if PATH_RE.match(t) and "*" not in t]
            for token in ticks:
                if "*" in token or not PATH_RE.match(token):
                    skipped += 1
            digests = HEX64_RE.findall(cell)
            bares = HEX_RE.findall(cell)

            for token in paths:
                path = token.split(":")[0]
                assertions += 1
                probe = git(root, "cat-file", "-e", "%s:%s" % (args.rev, path))
                if probe.returncode == 0:
                    resolved += 1
                else:
                    mismatches += 1

            if len(digests) == 1 and len(paths) == 1:
                path = paths[0].split(":")[0]
                assertions += 1
                blob = git(root, "show", "%s:%s" % (args.rev, path))
                if blob.returncode != 0:
                    mismatches += 1
                elif hashlib.sha256(blob.stdout).hexdigest() == digests[0]:
                    resolved += 1
                else:
                    mismatches += 1

            for token in bares:
                if not CTX_RE.search(cell):
                    skipped += 1
                    continue
                assertions += 1
                probe = git(root, "cat-file", "-e", token + "^{commit}")
                if probe.returncode == 0:
                    resolved += 1
                else:
                    mismatches += 1

    print("assertions=%d resolved=%d skipped=%d mismatches=%d"
          % (assertions, resolved, skipped, mismatches))
    return 0 if mismatches == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
'''


def candidate_command(path):
    if path.endswith(".py"):
        return [sys.executable, "-B", path]
    if os.access(path, os.X_OK):
        return [path]
    return [sys.executable, "-B", path]


def run_fixture(candidate, fixture, timeout):
    command = candidate_command(candidate) + [
        "--root", fixture["repo"],
        "--file", "SCORECARD.md",
        "--rev", fixture["rev"],
        "--format", "counts",
    ]
    try:
        proc = subprocess.run(
            command,
            cwd=fixture["repo"],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=ENV,
        )
    except subprocess.TimeoutExpired:
        return dict(ok=False, notes=["timeout"], rc=None, counts=None)
    except OSError as error:
        return dict(ok=False, notes=["exec-error:%s" % error], rc=None, counts=None)

    counts = None
    for line in proc.stdout.splitlines():
        match = COUNTS_RE.match(line.strip())
        if match:
            counts = dict(
                assertions=int(match.group(1)),
                resolved=int(match.group(2)),
                skipped=int(match.group(3)),
                mismatches=int(match.group(4)),
            )
    if counts is None:
        return dict(ok=False, notes=["no-counts-line", "rc=%s" % proc.returncode],
                    rc=proc.returncode, counts=None)

    notes = []
    # Frozen expectation only: fixture 1 -> 0 mismatches, fixtures 2-5 -> >=1.
    if fixture["expect"] == "zero":
        ok = counts["mismatches"] == 0
        if counts["assertions"] == 0:
            notes.append("note=assertions-zero-no-discrimination-here")
    else:
        ok = counts["mismatches"] >= 1
    # Reported, not scored: the counter contract also says exit 0 iff M == 0.
    if (proc.returncode == 0) != (counts["mismatches"] == 0):
        notes.append("note=exit-contract-deviation")
    return dict(ok=ok, notes=notes, rc=proc.returncode, counts=counts)


def score(candidate, fixtures, timeout, label):
    passed = 0
    for fixture in fixtures:
        result = run_fixture(candidate, fixture, timeout)
        counts = result["counts"]
        if counts is None:
            summary = "a=? r=? s=? m=?"
        else:
            summary = "a=%d r=%d s=%d m=%d" % (
                counts["assertions"], counts["resolved"],
                counts["skipped"], counts["mismatches"],
            )
        verdict = "PASS" if result["ok"] else "FAIL"
        extra = (" " + " ".join(result["notes"])) if result["notes"] else ""
        sys.stderr.write(
            "[%s] fixture=%s expect=%s rev=%s exit=%s %s verdict=%s%s\n"
            % (label, fixture["name"], fixture["expect"], fixture["rev"][:12],
               result["rc"], summary, verdict, extra)
        )
        if result["ok"]:
            passed += 1
    return passed


def main(argv):
    global ENV

    parser = argparse.ArgumentParser(
        description="C1 kill-rule fixture gate: 5 frozen fixtures vs one candidate.")
    parser.add_argument("candidate", help="path to the candidate counter (.py or executable)")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--keep", action="store_true", help="keep the throwaway fixture tree")
    parser.add_argument("--no-oracle", action="store_true",
                        help="skip the harness calibration oracle")
    parser.add_argument("--tmpdir", default=None,
                        help="parent directory for the throwaway fixture tree")
    args = parser.parse_args(argv)

    candidate = os.path.abspath(args.candidate)
    if not os.path.isfile(candidate):
        sys.stderr.write("gate-error: candidate is not a file: %s\n" % candidate)
        return 2

    root = tempfile.mkdtemp(prefix="c1-fixtures-", dir=args.tmpdir)
    ENV = build_env(root)
    try:
        fixtures = build_fixtures(root)
        sys.stderr.write(
            "candidate=%s fixtures_root=%s n=%d\n" % (candidate, root, len(fixtures)))

        gate_broken = False
        if not args.no_oracle:
            oracle_path = os.path.join(root, "_gate_oracle.py")
            with open(oracle_path, "w", encoding="utf-8") as handle:
                handle.write(ORACLE_SOURCE)
            oracle_passed = score(oracle_path, fixtures, args.timeout, "oracle")
            sys.stderr.write("oracle=%s fixtures=%d/%d\n"
                             % ("PASS" if oracle_passed == len(fixtures) else "BROKEN",
                                oracle_passed, len(fixtures)))
            if oracle_passed != len(fixtures):
                sys.stderr.write(
                    "GATE-BROKEN: the harness cannot award PASS to a non-vacuous "
                    "reader; the fixture set is not measuring what it claims\n")
                gate_broken = True

        passed = 0 if gate_broken else score(candidate, fixtures, args.timeout, "candidate")
        total = len(fixtures)
        verdict = "PASS" if (not gate_broken and passed == total) else "FALSE-GREEN-REJECTED"
        if gate_broken:
            passed = 0
        sys.stdout.write("control=%s fixtures=%d/%d\n" % (verdict, passed, total))
        if gate_broken:
            return 2
        return 0 if verdict == "PASS" else 1
    finally:
        if args.keep:
            sys.stderr.write("kept=%s\n" % root)
        else:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
