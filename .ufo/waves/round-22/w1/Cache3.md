STATUS: PASS — Witness for the extra required-like check, derived only from the producer source: `isolation_cleaned` must not be part of the required cache check identity. The 33-name set at `census/round-14/cache-demonstration.py:880-978` is the exact green identity, and it must be compared order-insensitively. The case-row phase identity is `initial-fresh, unchanged, dependency-modified, legacy-no-dependencies`. This is a source-only critique; nothing was executed.

Scope: source-inferred only. I read just the six contract-named files. No runner, fixture, probe, build or test was run. No tools were installed. The draft code is in this report only. I sent two short coordination messages, to SoujiR22.DraftCacheFix and SoujiR22.DraftScalarFix.

## Counterexample 1 (HIGH, false red): `isolation_cleaned` looks like a check but is not one

The frozen inventory row for `clean-cache-demonstration` puts `"isolation_cleaned": true` right next to `"checks": 33` (`census/round-21/step-inventory.json:187-197`; `census/round-21/run-acceptance.py:313-316`). It reads like a 34th required check.

The producer contradicts that reading:
- In `run_demonstration`, the `checks` dict has exactly 33 literal keys (`cache-demonstration.py:879-979`). I counted them one by one; the list is below. `isolation_cleaned` is not among them.
- `main()` adds `checks["isolation_cleaned"] = False` only in one case: `status == "ok"` and cleanup failed (`:1202-1206`). That same path also sets status to red and appends the name to `failed_checks`.
- So on every real green run the key is **absent**. When it is present, its value is always `False`.

The inventory key is consumed by the runner as `isolation.get("cleaned") is True` (`run-acceptance.py:468`). That is a top-level isolation field, not a check entry.

Impact: if a fix requires `"isolation_cleaned"` in the check set, or requires `checks.get("isolation_cleaned") is True`, every authentic green is rejected. That loses the real `clean-cache-demonstration` positive control, which conflicts with the preregistration rule to retain all 18 original real acceptance-step positive controls. Axes: calibration and operability.

## Counterexample 2 (HIGH, false red): comparing check names in source order

`emit` dumps with `sort_keys=True` (`cache-demonstration.py:1107`), so the JSON key order is alphabetical, not the source insertion order at `:880-978`. A fix that compares `list(checks) == CACHE_DEMO_CHECKS` in source order false-reds the real producer. The identity check must compare sets. `cases` is a list, so `sort_keys` does not change its order.

## Counterexample 3 (MEDIUM, false red): taking phase names from the docstring

The docstring calls case 4 `legacy-no-deps` (`:20`). The case row the code actually emits is `"legacy-no-dependencies"` (`:795`).

Two other names are easy to confuse:
- `"unchanged-recheck"` (`:610`) is only the `apply_policy` producer-phase label. It never appears in `cases` on a green run.
- The `make_case` phase for that row is `"unchanged"` (`:615`).

Phases emitted in order, from `:596`, `:615`, `:655`, `:795`: `initial-fresh`, `unchanged`, `dependency-modified`, `legacy-no-dependencies`.

## Counterexample 4 (MEDIUM, false red / operability): putting the name list into `expected_summary`

`inventory_projection` copies `expected_summary` verbatim (`run-acceptance.py:542-551`). `main` then refuses the whole run when that copy differs from frozen `step-inventory.json` (`:600-602`, exit 2, no record). The inventory's normalization note says it is exact against the r20 source.

Adding `"check_names": [...]` or `"phases": [...]` to the step dict therefore refuses all 18 steps, unless the frozen inventory is also rewritten, which changes its claimed r20 derivation. The safe correction keeps the identity as module constants outside the step dict. Then both the projection and the frozen inventory stay unchanged.

## Counterexample 5 (MEDIUM, crash on malformed data): non-dict `gate` or `isolation`

- `payload.get("gate", {}).get("sha256")` (`:467`) raises `AttributeError` when the producer JSON has `"gate": null` or a list.
- `isolation = payload.get("isolation", {})` followed by `isolation.get(...)` (`:455`, `:468-469`) fails the same way when `isolation` is a list.

`main` catches only `(OSError, ValueError, RuntimeError, Refusal, KeyError)` (`:652`), so the result is an uncaught traceback and no record. This breaks the preregistration rule to reject malformed producer data without a crash.

The real producer always emits dict `gate` (`gate_state`, `:1020`) and dict `isolation` (`:1022`, `:1200`), so the green control is unaffected.

## Adjacent witness for the scalar seat (not cache identity)

