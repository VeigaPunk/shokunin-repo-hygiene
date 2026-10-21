STATUS: PARTIAL — counterexample confirmed from source: the r21 cache-demo summarizer accepts a payload in which a required producer check is missing and an unrelated check stands in for it. A minimal expected policy is drafted below. Everything here comes from reading source. No runner, fixture, producer or gate was executed, so nothing is claimed as observed at runtime.

Seat: SoujiR22.Cache2 (critic, leaf). Base 41553adb139d06511dc386bb3ce4326aebfba675. Files read: only the six named contract files, plus one public URL (Python `json` docs). No tools were installed.

## Axes
- **calibration**: does `matched` actually mean that the named producer's required checks passed?
- **operability**: malformed producer data must be rejected without a crash, and the 18 real positive controls must stay green.
- **coverage**: the checks are identified by name and tied to case content, not only counted.

## Witness: the required check set, read from the named producer

The check dict is in `census/round-14/cache-demonstration.py`, `run_demonstration`, lines 879–979. It is a single dict literal with exactly 33 string keys:

`initial_fresh_once, producer_actual_subprocess_green, unchanged_gate_exit_zero, unchanged_gate_status_reusable, changed_dependency_exact_finding, legacy_exact_finding, unchanged_reused_without_producer, unchanged_retained_measured_commit, changed_dependency_gate_exit_one, changed_dependency_not_reused, changed_dependency_producer_executed, changed_dependency_fresh_digests, legacy_gate_exit_two, legacy_not_reused, legacy_producer_executed, legacy_fresh_digests, only_declared_dependency_changed, record_bytes_unchanged, gate_digest_recorded_and_unchanged, execution_log_matches_disk, isolation_confined, unsafe_control_would_retain_stale_green, unsafe_control_would_retain_legacy_green, baseline_authentic_retention, baseline_stale_green_reused, new_caller_refused_same_record_and_reexecuted, historical_legacy_records_refused, migrated_caller_reuses_unchanged, migrated_caller_refuses_stale, migrated_caller_refuses_legacy, migrated_caller_refuses_missing_revision, migrated_caller_refuses_unstable, migrated_caller_reruns_external_mutable`

This count of 33 agrees with the frozen `checks: 33` in `census/round-21/step-inventory.json` lines 187–197 and in `census/round-21/run-acceptance.py` lines 312–317.

The producer adds one more key, `isolation_cleaned`, only in one place: `main` lines 1202–1206, and only with value `False` when status goes red. A green payload therefore never contains it. The expected set must be exactly these 33 names, not a superset that admits `isolation_cleaned`.

There are exactly four case phases. They are set in order by the `make_case` calls at lines 595, 613, 654 and 794: `initial-fresh`, `unchanged`, `dependency-modified`, `legacy-no-dependencies`. Several case fields vary from run to run: `record`, `record_sha256`, the gate `stdout`, `seconds`, `produced_at`, and the `/var/tmp/souji-r14-cache-demo.*` mkdtemp paths (lines 556–572, 1151). Clone-root paths under `/var/tmp/souji-r21-replay-*` also vary (`run-acceptance.py` lines 567–569). None of these may be pinned.

## Findings

### HIGH — a missing required check is accepted when replaced by a bogus `true` check (calibration, coverage)

The cache-demo branch is `run-acceptance.py` lines 456–470. It checks `len(checks) == 33` and `all(value is True ...)`. It never checks which names are present.

Counterexample (synthetic, source-derived): start from the real green schema the producer emits. That is status `ok`, `measured_commit` and `harness_revision` equal to REV, 4 case rows, `failed_checks: []`, `producer_executions_new_policy: 3`, `inputs_unchanged_during_run: true`, `gate.sha256` equal to the gate digest, and `isolation {cleaned: true, residue: []}`. Then remove `baseline_stale_green_reused`, which is the authentic red-before evidence, and add `"baseline_ran": true`.

With return code 0 and empty stderr, every conjunct at lines 457–469 holds, so `demo_match` is true. `matched_gate_checks` (line 477) still reports 33. The acceptance turns green even though the regression-discriminating check is gone.

