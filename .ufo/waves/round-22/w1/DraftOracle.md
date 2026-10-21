STATUS: PASS — delivered the requested standalone synthetic result-oracle draft in this report only. Source-only; the fixture was not saved separately or executed.

## Axes

- **Calibration:** literal expected decisions target JSON scalar-type confusion, summary stderr acceptance, and cache-check identity; additional nested/missing/null controls keep scalar comparison semantics explicit.
- **Operability:** `--runner` selects the implementation; the draft imports the runner and calls only `summarize_result`. Its only synthetic file is a fake cache-gate byte file under `/var/tmp`, automatically removed by `TemporaryDirectory`.
- **Coverage:** all 18 original acceptance-step positive controls have explicit projected-result vectors, alongside malformed JSON/shape controls. No axis score is inferred.

## Source evidence and bounds

Read the pinned baseline with `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py`. Its `summarize_result` implementation decodes counters with ordinary `json.loads` and compares exact JSON using `observed == expected` (lines 420–445), checks summary return code/failure markers/counts without a stderr-empty predicate (lines 330–333, 367–419), and validates cache checks by dictionary length plus `all(value is True ...)` without their identities (lines 446–480). The corresponding 18 frozen step expectations are in `census/round-21/step-inventory.json` (lines 6–338). The 33 canonical cache check names are source-derived from `census/round-14/cache-demonstration.py` (lines 879–979).

**Source-inferred, not executed:** the baseline admits `False` for an expected integer zero / `True` for integer one (and equal floats), can accept otherwise-matching summary stdout with an unrecognized non-empty stderr diagnostic, and can accept a 33-entry all-true cache map with one required check replaced by an unrelated name. Direct `.get` calls on explicit `null` cache `gate` or `isolation` values can raise instead of returning a non-match. The draft expects those malformed payloads to return `matched: false` without an exception. No process, subprocess, `/proc`, production input, historical snapshot, or test was read or executed. LSP is not present in the mounted tool inventory, so no LSP result is claimed. No tool was installed.

The positive vectors compare the exact projected fields `name`, `returncode`, `observed_summary`, `failure_lines`, `observed_auxiliary_lines`, `matched_counts`, and `matched`. These are synthetic projections reconstructed from the frozen inventory and source logic—not recovered historical command outputs, raw output hashes, or proof of historical execution. The report makes no arbitrary malicious-producer attestation claim.

## Draft fixture (report-only; not materialized as a separate file)