- `payload.get("producer_executions_new_policy") == 3` (`:465`) accepts the JSON value `3.0`, because Python decodes a JSON real to `float` and `3.0 == 3`.
- The exact counters at `:427` accept `0.0` for `0` the same way.

So a type-exact fix must reject float as well as bool. Authority: the Python `json` conversion table (https://docs.python.org/3/library/json.html#json-to-py-table) and numeric equality semantics (https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex). Both are cited from known documentation; I did not open them this seat.

## Real witness: the exact 33 producer check names (`cache-demonstration.py:880-978`)

initial_fresh_once, producer_actual_subprocess_green, unchanged_gate_exit_zero, unchanged_gate_status_reusable, changed_dependency_exact_finding, legacy_exact_finding, unchanged_reused_without_producer, unchanged_retained_measured_commit, changed_dependency_gate_exit_one, changed_dependency_not_reused, changed_dependency_producer_executed, changed_dependency_fresh_digests, legacy_gate_exit_two, legacy_not_reused, legacy_producer_executed, legacy_fresh_digests, only_declared_dependency_changed, record_bytes_unchanged, gate_digest_recorded_and_unchanged, execution_log_matches_disk, isolation_confined, unsafe_control_would_retain_stale_green, unsafe_control_would_retain_legacy_green, baseline_authentic_retention, baseline_stale_green_reused, new_caller_refused_same_record_and_reexecuted, historical_legacy_records_refused, migrated_caller_reuses_unchanged, migrated_caller_refuses_stale, migrated_caller_refuses_legacy, migrated_caller_refuses_missing_revision, migrated_caller_refuses_unstable, migrated_caller_reruns_external_mutable.

There are 33 names, which matches inventory `checks: 33`.

## Minimal expected policy

A cache-demo step matches only when all of the following hold:
1. Every existing runner condition still holds, unchanged.
2. `set(checks) == CACHE_DEMO_CHECKS`. This is an exact set with no subset matching, which rejects a bogus substitute name and any extra `isolation_cleaned` key.
3. Every required value `is True`.
4. `len(CACHE_DEMO_CHECKS) == expected["checks"]`. This turns drift between the constant and the frozen count into a red result instead of a crash.
5. The case-row phases, read in list order, equal `CACHE_DEMO_PHASES`.
6. `len(CACHE_DEMO_PHASES) == expected["cases"]`.
7. `gate` and `isolation` are dicts; otherwise the step does not match.

These row fields are deliberately **not** compared, because they vary legitimately between runs:
- `record` and gate `command` paths, which contain the mkdtemp suffix `souji-r14-cache-demo.*` (`:1151`) and the clone root `souji-r21-replay-*` (`run-acceptance.py:567`).
- `record_sha256`, because the record embeds `measured_commit` (`:575-582`).
- `produced_at` (`:501`), `seconds` (`:312`, `:489`), and gate stdout and stderr.

Per-row values such as `gate_exit` (None, 0, 1, 2), `executions_after` (1, 1, 2, 3) and `retained` (F, T, F, F) are deterministic on green, but checks 1, 7, 11 and 15 already assert them from the same rows. They are optional, not minimal. If they are added, they must use type-exact comparisons (`is None`, `type(x) is int`).

```python
CACHE_DEMO_CHECKS = frozenset((
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
))
CACHE_DEMO_PHASES = ("initial-fresh", "unchanged", "dependency-modified",
                     "legacy-no-dependencies")
```

```python
    elif kind == "cache-demo":
        try:
            payload = json.loads(stdout)
        except (ValueError, TypeError):
            payload = None
        if not isinstance(payload, dict):
            payload_dict = {}
        else:
            payload_dict = payload
        checks = payload_dict.get("checks")
        case_rows = payload_dict.get("cases")
        gate_info = payload_dict.get("gate")
        isolation = payload_dict.get("isolation")
        expected = step["expected_summary"]
        gate_sha = sha256_bytes(read_regular(root / "tools/souji-evidence-cache.py"))
        check_names = set(checks) if isinstance(checks, dict) else set()
        phases = ([row.get("phase") if isinstance(row, dict) else None for row in case_rows]
                  if isinstance(case_rows, list) else None)
        demo_match = (
            isinstance(payload, dict)
            and payload.get("status") == expected["status"]
            and payload.get("measured_commit") == revision
            and payload.get("harness_revision") == revision
            and len(CACHE_DEMO_PHASES) == expected["cases"]
            and phases == list(CACHE_DEMO_PHASES)
            and len(CACHE_DEMO_CHECKS) == expected["checks"]
            and isinstance(checks, dict) and check_names == CACHE_DEMO_CHECKS
            and all(checks[name] is True for name in CACHE_DEMO_CHECKS)
            and payload.get("failed_checks") == expected["failed_checks"]
            and type(payload.get("producer_executions_new_policy")) is int
            and payload.get("producer_executions_new_policy") == expected["producer_executions_new_policy"]
            and payload.get("inputs_unchanged_during_run") is expected["inputs_unchanged_during_run"]
            and isinstance(gate_info, dict) and gate_info.get("sha256") == gate_sha
            and isinstance(isolation, dict)
            and isolation.get("cleaned") is expected["isolation_cleaned"]
            and isolation.get("residue") == []
        )
        result["observed_json"] = payload
        result["matched_counts"] = {
            "expected_cases": expected["cases"],
            "observed_cases": len(case_rows) if isinstance(case_rows, list) else 0,
            "observed_case_phases": phases,
            "expected_gate_checks": expected["checks"],
            "observed_gate_checks": len(check_names),
            "matched_gate_checks": sum(checks.get(name) is True for name in CACHE_DEMO_CHECKS)
                                   if isinstance(checks, dict) else 0,
            "missing_gate_checks": sorted(CACHE_DEMO_CHECKS - check_names),
            "unexpected_gate_checks": sorted(check_names - CACHE_DEMO_CHECKS),
            "new_policy_producer_executions": payload_dict.get("producer_executions_new_policy"),
        }
        matched = matched and demo_match and not stderr
```

The `type(...) is int` guard on `producer_executions_new_policy` belongs to the cache draft: SoujiR22.DraftScalarFix confirmed (IRC, 2026-10-21) that its recursive `type(actual) is type(expected)` fix covers counters only and leaves the cache numeric predicate with the cache draft owner. The guard rejects both `3.0` and `true`. JSON object keys are always `str`, so the `sorted(...)` calls cannot raise.

## Literal oracle vectors (expected decision: base, then changed)

Every vector starts from a real-shaped green payload:
- Fields: `status: ok`, `measured_commit` and `harness_revision` set to the revision, the 33 names all true, `failed_checks: []`, `producer_executions_new_policy: 3`, `inputs_unchanged_during_run: true`.
- `gate.sha256` equals the oracle root's `tools/souji-evidence-cache.py` digest. That file must exist in the oracle root, because `read_regular` raises `Refusal` otherwise (`:192-194`).
- `isolation: {cleaned: true, residue: []}`, four case rows with the real phases, return code 0, empty stderr.

| id | mutation | base | changed |
|---|---|---|---|
| CD1 | none (positive control) | match | match |
| CD2 | different mkdtemp/clone paths, record_sha256, produced_at, seconds | match | match |
| CD3 | keys in `sort_keys` order vs source order | match | match |
| CD4 | `migrated_caller_reruns_external_mutable` replaced by `bogus_check: true` (still 33) | match (false green) | reject |
| CD5 | add `isolation_cleaned: false`, status red, failed_checks `["isolation_cleaned"]`, isolation.cleaned false (the producer's real red path) | reject | reject |
| CD6 | 33 names plus `isolation_cleaned: true` (34) | reject | reject |
| CD7 | phase 4 `legacy-no-deps` | match (false green) | reject |
| CD8 | four rows `{}` | match (false green) | reject |
| CD9 | `"gate": null` | crash (AttributeError) | reject, no crash |
| CD10 | `"isolation": []` | crash (AttributeError) | reject, no crash |
| CD11 | one check value `1` | reject | reject |
| CD12 | `producer_executions_new_policy: 3.0` | match (false green) | reject |

CD4, CD7, CD8 and CD12 discriminate the base behavior from the changed behavior. CD1, CD2, CD3, CD5, CD6 and CD11 must stay stable across both. CD9 and CD10 fix the preregistered no-crash rule. CD5 is the producer's own `:1202-1206` path, so it uses no invented producer value; the paths and digests in CD2 are transient placeholders.

## Impacted axes and residuals

- **Calibration:** CD4, CD7 and CD8 close the counted-not-identified gap. Counterexamples 1–3 stop the fix from becoming a false red.
- **Operability:** counterexample 4 avoids refusing all 18 steps; counterexample 5 removes the crash.
- **Coverage:** the 18 positive controls are retained.

No trade-off was found that the judge must reject. This check identifies outputs; it does not authenticate the producer. Python `json.loads` keeps the last value of a duplicated key, and malicious-producer attestation is out of scope by preregistration. F5 bytes are untouched.
