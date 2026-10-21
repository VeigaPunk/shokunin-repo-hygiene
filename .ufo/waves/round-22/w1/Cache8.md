STATUS: PARTIAL — The attack's main hypothesis is refuted: the runner reads cleanup state from the same `isolation` object that the producer writes. Three related defects remain: a non-dict `gate`/`isolation` crashes the summarizer, a float `3.0` passes the integer `producer_executions_new_policy` check, and case rows plus check names are unbound. Two easy "fixes" would read the wrong container and turn every valid run red. Everything here is from reading the source; nothing was executed.

Axes: calibration, operability, coverage (no trade). Read only the six named files. No runs, probes, builds, or installs.

## Witness: where the producer actually puts isolation state (source, not executed)

- `census/round-14/cache-demonstration.py:1022-1029`: `run_demonstration` returns `payload["isolation"] = {base, root, results, records, under_var_tmp, fixture_files}`. `base` comes from `tempfile.mkdtemp(prefix="souji-r14-cache-demo.", dir="/var/tmp")` at `:1151`, so the path changes on every run.
- `:1084-1103`: `cleanup()` returns `{kept, cleaned, residue}`. Non-keep success gives `kept False`, `cleaned True`, `residue []`. Keep gives `kept True`, `cleaned False`, `residue [base]`.
- `:1200-1201`: `payload.setdefault("isolation", {}); payload["isolation"].update(state)`. The cleanup keys therefore land in `payload["isolation"]`. There is no top-level `isolation_cleaned` key.
- `:1202-1206`: only when cleanup fails is `checks["isolation_cleaned"] = False` added, together with `status` red and `failed_checks` += `isolation_cleaned`. The success-path `checks` dict (`:879-979`) has exactly 33 keys, and `isolation_cleaned` is not one of them. The `isolation_confined` check (`:937-941`) is about confinement under `/var/tmp`, not cleanup.
- Runner `census/round-21/run-acceptance.py:455,468-469`: `isolation = payload.get("isolation", {})`, then `isolation.get("cleaned") is True` and `isolation.get("residue") == []`. **The container is correct.** The inventory key `isolation_cleaned` (`census/round-21/step-inventory.json:196`) is a contract label that the runner maps to `isolation.cleaned`. It is not a payload field.

## Counterexamples (strongest first)

### HIGH (operability) — A non-dict `isolation` or `gate` crashes the summarizer

`run-acceptance.py:467`: `payload.get("gate", {}).get("sha256")`. `:468`: `isolation.get("cleaned")`, where `isolation = payload.get("isolation", {})` (`:455`). The `{}` default applies only when the key is absent. A JSON `null` or `[]` value reaches `.get`. The chain short-circuits, so this triggers only after every earlier conjunct is true.

Witnesses:
- A valid-shaped payload with `"gate": null` raises `AttributeError: 'NoneType' object has no attribute 'get'`.
- The same payload with a valid gate and `"isolation": []` raises `AttributeError: 'list'...`.

`main` catches only `(OSError, ValueError, RuntimeError, Refusal, KeyError)` (`:652`). `AttributeError` escapes with a traceback, and no record is written. Python's uncaught-exception exit status is 1, which is the same as the runner's "not all matched" code (`:655`) [INFERENCE: CPython convention, not executed]. The preregistration requires rejecting malformed producer data without a crash.

Impacted axes: operability, calibration.

### HIGH (calibration) — A float passes the integer producer-execution count

`:465`: `payload.get("producer_executions_new_policy") == 3`. A JSON `3.0` decodes to a float, and `3.0 == 3` is true. The producer always emits the int `len(executions)` (`cache-demonstration.py:850,1049`). Changing that one token in an otherwise valid payload therefore gives a false green.

The counter exact-JSON branch (`:427`) has the same float hole (for example `0.0` for `F2_entry`), alongside the bool hole that `AttackRunnerStepResults.md` reported. A type-strict repair has to reject both bool and float where the expected value is an int.

Source authority to cite: Python `json` decoding table ("number (int)" → `int`, "number (real)" → `float`) at https://docs.python.org/3/library/json.html#json-to-py-table, and numeric equality across types plus bool being a subtype of int at https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex. [INFERENCE: this seat did not open those URLs in this session; L1's SOURCES row must cite the pages it opened.]

Impacted axis: calibration.

### HIGH (calibration, coverage) — Wrong-container repair hazards that would cause false reds

