STATUS: PASS — Source-only attack confirmed: the pinned `clean-cache-demonstration` summarizer accepts a payload in which a required producer check is replaced by a bogus name. A minimal name-and-phase policy closes it without rejecting valid generated output. Nothing was executed; every decision below is source-inferred.

Seat: SoujiR22.Cache1 (critic, leaf). Base 41553adb139d06511dc386bb3ce4326aebfba675. Only the six contract-named files were read. No tools installed, no tests/builds/probes run, no other files written.

## Counterexample (source-inferred, not executed)

### C1 — bogus check name replaces a required check (HIGH; calibration)

The runner's cache-demo branch (`census/round-21/run-acceptance.py:446-480`) accepts `checks` when `isinstance(checks, dict) and len(checks) == 33 and all(value is True ...)` (lines 462-463). It never compares names.

The real producer (`census/round-14/cache-demonstration.py:879-979`) emits exactly these 33 keys on the `status: "ok"` path:

```text
initial_fresh_once, producer_actual_subprocess_green, unchanged_gate_exit_zero,
unchanged_gate_status_reusable, changed_dependency_exact_finding, legacy_exact_finding,
unchanged_reused_without_producer, unchanged_retained_measured_commit,
changed_dependency_gate_exit_one, changed_dependency_not_reused,
changed_dependency_producer_executed, changed_dependency_fresh_digests,
legacy_gate_exit_two, legacy_not_reused, legacy_producer_executed, legacy_fresh_digests,
only_declared_dependency_changed, record_bytes_unchanged,
gate_digest_recorded_and_unchanged, execution_log_matches_disk, isolation_confined,
unsafe_control_would_retain_stale_green, unsafe_control_would_retain_legacy_green,
baseline_authentic_retention, baseline_stale_green_reused,
new_caller_refused_same_record_and_reexecuted, historical_legacy_records_refused,
migrated_caller_reuses_unchanged, migrated_caller_refuses_stale,
migrated_caller_refuses_legacy, migrated_caller_refuses_missing_revision,
migrated_caller_refuses_unstable, migrated_caller_reruns_external_mutable
```

The 34th key, `isolation_cleaned: false`, appears only on the red cleanup path (lines 1202-1206), and that path also sets `status: "red"`. So exact set equality holds for every valid green output.

Witness derivation: start from the producer's real `ok` payload schema. Keep every field the runner checks at the value the runner itself requires: `status` `"ok"`, `measured_commit` and `harness_revision` equal to `<REV>` (lines 998 and 1010), `producer_executions_new_policy` 3 (line 1049), `inputs_unchanged_during_run` true (line 1216), `gate.sha256` equal to the runner-computed `<GATE_SHA256>` (lines 454 and 1020), and `isolation` `{cleaned: true, residue: []}` (lines 1200-1201). Then make one rename: `migrated_caller_reruns_external_mutable` becomes `bogus_check: true`. No other producer value is invented.

```json
{"status": "ok", "measured_commit": "<REV>", "harness_revision": "<REV>",
 "cases": ["<4 rows>"],
 "checks": {"initial_fresh_once": true, "...31 other real names...": true, "bogus_check": true},
 "failed_checks": [], "producer_executions_new_policy": 3,
 "inputs_unchanged_during_run": true, "gate": {"sha256": "<GATE_SHA256>"},
 "isolation": {"cleaned": true, "residue": []}}
```

With returncode 0 and empty stderr, line 480 yields `matched: true` on base. This is a false green.

`matched_counts.matched_gate_checks` (line 477) counts `True` values regardless of name. The record would therefore also claim 33/33 matched checks.

The realistic route is not a malicious producer. It is a committed producer regression. `INPUT_PATHS` binds `census/round-14/cache-demonstration.py` to whatever bytes the measured revision holds, not to a fixed digest. A commit that deletes the external-mutable assertion and adds any trivially-true key keeps the count at 33, and acceptance stays green.

### C2 — arbitrary case rows (MEDIUM; calibration)

Line 461 checks only `len(case_rows) == 4`. On base, `"cases": [{}, {}, {}, {}]` passes. The producer always emits rows whose `phase` sequence is `initial-fresh`, `unchanged`, `dependency-modified`, `legacy-no-dependencies` (`make_case` calls at lines 594-603, 612-622, 653-663 and 793-803).

Rejected inference trap: the second producer execution label is `"unchanged-recheck"` (line 610), but its case row phase is `"unchanged"` (line 615). If you derive phases from `producer("...")` labels instead of `make_case` arguments, the policy will reject every valid run.