The realistic version of this is a future producer revision that renames or replaces a check with a trivially-true one. Acceptance replays the producer bytes at `--rev`, so it would not notice.

### HIGH (hazard of the obvious fix) — putting the name set in `expected_summary` refuses all 18 positive controls (operability, identity)

`inventory_projection` (lines 538–552) copies `expected_summary` verbatim, and `main` (lines 600–602) refuses with exit 2 unless the projection equals the frozen inventory. Adding a `check_names` or `phases` key to the cache step's `expected_summary` in `make_steps` would therefore refuse every run before any step executes.

"Fixing" that by editing `step-inventory.json` would be false provenance. The file claims `source_sha256` of the r20 runner and says "otherwise exact".

**Smallest safe correction:** keep the policy as module-level constants outside the step dict, so the projection stays byte-identical.

### MEDIUM — malformed payload sub-objects crash the summarizer instead of rejecting (operability)

At line 467, `payload.get("gate", {}).get("sha256")` raises `AttributeError` when `gate` is present but is not an object. The same happens at line 455 then 468 with `isolation = payload.get("isolation", {})` and `isolation.get(...)` when `isolation` is a non-object such as `"x"`.

`main` catches only `OSError, ValueError, RuntimeError, Refusal, KeyError` (line 652). The `AttributeError` therefore escapes as a traceback with no record written. This contradicts the preregistered "reject malformed producer data without a crash".

Short-circuiting means it triggers only when all earlier conjuncts pass, which is exactly the near-green malformed case. Any new per-row phase check must guard `isinstance(row, dict)` for the same reason.

### MEDIUM — the cache branch also compares integers with `==` (calibration; coordinate with the scalar seat)

Line 465 compares `payload.get("producer_executions_new_policy") == 3`. A payload value of `3.0` passes, because the JSON decoder converts real numbers to `float` (docs conversion table) and `3.0 == 3`.

The scalar repair must cover this branch, not only the counter branch at line 427. Both branches should use a single type-exact equality helper. Two helpers would be two authorities.

### LOW — repeated JSON names collapse to the last value, making check identity ambiguous (coverage)

The Python docs, "Repeated Names Within an Object" (<https://docs.python.org/3/library/json.html#repeated-names-within-an-object>, opened this round), say: "ignores all but the last name-value pair for a given name … The object_pairs_hook parameter can be used to alter this behavior."

So `"legacy_not_reused": false, …, "legacy_not_reused": true` decodes to `true`. Even an exact-name-set check would then pass. The real producer cannot emit duplicates, because `emit` uses `json.dumps` over a dict (lines 1106–1108). Rejecting duplicates therefore costs no positive control. It turns duplicates into a `ValueError` that the existing `except` already handles, so it causes no crash.

### Rejected inference (for SOURCES)

I considered deriving the expected names at runtime by AST-parsing the producer's `checks` dict literal, which would avoid a hand-copied list. I rejected it. It makes acceptance self-certifying: if the producer drops or renames a check, the oracle silently follows. That violates the preregistration's "literal independently reviewed vectors".

The literal tuple below is the authority. Its provenance is cited by line, and an AST cross-check MAY live in the oracle fixture as a review aid only.

## Minimal expected policy (draft; L1 integrates)

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
    "unsafe_control_would_retain_stale_green", "unsafe_control_would_retain_legacy_green",
    "baseline_authentic_retention", "baseline_stale_green_reused",
    "new_caller_refused_same_record_and_reexecuted", "historical_legacy_records_refused",
    "migrated_caller_reuses_unchanged", "migrated_caller_refuses_stale",
    "migrated_caller_refuses_legacy", "migrated_caller_refuses_missing_revision",
    "migrated_caller_refuses_unstable", "migrated_caller_reruns_external_mutable",
))
CACHE_DEMO_PHASES = ("initial-fresh", "unchanged", "dependency-modified", "legacy-no-dependencies")


def unique_object(pairs):
    names = [name for name, _ in pairs]
    if len(set(names)) != len(names):
        raise ValueError("repeated JSON object name")
    return dict(pairs)