```python
#!/usr/bin/env python3
"""Synthetic-only oracle for the round-21 acceptance result summarizer."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

REVISION = "a" * 40
GATE_BYTES = b"synthetic cache gate; never executed\n"


def summary_step(name, argv, expected, pattern, count, **extra):
    return {
        "name": name,
        "argv": argv,
        "expected_summary": expected,
        "pass_pattern": pattern,
        "pass_count": count,
        "kind": "summary",
        **extra,
    }


def counter_step(name, argv, expected, exact=True):
    return {
        "name": name,
        "argv": argv,
        "expected_summary": expected,
        "exact_json": exact,
        "kind": "counter",
    }


# Literal source-inventory cases. argv strings are inert placeholders; this
# fixture never starts a command from them.
ORIGINAL_STEPS = [
    summary_step("auditor-selftest", ["<PYTHON>", "-B", "<ROOT>/tools/souji-seat-audit.py", "--selftest"],
                 "SELFTEST\tpass=118\tfail=0", r"^PASS\t", 118),
    summary_step("revision-helper-selftest", ["<PYTHON>", "-B", "<ROOT>/tools/souji-rev-pin.py", "--selftest"],
                 "SUMMARY total=11 failed=0", r"^CASE\tpass\t", 11),
    summary_step("r20-audit-contract", ["<PYTHON>", "-B", "<ROOT>/tests/fixtures/r20-audit-contract.py",
                 "--tool", "<ROOT>/tools/souji-seat-audit.py", "--base-tool", "<BASELINE>"],
                 "SUMMARY\ttotal=78\tpass=78\tfail=0\tbase_discriminating=11", r"^CASE\tPASS\t", 78),
    summary_step("r20-input-binding", ["<PYTHON>", "-B", "<ROOT>/tests/fixtures/r20-input-binding.py",
                 "--root", "<ROOT>", "--baseline", "12516f7dcdd5b165e5ee208d44a38d63b5bd5812"],
                 {"regex": r"SUMMARY\ttotal=52\tpass=52\tfail=0\tblocked=0\tinventory=exact\tbaseline_mismatches=(\d+)",
                  "auxiliary_lines": ["INVENTORY\texact\texpected=52 observed=52 missing=- unexpected=- duplicates=0"],
                  "baseline_mismatch_group": 1},
                 r"^CASE\tpass\t", 52, baseline_mismatch_count=True),
    summary_step("r19-seat-audit-shapes", ["<PYTHON>", "-B", "<ROOT>/tests/fixtures/r19-seat-audit-shapes.py",
                 "--tool", "<ROOT>/tools/souji-seat-audit.py"],
                 "SUMMARY total=17 failed=0 base_discriminating=12", r"^CASE\tpass\tchanged/", 17),
    summary_step("r19-carry-wrap", ["<PYTHON>", "-B", "<ROOT>/tests/fixtures/r19-carry-wrap.py",
                 "--tool", "<ROOT>/tools/souji-landing-gate.py"],
                 "SUMMARY total=4 failed=0 base_discriminating=2", r"^CASE\tpass\tchanged/", 4),
    summary_step("landing-gate-selftest", ["<PYTHON>", "-B", "<ROOT>/tools/souji-landing-gate.py", "--selftest"],
                 "SELFTEST\tpass=65\tfail=0", r"^CASE\tpass\t", 65),
    summary_step("r18-landing-pointers", ["<PYTHON>", "-B", "<ROOT>/tests/fixtures/r18-landing-pointers.py",
                 "--tool", "<ROOT>/tools/souji-landing-gate.py"],
                 "SUMMARY\ttotal=11\tfailed=0", r"^CASE\tPASS\t", 11),
    summary_step("r16-landing-gate", ["<PYTHON>", "-B", "<ROOT>/tests/fixtures/r16-landing-gate.py",
                 "--tool", "<ROOT>/tools/souji-landing-gate.py"],
                 "SUMMARY\ttotal=15\tfailed=0", r"^CASE\t[^\t]+\tPASS\t", 15),
    summary_step("carry-invariant-probe", ["<PYTHON>", "-B", "<ROOT>/census/round-19/probe-carry-invariants.py"],
                 "SUMMARY paragraphs=400 boundary_cuts=562 midline_cuts=842 violations=0", None, 0),
    summary_step("r19-revision-pin-fixture", ["<PYTHON>", "-B", "<ROOT>/tests/fixtures/r19-rev-pin.py",
                 "--tool", "<ROOT>/tools/souji-rev-pin.py", "--tool-dir", "<ROOT>"],
                 "SUMMARY total=13 failed=0 base_discriminating=6", r"^CASE\tpass\t", 13),
    summary_step("agreement-pin-check", ["<PYTHON>", "-B", "<ROOT>/census/round-19/verify-agreement-pin.py",
                 "--root", "<ROOT>", "--check", "<ROOT>/census/round-19/proc-agreement-pinned.json"],
                 "", None, 0, record_checks=1),
    {
        "name": "clean-cache-demonstration",
        "argv": ["<PYTHON>", "-B", "<ROOT>/census/round-14/cache-demonstration.py",
                 "--gate", "<ROOT>/tools/souji-evidence-cache.py"],
        "kind": "cache-demo",
        "expected_summary": {
            "status": "ok", "measured_commit": REVISION, "cases": 4, "checks": 33,
            "failed_checks": [], "producer_executions_new_policy": 3,
            "inputs_unchanged_during_run": True, "isolation_cleaned": True,
        },
    },
    counter_step("r13-counter-31984f4", ["<PYTHON>", "-B", "<ROOT>/census/round-13/count-claims.py",
                 "31984f473ce4bdab61a99b16cca194b28108cb81"],
                 {"F2_entry": 0, "admitted_entries": 4, "evidence_gate": 0,
                  "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81", "sources": 33,
                  "tiers": {"A": 29, "B": 3, "C": 1},
                  "statuses": {"mined": 16, "queued": 15, "rejected": 2}}),
    counter_step("r13-counter-6f8ee0f", ["<PYTHON>", "-B", "<ROOT>/census/round-13/count-claims.py",
                 "6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6"],
                 {"F2_entry": 1, "admitted_entries": 5, "evidence_gate": 1,
                  "measured_commit": "6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6", "sources": 37,
                  "tiers": {"A": 33, "B": 3, "C": 1},
                  "statuses": {"mined": 20, "queued": 15, "rejected": 2}}),
    counter_step("r14-counter-a31642d", ["<PYTHON>", "-B", "<ROOT>/census/round-14/count-claims.py",
                 "a31642d14006830ec62edf40b0354c3699728c4a"],
                 {"measured_commit": "a31642d14006830ec62edf40b0354c3699728c4a",
                  "cache_gate": 0, "cache_fixture": 0, "boundary_fixture": 0, "source_rows": 37,
                  "tiers": {"A": 33, "B": 3, "C": 1},
                  "statuses": {"mined": 20, "queued": 15, "rejected": 2},
                  "admitted_knowledge": 5, "held_knowledge": 1}),
    counter_step("r14-counter-552cae4", ["<PYTHON>", "-B", "<ROOT>/census/round-14/count-claims.py",
                 "552cae4204b3ab818419ad8adbfef3a4da29a3e0"],
                 {"measured_commit": "552cae4204b3ab818419ad8adbfef3a4da29a3e0",
                  "cache_gate": 1, "cache_fixture": 1, "boundary_fixture": 1, "source_rows": 40,
                  "tiers": {"A": 36, "B": 3, "C": 1},
                  "statuses": {"mined": 23, "queued": 15, "rejected": 2},
                  "admitted_knowledge": 5, "held_knowledge": 1}),
    counter_step("r13-counter-b576341", ["<PYTHON>", "-B", "<ROOT>/census/round-13/count-claims.py",
                 "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3"],
                 {"measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3",
                  "admitted_entries": 6}, exact=False),
]
STEP_BY_NAME = {step["name"]: step for step in ORIGINAL_STEPS}

# Exact check identities emitted by the named r14 cache demonstration source.
CACHE_CHECK_NAMES = (
    "initial_fresh_once", "producer_actual_subprocess_green", "unchanged_gate_exit_zero",
    "unchanged_gate_status_reusable", "changed_dependency_exact_finding", "legacy_exact_finding",
    "unchanged_reused_without_producer", "unchanged_retained_measured_commit",
    "changed_dependency_gate_exit_one", "changed_dependency_not_reused",
    "changed_dependency_producer_executed", "changed_dependency_fresh_digests",
    "legacy_gate_exit_two", "legacy_not_reused", "legacy_producer_executed", "legacy_fresh_digests",
    "only_declared_dependency_changed", "record_bytes_unchanged", "gate_digest_recorded_and_unchanged",
    "execution_log_matches_disk", "isolation_confined", "unsafe_control_would_retain_stale_green",
    "unsafe_control_would_retain_legacy_green", "baseline_authentic_retention",
    "baseline_stale_green_reused", "new_caller_refused_same_record_and_reexecuted",
    "historical_legacy_records_refused", "migrated_caller_reuses_unchanged",
    "migrated_caller_refuses_stale", "migrated_caller_refuses_legacy",
    "migrated_caller_refuses_missing_revision", "migrated_caller_refuses_unstable",
    "migrated_caller_reruns_external_mutable",
)

# Each summary vector is (literal observed line, literal auxiliary lines,
# exact count tuple). Count tuple fields follow SUMMARY_COUNT_FIELDS below.
SUMMARY_VECTORS = {
    "auditor-selftest": ("SELFTEST\tpass=118\tfail=0", (), (1, 118, 118, 118, 0, 0, 0, 0, None, 0)),
    "revision-helper-selftest": ("SUMMARY total=11 failed=0", (), (1, 11, 11, 11, 0, 0, 0, 0, None, 0)),
    "r20-audit-contract": ("SUMMARY\ttotal=78\tpass=78\tfail=0\tbase_discriminating=11", (), (1, 78, 78, 78, 0, 0, 0, 0, None, 0)),
    "r20-input-binding": ("SUMMARY\ttotal=52\tpass=52\tfail=0\tblocked=0\tinventory=exact\tbaseline_mismatches=0",
                          ("INVENTORY\texact\texpected=52 observed=52 missing=- unexpected=- duplicates=0",),
                          (1, 52, 52, 52, 1, 1, 1, 0, 0, 0)),
    "r19-seat-audit-shapes": ("SUMMARY total=17 failed=0 base_discriminating=12", (), (1, 17, 17, 17, 0, 0, 0, 0, None, 0)),
    "r19-carry-wrap": ("SUMMARY total=4 failed=0 base_discriminating=2", (), (1, 4, 4, 4, 0, 0, 0, 0, None, 0)),
    "landing-gate-selftest": ("SELFTEST\tpass=65\tfail=0", (), (1, 65, 65, 65, 0, 0, 0, 0, None, 0)),
    "r18-landing-pointers": ("SUMMARY\ttotal=11\tfailed=0", (), (1, 11, 11, 11, 0, 0, 0, 0, None, 0)),
    "r16-landing-gate": ("SUMMARY\ttotal=15\tfailed=0", (), (1, 15, 15, 15, 0, 0, 0, 0, None, 0)),
    "carry-invariant-probe": ("SUMMARY paragraphs=400 boundary_cuts=562 midline_cuts=842 violations=0", (), (1, 0, 0, 0, 0, 0, 0, 0, None, 0)),
    "r19-revision-pin-fixture": ("SUMMARY total=13 failed=0 base_discriminating=6", (), (1, 13, 13, 13, 0, 0, 0, 0, None, 0)),
    "agreement-pin-check": ("", (), (0, 0, 0, 0, 0, 0, 0, 0, None, 1)),
}
SUMMARY_PASS_FORMATS = {
    "auditor-selftest": "PASS\tcase-{i:03d}",
    "revision-helper-selftest": "CASE\tpass\tcase-{i:03d}",
    "r20-audit-contract": "CASE\tPASS\tcase-{i:03d}",
    "r20-input-binding": "CASE\tpass\tcase-{i:03d}",
    "r19-seat-audit-shapes": "CASE\tpass\tchanged/case-{i:03d}",
    "r19-carry-wrap": "CASE\tpass\tchanged/case-{i:03d}",
    "landing-gate-selftest": "CASE\tpass\tcase-{i:03d}",
    "r18-landing-pointers": "CASE\tPASS\tcase-{i:03d}",
    "r16-landing-gate": "CASE\tname-{i:03d}\tPASS\tcase",
    "r19-revision-pin-fixture": "CASE\tpass\tcase-{i:03d}",
}
SUMMARY_COUNT_FIELDS = (
    "summary_lines", "expected_pass_lines", "observed_pass_lines", "matched_pass_lines",
    "expected_auxiliary_lines", "observed_auxiliary_lines", "matched_auxiliary_lines",
    "baseline_mismatch_records", "baseline_mismatches_reported", "record_checks",
)

# Flat numeric-leaf maps are the literal expected projections for the five
# original counters. Their exact counts intentionally are not inferred from
# the result under test.
COUNTER_LEAVES = {
    "r13-counter-31984f4": (10, {"F2_entry": 0, "admitted_entries": 4, "evidence_gate": 0,
        "sources": 33, "tiers.A": 29, "tiers.B": 3, "tiers.C": 1,
        "statuses.mined": 16, "statuses.queued": 15, "statuses.rejected": 2}),
    "r13-counter-6f8ee0f": (10, {"F2_entry": 1, "admitted_entries": 5, "evidence_gate": 1,
        "sources": 37, "tiers.A": 33, "tiers.B": 3, "tiers.C": 1,
        "statuses.mined": 20, "statuses.queued": 15, "statuses.rejected": 2}),
    "r14-counter-a31642d": (12, {"cache_gate": 0, "cache_fixture": 0, "boundary_fixture": 0,
        "source_rows": 37, "tiers.A": 33, "tiers.B": 3, "tiers.C": 1,
        "statuses.mined": 20, "statuses.queued": 15, "statuses.rejected": 2,
        "admitted_knowledge": 5, "held_knowledge": 1}),
    "r14-counter-552cae4": (12, {"cache_gate": 1, "cache_fixture": 1, "boundary_fixture": 1,
        "source_rows": 40, "tiers.A": 36, "tiers.B": 3, "tiers.C": 1,
        "statuses.mined": 23, "statuses.queued": 15, "statuses.rejected": 2,
        "admitted_knowledge": 5, "held_knowledge": 1}),
    "r13-counter-b576341": (1, {"admitted_entries": 6}),
}
CACHE_POSITIVE_COUNTS = {
    "expected_cases": 4, "observed_cases": 4, "expected_gate_checks": 33,
    "observed_gate_checks": 33, "matched_gate_checks": 33,
    "new_policy_producer_executions": 3,
}


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def clone_json(value):
    return json.loads(json.dumps(value))


def build_cache_payload(root):
    old = {"observations/alpha.txt": "a" * 64, "observations/beta.txt": "b" * 64}
    changed = {"observations/alpha.txt": "a" * 64, "observations/beta.txt": "c" * 64}
    phases = (
        ("initial-fresh", old, True, None, None, 1, "fresh-execution", False),
        ("unchanged", old, True, 0, True, 1, "retained-from-record", True),
        ("dependency-modified", changed, False, 1, False, 2, "fresh-execution", False),
        ("legacy-no-dependencies", old, False, 2, False, 3, "fresh-execution", False),
    )
    cases = []
    for phase, observed, digests_match, gate_exit, reusable, executions, origin, retained in phases:
        declared = {"name": "r14-cache-demonstration", "matched": True,
                    "measured_commit": REVISION}
        if phase != "legacy-no-dependencies":
            declared["dependencies"] = dict(old)
        result = {"name": "r14-cache-demonstration", "matched": True,
                  "measured_commit": REVISION, "harness_revision": REVISION,
                  "dependencies": dict(observed), "dependencies_stable": True,
                  "result_origin": origin}
        cases.append({
            "phase": phase, "record": "synthetic/record.json", "record_sha256": "0" * 64,
            "declared": declared, "observed_dependencies": dict(observed),
            "declared_dependency_digests_match": digests_match,
            "gate": None if gate_exit is None else {"exit_code": gate_exit, "findings": []},
            "gate_exit": gate_exit, "reusable": reusable, "result": result,
            "retained": retained,
            "producer_execution": None if retained else {"phase": phase, "executions_after": executions},
            "executions_after": executions,
        })
    gate_digest = hashlib.sha256(GATE_BYTES).hexdigest()
    return {
        "schema": "souji-r14-cache-demonstration-v1",
        "demonstration": "digest-bound-retention",
        "status": "ok", "measured_commit": REVISION, "harness_revision": REVISION,
        "cases": cases, "checks": {name: True for name in CACHE_CHECK_NAMES},
        "failed_checks": [], "producer_executions_new_policy": 3,
        "inputs_unchanged_during_run": True,
        "gate": {"sha256": gate_digest},
        "isolation": {"cleaned": True, "residue": []},
        "deletion_certification": "OFF",
    }


def synthetic_stdout(step, root):
    kind = step.get("kind", "summary")
    if kind == "summary":
        summary, auxiliary, _ = SUMMARY_VECTORS[step["name"]]
        lines = ([summary] if summary else []) + list(auxiliary)
        line_format = SUMMARY_PASS_FORMATS.get(step["name"])
        if line_format:
            lines.extend(line_format.format(i=index) for index in range(step["pass_count"]))
        return (("\n".join(lines) + "\n") if lines else "").encode("utf-8")
    if kind == "counter":
        payload = clone_json(step["expected_summary"])
        if not step["exact_json"]:
            payload["producer_note"] = "synthetic top-level extension"
        return json_bytes(payload)
    if kind == "cache-demo":
        return json_bytes(build_cache_payload(root))
    raise ValueError("unknown synthetic step kind: " + str(kind))


def expected_projection(step):
    name = step["name"]
    kind = step.get("kind", "summary")
    if kind == "summary":
        summary, auxiliary, counts = SUMMARY_VECTORS[name]
        matched_counts = dict(zip(SUMMARY_COUNT_FIELDS, counts))
        observed_summary = [summary] if summary else []
        observed_auxiliary = list(auxiliary)
    elif kind == "counter":
        exact_count, leaves = COUNTER_LEAVES[name]
        matched_counts = {
            "expected_fields": leaves, "observed_numeric_fields": leaves,
            "matched_expected_fields": exact_count, "expected_field_count": exact_count,
            "historical_counter_records": 1,
        }
        observed_summary, observed_auxiliary = [], None
    elif kind == "cache-demo":
        matched_counts = CACHE_POSITIVE_COUNTS
        observed_summary, observed_auxiliary = [], None
    else:
        raise ValueError("unknown expected step kind: " + str(kind))
    return {
        "name": name, "returncode": 0, "observed_summary": observed_summary,
        "failure_lines": [], "observed_auxiliary_lines": observed_auxiliary,
        "matched_counts": matched_counts, "matched": True,
    }


def project(result):
    return {
        "name": result.get("name"), "returncode": result.get("returncode"),
        "observed_summary": result.get("observed_summary"),
        "failure_lines": result.get("failure_lines"),
        "observed_auxiliary_lines": result.get("observed_auxiliary_lines"),
        "matched_counts": result.get("matched_counts"), "matched": result.get("matched"),
    }


EXPECTED_EDGE_DECISIONS = {
    "defect.counter.false-for-zero": False,
    "defect.counter.true-for-one": False,
    "defect.counter.float-for-zero": False,
    "defect.counter.nested-true-for-one": False,
    "defect.summary.nonempty-stderr": False,
    "defect.cache.replaced-required-check": False,
    "control.counter.subset-top-level-extension": True,
    "defect.counter.subset-missing-is-not-null": False,
    "control.counter.subset-present-null": True,
    "defect.counter.subset-nested-boolean": False,
    "defect.counter.subset-nested-extra-key": False,
    "defect.counter.subset-list-length": False,
    "malformed.counter.invalid-json": False,
    "malformed.counter.non-object-json": False,
    "malformed.cache.invalid-json": False,
    "malformed.cache.null-gate": False,
    "malformed.cache.null-isolation": False,
    "malformed.cache.checks-not-object": False,
    "malformed.cache.cases-not-list": False,
    "malformed.cache.top-level-array": False,
}


def subset_step(name, expected):
    return {"name": name, "argv": ["<PYTHON>", "<synthetic-json>"],
            "kind": "counter", "exact_json": False, "expected_summary": expected}


def edge_vectors(root):
    vectors = []

    def add(name, step, stdout, stderr=b""):
        vectors.append((name, step, stdout, stderr, EXPECTED_EDGE_DECISIONS[name]))

    step = clone_json(STEP_BY_NAME["r13-counter-31984f4"])
    payload = clone_json(step["expected_summary"])
    payload["F2_entry"] = False
    add("defect.counter.false-for-zero", step, json_bytes(payload))

    step = clone_json(STEP_BY_NAME["r13-counter-6f8ee0f"])
    payload = clone_json(step["expected_summary"])
    payload["F2_entry"] = True
    add("defect.counter.true-for-one", step, json_bytes(payload))

    step = clone_json(STEP_BY_NAME["r13-counter-31984f4"])
    payload = clone_json(step["expected_summary"])
    payload["F2_entry"] = 0.0
    add("defect.counter.float-for-zero", step, json_bytes(payload))

    step = clone_json(STEP_BY_NAME["r13-counter-6f8ee0f"])
    payload = clone_json(step["expected_summary"])
    payload["tiers"]["C"] = True
    add("defect.counter.nested-true-for-one", step, json_bytes(payload))

    step = clone_json(STEP_BY_NAME["auditor-selftest"])
    add("defect.summary.nonempty-stderr", step, synthetic_stdout(step, root),
        b"ERROR: synthetic self-test diagnostic\n")

    step = clone_json(STEP_BY_NAME["clean-cache-demonstration"])
    payload = build_cache_payload(root)
    del payload["checks"]["initial_fresh_once"]
    payload["checks"]["unrelated_replacement"] = True
    add("defect.cache.replaced-required-check", step, json_bytes(payload))

    add("control.counter.subset-top-level-extension",
        subset_step("subset-top-level-extension", {"admitted_entries": 6}),
        json_bytes({"admitted_entries": 6, "extension": "allowed"}))
    add("defect.counter.subset-missing-is-not-null",
        subset_step("subset-missing-is-not-null", {"selected": None}), json_bytes({}))
    add("control.counter.subset-present-null",
        subset_step("subset-present-null", {"selected": None}), json_bytes({"selected": None}))
    add("defect.counter.subset-nested-boolean",
        subset_step("subset-nested-boolean", {"shape": {"rows": [{"count": 1}]}}),
        json_bytes({"shape": {"rows": [{"count": True}]}}))
    add("defect.counter.subset-nested-extra-key",
        subset_step("subset-nested-extra-key", {"shape": {"rows": [{"count": 1}]}}),
        json_bytes({"shape": {"rows": [{"count": 1, "extra": 0}]}}))
    add("defect.counter.subset-list-length",
        subset_step("subset-list-length", {"shape": {"rows": [{"count": 1}]}}),
        json_bytes({"shape": {"rows": [{"count": 1}, {"count": 1}]}}))

    step = clone_json(STEP_BY_NAME["r13-counter-31984f4"])
    add("malformed.counter.invalid-json", step, b"{not-json")
    add("malformed.counter.non-object-json", step, b"null")
    step = clone_json(STEP_BY_NAME["clean-cache-demonstration"])
    add("malformed.cache.invalid-json", step, b"{not-json")
    payload = build_cache_payload(root)
    payload["gate"] = None
    add("malformed.cache.null-gate", step, json_bytes(payload))
    payload = build_cache_payload(root)
    payload["isolation"] = None
    add("malformed.cache.null-isolation", step, json_bytes(payload))
    payload = build_cache_payload(root)
    payload["checks"] = [True] * 33
    add("malformed.cache.checks-not-object", step, json_bytes(payload))
    payload = build_cache_payload(root)
    payload["cases"] = {"not": "a list"}
    add("malformed.cache.cases-not-list", step, json_bytes(payload))
    add("malformed.cache.top-level-array", step, b"[]")
    return vectors


def import_runner(raw_path):
    sys.dont_write_bytecode = True
    path = Path(raw_path).resolve(strict=True)
    spec = importlib.util.spec_from_file_location("souji_r22_result_oracle_target", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import the configured runner")
    target = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(target)
    if not callable(getattr(target, "summarize_result", None)):
        raise RuntimeError("configured runner has no summarize_result")
    return target, path


def observe(target, step, stdout, stderr):
    try:
        result = target.summarize_result(step, 0, stdout, stderr, REVISION, ROOT_FOR_CALLS)
    except Exception as exc:
        return None, "raised:" + type(exc).__name__
    if type(result) is not dict:
        return None, "non-dict-result"
    return result, None


ROOT_FOR_CALLS = None


def run_cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runner", required=True, help="path to the acceptance runner source to import")
    args = parser.parse_args()
    target, runner_path = import_runner(args.runner)
    rows = []
    with tempfile.TemporaryDirectory(prefix="souji-r22-result-oracle-", dir="/var/tmp") as temp:
        root = Path(temp)
        global ROOT_FOR_CALLS
        ROOT_FOR_CALLS = root
        gate = root / "tools" / "souji-evidence-cache.py"
        gate.parent.mkdir()
        gate.write_bytes(GATE_BYTES)

        for step in ORIGINAL_STEPS:
            name = step["name"]
            stdout = synthetic_stdout(step, root)
            result, error = observe(target, step, stdout, b"")
            actual = {"raised": error} if error else project(result)
            expected = expected_projection(step)
            rows.append({"name": name, "expected": expected, "observed": actual,
                         "passed": actual == expected})

        for name, step, stdout, stderr, expected in edge_vectors(root):
            result, error = observe(target, step, stdout, stderr)
            actual = error if error else result.get("matched")
            rows.append({"name": name, "expected": expected, "observed": actual,
                         "passed": type(actual) is bool and actual is expected})

    passed = all(row["passed"] for row in rows)
    print(json.dumps({"schema": "souji-r22-result-oracle-v1", "runner": str(runner_path),
                      "vectors": rows, "all_vectors_match": passed}, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(run_cli())
```

## Expected decisions and handoff

The fixture's fixed oracle is **18/18 original positives = true**, then the named false-green vectors `false-for-zero`, `true-for-one`, `float-for-zero`, `nested-true-for-one`, `summary.nonempty-stderr`, and `cache.replaced-required-check` = **false**. Subset controls explicitly retain top-level extensions and present nulls, while rejecting missing/null confusion and recursively mismatched nested scalar/shape values. Malformed counter/cache inputs are literal **false** vectors; any summarizer exception is recorded as an unexpected outcome, not allowed to abort the fixture process.

No check was run, so these are design expectations, not observed decisions. Intended use by L1 is the same report-drafted fixture pointed first at the pinned baseline source and then at the integrated candidate via `--runner`; baseline-red and candidate-green outcomes remain unobserved. No source implementation, F5 byte, historical record, or external state was changed. File changed: `.ufo/waves/round-22/w1/DraftOracle.md` only.