### C3 — malformed `gate` or `isolation` crashes the runner (MEDIUM; operability)

Line 467 calls `payload.get("gate", {}).get("sha256")`, and line 455 then line 468 call `isolation.get(...)`. If a payload has `"gate": null` (or a list), or `"isolation": null`, and every earlier conjunct is true, the result is `AttributeError`. That error is outside `main`'s caught set at line 652 (`OSError, ValueError, RuntimeError, Refusal, KeyError`). The runner dies with a traceback and writes no record. The preregistration requires "Reject malformed producer data without a crash." Valid producer output always has dict `gate` (from `inspect_gate`) and dict `isolation` (line 1200), so a type guard costs no positives.

### C4 — float accepted for an integer field in the same branch (LOW; cross-seat, scalar-type claim)

Line 465 uses `== 3`, so JSON `3.0` passes. A bool cannot equal 3, so the bool form of the defect does not bite here. The float form does. Whoever owns the JSON scalar-type repair should apply the same strict-int rule to this field. The valid producer emits `len(executions)`, which is an int.

### Noted, not claimed

- `json.loads` keeps the last of duplicate keys. A forged stdout could repeat a check name, with `false` first and `true` last. The real producer uses `json.dumps(dict)` and cannot emit duplicates. The preregistration disclaims malicious-producer attestation, so this is optional hardening (`object_pairs_hook` that rejects duplicates), not part of this claim.
- A deeply nested stdout raises `RecursionError`, a subclass of `RuntimeError`. `main` catches it and refuses with no record, instead of writing a red step. This is an operability limit only.

## Rejected inference

Do not derive the expected name set from the producer source at the measured revision, for example by AST-parsing the `checks` literal. That would be circular: a producer regression that renames or drops a check would change the oracle in lockstep and stay green. The expected set has to be an independent, reviewed constant.

## Smallest safe correction (draft; L1 integrates)

Placement: put the oracle in the runner as module constants, next to `COUNTER_EXPECTATIONS`. Do not put it in `census/round-21/step-inventory.json`. That inventory asserts derivation from `census/round-20/run-acceptance.py` at sha256 `6d38a3d0…` with names and expectations "otherwise exact" (`step-inventory.json:2-5`). Adding a names list would create false provenance and break the line-601 projection equality. The projection compares `expected_summary`, and that field stays unchanged.

The runner constant ties to the inventory count through `len(CACHE_DEMO_CHECKS) == expected["checks"]`. If they drift, the step goes red. It does not silently pass.

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
CACHE_DEMO_CASE_PHASES = ("initial-fresh", "unchanged", "dependency-modified", "legacy-no-dependencies")
```

Replacement for the cache-demo branch (`run-acceptance.py:446-480`):

```python
    elif kind == "cache-demo":
        try:
            payload = json.loads(stdout)
        except (ValueError, TypeError):
            payload = None
        is_dict = isinstance(payload, dict)
        checks = payload.get("checks") if is_dict else None
        case_rows = payload.get("cases") if is_dict else None
        gate = payload.get("gate") if is_dict else None
        isolation = payload.get("isolation") if is_dict else None
        expected = step["expected_summary"]
        gate_sha = sha256_bytes(read_regular(root / "tools/souji-evidence-cache.py"))
        check_names = set(checks) if isinstance(checks, dict) else set()
        phases = ([row.get("phase") if isinstance(row, dict) else None for row in case_rows]
                  if isinstance(case_rows, list) else None)
        executions = payload.get("producer_executions_new_policy") if is_dict else None
        demo_match = (
            is_dict
            and payload.get("status") == expected["status"]
            and payload.get("measured_commit") == revision
            and payload.get("harness_revision") == revision
            and isinstance(case_rows, list) and len(case_rows) == expected["cases"]
            and len(CACHE_DEMO_CASE_PHASES) == expected["cases"]
            and phases == list(CACHE_DEMO_CASE_PHASES)
            and isinstance(checks, dict) and len(checks) == expected["checks"]
            and len(CACHE_DEMO_CHECKS) == expected["checks"]
            and check_names == CACHE_DEMO_CHECKS
            and all(value is True for value in checks.values())
            and payload.get("failed_checks") == expected["failed_checks"]
            and type(executions) is int
            and executions == expected["producer_executions_new_policy"]
            and payload.get("inputs_unchanged_during_run") is expected["inputs_unchanged_during_run"]
            and isinstance(gate, dict) and gate.get("sha256") == gate_sha
            and isinstance(isolation, dict)
            and isolation.get("cleaned") is expected["isolation_cleaned"]
            and isolation.get("residue") == []
        )
        result["observed_json"] = payload
        result["gate_check_identity"] = {
            "missing": sorted(CACHE_DEMO_CHECKS - check_names),
            "unexpected": sorted(check_names - CACHE_DEMO_CHECKS),
            "observed_case_phases": phases,
        }
        result["matched_counts"] = {
            "expected_cases": expected["cases"],
            "observed_cases": len(case_rows) if isinstance(case_rows, list) else 0,
            "expected_gate_checks": expected["checks"],
            "observed_gate_checks": len(checks) if isinstance(checks, dict) else 0,
            "matched_gate_checks": sum(checks.get(name) is True for name in CACHE_DEMO_CHECKS) if isinstance(checks, dict) else 0,
            "new_policy_producer_executions": executions,
        }
        matched = matched and demo_match and not stderr