```

Cache-demo branch, replacing lines 448–469 and 477:

```python
        try:
            payload = json.loads(stdout, object_pairs_hook=unique_object)
        except (ValueError, TypeError):
            payload = None
        ...
        gate = payload.get("gate") if isinstance(payload, dict) else None
        isolation = payload.get("isolation") if isinstance(payload, dict) else None
        phases = ([row.get("phase") if isinstance(row, dict) else None for row in case_rows]
                  if isinstance(case_rows, list) else None)
        demo_match = (
            isinstance(payload, dict)
            and ...                                    # status / measured_commit / harness_revision unchanged
            and isinstance(case_rows, list) and len(case_rows) == expected["cases"]
            and phases == list(CACHE_DEMO_PHASES)
            and isinstance(checks, dict) and len(checks) == expected["checks"]
            and set(checks) == CACHE_DEMO_CHECKS
            and all(value is True for value in checks.values())
            and ...                                    # failed_checks; producer_executions via the shared type-exact helper
            and isinstance(gate, dict) and gate.get("sha256") == gate_sha
            and isinstance(isolation, dict)
            and isolation.get("cleaned") is expected["isolation_cleaned"]
            and isolation.get("residue") == []
        )
        ...
            "matched_gate_checks": (sum(checks.get(name) is True for name in CACHE_DEMO_CHECKS)
                                    if isinstance(checks, dict) else 0),
```

Properties of this policy:
- **Fail-closed coupling.** If the frozen `checks: 33` and the name set ever diverge, `len(checks) == 33` and `set(checks) == CACHE_DEMO_CHECKS` cannot both hold, so every run goes red rather than silently weaker.
- **Positive-control invariance.** On a real green payload, `matched_gate_checks` stays 33 and all other `matched_counts` keys and values are unchanged. The replay-matrix signature (`AttackRunnerStepResults.md` line 30) is therefore unchanged for the real cache step. `inventory_projection` is untouched because `expected_summary` is not edited.
- **Path variation is preserved.** Only `phase` is read from each case row. Paths, digests, timestamps and gate stdout are not compared.
- **Missing/unexpected diagnostics.** If L1 wants them, they belong in a new result key, not in `matched_counts`, so the historical projection stays exact. L1 must confirm which keys the oracle projects.

## Literal oracle vectors (expected decisions; not executed)

Base is 41553adb. All vectors share the green template: rc 0, empty stderr, the real schema above, the 33 names all `true`, and the four phases in order.

| vector | base | changed |
|---|---|---|
| real green template | match | match |
| missing `baseline_stale_green_reused` + bogus `baseline_ran: true` | match (false green) | no match |
| 32 names (one dropped) | no match | no match |
| 33 names + `isolation_cleaned: true` (34 keys) | no match | no match |
| phases reordered (`unchanged` first) | match (false green) | no match |
| case row is `"x"` instead of an object | match (false green) | no match |
| `"gate": []` | crash (`AttributeError`) | no match |
| `"isolation": "x"` | crash (`AttributeError`) | no match |
| duplicated `legacy_not_reused` false then true | match (false green) | no match (`ValueError`) |
| `producer_executions_new_policy: 3.0` | match (false green) | no match via the shared type-exact helper (scalar seat) |

## Impacted axes and trade
The fix improves calibration and coverage on the cache-demo step and adds operability (malformed input is rejected instead of crashing). It harms no axis provided the policy stays out of `expected_summary`. If the name set is placed in the step dict or the frozen inventory, all 18 controls are refused and the change must be rejected. F5 code, the 160-byte reason scope, and the reap/NAMESPACE holds are untouched by this change.

## Verification
Nothing was executed. L1 should run three checks after integration:
1. The same committed synthetic result-oracle fixture over the base and changed `summarize_result`, using the vectors above.
2. The full r21 replay (`census/round-21/run-acceptance.py --root <src> --rev <full-id> --output <new>`), expecting 18/18 and unchanged cache-step `matched_counts`.
3. `inventory_projection` equality, which is implicit in step 2.

Report: .ufo/waves/round-22/w1/Cache2.md