1. **Requiring `isolation_cleaned` in the check-name set.** Valid success runs never contain it (`:1202-1206`), so every real run goes red. This also breaks the 18 real positive controls.
2. **Unifying the cache-demo branch with the counter subset matcher** (`observed.get(key) == value`, `:430-431`). The real payload has no top-level `isolation_cleaned` (it is `None`). It has `cases` as a list rather than `4`, and `checks` as a dict rather than `33`. All three fail on a valid run.
3. **Moving check names or case policy into `expected_summary`.** `inventory_projection` copies `expected_summary` (`:541-543`), and `:600-602` refuses with "acceptance commands differ from the frozen r20 inventory". Editing `step-inventory.json` instead breaks its "expectations … otherwise exact" provenance claim against r20 `source_sha256`. Keep the identities as summarizer module constants.
4. **Pinning `isolation.base/root/results/records` or case `record` paths.** These come from mkdtemp and change on every run, and `produced_at`/`seconds`/`observed_at` change too. Pinning them causes false reds.

Impacted axes: calibration, coverage.

### MEDIUM (calibration) — Case rows are counted, not bound

`:461` checks only `len(case_rows) == 4`, so four `{}` rows pass. Every honest `status: ok` run produces the deterministic projection below:

| phase | gate_exit | retained | executions_after |
|---|---|---|---|
| `initial-fresh` | null | false | 1 |
| `unchanged` | 0 | true | 1 |
| `dependency-modified` | 1 | false | 2 |
| `legacy-no-dependencies` | 2 | false | 3 |

It follows from `make_case` (`cache-demonstration.py:556-573`) and the four appends (`:594-603,612-622,653-663,793-803`). Initial `decision=None` gives `gate_exit` `None`. `retained` means `result_origin == "retained-from-record"`. The values are also implied by checks `initial_fresh_once`, `unchanged_gate_exit_zero`, `unchanged_reused_without_producer`, `unchanged_retained_measured_commit`, `changed_dependency_gate_exit_one`, `changed_dependency_not_reused`, `changed_dependency_producer_executed`, `legacy_gate_exit_two`, `legacy_not_reused` and `legacy_producer_executed` (`:880-924`). Binding the projection therefore cannot turn a valid run red. The comparison must be type-strict, because `False` would otherwise equal the `0` in `gate_exit`.

### MEDIUM (calibration) — Check identity: the exact 33 names

These are derived from the dict literal at `cache-demonstration.py:879-979`, not invented:

`initial_fresh_once`, `producer_actual_subprocess_green`, `unchanged_gate_exit_zero`, `unchanged_gate_status_reusable`, `changed_dependency_exact_finding`, `legacy_exact_finding`, `unchanged_reused_without_producer`, `unchanged_retained_measured_commit`, `changed_dependency_gate_exit_one`, `changed_dependency_not_reused`, `changed_dependency_producer_executed`, `changed_dependency_fresh_digests`, `legacy_gate_exit_two`, `legacy_not_reused`, `legacy_producer_executed`, `legacy_fresh_digests`, `only_declared_dependency_changed`, `record_bytes_unchanged`, `gate_digest_recorded_and_unchanged`, `execution_log_matches_disk`, `isolation_confined`, `unsafe_control_would_retain_stale_green`, `unsafe_control_would_retain_legacy_green`, `baseline_authentic_retention`, `baseline_stale_green_reused`, `new_caller_refused_same_record_and_reexecuted`, `historical_legacy_records_refused`, `migrated_caller_reuses_unchanged`, `migrated_caller_refuses_stale`, `migrated_caller_refuses_legacy`, `migrated_caller_refuses_missing_revision`, `migrated_caller_refuses_unstable`, `migrated_caller_reruns_external_mutable`.

The count is 33, which matches inventory `checks: 33`.

### LOW (tradeoff, not a defect) — Deeply nested stdout

Deeply nested stdout raises `RecursionError` (a `RuntimeError` subclass) from `json.loads`. It is not caught at `:448-450`, but it is caught at `:652`, so the whole run is refused with exit 2. That fails closed. Treat it as a disclosed limit.

## Smallest safe correction (draft only; L1 integrates)

The F5 code, `step-inventory.json`, and the inventory projection stay untouched. `json_equal` is the type-strict helper that the scalar-type seat also needs, so it should be shared rather than duplicated.

