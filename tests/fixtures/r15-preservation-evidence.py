#!/usr/bin/env python3
"""r15-preservation-evidence.py — black-box replay for the C2 admission gate.

This fixture is an external regression harness, not a certifier. It invokes
tools/souji-preservation-evidence.py only through its documented CLI and
asserts exit codes and finding ids. It grants no tool-safety certification
and never executes a recorded command.

Scratch space is always a tempfile.mkdtemp(dir="/var/tmp") tree, removed in a
finally block. There is no /tmp fallback and an inherited TMPDIR does not
move the base. Run it from anywhere:

    python3 tests/fixtures/r15-preservation-evidence.py

Exit codes: 0 all checks passed, 1 assertion failed, 2 prerequisite missing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LANE = Path(__file__).resolve().parents[2]
DEFAULT_TOOL = LANE / "tools" / "souji-preservation-evidence.py"
DEFAULT_FROZEN = LANE / "tests" / "fixtures" / "r15-preservation-frozen"
CONFIG_FIXTURE = "tests/fixtures/r15-census-config.py"
NAMESPACE_FIXTURE = "tests/fixtures/r14-census-boundary.py"
INSTALLED_TOOL = "tools/souji-census.sh"

ENV = {
    "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    "LC_ALL": "C",
    "TMPDIR": "/var/tmp",
    "PYTHONDONTWRITEBYTECODE": "1",
}

# Pinned literal universe — duplicated here on purpose: the harness never
# derives ids from the checker or the fixture under test.
BENIGN = ["R15CFG-01", "R15CFG-04", "R15CFG-06", "R15CFG-09", "R15CFG-10",
          "R15CFG-12", "R15CFG-13", "R15CFG-15", "R15CFG-16"]
REFUSAL = ["R15CFG-02", "R15CFG-03", "R15CFG-07", "R15CFG-11", "R15CFG-14",
           "R15CFG-17", "R15CFG-19"]
SAFETY = ["R15CFG-08"]
PRESERVE = ["R15CFG-05", "R15CFG-18", "R15CFG-20"]
NS = ["R14C2-%02d" % i for i in range(1, 13)]
IDS = sorted(BENIGN + REFUSAL + SAFETY + PRESERVE)
PREHARM_FAILS = set(REFUSAL) | set(SAFETY) | {"R15CFG-18", "R15CFG-20"}
HARM_FAILS = set(BENIGN) | set(SAFETY)

PREHARM_COMMIT = "a31642d14006830ec62edf40b0354c3699728c4a"
PREHARM_SHA = "6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026"
BASELINE_COMMIT = "cc2168325768d5356a82c039dcdf787377c55784"
BASELINE_SHA = "fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9"
SELFTEST_COMMIT = "0123456789abcdef0123456789abcdef01234567"


def sha_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(text, encoding="utf-8")


def invoke(tool, *arguments):
    return subprocess.run(
        [sys.executable, str(tool), *arguments],
        capture_output=True,
        text=True,
        timeout=180,
        env=ENV,
    )


def check(results, name, proc, want_rc, needles):
    problems = []
    if proc.returncode != want_rc:
        problems.append("rc=%r want %d" % (proc.returncode, want_rc))
    for needle in needles:
        if needle not in proc.stdout:
            problems.append("stdout missing %r" % needle)
    results.append((name, problems, proc))
    return not problems


def detail(cid, status):
    if status == "FAIL":
        return "contract difference observed_exit=2 observed_finding=path-protected"
    if cid in REFUSAL or cid in NS:
        return "guard held observed_exit=2 observed_finding=path-protected"
    return "ok observed_exit=0 observed_finding=none"


def arm(commit, tool_sha, statuses, tool_path):
    rows = [(cid, status) for cid, status in statuses]
    failed = sum(1 for _, status in rows if status == "FAIL")
    lines = ["TOOL\t%s\tsha256=%s" % (tool_path, tool_sha), "TOOL-KIND\tother"]
    for cid, status in rows:
        lines.append("CASE\t%s\t%s\t%s" % (cid, status, detail(cid, status)))
    lines.append("SUMMARY\ttotal=%d\tfailed=%d" % (len(rows), failed))
    stdout = "\n".join(lines) + "\n"
    return {
        "tool": {"commit": commit, "sha256": tool_sha},
        "argv": ["timeout", "300", "python3", "-B",
                 "tests/fixtures/r15-census-config.py", "--tool", tool_path],
        "exit_code": 0 if failed == 0 else 1,
        "timed_out": False,
        "stdout": stdout,
        "stdout_sha256": sha_text(stdout),
        "stdout_bytes_total": len(stdout.encode("utf-8")),
        "stdout_truncated": False,
        "stderr": "",
        "cases": [{"id": cid, "status": status.lower(),
                   "detail": detail(cid, status)} for cid, status in rows],
        "summary": {"total": len(rows), "failed": failed},
    }


def want_status(arm_name, cid):
    if arm_name == "baseline":
        return "FAIL" if cid in HARM_FAILS else "PASS"
    if arm_name == "baseline_preharm":
        return "FAIL" if cid in PREHARM_FAILS else "PASS"
    return "PASS"


def build_root(base, name):
    """Synthetic checkout: real fixtures, stand-in repaired tool bytes."""
    root = base / name
    (root / "tools").mkdir(parents=True)
    (root / "tests/fixtures").mkdir(parents=True)
    shutil.copyfile(LANE / CONFIG_FIXTURE, root / CONFIG_FIXTURE)
    shutil.copyfile(LANE / NAMESPACE_FIXTURE, root / NAMESPACE_FIXTURE)
    (root / CONFIG_FIXTURE).chmod(0o644)
    (root / NAMESPACE_FIXTURE).chmod(0o644)
    # The stand-in is not the installed tool: records bind to this file.
    write_text(root / INSTALLED_TOOL,
               "#!/bin/sh\n# external-fixture repaired tool stand-in\n")
    return root


def build_record(root):
    tool_sha = sha_file(root / INSTALLED_TOOL)
    return {
        "schema": "souji-preservation-record-v1",
        "declared_consistency_only": True,
        "measured_commit": SELFTEST_COMMIT,
        "fixture": {"path": CONFIG_FIXTURE, "sha256": sha_file(root / CONFIG_FIXTURE)},
        "namespace_fixture": {"path": NAMESPACE_FIXTURE,
                              "sha256": sha_file(root / NAMESPACE_FIXTURE)},
        "runs": {
            "baseline_preharm": arm(
                PREHARM_COMMIT, PREHARM_SHA,
                [(cid, want_status("baseline_preharm", cid)) for cid in IDS],
                "/var/tmp/preharm.sh"),
            "baseline": arm(
                BASELINE_COMMIT, BASELINE_SHA,
                [(cid, want_status("baseline", cid)) for cid in IDS],
                "/var/tmp/harm.sh"),
            "changed": arm(
                SELFTEST_COMMIT, tool_sha,
                [(cid, "PASS") for cid in IDS],
                str(root / INSTALLED_TOOL)),
        },
        "namespace_controls": arm(
            SELFTEST_COMMIT, tool_sha,
            [(cid, "PASS") for cid in NS],
            str(root / INSTALLED_TOOL)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tool", default=str(DEFAULT_TOOL))
    parser.add_argument("--frozen-dir", default=str(DEFAULT_FROZEN))
    args = parser.parse_args()

    tool = Path(args.tool).resolve()
    frozen = Path(args.frozen_dir).resolve()
    if not tool.is_file():
        print("fixture: tool missing: %s" % tool)
        return 2
    if not (LANE / CONFIG_FIXTURE).is_file() \
            or not (LANE / NAMESPACE_FIXTURE).is_file():
        print("fixture: lane fixtures missing")
        return 2

    base = Path(tempfile.mkdtemp(prefix="souji-r15-preservation-fixture.", dir="/var/tmp"))
    results = []
    try:
        selftest = invoke(tool, "--selftest")
        passed = check(results, "selftest", selftest, 0, ["selftest: ", " passed"])
        if passed:
            match = re.search(r"(?m)^selftest: (\d+)/(\d+) passed$", selftest.stdout)
            if match is None or match.group(1) != match.group(2) \
                    or int(match.group(2)) < 1:
                results[-1][1].append("selftest summary missing or incomplete")

        # positive: honest paired record on a synthetic checkout.
        root = build_root(base, "external-clean")
        record = build_record(root)
        clean = invoke(tool, "--root", str(root), "--record", json.dumps(record))
        check(results, "external-clean", clean, 0,
              ["souji-preservation-evidence: clean",
               "arms: baseline_preharm,baseline,changed,namespace_controls"])

        # green-only: the harm baseline arm is missing.
        root = build_root(base, "external-green-only")
        record = build_record(root)
        del record["runs"]["baseline"]
        proc = invoke(tool, "--root", str(root), "--record", json.dumps(record))
        check(results, "external-green-only", proc, 2,
              ["souji-preservation-evidence: could-not-evaluate",
               "finding run-missing:"])

        # weakened red: baseline arm claims benign controls passed.
        root = build_root(base, "external-weakened-red")
        record = build_record(root)
        record["runs"]["baseline"] = arm(
            BASELINE_COMMIT, BASELINE_SHA,
            [(cid, "PASS") for cid in IDS], "/var/tmp/harm.sh")
        proc = invoke(tool, "--root", str(root), "--record", json.dumps(record))
        check(results, "external-weakened-red", proc, 1,
              ["souji-preservation-evidence: failed",
               "finding baseline-not-red:",
               "finding case-status-unexpected:"])

        # missing namespace controls.
        root = build_root(base, "external-no-ns")
        record = build_record(root)
        del record["namespace_controls"]
        proc = invoke(tool, "--root", str(root), "--record", json.dumps(record))
        check(results, "external-no-ns", proc, 2,
              ["souji-preservation-evidence: could-not-evaluate",
               "finding run-missing:"])

        # changed arm bound to the pinned harm digest is not a repair.
        root = build_root(base, "external-changed-is-baseline")
        record = build_record(root)
        record["runs"]["changed"] = arm(
            SELFTEST_COMMIT, BASELINE_SHA,
            [(cid, "PASS") for cid in IDS], str(root / INSTALLED_TOOL))
        proc = invoke(tool, "--root", str(root), "--record", json.dumps(record))
        check(results, "external-changed-is-baseline", proc, 2,
              ["souji-preservation-evidence: could-not-evaluate",
               "finding pinned-mismatch:"])

        # frozen input: evaluate shipped pins against the live lane. The
        # shipped snapshot is pinned to the pre-integration state, so any of
        # clean / failed / could-not-evaluate is honest; the check requires
        # the status banner and a pin coverage line, and forbids a crash rc.
        if (frozen / "expected.json").is_file():
            proc = invoke(tool, "--frozen", str(frozen), "--root", str(LANE))
            problems = []
            if proc.returncode not in (0, 1, 2):
                problems.append("unexpected rc %d" % proc.returncode)
            for needle in ("souji-preservation-evidence:", "frozen_files:"):
                if needle not in proc.stdout:
                    problems.append("stdout missing %r" % needle)
            results.append(("frozen-lane", problems, proc))

            # tampered copy of the frozen dir must be refused.
            tampered_dir = base / "frozen-tampered"
            shutil.copytree(frozen, tampered_dir)
            write_text(tampered_dir / "record.json", "{}\n")
            proc = invoke(tool, "--frozen", str(tampered_dir), "--root", str(LANE))
            check(results, "frozen-tampered", proc, 2,
                  ["souji-preservation-evidence: could-not-evaluate",
                   "finding snapshot_tampered:"])
    except subprocess.TimeoutExpired:
        results.append(("timeout", ["a CLI invocation exceeded 180s"], None))
    finally:
        shutil.rmtree(base, ignore_errors=True)

    failures = [item for item in results if item[1]]
    for name, problems, proc in results:
        if not problems:
            print("ok %s" % name)
            continue
        print("FAIL %s: %s" % (name, "; ".join(problems)))
        if proc is not None:
            if proc.stdout:
                print("  stdout:\n    " + proc.stdout.strip().replace("\n", "\n    "))
            if proc.stderr:
                print("  stderr:\n    " + proc.stderr.strip().replace("\n", "\n    "))
    print("fixture: %d/%d checks passed" % (len(results) - len(failures), len(results)))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
