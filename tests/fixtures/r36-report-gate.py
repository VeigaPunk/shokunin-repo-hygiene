#!/usr/bin/env python3
"""r36-report-gate.py — fixture for tools/souji-pre-report-gate.sh --contract.

Discriminating cases for the r36 report-contract predicates: each case builds
an isolated real-git lane (bare origin + clone, pushed), writes one report
shape, and checks the gate's exit code. A conforming report must pass; each
single contract defect must fail with the named detail; the legacy invocation
without --contract must still pass (the r27 predicates 1-5 keep their frozen
behaviour and the run prints `check-report-contract=SKIPPED`).

The last case is the control: an always-pass stub gate must NOT reproduce the
defect verdicts. If the stub passes every defect case, the fixture itself is
falsified and `control=STUB-NOT-REJECTED`.

CLI:
  python3 -B tests/fixtures/r36-report-gate.py [--gate PATH] [--work DIR]

Exit: 0 all cases pass and the control is rejected, 1 otherwise, 2 usage.
Scratch lives under TMPDIR (default /var/tmp) and is removed in finally.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

CONFORMING = """# souji — round N report

## Work performed

- C1 the first claim landed; evidence `census/round-1/records/c1-after.tsv`.

## Landed changes

- `tools/example.py` (LOG entry `Round36`).

## Before -> after measurements

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 first | calibration 7 | `f=1` | `f=0` | `python3 -B tools/example.py --rev <rev>` | `0123456789abcdef0123456789abcdef01234567` |

## Sources & frontier

SOURCES: unchanged — fixture.

## Trend verdicts

- expansion: improved — fixture.
- quality: unchanged — fixture.
- discernment: unprovable-but-better — fixture.

## SHONEN

- [~] box one `census/round-1/records/c1-after.tsv`
- [~] box two `census/round-1/records/c1-after.tsv`

## Stale-lane

- respawn-per-round driver; no other mission open.
"""

SHONEN = """# lane — promotion checklist

