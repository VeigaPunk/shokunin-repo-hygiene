#!/usr/bin/env python3
"""Clone-isolated, byte-bound round-21 acceptance replay.

Replay a committed revision from any local repository containing it. The runner has a fixed,
small command allowlist; every command's exact result and owned-input digests
are retained in a new exclusive JSON file.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

BASELINE = "12516f7dcdd5b165e5ee208d44a38d63b5bd5812"
EXPECTED_COMMANDS = 18

# These are the actual bounded closures declared by the current r13/r14
# callers, plus each program/fixture whose behavior this acceptance exercises.
R13_MEASURED = (
    "tools/souji-verify.sh",
    "tools/souji-vault-verify.sh",
    "tools/souji-quarantine.sh",
    "tools/souji-census.sh",
    "tools/souji-cert-evidence.py",
    "tools/souji-repo-structure.sh",
    "tools/souji-evidence-cache.py",
    "tests/fixtures/r13-cert-evidence.py",
    "tests/fixtures/r13-repo-structure.sh",
    "tests/fixtures/r13-quarantine-bounds.sh",
    "tests/fixtures/r13-cert-frozen",
    "census/round-13/run-verification.py",
    "tools/souji-rev-pin.py",
    "tools/souji-round9-selftest.sh",
    "corpus/SOURCES.md",
    "corpus/knowledge",
    "LOG.md",
    "census/round-13/replay-wrong-bytes.json",
    "census/round-13/replay-candidate.json",
    "census/round-13/replay-fragments",
    "census/round-10/cert-16.json",
    "tools/cand-census-03.sh",
    "census/round-13/verification.json",
    "census/round-13/count-claims.py",
)
R14_MEASURED = (
    "tools/souji-evidence-cache.py",
    "tools/souji-census.sh",
    "tests/fixtures/r14-evidence-cache.py",
    "tests/fixtures/r14-census-boundary.py",
    "census/round-14/cache-demonstration.py",
    "census/round-14/check-timeout-anchor.py",
    "census/round-14/run-verification.py",
    "census/round-13/run-verification.py",
    "tools/souji-rev-pin.py",
    "census/round-14/run-targeted.py",
    "tests/fixtures/r14-cache-frozen",
    "corpus/SOURCES.md",
    "census/round-13/verification.json",
    "census/round-14/verification-attempt-1.json",
    "census/round-14/count-claims.py",
)
INPUT_PATHS = tuple(sorted(set((
    *R13_MEASURED,
    *R14_MEASURED,
    "tools/souji-seat-audit.py",
    "tools/souji-landing-gate.py",
    "tools/souji-proc-census.sh",
    "tests/fixtures/r19-seat-audit-shapes.py",
    "tests/fixtures/r18-proc-census.sh",
    "tests/fixtures/r19-carry-wrap.py",
    "tests/fixtures/r18-landing-pointers.py",
    "tests/fixtures/r16-landing-gate.py",
    "tests/fixtures/r19-rev-pin.py",
    "census/round-19/probe-carry-invariants.py",
    "census/round-19/carry-invariants.txt",
    "census/round-19/verify-agreement-pin.py",
    "census/round-19/proc-agreement-pinned.json",
    "census/round-18/leak-count.py",
    "census/round-18/proc-agreement-counterfix.json",
    "census/round-18/proc-agreement-final.json",
    "census/round-18/counter-exclusion-repair.json",
    "corpus/README.md",
    "census/round-13/counts.json",
    "census/round-14/counts.json",
    "tests/fixtures/r20-audit-contract.py",
    "tests/fixtures/r20-input-binding.py",
    "census/round-21/run-acceptance.py",
    "census/round-21/step-inventory.json",
))))
INPUT_DIRS = (
    "tests/fixtures/r13-cert-frozen",
    "tests/fixtures/r14-cache-frozen",
    "census/round-13/replay-fragments",
    "corpus/knowledge",
)

CHILD_ENV = {
    "PATH": "/usr/bin:/bin",
    "LC_ALL": "C",
    "PYTHONUTF8": "1",
    "PYTHONDONTWRITEBYTECODE": "1",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_OPTIONAL_LOCKS": "0",
    "GIT_NO_LAZY_FETCH": "1",
    "GIT_TERMINAL_PROMPT": "0",
}
SUMMARY_RE = re.compile(r"^(?:SUMMARY|SELFTEST)(?:\t| ).*$")

COUNTER_EXPECTATIONS = (
    (
        "r13-counter-31984f4",
        "census/round-13/count-claims.py",
        "31984f473ce4bdab61a99b16cca194b28108cb81",
        {
            "F2_entry": 0, "admitted_entries": 4, "evidence_gate": 0,
            "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81",
            "sources": 33,
            "tiers": {"A": 29, "B": 3, "C": 1},
            "statuses": {"mined": 16, "queued": 15, "rejected": 2},
        }, True,
    ),
    (
        "r13-counter-6f8ee0f",
        "census/round-13/count-claims.py",
        "6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6",
        {
            "F2_entry": 1, "admitted_entries": 5, "evidence_gate": 1,
            "measured_commit": "6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6",
            "sources": 37,
            "tiers": {"A": 33, "B": 3, "C": 1},
            "statuses": {"mined": 20, "queued": 15, "rejected": 2},
        }, True,
    ),
    (
        "r14-counter-a31642d",
        "census/round-14/count-claims.py",
        "a31642d14006830ec62edf40b0354c3699728c4a",
        {
            "measured_commit": "a31642d14006830ec62edf40b0354c3699728c4a",
            "cache_gate": 0, "cache_fixture": 0, "boundary_fixture": 0,
            "source_rows": 37,
            "tiers": {"A": 33, "B": 3, "C": 1},
            "statuses": {"mined": 20, "queued": 15, "rejected": 2},
            "admitted_knowledge": 5, "held_knowledge": 1,
        }, True,
    ),
    (
        "r14-counter-552cae4",
        "census/round-14/count-claims.py",
        "552cae4204b3ab818419ad8adbfef3a4da29a3e0",
        {
            "measured_commit": "552cae4204b3ab818419ad8adbfef3a4da29a3e0",
            "cache_gate": 1, "cache_fixture": 1, "boundary_fixture": 1,
            "source_rows": 40,
            "tiers": {"A": 36, "B": 3, "C": 1},
            "statuses": {"mined": 23, "queued": 15, "rejected": 2},
            "admitted_knowledge": 5, "held_knowledge": 1,
        }, True,
    ),
    (
        "r13-counter-b576341",
        "census/round-13/count-claims.py",
        "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3",
        {
            "measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3",
            "admitted_entries": 6,
        }, False,
    ),
)


class Refusal(ValueError):
    """An unsafe or unbound acceptance invocation."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_regular(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise Refusal("input is not a regular non-symlink file: " + str(path))
    return path.read_bytes()


