STATUS: PASS — I found the authoritative cache-check container, a 33-name witness, three ways a repair could read the wrong container (two give false reds and one makes the whole run refuse), and one crash path on malformed data. Every finding below is inferred from source. Nothing was executed, no git command was run, and no tool was installed.

Scope: I read only the six named files. The bytes were the working-tree copies of `census/round-14/cache-demonstration.py` and `census/round-21/run-acceptance.py`. Before relying on the witness, L1 SHOULD confirm that these bytes equal `41553adb139d06511dc386bb3ce4326aebfba675:<path>`. Both paths are already bound in `INPUT_PATHS` (`run-acceptance.py:55-71`, through `R14_MEASURED`).

## Axes

- **Calibration:** false-green and false-red decisions on the `clean-cache-demonstration` step.
- **Operability:** the runner must not refuse or crash on valid or malformed producer data.
- **Coverage:** checks must be identified by exact name, not counted.

No trade between axes is allowed.

## Authoritative container (witness)

The producer has exactly one container of checks: the top-level `payload["checks"]` dict literal at `census/round-14/cache-demonstration.py:879-978`. `failed_checks` is derived from that dict (`:1052`), and `status` is "ok" only if every value is truthy (`:996`). The literal has 33 keys, which matches the frozen inventory's `"checks": 33` (`census/round-21/step-inventory.json:187-197`). In source order the keys are:

```text
initial_fresh_once
producer_actual_subprocess_green
unchanged_gate_exit_zero
unchanged_gate_status_reusable
changed_dependency_exact_finding
legacy_exact_finding
unchanged_reused_without_producer
unchanged_retained_measured_commit
changed_dependency_gate_exit_one
changed_dependency_not_reused
changed_dependency_producer_executed
changed_dependency_fresh_digests
legacy_gate_exit_two
legacy_not_reused
legacy_producer_executed
legacy_fresh_digests
only_declared_dependency_changed
record_bytes_unchanged
gate_digest_recorded_and_unchanged
execution_log_matches_disk
isolation_confined
unsafe_control_would_retain_stale_green
unsafe_control_would_retain_legacy_green
baseline_authentic_retention
baseline_stale_green_reused
new_caller_refused_same_record_and_reexecuted
historical_legacy_records_refused
migrated_caller_reuses_unchanged
migrated_caller_refuses_stale
migrated_caller_refuses_legacy
migrated_caller_refuses_missing_revision
migrated_caller_refuses_unstable
migrated_caller_reruns_external_mutable
```

Each value is a Python `bool` from a comparison or `and` chain, and `json.dumps` emits it as JSON `true` or `false`. The runner's existing `value is True` check (`run-acceptance.py:463`) is therefore already strict about type. The gap is identity: the runner checks `len(checks) == 33` (`:462`) and never looks at the names.

The only other source of a `checks` key is `main()`. On the red path, when cleanup fails, it appends `checks["isolation_cleaned"] = False` and `failed_checks += ["isolation_cleaned"]` (`cache-demonstration.py:1202-1206`). That key is absent from the valid (ok) payload.

The case rows come from `make_case` (`:556-572`). On the valid path there are exactly four, with `phase` values in this order:

- `initial-fresh` (`:596`)
- `unchanged` (`:615`)
- `dependency-modified` (`:655`)
- `legacy-no-dependencies` (`:795`)

## Counterexamples: wrong containers

### 1. Reading `isolation_cleaned` from `checks` (false red; operability, calibration)

`expected_summary` contains `"isolation_cleaned": true` (`step-inventory.json:196`). Its authority is `payload["isolation"]["cleaned"]` (`run-acceptance.py:468`, `cache-demonstration.py:1200-1201`), not `checks`.

A repair that adds `isolation_cleaned` to the expected name set, or requires `checks.get("isolation_cleaned") is True`, rejects every valid run. The valid payload has 33 keys and no `isolation_cleaned`. The only payload that does carry that key carries it as `False`, together with `status: "red"`.