- [~] box one
- [~] box two
"""

STUB_GATE = """#!/usr/bin/env bash
printf 'check-tip=PASS\\ncheck-report=PASS\\ncheck-shonen=PASS\\ncheck-clean=PASS\\ncheck-prereg=PASS\\ncheck-report-contract=PASS\\nexit 0\\n'
"""


class Case:
    def __init__(self, name, report, args, expect_rc, expect_text=None, shonen=SHONEN):
        self.name = name
        self.report = report
        self.args = args
        self.expect_rc = expect_rc
        self.expect_text = expect_text
        self.shonen = shonen


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)


def build_lane(root, name, dirty=False):
    base = os.path.join(root, name)
    os.makedirs(base)
    origin = os.path.join(base, "origin.git")
    lane = os.path.join(base, "lane")
    run(["git", "init", "--bare", "-q", origin])
    run(["git", "clone", "-q", origin, lane])
    env = dict(os.environ)
    env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "fixture"
    env["GIT_AUTHOR_EMAIL"] = env["GIT_COMMITTER_EMAIL"] = "fixture@example.invalid"

    def g(*args):
        return subprocess.run(
            ["git", "-C", lane] + list(args), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
        )

    g("checkout", "-q", "-b", "master")
    open(os.path.join(lane, "base.txt"), "w").write("base\n")
    g("add", "base.txt")
    g("commit", "-qm", "base")
    g("push", "-q", "-u", "origin", "master")
    if dirty:
        open(os.path.join(lane, "dirty.txt"), "w").write("dirty\n")
    return lane


def install_shonen(lane, text):
    """Write SHONEN.md and commit it, so the clean predicate stays meaningful."""
    write(os.path.join(lane, "SHONEN.md"), text)
    env = dict(os.environ)
    env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "fixture"
    env["GIT_AUTHOR_EMAIL"] = env["GIT_COMMITTER_EMAIL"] = "fixture@example.invalid"
    for args in (["add", "SHONEN.md"], ["commit", "-qm", "shonen"], ["push", "-q", "origin", "master"]):
        subprocess.run(["git", "-C", lane] + args, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def link_tools(lane, lane_root):
    target = os.path.join(lane_root, "tools")
    link = os.path.join(lane, "tools")
    if os.path.isdir(target) and not os.path.exists(link):
        os.symlink(target, link)
        exclude = os.path.join(lane, ".git", "info", "exclude")
        os.makedirs(os.path.dirname(exclude), exist_ok=True)
        with open(exclude, "a", encoding="utf-8") as handle:
            handle.write("tools\n")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def cases():
    without = lambda text: CONFORMING.replace(text, "", 1)  # noqa: E731
    return [
        Case("conforming", CONFORMING, ["--contract"], 0),
        Case("missing-landed-changes", without("## Landed changes"), ["--contract"], 1, "check-report-contract=FAIL"),
        Case("missing-sources-frontier", without("## Sources & frontier"), ["--contract"], 1, "check-report-contract=FAIL"),
        Case(
            "shonen-no-box-lines",
            CONFORMING.replace(
                "- [~] box one `census/round-1/records/c1-after.tsv`\n- [~] box two `census/round-1/records/c1-after.tsv`\n",
                "",
            ),
            ["--contract"],
            1,
            "check-report-contract=FAIL",
        ),
        Case(
            "trend-verdict-missing",
            CONFORMING.replace("- discernment: unprovable-but-better — fixture.\n", ""),
            ["--contract"],
            1,
            "check-report-contract=FAIL",
        ),
        Case(
            "stale-lane-absent",
            without("- respawn-per-round driver; no other mission open."),
            ["--contract"],
            1,
            "check-report-contract=FAIL",
        ),
        Case(
            "measured-commit-absent",
            CONFORMING.replace("`0123456789abcdef0123456789abcdef01234567`", "`pending`").replace(
                "`python3 -B tools/example.py --rev <rev>`", "`run`"
            ),
            ["--contract"],
            1,
            "check-report-contract=FAIL",
        ),
        Case(
            "commit-too-short",
            CONFORMING.replace("`0123456789abcdef0123456789abcdef01234567`", "`abcdef`"),
            ["--contract"],
            1,
            "check-report-contract=FAIL",
        ),
        Case(
            "command-not-backticked",
            CONFORMING.replace(
                "| C1 first | calibration 7 | `f=1` | `f=0` | `python3 -B tools/example.py --rev <rev>` | `0123456789abcdef0123456789abcdef01234567` |",
                "| C1 first | calibration 7 | f=1 | f=0 | pending | `0123456789abcdef0123456789abcdef01234567` |",
            ),
            ["--contract"],
            1,
            "check-report-contract=FAIL",
        ),
        Case(
            "sections-all-fenced",
            "```\n" + CONFORMING + "\n```\n",
            ["--contract"],
            1,
            "check-report-contract=FAIL",
        ),
        Case(
            "fenced-quoted-heading",
            CONFORMING + "\n```\n## Work performed\n```\n",
            ["--contract"],
            0,
        ),
        Case(
            "h3-work-performed",
            CONFORMING.replace("## Work performed", "### Work performed"),
            ["--contract"],
            1,
            "check-report-contract=FAIL",
        ),
        Case(
            "substring-heading",
            CONFORMING.replace("## Work performed", "## Not work performed this round"),
            ["--contract"],
            1,
            "check-report-contract=FAIL",
        ),
        Case(
            # measurements stays green (a 7-hex commit and two spans), so the only
            # failing predicate is `evidence`: it isolates the mutant (A3).
            "evidence-non-pointer-tokens",
            CONFORMING.replace("census/round-1/records/c1-after.tsv", "x")
            .replace("`tools/example.py`", "`x`")
            .replace("`python3 -B tools/example.py --rev <rev>`", "`run`")
            .replace("`0123456789abcdef0123456789abcdef01234567`", "`0123456`")
            .replace("`f=1`", "`a`")
            .replace("`f=0`", "`b`"),
            ["--contract"],
            1,
            "check-report-contract=FAIL",
        ),
        Case(
            # a slash-shaped token outside the allowlist: kills the "any path" mutant.
            "evidence-path-outside-allowlist",
            CONFORMING.replace("census/round-1/records/c1-after.tsv", "x")
            .replace("`tools/example.py`", "`x`")
            .replace("`python3 -B tools/example.py --rev <rev>`", "`archive/x.tsv`")
            .replace("`0123456789abcdef0123456789abcdef01234567`", "`0123456`")
            .replace("`f=1`", "`a`")
            .replace("`f=0`", "`b`"),
            ["--contract"],
            1,
            "check-report-contract=FAIL",
        ),
        Case(
            "evidence-seven-hex-commit",
            CONFORMING.replace("`0123456789abcdef0123456789abcdef01234567`", "`0123456`"),
            ["--contract"],
            0,
        ),
        Case(
            "claim-ids-four",
            CONFORMING.replace("- C1 the first claim landed", "- C1 C2 C3 C4 the first claim landed"),
            ["--contract"],
            1,
            "check-report-contract=FAIL",
        ),
        Case("legacy-defective-passes", without("## Landed changes"), [], 0, "check-report-contract=SKIPPED"),
        Case("dirty-lane", CONFORMING, ["--contract"], 1, "check-clean=FAIL"),
        Case("prereg-absent", CONFORMING, ["--contract"], 1, "check-prereg=FAIL"),
    ]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate")
    ap.add_argument("--work")
    args = ap.parse_args(argv)
    lane_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    gate = args.gate or os.path.join(lane_root, "tools", "souji-pre-report-gate.sh")
    scratch = tempfile.mkdtemp(prefix="souji-r36-report-gate.", dir=args.work or os.environ.get("TMPDIR") or "/var/tmp")
    passed = failed = 0
    control_ok = True
    try:
        for case in cases():
            root = os.path.join(scratch, case.name)
            os.makedirs(root)
            lane = build_lane(root, "lane", dirty=(case.name == "dirty-lane"))
            report = os.path.join(root, "report.md")
            prereg = os.path.join(root, "prereg.txt")
            write(report, case.report)
            if case.name == "prereg-absent":
                if os.path.exists(prereg):
                    os.unlink(prereg)
            else:
                write(prereg, "prereg\n")
            install_shonen(lane, case.shonen)
            link_tools(lane, lane_root)
            proc = run(
                ["bash", gate, "--lane", lane, "--branch", "master", "--report", report, "--prereg", prereg] + case.args
            )
            combined = proc.stdout + proc.stderr
            ok = proc.returncode == case.expect_rc and (case.expect_text is None or case.expect_text in combined)
            if ok:
                passed += 1
                print("case-%s=PASS rc=%d" % (case.name, proc.returncode))
            else:
                failed += 1
                print("case-%s=FAIL expected_rc=%d actual_rc=%d expect_text=%r" % (case.name, case.expect_rc, proc.returncode, case.expect_text))
                print("---- output ----\n%s" % combined[-1500:])
        # Control: an always-pass stub gate must disagree with the defect cases.
        stub_path = os.path.join(scratch, "stub-gate.sh")
        write(stub_path, STUB_GATE)
        os.chmod(stub_path, 0o755)
        replicated = []
        for case in cases():
            if case.expect_rc == 0:
                continue
            root = os.path.join(scratch, "stub-" + case.name)
            os.makedirs(root)
            lane = build_lane(root, "lane", dirty=(case.name == "dirty-lane"))
            report = os.path.join(root, "report.md")
            prereg = os.path.join(root, "prereg.txt")
            write(report, case.report)
            write(prereg, "prereg\n")
            install_shonen(lane, case.shonen)
            proc = run(
                ["bash", stub_path, "--lane", lane, "--branch", "master", "--report", report, "--prereg", prereg] + case.args
            )
            if proc.returncode == case.expect_rc:
                replicated.append(case.name)
        if replicated:
            control_ok = False
            print("control=STUB-NOT-REJECTED replicated=%s" % ",".join(replicated))
        else:
            print("control=STUB-REJECTED")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print("SUMMARY cases=%d pass=%d fail=%d control=%s" % (passed + failed, passed, failed, "STUB-REJECTED" if control_ok else "STUB-NOT-REJECTED"))
    return 0 if failed == 0 and control_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