```

Why this preserves the existing controls:

- `matched_counts` keeps its key set. For valid output its values are unchanged, including `matched_gate_checks` at 33. The replay-matrix signature tuple (name, returncode, observed summary, matched counts, matched flag, per `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`) is therefore identical for valid runs.
- The diagnostics go in the new `gate_check_identity` key, outside that tuple.
- Case rows are projected only to `phase`. Paths under the `mkdtemp` `souji-r14-cache-demo.*` directory, `record_sha256`, gate stdout, `seconds`, `produced_at` and `observed_at` all vary per run and are never compared.
- If the scalar-type owner adopts a shared strict-int helper, use it in place of the inline `type(executions) is int`.

Optional tightening, not needed for this claim: also compare per-row `(gate_exit, retained, executions_after)` against `(None, False, 1)`, `(0, True, 1)`, `(1, False, 2)`, `(2, False, 3)`, with strict int/bool typing (`True == 1` otherwise passes). Each tuple follows from producer checks that are already required to be true (lines 880, 885, 901-924). It adds case-content binding at the cost of a second oracle surface.

## Expected decision vectors (for L1's synthetic result-oracle fixture)

These call `summarize_result` directly with crafted stdout bytes and no process. A synthetic `root` must contain `tools/souji-evidence-cache.py` so `gate_sha` resolves. All other fields follow the witness above.

| vector | base | changed |
|---|---|---|
| exact 33 real names, all `true`; 4 rows with real phases | match | match |
| same as above but different `/var/tmp` paths, `seconds` and timestamps in rows | match | match |
| one real name renamed to `bogus_check` (still 33, all `true`) | **match (false green)** | reject |
| 33 real names plus `bogus_check` (34 keys) | reject (count) | reject |
| 32 real names | reject | reject |
| rows `[{}, {}, {}, {}]` | **match (false green)** | reject |
| rows with phases where `unchanged` is replaced by `unchanged-recheck` | **match** | reject |
| phases in a different order | **match** | reject |
| `"gate": null`, everything else valid | **crash (AttributeError, no record)** | reject |
| `"isolation": []`, everything else valid | **crash** | reject |
| `producer_executions_new_policy: 3.0` | **match** | reject |
| producer red cleanup path (`isolation_cleaned: false`, `status: "red"`) | reject | reject |

## Impacted axes

- **Calibration:** C1 and C2 are false greens; C4 is a scalar false green.
- **Operability:** C3 crashes with no record; `gate_check_identity` gives a named diagnostic.
- **Coverage:** unchanged; the 18-step inventory and its projection are byte-identical.

No trade-off was found that the judge must reject.

## Identity risk for L1

`combined_snapshot` hard-codes `census/round-21/run-acceptance.py` (line 223), and `INPUT_PATHS` includes it. Editing that file in place changes bytes that r21 records are bound to. If round 22 copies the runner to a new path instead, the line-223 path, `INPUT_PATHS` and the line-600 inventory path must all move together. That choice belongs to L1.

The F5 production code and the 160-byte synthetic-only reason scope are untouched by this correction.

## Report trailers

- Report: `.ufo/waves/round-22/w1/Cache1.md`
- Read: `census/round-21/run-acceptance.py`, `census/round-21/step-inventory.json`, `census/round-14/cache-demonstration.py`, `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`, `.ufo/waves/round-22/preregistration.txt`, `corpus/QUALITY.md`
- Executed: none. Installed: none.
- L1 should run: the round-22 synthetic result-oracle fixture over base and changed code using the vectors above, then the full 18-step acceptance replay.