Fix: the expected name set MUST be exactly the 33 names above and MUST exclude `isolation_cleaned`.

### 2. Taking phases from the docstring or `executions` (false red; calibration)

Two plausible sources give the wrong phase values:

- **Docstring:** it lists `legacy-no-deps` (`cache-demonstration.py:20`), but the code emits `legacy-no-dependencies` (`:795`).
- **Execution log:** `executions[*].phase` holds the `producer(phase)` labels. On the valid path that is three entries: `initial-fresh`, `dependency-modified`, `legacy-no-dependencies`. The second case's policy label is `unchanged-recheck` (`:610`), but that case is retained and has no execution, so `executions` has 3 entries while `cases` has 4.

Expecting case phases from either source rejects the valid case rows. Taking `len(executions)` as `cases` gives 3, not 4.

Fix: phases come only from `cases[*].phase`, using the four `make_case` labels listed above.

### 3. Putting the name set in `expected_summary` (refusal; operability)

`inventory_projection` copies `expected_summary` verbatim into the comparison (`run-acceptance.py:537-552`). `main()` refuses when the projection differs from the frozen `step-inventory.json` (`:600-602`).

If `make_steps` changes `"checks": 33` to a list of names, or adds a key inside `expected_summary`, every invocation exits 2 with "acceptance commands differ from the frozen r20 inventory". That loses all 18 real positive controls, not just the cache step.

Editing `step-inventory.json` to match is not a safe alternative. Its `normalization` field asserts "All names/args/expectations/inventory order otherwise exact" against the r20 source digest (`step-inventory.json:2-5`), so that change would create false provenance.

Fix: keep the literal as a runner module constant, like `COUNTER_EXPECTATIONS`. Alternatively, store it under a step key that the projection does not copy. The projection copies only `name`, `expected_summary`, `pass_pattern`, `pass_count`, `record_checks`, `exact_json`, `baseline_mismatch_count`, `kind` and `argv`.

### 4. Containers that cannot establish identity

These look like check containers but cannot prove the 33 names:

- **`failed_checks == []`:** an empty list is satisfied by any `checks` dict whose values are all true, including one with bogus names.
- **Nested booleans:** `baseline_control.*`, `migrated_caller.*`, `unsafe_policy_control.*` and `record.unchanged` hold booleans that feed checks but are not checks themselves.
- **`matched_counts.matched_gate_checks`:** it counts `True` values and stays at 33 for 33 bogus names.

The r21 MEDIUM finding (`.ufo/waves/round-21/w2/AttackRunnerStepResults.md:17-21`) still stands. A payload with four arbitrary case rows and 33 unrelated keys, all true, passes `demo_match` today.

### 5. Comparing whole case rows against a literal (false red; preserving transient variation)

Several case-row fields vary between valid runs:

- **Paths:** `record` and `gate.command` contain paths with a `mkdtemp` suffix under `/var/tmp/souji-r14-cache-demo.*` (`cache-demonstration.py:1151`), and the clone root is `/var/tmp/souji-r21-replay-*`.
- **Timing:** `gate.seconds` and `producer_execution.seconds`.
- **Timestamps:** `producer_execution.produced_at`.
- **Gate output:** `gate.stdout` and `gate.stderr`, which come from the gate's own output.

Case 1 also legitimately has `gate: null`, `gate_exit: null`, `reusable: null` and `producer_execution` as a dict, while case 2 has `producer_execution: null`.

A repair that requires `isinstance(row["gate_exit"], int)` on every row, or exact equality with a frozen row, rejects a valid run. Gate exits, retention and execution counts per case are already identified by named checks: `unchanged_gate_exit_zero`, `changed_dependency_gate_exit_one`, `legacy_gate_exit_two`, `initial_fresh_once`, `*_producer_executed` and `unchanged_reused_without_producer`. Duplicating them on the case rows adds no coverage.

