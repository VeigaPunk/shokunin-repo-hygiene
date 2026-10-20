#!/usr/bin/env python3
"""External fixture for the round-18 LG-DANGLING-PTR landing-gate check.

Usage: python3 tests/fixtures/r18-landing-pointers.py [--tool PATH]

The selected gate is invoked with its normal interface:
    python3 tools/souji-landing-gate.py --root ROOT --rev REV --round N

The synthetic cases use throwaway git repositories under /var/tmp. They pin
exact exit codes and finding-id/path multisets; finding paths are the expanded
offending tokens, and details carry citation locations. The historical replay
asserts that the two routed round-17 dangling pointers remain visible
at the round-18 replay revision. The fixture never edits a lane repository.

Cases cover an uncommitted SKILL citation, a committed knowledge citation,
line-suffixed lesson references, partial brace expansion, round-6..11 range
expansion, placeholder skipping, committed pointer exemptions, malformed
exemption TSV (exit 2), and the round-17 feature boundary. The vacuity guard
proves a silent rc-0 tool fails the required dangling-pointer assertion.
"""

import argparse
import collections
import os
import shutil
import subprocess
import sys
import tempfile

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
DEFAULT_TOOL = os.path.join(LANE, "tools", "souji-landing-gate.py")
REPLAY_REV = "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3"
REPLAY_ROUND = 18
ROUND = 77  # Synthetic wave number; kept separate from lane rounds.
FINDING = "LG-DANGLING-PTR"

GIT_ENV = {
    "GIT_AUTHOR_NAME": "r18-landing-pointers-fixture",
    "GIT_AUTHOR_EMAIL": "r18-pointers@fixture.invalid",
    "GIT_COMMITTER_NAME": "r18-landing-pointers-fixture",
    "GIT_COMMITTER_EMAIL": "r18-pointers@fixture.invalid",
    "GIT_AUTHOR_DATE": "2026-10-20T00:00:00Z",
    "GIT_COMMITTER_DATE": "2026-10-20T00:00:00Z",
    "GIT_CONFIG_NOSYSTEM": "1",
    "HOME": "/nonexistent-fixture-home",
}

BASE_DOCS = {
    "SKILL.md": "# Synthetic lane skill\n",
    "SCORECARD.md": "# Synthetic scorecard\n",
    "PROVINCE.md": "# Synthetic province\n",
    "corpus/QUALITY.md": "# Synthetic quality\n",
    "corpus/README.md": "# Synthetic corpus\n",
    "corpus/knowledge/authority.md": "# Synthetic knowledge\n",
    "LOG.md": "# Synthetic log\n\n## Round %d\n\nNo events.\n" % ROUND,
}


def git(repo, *args):
    env = dict(os.environ)
    env.update(GIT_ENV)
    proc = subprocess.run(
        ["git", "-C", str(repo)] + list(args),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
    )
    if proc.returncode:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), proc.stderr.strip()))
    return proc.stdout.strip()