```python
CACHE_DEMO_CHECKS = frozenset((
    "initial_fresh_once", "producer_actual_subprocess_green", "unchanged_gate_exit_zero",
    "unchanged_gate_status_reusable", "changed_dependency_exact_finding", "legacy_exact_finding",
    "unchanged_reused_without_producer", "unchanged_retained_measured_commit",
    "changed_dependency_gate_exit_one", "changed_dependency_not_reused",
    "changed_dependency_producer_executed", "changed_dependency_fresh_digests",
    "legacy_gate_exit_two", "legacy_not_reused", "legacy_producer_executed", "legacy_fresh_digests",
    "only_declared_dependency_changed", "record_bytes_unchanged",
    "gate_digest_recorded_and_unchanged", "execution_log_matches_disk", "isolation_confined",
    "unsafe_control_would_retain_stale_green", "unsafe_control_would_retain_legacy_green",
    "baseline_authentic_retention", "baseline_stale_green_reused",
    "new_caller_refused_same_record_and_reexecuted", "historical_legacy_records_refused",
    "migrated_caller_reuses_unchanged", "migrated_caller_refuses_stale",
    "migrated_caller_refuses_legacy", "migrated_caller_refuses_missing_revision",
    "migrated_caller_refuses_unstable", "migrated_caller_reruns_external_mutable",
))
CACHE_DEMO_CASES = [
    {"phase": "initial-fresh", "gate_exit": None, "retained": False, "executions_after": 1},
    {"phase": "unchanged", "gate_exit": 0, "retained": True, "executions_after": 1},
    {"phase": "dependency-modified", "gate_exit": 1, "retained": False, "executions_after": 2},
    {"phase": "legacy-no-dependencies", "gate_exit": 2, "retained": False, "executions_after": 3},
]


def json_equal(observed, expected) -> bool:
    if type(observed) is not type(expected):
        return False
    if isinstance(expected, dict):
        return (observed.keys() == expected.keys()
                and all(json_equal(observed[key], value) for key, value in expected.items()))
    if isinstance(expected, list):
        return len(observed) == len(expected) and all(map(json_equal, observed, expected))
    return observed == expected
```

Cache-demo branch body. The container stays `payload["isolation"]`. Each nested object is type-guarded before `.get`, and paths are never pinned.

```python
        gate_state = payload.get("gate") if isinstance(payload, dict) else None
        isolation = payload.get("isolation") if isinstance(payload, dict) else None
        case_projection = (
            [{key: row[key] for key in CACHE_DEMO_CASES[0] if key in row}
             if isinstance(row, dict) else None for row in case_rows]
            if isinstance(case_rows, list) else None)
        demo_match = (
            isinstance(payload, dict)
            and payload.get("status") == expected["status"]
            and payload.get("measured_commit") == revision
            and payload.get("harness_revision") == revision
            and isinstance(case_rows, list) and len(case_rows) == expected["cases"]
            and json_equal(case_projection, CACHE_DEMO_CASES)
            and isinstance(checks, dict) and len(checks) == expected["checks"]
            and checks.keys() == CACHE_DEMO_CHECKS
            and all(value is True for value in checks.values())
            and json_equal(payload.get("failed_checks"), expected["failed_checks"])
            and json_equal(payload.get("producer_executions_new_policy"),
                           expected["producer_executions_new_policy"])
            and payload.get("inputs_unchanged_during_run") is expected["inputs_unchanged_during_run"]
            and isinstance(gate_state, dict) and gate_state.get("sha256") == gate_sha
            and isinstance(isolation, dict)
            and isolation.get("cleaned") is expected["isolation_cleaned"]
            and json_equal(isolation.get("residue"), [])
        )
```

`isolation.get("kept") is False` is optional. On real runs, `cleaned True` already implies it (`:1084-1103`), so it closes only a forged contradiction and is not required for this claim.

## Synthetic oracle vectors

Use one fixture over the base and the changed summarizer. The fixture must supply a synthetic root containing `tools/souji-evidence-cache.py`, whose sha256 is the vector's `gate.sha256` (`:454`). It must also catch exceptions around the base call so that "crash" is recorded as a decision rather than aborting the fixture.

| vector | mutation from a real-shaped `ok` payload | base (inferred) | changed |
|---|---|---|---|
| P1 | none; `isolation.base=/var/tmp/souji-r14-cache-demo.aaaa1111` | match | match |
| P2 | P1 with a different mkdtemp suffix, timestamps and seconds | match | match |
| N1 | `"gate": null` | crash | no-match |
| N2 | `"isolation": []` | crash | no-match |
| N3 | `producer_executions_new_policy: 3.0` | match (false green) | no-match |
| N4 | one real check renamed to `isolation_cleaned` (still 33, all true) | match (false green) | no-match |
| N5 | `cases: [{},{},{},{}]` | match (false green) | no-match |
| N6 | `cases[1].gate_exit: false` | match (false green) | no-match |
| C1 | `isolation.cleaned` absent, top-level `isolation_cleaned: true` | no-match | no-match |
| C2 | real failure shape: `status: red`, 34 checks incl. `isolation_cleaned: false`, `isolation.cleaned: false` | no-match | no-match |

C1 is the wrong-container control. P1 and P2 preserve generated rows and path variation.

## Limits

- Every base and changed decision above is inferred from the source. None was executed.
- This seat did not open the public Python docs URLs. The vectors cover only summarizer predicates, not producer authenticity (per preregistration).
- No tools were installed. No files were written other than this report.

Report: .ufo/waves/round-22/w1/Cache8.md