def decode_exact(data: bytes) -> str:
    return data.decode("utf-8", "surrogateescape")


def load_pin_helper(root: Path):
    helper = root / "tools" / "souji-rev-pin.py"
    read_regular(helper)
    spec = importlib.util.spec_from_file_location("souji_r20_acceptance_rev_pin", helper)
    if spec is None or spec.loader is None:
        raise Refusal("revision helper cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def external_inputs(baseline_tool: Path | None) -> dict[str, str]:
    if baseline_tool is None:
        return {}
    return {
        "baseline:tools/souji-seat-audit.py": sha256_bytes(read_regular(baseline_tool))
    }


def combined_snapshot(pin, root: Path, revision: str,
                      baseline_tool: Path | None) -> dict[str, str]:
    runtime_runner = read_regular(Path(__file__))
    committed_runner = read_regular(root / "census/round-21/run-acceptance.py")
    if runtime_runner != committed_runner:
        raise Refusal("running acceptance runner differs from committed measured bytes")
    result = pin.input_snapshot(str(root), revision, INPUT_PATHS)
    result.update(external_inputs(baseline_tool))
    return dict(sorted(result.items()))


def output_path(raw: str, root: Path) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        raise Refusal("output must be an absolute path outside the source repository")
    parent = candidate.parent.resolve(strict=True)
    if parent != candidate.parent or not parent.is_dir():
        raise Refusal("output parent must be an existing canonical non-symlink directory")
    candidate = parent / candidate.name
    if candidate == root or root in candidate.parents:
        raise Refusal("output must be outside the source repository")
    if candidate.exists() or candidate.is_symlink():
        raise Refusal("refusing existing output: " + str(candidate))
    return candidate


def extract_baseline_auditor(root: Path, temp_root: Path) -> tuple[Path, dict]:
    command = ["git", "-C", str(root), "show", BASELINE + ":tools/souji-seat-audit.py"]
    proc = subprocess.run(command, cwd=root, env=CHILD_ENV,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    details = {
        "command": shlex.join(command),
        "returncode": proc.returncode,
        "stdout_bytes": len(proc.stdout),
        "stdout_sha256": sha256_bytes(proc.stdout),
        "stderr": decode_exact(proc.stderr),
        "stderr_sha256": sha256_bytes(proc.stderr),
    }
    if proc.returncode != 0:
        raise Refusal("cannot extract baseline auditor from the preregistered revision")
    path = temp_root / "baseline-souji-seat-audit.py"
    with path.open("xb") as handle:
        handle.write(proc.stdout)
    path.chmod(0o600)
    details["file_sha256"] = sha256_bytes(read_regular(path))
    return path, details


def make_steps(root: Path, baseline_tool: Path, revision: str, agreement_root: Path) -> list[dict]:
    py = sys.executable
    auditor = root / "tools" / "souji-seat-audit.py"
    rev_pin = root / "tools" / "souji-rev-pin.py"
    gate = root / "tools" / "souji-landing-gate.py"
    def py_step(script: str, *args: str) -> list[str]:
        return [py, "-B", str(root / script), *args]
    steps = [
        {"name": "auditor-selftest", "argv": py_step("tools/souji-seat-audit.py", "--selftest"),
         "expected_summary": "SELFTEST\tpass=118\tfail=0", "pass_pattern": r"^PASS\t", "pass_count": 118},
        {"name": "revision-helper-selftest", "argv": py_step("tools/souji-rev-pin.py", "--selftest"),
         "expected_summary": "SUMMARY total=11 failed=0", "pass_pattern": r"^CASE\tpass\t", "pass_count": 11},
        {"name": "r20-audit-contract", "argv": [py, "-B", str(root / "tests/fixtures/r20-audit-contract.py"), "--tool", str(auditor), "--base-tool", str(baseline_tool)],
         "expected_summary": "SUMMARY\ttotal=78\tpass=78\tfail=0\tbase_discriminating=11",
         "pass_pattern": r"^CASE\tPASS\t", "pass_count": 78},
        {"name": "r20-input-binding", "argv": [py, "-B", str(root / "tests/fixtures/r20-input-binding.py"), "--root", str(root), "--baseline", BASELINE],
         "expected_summary": {
             "regex": r"SUMMARY\ttotal=52\tpass=52\tfail=0\tblocked=0\tinventory=exact\tbaseline_mismatches=(\d+)",
             "auxiliary_lines": ["INVENTORY\texact\texpected=52 observed=52 missing=- unexpected=- duplicates=0"],
             "baseline_mismatch_group": 1,
         },
         "baseline_mismatch_count": True,
         "pass_pattern": r"^CASE\tpass\t", "pass_count": 52},
        {"name": "r19-seat-audit-shapes", "argv": py_step("tests/fixtures/r19-seat-audit-shapes.py", "--tool", str(auditor)),
         "expected_summary": "SUMMARY total=17 failed=0 base_discriminating=12",
         "pass_pattern": r"^CASE\tpass\tchanged/", "pass_count": 17},
        {"name": "r19-carry-wrap", "argv": py_step("tests/fixtures/r19-carry-wrap.py", "--tool", str(gate)),
         "expected_summary": "SUMMARY total=4 failed=0 base_discriminating=2",
         "pass_pattern": r"^CASE\tpass\tchanged/", "pass_count": 4},
        {"name": "landing-gate-selftest", "argv": py_step("tools/souji-landing-gate.py", "--selftest"),
         "expected_summary": "SELFTEST\tpass=65\tfail=0", "pass_pattern": r"^CASE\tpass\t", "pass_count": 65},
        {"name": "r18-landing-pointers", "argv": py_step("tests/fixtures/r18-landing-pointers.py", "--tool", str(gate)),
         "expected_summary": "SUMMARY\ttotal=11\tfailed=0", "pass_pattern": r"^CASE\tPASS\t", "pass_count": 11},
        {"name": "r16-landing-gate", "argv": py_step("tests/fixtures/r16-landing-gate.py", "--tool", str(gate)),
         "expected_summary": "SUMMARY\ttotal=15\tfailed=0",
         "pass_pattern": r"^CASE\t[^\t]+\tPASS\t", "pass_count": 15},
        {"name": "carry-invariant-probe", "argv": py_step("census/round-19/probe-carry-invariants.py"),
         "expected_summary": "SUMMARY paragraphs=400 boundary_cuts=562 midline_cuts=842 violations=0",
         "pass_pattern": None, "pass_count": 0},
        {"name": "r19-revision-pin-fixture", "argv": py_step("tests/fixtures/r19-rev-pin.py", "--tool", str(rev_pin), "--tool-dir", str(root)),
         "expected_summary": "SUMMARY total=13 failed=0 base_discriminating=6",
         "pass_pattern": r"^CASE\tpass\t", "pass_count": 13},
        {"name": "agreement-pin-check", "argv": py_step("census/round-19/verify-agreement-pin.py", "--root", str(agreement_root), "--check", str(root / "census/round-19/proc-agreement-pinned.json")),
         "expected_summary": "", "pass_pattern": None, "pass_count": 0, "record_checks": 1},
        {"name": "clean-cache-demonstration", "argv": py_step("census/round-14/cache-demonstration.py", "--gate", str(root / "tools/souji-evidence-cache.py")),
         "kind": "cache-demo", "expected_summary": {
             "status": "ok", "measured_commit": revision, "cases": 4,
             "checks": 33, "failed_checks": [], "producer_executions_new_policy": 3,
             "inputs_unchanged_during_run": True, "isolation_cleaned": True,
         }},
    ]
    for name, script, revision_arg, expected, exact in COUNTER_EXPECTATIONS:
        steps.append({
            "name": name,
            "argv": py_step(script, revision_arg),
            "kind": "counter",
            "expected_summary": expected,
            "exact_json": exact,
        })
    return steps


def failure_lines(text: str) -> list[str]:
    return [line for line in text.splitlines()
            if line.startswith(("FAIL\t", "CASE\tFAIL\t"))
            or re.match(r"^CASE\t[^\t]+\tFAIL(?:\t|$)", line)]


def numeric_leaves(value, prefix: str = "") -> dict[str, int]:
    found: dict[str, int] = {}
    if isinstance(value, dict):
        for key, item in value.items():
            child = key if not prefix else prefix + "." + key
            found.update(numeric_leaves(item, child))
    elif isinstance(value, int) and not isinstance(value, bool):
        found[prefix] = value
    return found


def summarize_result(step: dict, returncode: int | None,
                     stdout_bytes: bytes, stderr_bytes: bytes,
                     revision: str, root: Path) -> dict:
    stdout = decode_exact(stdout_bytes)
    stderr = decode_exact(stderr_bytes)
    summary_lines = [line for line in stdout.splitlines() if SUMMARY_RE.match(line)]
    failures = failure_lines(stdout + ("\n" if stdout and stderr else "") + stderr)
    result = {
        "name": step["name"],
        "argv": step["argv"],
        "command": shlex.join(step["argv"]),
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
        "stdout_sha256": sha256_bytes(stdout_bytes),
        "stderr_sha256": sha256_bytes(stderr_bytes),
        "expected_summary": step["expected_summary"],
        "observed_summary": summary_lines,
        "failure_lines": failures,
    }
    matched = returncode == 0 and not failures
    kind = step.get("kind", "summary")
    if kind == "summary":
        expected = step["expected_summary"]
        reported_baseline_mismatches = None
        if isinstance(expected, str):
            summary_match = summary_lines == ([expected] if expected else [])
            expected_auxiliary = []
        else:
            summary_match = len(summary_lines) == 1
            summary_match = (
                summary_match
                and re.fullmatch(expected["regex"], summary_lines[0]) is not None
            )
            expected_auxiliary = expected.get("auxiliary_lines", [])
            group = expected.get("baseline_mismatch_group")
            if group is not None and summary_match:
                baseline_match = re.fullmatch(expected["regex"], summary_lines[0])
                reported_baseline_mismatches = int(baseline_match.group(group))
        observed_auxiliary = [
            line for line in stdout.splitlines() if line.startswith("INVENTORY\t")
        ]
        auxiliary_match = observed_auxiliary == expected_auxiliary
        summary_match = summary_match and auxiliary_match
        baseline_mismatch_lines = sum(
            line.startswith("BASELINE_MISMATCH\t") for line in stdout.splitlines()
        )
        if step.get("baseline_mismatch_count"):
            summary_match = (
                summary_match
                and reported_baseline_mismatches == baseline_mismatch_lines
            )
        result["observed_auxiliary_lines"] = observed_auxiliary
        pattern = step.get("pass_pattern")
        pass_count = (len(re.findall(pattern, stdout, re.MULTILINE))
                      if pattern else 0)
        expected_passes = step["pass_count"]
        pass_match = pass_count == expected_passes
        result["matched_counts"] = {
            "summary_lines": len(summary_lines),
            "expected_pass_lines": expected_passes,
            "observed_pass_lines": pass_count,
            "matched_pass_lines": min(pass_count, expected_passes),
            "expected_auxiliary_lines": len(expected_auxiliary),
            "observed_auxiliary_lines": len(observed_auxiliary),
            "matched_auxiliary_lines": sum(line in observed_auxiliary for line in expected_auxiliary),
            "baseline_mismatch_records": baseline_mismatch_lines,
            "baseline_mismatches_reported": reported_baseline_mismatches,
            "record_checks": step.get("record_checks", 0),
        }
        matched = matched and summary_match and pass_match
        if step["name"] == "carry-invariant-probe":
            matched = matched and not any(line.startswith("VIOLATION\t") for line in stdout.splitlines())
    elif kind == "counter":
        try:
            observed = json.loads(stdout)
        except (ValueError, TypeError):
            observed = None
        expected = step["expected_summary"]
        if step["exact_json"]:
            json_match = observed == expected
            expected_fields = numeric_leaves(expected)
        else:
            json_match = (isinstance(observed, dict)
                          and all(observed.get(key) == value for key, value in expected.items()))
            expected_fields = numeric_leaves(expected)
        observed_fields = numeric_leaves(observed) if isinstance(observed, dict) else {}
        result["observed_json"] = observed
        result["matched_counts"] = {
            "expected_fields": expected_fields,
            "observed_numeric_fields": observed_fields,
            "matched_expected_fields": sum(
                1 for key, value in expected_fields.items()
                if observed_fields.get(key) == value
            ),
            "expected_field_count": len(expected_fields),
            "historical_counter_records": 1,
        }
        matched = matched and json_match and not stderr
    elif kind == "cache-demo":
        try:
            payload = json.loads(stdout)
        except (ValueError, TypeError):
            payload = None
        checks = payload.get("checks") if isinstance(payload, dict) else None
        case_rows = payload.get("cases") if isinstance(payload, dict) else None
        expected = step["expected_summary"]
        gate_sha = sha256_bytes(read_regular(root / "tools/souji-evidence-cache.py"))
        isolation = payload.get("isolation", {}) if isinstance(payload, dict) else {}
        demo_match = (
            isinstance(payload, dict)
            and payload.get("status") == expected["status"]
            and payload.get("measured_commit") == revision
            and payload.get("harness_revision") == revision
            and isinstance(case_rows, list) and len(case_rows) == expected["cases"]
            and isinstance(checks, dict) and len(checks) == expected["checks"]
            and all(value is True for value in checks.values())
            and payload.get("failed_checks") == expected["failed_checks"]
            and payload.get("producer_executions_new_policy") == expected["producer_executions_new_policy"]
            and payload.get("inputs_unchanged_during_run") is expected["inputs_unchanged_during_run"]
            and payload.get("gate", {}).get("sha256") == gate_sha
            and isolation.get("cleaned") is expected["isolation_cleaned"]
            and isolation.get("residue") == []
        )
        result["observed_json"] = payload
        result["matched_counts"] = {
            "expected_cases": expected["cases"],
            "observed_cases": len(case_rows) if isinstance(case_rows, list) else 0,
            "expected_gate_checks": expected["checks"],
            "observed_gate_checks": len(checks) if isinstance(checks, dict) else 0,
            "matched_gate_checks": sum(value is True for value in checks.values()) if isinstance(checks, dict) else 0,
            "new_policy_producer_executions": payload.get("producer_executions_new_policy") if isinstance(payload, dict) else None,
        }
        matched = matched and demo_match and not stderr
    result["matched"] = bool(matched)
    return result


def write_exclusive(path: Path, payload: dict) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=True, indent=2, sort_keys=True)
        handle.write("\n")


def historical_agreement_root(root: Path, temp_root: Path) -> Path:
    """Check the immutable agreement's original bytes, not an upgraded tool."""
    record = json.loads(read_regular(root / "census/round-19/proc-agreement-pinned.json"))
    selected = temp_root / "agreement-inputs"
    selected.mkdir()
    for kind in ("tool", "counter"):
        entry = record[kind]
        relative = Path(entry["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise Refusal("unsafe agreement path")
        command = ["git", "-C", str(root), "show", entry["measured_commit"] + ":" + entry["path"]]
        proc = subprocess.run(command, env=CHILD_ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode or sha256_bytes(proc.stdout) != entry["sha256"]:
            raise Refusal("historical agreement artifact does not match recorded digest: " + kind)
        target = selected / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(proc.stdout)
    for relative, digest in record["agreement"].items():
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts:
            raise Refusal("unsafe agreement path")
        data = read_regular(root / relative)
        if sha256_bytes(data) != digest:
            raise Refusal("historical agreement changed: " + relative)
        target = selected / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return selected


def source_state(source: Path) -> dict:
    def git(*args):
        proc = subprocess.run(["git", "-c", "core.fsmonitor=false", "-C", str(source), *args], env=CHILD_ENV,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode:
            raise Refusal("source state cannot be read: " + decode_exact(proc.stderr))
        return decode_exact(proc.stdout).strip()
    bare = git("rev-parse", "--is-bare-repository") == "true"
    return {"head": git("rev-parse", "--verify", "HEAD^{commit}"),
            "bare": bare, "status": "" if bare else git("status", "--porcelain", "--untracked-files=no")}


def inventory_projection(steps: list[dict], root: Path, baseline: Path,
                         revision: str, agreement_root: Path) -> list[dict]:
    result = []
    for step in steps:
        row = {key: step[key] for key in ("name", "expected_summary", "pass_pattern",
               "pass_count", "record_checks", "exact_json", "baseline_mismatch_count") if key in step}
        row["kind"] = step.get("kind", "summary")
        row["argv"] = [
            arg.replace(str(agreement_root), "<ROOT>").replace(str(root), "<ROOT>")
               .replace(str(baseline), "<BASELINE>").replace(revision, "<REV>")
            for arg in step["argv"]
        ]
        row["argv"][0] = "<PYTHON>"
        result.append(json.loads(json.dumps(row).replace(revision, "<REV>")))
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="local source repository; never modified")
    parser.add_argument("--rev", required=True, help="full 40-hex durable integrated commit")
    parser.add_argument("--output", required=True, help="new exclusive JSON output path")
    args = parser.parse_args(argv)
    try:
        source = Path(args.root).resolve(strict=True)
        output = output_path(args.output, source)
        if not re.fullmatch(r"[0-9a-f]{40}", args.rev):
            raise Refusal("--rev must be a full 40-hex commit")
        original_state = source_state(source)
        with tempfile.TemporaryDirectory(prefix="souji-r21-replay-", dir="/var/tmp") as temp:
            temp_root = Path(temp)
            root = temp_root / "src"
            clone_cmd = ["git", "-c", "core.hooksPath=/dev/null", "clone", "--quiet", "--no-local", "--no-checkout",
                         "-c", "core.hooksPath=/dev/null", "--", str(source), str(root)]
            proc = subprocess.run(clone_cmd, env=CHILD_ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if proc.returncode:
                raise Refusal("clone failed: " + decode_exact(proc.stderr))
            proc = subprocess.run(["git", "-C", str(root), "-c", "core.hooksPath=/dev/null", "checkout", "--quiet", "--detach", args.rev],
                                  env=CHILD_ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if proc.returncode:
                raise Refusal("revision checkout failed: " + decode_exact(proc.stderr))
            clone_state = source_state(root)
            if clone_state["head"] != args.rev or clone_state["status"]:
                raise Refusal("clone HEAD/tree does not match revision")
            pin = load_pin_helper(root)
            pin.resolve_durable(str(root), args.rev, INPUT_PATHS, tree_check=True)
            baseline_tool, extraction = extract_baseline_auditor(root, temp_root)
            agreement_root = historical_agreement_root(root, temp_root)
            initial_snapshot = combined_snapshot(pin, root, args.rev, baseline_tool)
            steps = make_steps(root, baseline_tool, args.rev, agreement_root)
            if len(steps) != EXPECTED_COMMANDS or len(COUNTER_EXPECTATIONS) != 5:
                raise Refusal("fixed acceptance inventory changed")
            frozen = json.loads(read_regular(root / "census/round-21/step-inventory.json"))
            if inventory_projection(steps, root, baseline_tool, args.rev, agreement_root) != frozen["steps"]:
                raise Refusal("acceptance commands differ from the frozen r20 inventory")
            literal_lane = "/home/vgpnk/Projects/shokunin/" + "souji-shokunin"
            for step in steps:
                program = Path(step["argv"][2])
                if literal_lane in decode_exact(read_regular(program)):
                    raise Refusal("executed program contains non-relocatable lane literal: " + str(program.relative_to(root)))
            results = []
            for step in steps:
                before = combined_snapshot(pin, root, args.rev, baseline_tool)
                if before != initial_snapshot:
                    raise Refusal("owned acceptance inputs drifted before " + step["name"])
                try:
                    proc = subprocess.run(step["argv"], cwd=root, env=CHILD_ENV,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    returncode, stdout_bytes, stderr_bytes = proc.returncode, proc.stdout, proc.stderr
                except OSError as exc:
                    returncode, stdout_bytes = None, b""
                    stderr_bytes = ("invocation failed: %s: %s" % (type(exc).__name__, exc)).encode("utf-8", "replace")
                after = combined_snapshot(pin, root, args.rev, baseline_tool)
                if before != after:
                    raise Refusal("owned acceptance inputs drifted during " + step["name"])
                result = summarize_result(step, returncode, stdout_bytes, stderr_bytes, args.rev, root)
                result["input_sha256_before"] = before
                result["input_sha256_after"] = after
                results.append(result)
            final_snapshot = combined_snapshot(pin, root, args.rev, baseline_tool)
            pin.resolve_durable(str(root), args.rev, INPUT_PATHS, tree_check=True)
            final_state = source_state(source)
            if final_snapshot != initial_snapshot or final_state != original_state:
                raise Refusal("source or measured inputs drifted before output")
            record = {
                "schema": "souji-round21-replay-acceptance-v1",
                "root": str(root), "source_root": str(source), "source_state_before": original_state,
                "source_state_after": final_state, "source_unchanged": True,
                "measured_commit": args.rev, "baseline_commit": BASELINE,
                "revision_check": {"durable_full_id": True, "clone_head_equals_revision": True,
                                   "source_head_equals_revision": original_state["head"] == args.rev,
                                   "current_inputs_equal_revision": True},
                "expected_command_count": EXPECTED_COMMANDS, "observed_command_count": len(results),
                "matched_command_count": sum(item["matched"] for item in results),
                "all_matched": all(item["matched"] for item in results),
                "input_sha256_before": initial_snapshot, "input_sha256_after": final_snapshot,
                "inputs_unchanged": initial_snapshot == final_snapshot,
                "baseline_extraction": extraction, "clone_command": clone_cmd,
                "agreement_check_scope": "Original tool/counter bytes from their recorded revisions, verified against immutable record digests; no live census.",
                "scope": "Committed public repository inputs only, isolated clone; source HEAD/tree not measured; no live proc, signals or private data.",
                "commands": results,
            }
            write_exclusive(output, record)
    except (OSError, ValueError, RuntimeError, Refusal, KeyError) as exc:
        print("run-acceptance: refused with no new result: %s" % exc, file=sys.stderr)
        return 2
    return 0 if record["all_matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