def write_file(repo, relpath, text):
    path = os.path.join(repo, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


class Repo(object):
    """A disposable git repository used as a gate --root."""

    def __init__(self, parent, name, round_no=ROUND):
        self.path = os.path.join(parent, name)
        os.makedirs(self.path)
        git(self.path, "init", "-q", "-b", "main")
        git(self.path, "config", "commit.gpgsign", "false")
        for relpath, text in BASE_DOCS.items():
            if relpath == "LOG.md":
                text = "# Synthetic log\n\n## Round %d\n\nNo events.\n" % round_no
            self.write(relpath, text)
        self.write(
            "corpus/lessons/round-%d.md" % round_no,
            "# Round %d lesson\n\nNo seat-reported failures.\n" % round_no,
        )
        self.write(
            ".ufo/waves/round-%d/w1/Seat.md" % round_no,
            "# Seat\n\nSTATUS: clean\n",
        )
        self.write("tools/ok.sh", "#!/bin/sh\necho ok\n")

    def write(self, relpath, text):
        write_file(self.path, relpath, text)

    def commit(self, message="fixture"):
        git(self.path, "add", "-A")
        git(self.path, "commit", "-q", "-m", message, "--allow-empty")
        return git(self.path, "rev-parse", "HEAD")


class Gate(object):
    def __init__(self, tool):
        self.tool = tool

    def run(self, root, rev, round_no, tool=None):
        selected = tool or self.tool
        argv = ([sys.executable, selected] if selected.endswith(".py")
                else [selected])
        cmd = argv + ["--root", str(root), "--rev", str(rev),
                      "--round", str(round_no)]
        try:
            return subprocess.run(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True,
                                  timeout=180)
        except FileNotFoundError as exc:
            class Missing(object):
                returncode = 127
                stdout = ""
                stderr = str(exc)
            return Missing()


def finding_multiset(proc):
    """Count all emitted finding IDs by their TSV path column."""
    counts = collections.Counter()
    for line in proc.stdout.splitlines():
        fields = line.split("\t", 2)
        if len(fields) >= 2 and fields[0].startswith("LG-"):
            counts[(fields[0], fields[1])] += 1
    return counts


def check(proc, expected_exit, expected_findings, detail_requirements=(),
          minimum=False):
    observed = finding_multiset(proc)
    failures = []
    if proc.returncode != expected_exit:
        failures.append("exit=%d expected=%d" % (proc.returncode, expected_exit))
    if minimum:
        for finding, count in expected_findings.items():
            if observed[finding] < count:
                failures.append("%r count=%d expected-at-least=%d"
                                % (finding, observed[finding], count))
    elif observed != expected_findings:
        failures.append("findings=%r expected=%r" % (observed, expected_findings))
    for fragments in detail_requirements:
        if not any(all(fragment in line for fragment in fragments)
                   for line in proc.stdout.splitlines()):
            failures.append("missing detail %r" % (fragments,))
    detail = "exit=%d findings=%r" % (proc.returncode, observed)
    if failures:
        detail += " FAIL(" + "; ".join(failures) + ")"
    return not failures, detail


def emit_case(results, name, proc, expected_exit, expected_findings,
              detail_requirements=(), minimum=False):
    ok, detail = check(proc, expected_exit, expected_findings,
                       detail_requirements, minimum)
    results.append((name, ok, detail))
    print("CASE\t%s\t%s\t%s" % ("PASS" if ok else "FAIL", name, detail))


def empty_findings():
    return collections.Counter()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", default=DEFAULT_TOOL)
    args = parser.parse_args(argv)
    tool = os.path.abspath(args.tool)
    if not os.path.isfile(tool):
        print("PREREQ\tFAIL\ttool not found: %s" % tool)
        print("SUMMARY\ttotal=0\tfailed=1")
        return 2
    if shutil.which("git") is None:
        print("PREREQ\tFAIL\tgit not found on PATH")
        print("SUMMARY\ttotal=0\tfailed=1")
        return 2

    gate = Gate(tool)
    results = []
    scratch = tempfile.mkdtemp(prefix="souji-r18-pointer-fixture-",
                               dir="/var/tmp" if os.path.isdir("/var/tmp") else None)
    try:
        # Missing committed target: the source location is SKILL.md.
        vacuity_repo = Repo(scratch, "skill-dangling")
        vacuity_repo.write("SKILL.md", "# Skill\n\nEvidence: `census/round-18/x.json`.\n")
        vacuity_rev = vacuity_repo.commit("dangling skill citation")
        emit_case(results, "skill-uncommitted-target",
                  gate.run(vacuity_repo.path, vacuity_rev, ROUND), 1,
                  collections.Counter({(FINDING, "census/round-18/x.json"): 1}),
                  [("SKILL.md", "census/round-18/x.json")])

        # A committed target cited from the knowledge corpus is not dangling.
        repo = Repo(scratch, "knowledge-committed")
        repo.write("census/round-18/kept.json", '{"kept": true}\n')
        repo.write("corpus/knowledge/authority.md",
                   "Evidence: `census/round-18/kept.json`.\n")
        rev = repo.commit("committed knowledge citation")
        emit_case(results, "knowledge-committed-target",
                  gate.run(repo.path, rev, ROUND), 0, empty_findings())

        # A :line-range suffix belongs to the citation, not the file path.
        repo = Repo(scratch, "lesson-line-suffix")
        repo.write("census/round-18/source.md", "line one\n" * 20)
        repo.write("corpus/lessons/round-%d.md" % ROUND,
                   "# Round %d lesson\n\nSee `census/round-18/source.md:12-14`.\n"
                   % ROUND)
        rev = repo.commit("lesson line suffix")
        emit_case(results, "lesson-line-suffix-resolves",
                  gate.run(repo.path, rev, ROUND), 0, empty_findings())

        # Simple brace expansion yields two paths; only the absent member fires.
        repo = Repo(scratch, "brace-one-missing")
        repo.write("census/round-18/a.json", "{}\n")
        repo.write("SKILL.md", "# Skill\n\nEvidence: `census/round-18/{a.json,b.json}`.\n")
        rev = repo.commit("one missing brace alternative")
        emit_case(results, "brace-one-missing",
                  gate.run(repo.path, rev, ROUND), 1,
                  collections.Counter({(FINDING, "census/round-18/b.json"): 1}),
                  [("SKILL.md", "census/round-18/b.json")])

        # Each member of round-6..11 exists; expansion must resolve all six.
        repo = Repo(scratch, "round-range")
        for round_no in range(6, 12):
            repo.write("census/round-%d/receipt.txt" % round_no,
                       "round %d receipt\n" % round_no)
        repo.write("corpus/knowledge/authority.md",
                   "Receipts: `census/round-6..11/receipt.txt`.\n")
        rev = repo.commit("round range expansion")
        emit_case(results, "round-range-expands",
                  gate.run(repo.path, rev, ROUND), 0, empty_findings())

        # Angle-bracket placeholder paths are deliberately not filesystem claims.
        repo = Repo(scratch, "placeholder")
        repo.write("SKILL.md", "# Skill\n\nFuture: `census/round-N/<new>.json`.\n")
        rev = repo.commit("placeholder citation")
        emit_case(results, "placeholder-skipped",
                  gate.run(repo.path, rev, ROUND), 0, empty_findings())

        # Explicit TSV exemptions are committed and include a reason column.
        repo = Repo(scratch, "exemption")
        repo.write("corpus/knowledge/authority.md",
                   "Generated: `census/round-18/generated.json`.\n")
        repo.write("corpus/pointer-exemptions.tsv",
                   "census/round-18/generated.json\truntime-generated\n")
        rev = repo.commit("exempt generated path")
        emit_case(results, "exemption-honored",
                  gate.run(repo.path, rev, ROUND), 0, empty_findings())

        # A malformed exemption manifest is a refusal, not a clean result.
        repo = Repo(scratch, "malformed-exemption")
        repo.write("corpus/knowledge/authority.md",
                   "Generated: `census/round-18/generated.json`.\n")
        repo.write("corpus/pointer-exemptions.tsv",
                   "census/round-18/generated.json\n")
        rev = repo.commit("malformed exemption")
        proc = gate.run(repo.path, rev, ROUND)
        emit_case(results, "malformed-exemption-exit2", proc, 2,
                  empty_findings())

        # The round-18 check is gated off for a round-17 replay.
        repo = Repo(scratch, "round-17-boundary", round_no=17)
        repo.write("SKILL.md", "# Skill\n\nEvidence: `census/round-18/x.json`.\n")
        rev = repo.commit("round 17 boundary")
        emit_case(results, "round-17-no-pointer-finding",
                  gate.run(repo.path, rev, 17), 0, empty_findings())

        # The named historical replay uses the specified immutable root and REV.
        # This case is exercised against the selected --tool; a stub can verify
        # the assertion contract without asking it to read the live repository.
        replay = gate.run(LANE, REPLAY_REV, REPLAY_ROUND)
        historical = collections.Counter({
            (FINDING, "census/round-17/gate-replays-ddb7347.json"): 2,
            (FINDING, "census/round-17/jj-receipts-ddb7347.txt"): 4,
        })
        required = (
            ("SKILL.md", "163", "census/round-17/gate-replays-ddb7347.json"),
            ("SKILL.md", "165", "census/round-17/gate-replays-ddb7347.json"),
            ("corpus/knowledge/jj-colocation-receipts.md", "2",
             "census/round-17/jj-receipts-ddb7347.txt"),
            ("corpus/knowledge/jj-colocation-receipts.md", "44",
             "census/round-17/jj-receipts-ddb7347.txt"),
            ("corpus/knowledge/jj-colocation-receipts.md", "126",
             "census/round-17/jj-receipts-ddb7347.txt"),
            ("corpus/knowledge/jj-colocation-receipts.md", "148",
             "census/round-17/jj-receipts-ddb7347.txt"),
        )
        # b576341 has no .ufo/waves/round-18/ reports, so the carry check is
        # could-not-evaluate (exit 2); the pointer findings must still be
        # reported (r18 L1 integration: pointer scan runs before carry).
        emit_case(results, "historical-b576341-round-18", replay, 2,
                  historical, required, minimum=True)

        # A vacuous rc-0/no-output gate must fail this fixture's core assertion.
        empty_tool = os.path.join(scratch, "empty-tool.py")
        with open(empty_tool, "w", encoding="utf-8") as fh:
            fh.write("import sys\nsys.exit(0)\n")
        vacuity_proc = gate.run(vacuity_repo.path, vacuity_rev, ROUND,
                                tool=empty_tool)
        vacuous_ok, _ = check(
            vacuity_proc, 1,
            collections.Counter({(FINDING, "census/round-18/x.json"): 1}),
            [("SKILL.md", "census/round-18/x.json")],
        )
        vacuity_pass = (vacuity_proc.returncode == 0
                        and not vacuity_proc.stdout.strip()
                        and not vacuous_ok)
        detail = ("stub rc=%d stdout_bytes=%d; required finding assertion failed: %s"
                  % (vacuity_proc.returncode, len(vacuity_proc.stdout),
                     "yes" if not vacuous_ok else "NO"))
        results.append(("vacuity-stub", vacuity_pass, detail))
        print("CASE\t%s\tvacuity-stub\t%s"
              % ("PASS" if vacuity_pass else "FAIL", detail))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    failed = sum(1 for _, ok, _ in results if not ok)
    print("SUMMARY\ttotal=%d\tfailed=%d" % (len(results), failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