## Malformed-data crash in the existing cache branch (operability)

`run-acceptance.py:455` sets `isolation = payload.get("isolation", {})`, and `:467` calls `payload.get("gate", {}).get("sha256")`. If the producer emits `"gate": null`, a non-dict `"gate"`, or a non-dict `"isolation"`, the `.get` call raises `AttributeError`. Both calls are reached only after the earlier conjuncts in the `and` chain pass.

`main()` catches only `(OSError, ValueError, RuntimeError, Refusal, KeyError)` (`:652`). The result is an uncaught traceback with no record and exit code 1, the same code as a legitimate red run.

Witness: take a valid payload and change only `"gate"` to `null` (or `"isolation"` to `[]`).

## Adjacent scalar gap (same branch; calibration)

`payload.get("producer_executions_new_policy") == 3` (`:465`) accepts `3.0`. The JSON decoder maps a number with a fraction to `float`, and `3.0 == 3` is true in Python. The producer always emits `len(executions)`, which is an int, so requiring `type(x) is int` loses nothing on valid data.

Accepting `true` instead of an integer is not a risk here, because `True == 3` is false. This belongs to the round's JSON scalar-type claim, so it SHOULD use the same exact-type helper L1 adopts for counters.

## Smallest safe correction (draft only; L1 integrates)

Leave `make_steps` and `step-inventory.json` untouched. Add these module constants:

```python
CACHE_DEMO_CHECKS = (
    "initial_fresh_once", "producer_actual_subprocess_green",
    "unchanged_gate_exit_zero", "unchanged_gate_status_reusable",
    "changed_dependency_exact_finding", "legacy_exact_finding",
    "unchanged_reused_without_producer", "unchanged_retained_measured_commit",
    "changed_dependency_gate_exit_one", "changed_dependency_not_reused",
    "changed_dependency_producer_executed", "changed_dependency_fresh_digests",
    "legacy_gate_exit_two", "legacy_not_reused", "legacy_producer_executed",
    "legacy_fresh_digests", "only_declared_dependency_changed",
    "record_bytes_unchanged", "gate_digest_recorded_and_unchanged",
    "execution_log_matches_disk", "isolation_confined",
    "unsafe_control_would_retain_stale_green",
    "unsafe_control_would_retain_legacy_green",
    "baseline_authentic_retention", "baseline_stale_green_reused",
    "new_caller_refused_same_record_and_reexecuted",
    "historical_legacy_records_refused", "migrated_caller_reuses_unchanged",
    "migrated_caller_refuses_stale", "migrated_caller_refuses_legacy",
    "migrated_caller_refuses_missing_revision",
    "migrated_caller_refuses_unstable",
    "migrated_caller_reruns_external_mutable",
)
CACHE_DEMO_PHASES = ("initial-fresh", "unchanged", "dependency-modified",
                     "legacy-no-dependencies")
```

Replace the `cache-demo` branch with:

```python
    elif kind == "cache-demo":
        try:
            payload = json.loads(stdout)
        except (ValueError, TypeError):
            payload = None
        if not isinstance(payload, dict):
            payload = {}
        checks = payload.get("checks")
        case_rows = payload.get("cases")
        gate = payload.get("gate")
        isolation = payload.get("isolation")
        expected = step["expected_summary"]
        gate_sha = sha256_bytes(read_regular(root / "tools/souji-evidence-cache.py"))
        names = set(checks) if isinstance(checks, dict) else set()
        identity = {
            "missing": sorted(set(CACHE_DEMO_CHECKS) - names),
            "unexpected": sorted(names - set(CACHE_DEMO_CHECKS)),
            "not_true": sorted(name for name in CACHE_DEMO_CHECKS
                               if isinstance(checks, dict) and name in checks
                               and checks[name] is not True),
            "case_phases": ([row.get("phase") if isinstance(row, dict) else None
                             for row in case_rows]
                            if isinstance(case_rows, list) else None),
        }
        executions = payload.get("producer_executions_new_policy")
        demo_match = (
            bool(payload)
            and payload.get("status") == expected["status"]
            and payload.get("measured_commit") == revision
            and payload.get("harness_revision") == revision
            and isinstance(case_rows, list) and len(case_rows) == expected["cases"]
            and identity["case_phases"] == list(CACHE_DEMO_PHASES)
            and isinstance(checks, dict) and len(checks) == expected["checks"]
            and not identity["missing"] and not identity["unexpected"]
            and not identity["not_true"]
            and payload.get("failed_checks") == expected["failed_checks"]
            and type(executions) is int
            and executions == expected["producer_executions_new_policy"]
            and payload.get("inputs_unchanged_during_run") is expected["inputs_unchanged_during_run"]
            and isinstance(gate, dict) and gate.get("sha256") == gate_sha
            and isinstance(isolation, dict)
            and isolation.get("cleaned") is expected["isolation_cleaned"]
            and isolation.get("residue") == []
        )
        result["observed_json"] = payload or None
        result["check_identity"] = identity
        # existing matched_counts block unchanged, reading `checks`/`case_rows`/`payload`
        matched = matched and demo_match and not stderr
```

Notes on the draft:

- **Kept as-is:** `matched_counts` keeps its current keys and values, so the matrix tuple (`name, rc, observed_summary, matched_counts, matched`) and the historical projections stay comparable. The new diagnostics go under a separate `check_identity` key, which is path-free and deterministic across runs.
- **`observed_json`:** on a non-dict parse it stays `None`, as today.
- **Static guard:** `main()` MAY refuse when `len(set(CACHE_DEMO_CHECKS)) != 33` or `len(CACHE_DEMO_PHASES) != 4`, next to the `EXPECTED_COMMANDS` guard. A duplicated name already fails closed (red, not green) through `unexpected`, so the guard is optional.
- **Phase identity:** this is the smallest row check that preserves valid rows. It compares one string per row and ignores every path, timing and gate-output field.

## Expected decision vectors

These are literal vectors for L1's fixture. They derive from the source, not from executing anything. Every case starts from the valid payload with rc 0 and empty stderr.

| case | mutation | base decision | changed decision |
|---|---|---|---|
| ok | none (33 names, 4 phases) | match | match |
| swap | one real name replaced by a bogus name, value `true` | match (false green) | red (`missing`/`unexpected`) |
| drop+add | `isolation_confined` removed, `isolation_cleaned: true` added | match (false green) | red |
| phases | phase 4 changed to `legacy-no-deps` | match (false green) | red |
| path-variation | different `/var/tmp` suffix, `seconds` and `produced_at` in every row | match | match |
| case1-null | case 1 with `gate`/`gate_exit`/`reusable` null (the valid shape) | match | match |
| float-exec | `producer_executions_new_policy: 3.0` | match (false green) | red |
| gate-null | `"gate": null` | crash (AttributeError, exit 1, no record) | red, record written |
| iso-list | `"isolation": []` | crash | red |
| red-cleanup | `checks` gains `isolation_cleaned: false`, status red | red | red |

## Residual limit (not a defect under the claim)

`json.loads` keeps the last value of a duplicated key. A hand-crafted stdout such as `{"checks": {"x": false, "x": true}}` collapses to a passing entry. The real producer emits through `json.dumps` of a dict and cannot duplicate keys. The preregistration also disclaims attesting to an arbitrary malicious producer, so rejecting duplicates through `object_pairs_hook` is optional hardening, not part of this claim.

Report: .ufo/waves/round-22/w1/Cache6.md
Evidence: census/round-14/cache-demonstration.py, census/round-21/run-acceptance.py, census/round-21/step-inventory.json, .ufo/waves/round-21/w2/AttackRunnerStepResults.md, .ufo/waves/round-22/preregistration.txt
