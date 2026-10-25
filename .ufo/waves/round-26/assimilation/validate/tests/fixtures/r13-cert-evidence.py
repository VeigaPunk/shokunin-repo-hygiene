#!/usr/bin/env python3
"""r13-cert-evidence.py — black-box replay for tools/souji-cert-evidence.py.

This fixture is an external regression harness, not a certifier. It invokes the
gate only through its documented CLI and asserts exit codes and finding ids.
It grants no tool-safety certification.

Scratch space is always a tempfile.mkdtemp(dir="/var/tmp") tree, removed in a
finally block. There is no /tmp fallback and an inherited TMPDIR does not move
the base. Run it from anywhere:

    python3 tests/fixtures/r13-cert-evidence.py

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
DEFAULT_TOOL = LANE / "tools" / "souji-cert-evidence.py"
DEFAULT_FROZEN = LANE / "tests" / "fixtures" / "r13-cert-frozen"
ENV = {
    "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    "LC_ALL": "C",
    "TMPDIR": "/var/tmp",
    "PYTHONDONTWRITEBYTECODE": "1",
}


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path, obj):
    write_text(path, json.dumps(obj, indent=2, sort_keys=True) + "\n")


def invoke(tool, *arguments):
    return subprocess.run(
        [sys.executable, str(tool), *arguments],
        capture_output=True,
        text=True,
        timeout=180,
        env=ENV,
    )


def check(results, name, proc, want_rc, needles):
    observed = proc.returncode
    problems = []
    if observed != want_rc:
        problems.append("rc=%r want %d" % (observed, want_rc))
    for needle in needles:
        if needle not in proc.stdout:
            problems.append("stdout missing %r" % needle)
    results.append((name, problems, proc))
    return not problems


def build_clean_root(root):
    artifact = "#!/bin/sh\n# r13 external fixture artifact\nprintf 'external ok\\n'\n"
    evidence = "external ok\n"
    write_text(root / "installed/tool.sh", artifact)
    write_text(root / "evidence/run.txt", evidence)
    fragment = {
        "author": "external-fixture-author",
        "class": "external-consistency-fixture",
        "artifact": "installed/tool.sh",
        "sha256": sha256_text(artifact),
        "command": "sh installed/tool.sh",
        "exit_code": 0,
        "verdict": "pass",
        "evidence": "evidence/run.txt",
        "evidence_sha256": sha256_text(evidence),
    }
    write_json(root / "fragments/one.json", fragment)
    write_json(root / "manifest.json", {"fragments": ["fragments/one.json"]})
    return fragment


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
    if not (frozen / "expected.json").is_file():
        print("fixture: frozen snapshot missing: %s" % frozen)
        return 2

    base = Path(tempfile.mkdtemp(prefix="souji-r13-cert-fixture.", dir="/var/tmp"))
    results = []
    try:
        selftest = invoke(tool, "--selftest")
        passed = check(results, "selftest", selftest, 0, ["selftest: ", " passed"])
        if passed:
            match = re.search(r"(?m)^selftest: (\d+)/(\d+) passed$", selftest.stdout)
            if match is None or match.group(1) != match.group(2) or int(match.group(2)) < 1:
                results[-1][1].append("selftest summary missing or incomplete")

        root = base / "external-clean"
        root.mkdir()
        build_clean_root(root)
        clean = invoke(tool, "--root", str(root), "--manifest", str(root / "manifest.json"))
        check(
            results,
            "external-clean",
            clean,
            0,
            ["souji-cert-evidence: clean", "evidence_valid/NOT_CERTIFICATION"],
        )

        bad_root = base / "external-digest-mismatch"
        bad_root.mkdir()
        fragment = build_clean_root(bad_root)
        fragment["sha256"] = "0" * 64
        write_json(bad_root / "fragments/one.json", fragment)
        mismatch = invoke(
            tool,
            "--root",
            str(bad_root),
            "--manifest",
            str(bad_root / "manifest.json"),
        )
        check(
            results,
            "external-digest-mismatch",
            mismatch,
            2,
            ["souji-cert-evidence: could-not-evaluate", "finding artifact-digest-mismatch:"],
        )

        clean_frozen = invoke(tool, "--frozen", str(frozen))
        check(
            results,
            "frozen-clean",
            clean_frozen,
            0,
            ["souji-cert-evidence: clean", "frozen_files=7"],
        )

        tampered_copy = base / "frozen-tampered"
        shutil.copytree(frozen, tampered_copy)
        with (tampered_copy / "installed/fixture-alpha.sh").open("ab") as handle:
            handle.write(b"# tampered\n")
        tampered = invoke(tool, "--frozen", str(tampered_copy))
        check(
            results,
            "frozen-tampered",
            tampered,
            2,
            ["souji-cert-evidence: could-not-evaluate", "finding snapshot_tampered:"],
        )
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
