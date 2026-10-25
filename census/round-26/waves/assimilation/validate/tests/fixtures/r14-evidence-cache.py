#!/usr/bin/env python3
"""r14-evidence-cache.py — external replay for tools/souji-evidence-cache.py.

This fixture is a black-box regression harness, not a certifier. It invokes
the gate only through its documented CLI, with `--record` as a regular JSON
file path (the retention-runner integration form), and asserts exit codes and
exact finding ids as literals. Expected ids are never read back from the tool.

Cases cover the declared-dependency contract: a clean record, a changed
dependency, an unrelated changed file, a missing dependency, a symlinked
dependency, a malformed digest, a path escape, an incident `matched: false`
record, a legacy record without dependencies, empty dependencies, duplicate
JSON keys, a non-regular dependency, a malformed measured_commit, a
non-boolean matched, an undeclared required dependency, a protected root and
record path, and the committed pinned snapshot (clean, tampered, and
verdict-mismatch).

Scratch space is always `tempfile.mkdtemp(dir="/var/tmp")`, removed in a
finally block. The scratch HOME is synthetic and lives under that tree; no
real credential store is read. There is no /dev/shm use and no /tmp fallback.

    python3 tests/fixtures/r14-evidence-cache.py [--tool PATH] [--frozen-dir DIR]

Exit codes: 0 all checks passed, 1 assertion failed, 2 prerequisite missing.
A missing --tool path is a distinct prerequisite diagnostic, so an absent
baseline cannot be mistaken for a passing run.
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
DEFAULT_TOOL = LANE / "tools" / "souji-evidence-cache.py"
DEFAULT_FROZEN = LANE / "tests" / "fixtures" / "r14-cache-frozen"
COMMIT = "0123456789abcdef0123456789abcdef01234567"
COMMIT_ALT = "89abcdef0123456789abcdef0123456789abcdef"
MIN_CASES = 20


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path, obj):
    write_text(path, json.dumps(obj, indent=2, sort_keys=True) + "\n")


def invoke(tool, env, *arguments):
    return subprocess.run(
        [sys.executable, str(tool), *arguments],
        capture_output=True,
        text=True,
        timeout=180,
        env=env,
    )


def finding_ids(proc):
    return sorted(re.findall(r"(?m)^finding ([a-z0-9_-]+):", proc.stdout))


def check(results, name, proc, want_rc, want_ids, extra_needles=(), exact_lines=()):
    problems = []
    if proc.returncode != want_rc:
        problems.append("rc=%r want %d" % (proc.returncode, want_rc))
    observed = finding_ids(proc)
    if observed != sorted(want_ids):
        problems.append("findings=%r want %r" % (observed, sorted(want_ids)))
    for needle in extra_needles:
        if needle not in proc.stdout:
            problems.append("stdout missing %r" % (needle,))
    for line in exact_lines:
        if not re.search(r"(?m)^%s$" % re.escape(line), proc.stdout):
            problems.append("stdout missing exact line %r" % (line,))
    results.append((name, problems, proc))
    return not problems


def case_root(base, name):
    root = base / "cases" / name
    root.mkdir(parents=True)
    write_text(root / "src/a.txt", "alpha dependency\n")
    write_text(root / "src/b.txt", "beta dependency\n")
    write_text(root / "notes/unrelated.txt", "not a dependency\n")
    return root


def base_record(root, dependencies=None, matched=True, commit=COMMIT):
    if dependencies is None:
        dependencies = {
            "src/a.txt": sha256_text((root / "src/a.txt").read_text(encoding="utf-8")),
            "src/b.txt": sha256_text((root / "src/b.txt").read_text(encoding="utf-8")),
        }
    return {
        "name": "r14-fixture",
        "matched": matched,
        "measured_commit": commit,
        "dependencies": dependencies,
    }


def emit_record(root, record):
    write_json(root / "record.json", record)
    return str(root / "record.json")


def frozen_expected(root, verdict="reusable"):
    return {
        "record": "record.json",
        "verdict": verdict,
        "files": {
            "record.json": sha256_text((root / "record.json").read_text(encoding="utf-8")),
            "src/a.txt": sha256_text((root / "src/a.txt").read_text(encoding="utf-8")),
            "src/b.txt": sha256_text((root / "src/b.txt").read_text(encoding="utf-8")),
        },
    }


def run_case(root, env, tool, record_path, *extra):
    return invoke(tool, env, "--root", str(root), "--record", record_path, *extra)


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
    if not frozen.is_dir():
        print("fixture: frozen snapshot directory missing: %s" % frozen)
        return 2

    try:
        base = Path(tempfile.mkdtemp(prefix="souji-r14-cache-fixture.", dir="/var/tmp"))
    except OSError as exc:
        print("fixture: scratch unavailable: %s" % exc)
        return 2
    results = []
    try:
        home = base / "home"
        (home / ".ssh").mkdir(parents=True)
        write_text(home / ".ssh/id_ed25519", "synthetic home, never read\n")
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "LC_ALL": "C",
            "TMPDIR": "/var/tmp",
            "HOME": str(home),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        selftest = invoke(tool, env, "--selftest")
        if check(results, "selftest", selftest, 0, [], ["selftest: ", " passed"]):
            match = re.search(r"(?m)^selftest: (\d+)/(\d+) passed$", selftest.stdout)
            if match is None or match.group(1) != match.group(2) or int(match.group(2)) < MIN_CASES:
                results[-1][1].append(
                    "selftest summary missing or below %d cases" % MIN_CASES)

        root = case_root(base, "clean")
        record = emit_record(root, base_record(root))
        clean = run_case(root, env, tool, record)
        check(results, "external-clean", clean, 0, [],
              exact_lines=["souji-evidence-cache: reusable",
                           "measured_commit: " + COMMIT,
                           "dependencies: 2"])

        root = case_root(base, "changed-dependency")
        record = emit_record(root, base_record(root))
        write_text(root / "src/a.txt", "changed after the measurement\n")
        changed = run_case(root, env, tool, record)
        check(results, "changed-dependency", changed, 1,
              ["dependency-digest-mismatch"],
              exact_lines=["souji-evidence-cache: stale",
                           "measured_commit: " + COMMIT])

        root = case_root(base, "unrelated-change")
        record = emit_record(root, base_record(root))
        write_text(root / "notes/unrelated.txt", "edited after the measurement\n")
        unrelated = run_case(root, env, tool, record)
        check(results, "unchanged-unrelated-change", unrelated, 0, [],
              exact_lines=["souji-evidence-cache: reusable"])

        root = case_root(base, "missing-dependency")
        record = emit_record(root, base_record(root))
        (root / "src/b.txt").unlink()
        missing = run_case(root, env, tool, record)
        check(results, "missing-dependency", missing, 1, ["dependency-missing"],
              ["souji-evidence-cache: stale"])

        root = case_root(base, "symlink-dependency")
        target = root / "src/real.txt"
        write_text(target, "alpha dependency\n")
        (root / "src/a.txt").unlink()
        os.symlink(target, root / "src/a.txt")
        record = emit_record(root, base_record(root, dependencies={
            "src/a.txt": sha256_text("alpha dependency\n"),
            "src/b.txt": sha256_text("beta dependency\n"),
        }))
        symlinked = run_case(root, env, tool, record)
        check(results, "symlink-dependency", symlinked, 2, ["path-symlink"],
              ["souji-evidence-cache: could-not-evaluate"])

        root = case_root(base, "malformed-hash")
        record = emit_record(root, base_record(root, dependencies={
            "src/a.txt": "A" * 64,
            "src/b.txt": sha256_text("beta dependency\n"),
        }))
        bad_hash = run_case(root, env, tool, record)
        check(results, "malformed-hash", bad_hash, 2, ["dependency-digest-invalid"],
              ["souji-evidence-cache: could-not-evaluate"])

        root = case_root(base, "escape")
        write_text(base / "cases/outside.txt", "outside every root\n")
        record = emit_record(root, base_record(root, dependencies={
            "src/a.txt": sha256_text("alpha dependency\n"),
            "../outside.txt": sha256_text("outside every root\n"),
        }))
        escaped = run_case(root, env, tool, record)
        check(results, "path-escape", escaped, 2, ["path-escape"],
              ["souji-evidence-cache: could-not-evaluate"])

        root = case_root(base, "failed")
        record = emit_record(root, base_record(root, matched=False))
        failed = run_case(root, env, tool, record)
        check(results, "matched-false", failed, 1, ["matched-false"],
              exact_lines=["souji-evidence-cache: failed",
                           "measured_commit: " + COMMIT])

        root = case_root(base, "legacy")
        record = base_record(root)
        del record["dependencies"]
        legacy = run_case(root, env, tool, emit_record(root, record))
        check(results, "legacy-no-dependencies", legacy, 2, ["dependencies-legacy"],
              ["souji-evidence-cache: could-not-evaluate"])

        root = case_root(base, "empty-deps")
        empty = run_case(root, env, tool, emit_record(root, base_record(root, dependencies={})))
        check(results, "empty-dependencies", empty, 2, ["dependencies-empty"],
              ["souji-evidence-cache: could-not-evaluate"])

        root = case_root(base, "duplicate-keys")
        record = base_record(root)
        text = json.dumps(record, sort_keys=True)
        text = text[:-1] + ', "matched": false}\n'
        write_text(root / "record.json", text)
        duplicated = run_case(root, env, tool, str(root / "record.json"))
        check(results, "duplicate-json-keys", duplicated, 2, ["record-malformed"],
              ["souji-evidence-cache: could-not-evaluate"])

        root = case_root(base, "nonregular")
        (root / "src/dir").mkdir()
        record = emit_record(root, base_record(root, dependencies={
            "src/a.txt": sha256_text("alpha dependency\n"),
            "src/dir": "0" * 64,
        }))
        nonregular = run_case(root, env, tool, record)
        check(results, "nonregular-dependency", nonregular, 2,
              ["dependency-not-regular"],
              ["souji-evidence-cache: could-not-evaluate"])

        root = case_root(base, "bad-commit")
        record = emit_record(root, base_record(root, commit="deadbeef"))
        bad_commit = run_case(root, env, tool, record)
        check(results, "malformed-measured-commit", bad_commit, 2,
              ["measured_commit-invalid"],
              ["souji-evidence-cache: could-not-evaluate"])

        root = case_root(base, "bool-matched")
        record = base_record(root)
        record["matched"] = 1
        bool_matched = run_case(root, env, tool, emit_record(root, record))
        check(results, "nonboolean-matched", bool_matched, 2,
              ["matched-false-type"],
              ["souji-evidence-cache: could-not-evaluate"])

        root = case_root(base, "require-undeclared")
        record = emit_record(root, base_record(root))
        required = run_case(root, env, tool, record, "--require", "notes/unrelated.txt")
        check(results, "require-undeclared", required, 2,
              ["dependency-undeclared"],
              ["souji-evidence-cache: could-not-evaluate"])

        root = case_root(base, "root-protected")
        record = emit_record(root, base_record(root))
        root_refused = invoke(tool, env, "--root", str(home),
                              "--record", record)
        check(results, "protected-root", root_refused, 2, ["root-protected"],
              ["souji-evidence-cache: could-not-evaluate"])

        root = case_root(base, "record-protected")
        record = emit_record(root, base_record(root))
        record_refused = invoke(tool, env, "--root", str(root),
                                "--record", str(home / ".ssh/id_ed25519"))
        check(results, "protected-record", record_refused, 2, ["record-protected"],
              ["souji-evidence-cache: could-not-evaluate"])

        clean_frozen = invoke(tool, env, "--frozen", str(frozen))
        check(results, "frozen-clean", clean_frozen, 0, [],
              exact_lines=["souji-evidence-cache: reusable",
                           "measured_commit: " + COMMIT,
                           "frozen_files: 2"])

        tampered = base / "frozen-tampered"
        shutil.copytree(frozen, tampered, symlinks=True)
        with (tampered / "dependency.txt").open("ab") as handle:
            handle.write(b"tampered\n")
        tampered_proc = invoke(tool, env, "--frozen", str(tampered))
        check(results, "frozen-tampered", tampered_proc, 2, ["snapshot_tampered"],
              ["souji-evidence-cache: could-not-evaluate"])

        mismatch = base / "frozen-mismatch"
        shutil.copytree(frozen, mismatch, symlinks=True)
        expected = json.loads((mismatch / "expected.json").read_text(encoding="utf-8"))
        expected["verdict"] = "stale"
        write_json(mismatch / "expected.json", expected)
        mismatch_proc = invoke(tool, env, "--frozen", str(mismatch))
        check(results, "frozen-verdict-mismatch", mismatch_proc, 2,
              ["snapshot-verdict-mismatch"],
              ["souji-evidence-cache: could-not-evaluate"])

        root = case_root(base, "alt-commit")
        record = emit_record(root, base_record(root, commit=COMMIT_ALT))
        alt = run_case(root, env, tool, record)
        check(results, "per-result-commit", alt, 0, [],
              exact_lines=["measured_commit: " + COMMIT_ALT])
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
    if len(results) < MIN_CASES:
        failures.append(("case-count", ["%d cases ran, want >= %d"
                                        % (len(results), MIN_CASES)], None))
        print("FAIL case-count: %d cases ran, want >= %d"
              % (len(results), MIN_CASES))
    print("fixture: %d/%d checks passed" % (len(results) - len(failures), len(results)))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
