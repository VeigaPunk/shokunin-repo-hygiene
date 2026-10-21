STATUS: PARTIAL — complete source-derived draft; it was not applied or executed.

Axes: calibration (exact cache check identities), coverage (the four declared cache phases and their row shape), operability (malformed containers fail closed without an attribute/type crash).

## Finding

`census/round-21/run-acceptance.py:446-480` currently accepts the cache demonstration when the checks dictionary has the expected length and all its values are `True`, and when the cases list has the expected length. A producer can therefore substitute a different set of 33 true checks or four unrelated rows and still satisfy those predicates. The current branch also calls `.get()` on `gate` and `isolation` values without first establishing that they are dictionaries.

The stable identity/shape to assert is present in the named source: `census/round-14/cache-demonstration.py:556-572` defines the cache case row; lines 594-622, 653-663, and 793-803 emit phases `initial-fresh`, `unchanged`, `dependency-modified`, and `legacy-no-dependencies`; lines 879-979 define 33 named checks. The final payload exposes `cases`, `checks`, and `failed_checks` at lines 1046-1052. None of the proposed predicates compares transient record paths or digest values.

The expectations must be module constants, not additions to the cache step's `expected_summary`: `run-acceptance.py:538-553` projects that field into the frozen inventory, and `:597-602` refuses a projection mismatch. Keep the existing step/inventory unchanged (`cases: 4`, `checks: 33`).

## Draft code (report-only; no source files changed)

Add these module constants and helper near `SUMMARY_RE` / `numeric_leaves` in `run-acceptance.py`:

```python
CACHE_DEMO_CHECK_NAMES = (
    "initial_fresh_once",
    "producer_actual_subprocess_green",
    "unchanged_gate_exit_zero",
    "unchanged_gate_status_reusable",
    "changed_dependency_exact_finding",
    "legacy_exact_finding",
    "unchanged_reused_without_producer",
    "unchanged_retained_measured_commit",
    "changed_dependency_gate_exit_one",
    "changed_dependency_not_reused",
    "changed_dependency_producer_executed",
    "changed_dependency_fresh_digests",
    "legacy_gate_exit_two",
    "legacy_not_reused",
    "legacy_producer_executed",
    "legacy_fresh_digests",
    "only_declared_dependency_changed",
    "record_bytes_unchanged",
    "gate_digest_recorded_and_unchanged",
    "execution_log_matches_disk",
    "isolation_confined",
    "unsafe_control_would_retain_stale_green",
    "unsafe_control_would_retain_legacy_green",
    "baseline_authentic_retention",
    "baseline_stale_green_reused",
    "new_caller_refused_same_record_and_reexecuted",
    "historical_legacy_records_refused",
    "migrated_caller_reuses_unchanged",
    "migrated_caller_refuses_stale",
    "migrated_caller_refuses_legacy",
    "migrated_caller_refuses_missing_revision",
    "migrated_caller_refuses_unstable",
    "migrated_caller_reruns_external_mutable",
)
CACHE_DEMO_CASE_PHASES = (
    "initial-fresh",
    "unchanged",
    "dependency-modified",
    "legacy-no-dependencies",
)
CACHE_DEMO_CASE_FIELDS = frozenset({
    "phase", "record", "record_sha256", "declared", "observed_dependencies",
    "declared_dependency_digests_match", "gate", "gate_exit", "reusable",
    "result", "retained", "producer_execution", "executions_after",
})


def cache_demo_cases_match(rows, expected_phases):
    if not isinstance(rows, list) or len(rows) != len(expected_phases):
        return False
    for row, phase in zip(rows, expected_phases):
        if (not isinstance(row, dict)
                or set(row) != CACHE_DEMO_CASE_FIELDS
                or row.get("phase") != phase):
            return False
        if (not isinstance(row["record"], str)
                or not isinstance(row["record_sha256"], str)
                or not isinstance(row["declared"], dict)
                or not isinstance(row["observed_dependencies"], dict)
                or type(row["declared_dependency_digests_match"]) is not bool
                or not isinstance(row["result"], dict)
                or type(row["retained"]) is not bool
                or (row["producer_execution"] is not None
                    and not isinstance(row["producer_execution"], dict))
                or not isinstance(row["executions_after"], int)
                or isinstance(row["executions_after"], bool)):
            return False
        if phase == "initial-fresh":
            if (row["gate"] is not None or row["gate_exit"] is not None
                    or row["reusable"] is not None):
                return False
        elif (not isinstance(row["gate"], dict)
                or type(row["gate_exit"]) is not int
                or type(row["reusable"]) is not bool):
            return False
    return True
```

Replace only the `cache-demo` branch in `summarize_result` with the following; leave the existing `make_steps` / frozen step inventory projection unchanged:

```python
    elif kind == "cache-demo":
        try:
            payload = json.loads(stdout)
        except (ValueError, TypeError):
            payload = None
        expected = step["expected_summary"]
        payload_dict = payload if isinstance(payload, dict) else None
        checks = payload_dict.get("checks") if payload_dict is not None else None
        case_rows = payload_dict.get("cases") if payload_dict is not None else None
        gate = payload_dict.get("gate") if payload_dict is not None else None
        isolation = payload_dict.get("isolation") if payload_dict is not None else None
        gate_sha = sha256_bytes(read_regular(root / "tools/souji-evidence-cache.py"))
        check_names_match = (
            isinstance(checks, dict)
            and set(checks) == set(CACHE_DEMO_CHECK_NAMES)
            and all(value is True for value in checks.values())
        )
        cases_match = cache_demo_cases_match(case_rows, CACHE_DEMO_CASE_PHASES)
        demo_match = (
            payload_dict is not None
            and payload_dict.get("status") == expected["status"]
            and payload_dict.get("measured_commit") == revision
            and payload_dict.get("harness_revision") == revision
            and len(CACHE_DEMO_CASE_PHASES) == expected["cases"]
            and len(CACHE_DEMO_CHECK_NAMES) == expected["checks"]
            and cases_match
            and check_names_match
            and payload_dict.get("failed_checks") == expected["failed_checks"]
            and type(payload_dict.get("producer_executions_new_policy")) is int
            and payload_dict.get("producer_executions_new_policy") == expected["producer_executions_new_policy"]
            and payload_dict.get("inputs_unchanged_during_run") is expected["inputs_unchanged_during_run"]
            and isinstance(gate, dict)
            and gate.get("sha256") == gate_sha
            and isinstance(isolation, dict)
            and isolation.get("cleaned") is expected["isolation_cleaned"]
            and isolation.get("residue") == []
        )
        result["observed_json"] = payload
        result["matched_counts"] = {
            "expected_cases": expected["cases"],
            "observed_cases": len(case_rows) if isinstance(case_rows, list) else 0,
            "matched_case_phases": sum(
                isinstance(row, dict) and row.get("phase") == phase
                for row, phase in zip(case_rows, CACHE_DEMO_CASE_PHASES)
            ) if isinstance(case_rows, list) else 0,
            "expected_gate_checks": expected["checks"],
            "observed_gate_checks": len(checks) if isinstance(checks, dict) else 0,
            "matched_gate_checks": sum(
                checks.get(name) is True for name in CACHE_DEMO_CHECK_NAMES
            ) if isinstance(checks, dict) else 0,
            "new_policy_producer_executions": (
                payload_dict.get("producer_executions_new_policy")
                if payload_dict is not None else None
            ),
        }
        matched = matched and demo_match and not stderr
```

This checks the full set of check names (order-independent), all check values by identity with `True`, exact ordered case phases, and the row field/container/scalar shapes emitted by `make_case`. It type-checks the producer execution count as an exact `int` (so JSON `3.0` cannot equal the expected `3`) and transient `record` / `record_sha256` values as strings without assuming their contents. `gate` and `isolation` are guarded before nested access. `isolation_cleaned` is an acceptance expectation, not one of the demonstration's named `checks` keys; the demonstration adds an `isolation_cleaned` check only on cleanup failure (`cache-demonstration.py:1202-1205`).

## Evidence and limits

- Source inspection only: the count-based acceptance predicates and the exact frozen inventory comparison; cache case schema, four phases, 33 named checks, and final payload, as cited above.
- No tests, probes, build, formatter, or runtime command was run, per wave restrictions. No tools were installed.
- This is a code draft in the assigned report only; it is not integrated or verified. Main integration should compose it with the separate JSON scalar-type and summary-stderr repairs, then run the parent-owned acceptance after all seats land.
- Scope remains limited to the cache check/case false-green. It does not attest producer execution, authenticate arbitrary malicious output, or bind transient paths/digests.
