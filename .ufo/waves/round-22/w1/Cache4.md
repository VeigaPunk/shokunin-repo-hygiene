STATUS: PASS — A real false check value from the producer exists and is source-derived, with no invented values: `cache-demonstration.py --keep` always emits `checks.isolation_cleaned: false`, 34 checks, `status: "red"` and exit 1. The minimal safe policy is exact set equality with the 33 literal producer check names, `is True` for each value, and no new key under `expected_summary`. Source-only; nothing was executed except read-only blob digests (listed under Evidence).

## Axes

- Calibration: identity must reject renamed/replaced checks without a false red on real greens.
- Operability: the frozen-inventory refusal must not trip, and transient paths/timings must not be pinned.
- Coverage: keep all 18 real positive controls; the cache step's real green must still match.

## Evidence (executed: read-only blob digests only)

`git cat-file blob 41553adb…:<p> | sha256sum` versus the working-tree `sha256sum`, with `GIT_OPTIONAL_LOCKS=0`. All three files are identical to base, so the line numbers below hold at base:

| path | sha256 (base = wt) |
|---|---|
| census/round-14/cache-demonstration.py | 373daa9d5d0ce18fb90fcf79d8a073e480eb52fe4a4c00850bb3b22599d926b2 |
| census/round-21/run-acceptance.py | 1141839963d04e9e1b968d123fa8ffebeef5d33438537cdc636350c970eeaa2b |
| census/round-21/step-inventory.json | 8b7b1cd8d19561d9f4e8f06e797038b03379350cb3f3932edf04bda7aa7d1310 |

Everything else below is source-inferred.

## Finding 1: a real false check value from the producer (the witness)

`cache-demonstration.py` builds `checks` as a literal dict of exactly 33 keys (lines 879–979). Those keys are the only check names emitted on a green run. The single other check name the producer can emit is added after cleanup, and it is only ever `False`:

- lines 1084–1090: `cleanup(base, keep=True)` returns `cleaned: False, residue: [str(base)]`.
- lines 1202–1206: `if payload["status"] == "ok" and not state["cleaned"]` sets `status = "red"`, `checks["isolation_cleaned"] = False`, appends `failed_checks += ["isolation_cleaned"]` and sets `code = 1`.

Witness (deterministic from the `--keep` argv, also reachable when `rmtree(ignore_errors=True)` fails): the payload has 34 checks, one of which is `"isolation_cleaned": false`. It also has `status: "red"`, `failed_checks: ["isolation_cleaned"]`, `isolation.cleaned: false`, a non-empty `isolation.residue`, and exit code 1. The current runner (lines 456–480) already rejects this on six independent conjuncts. Any repair must keep rejecting it.

Counterexample to a plausible fix (calibration, false red): `step-inventory.json` lines 187–197 put `"isolation_cleaned": true` in `expected_summary`. That value means `isolation.cleaned` (runner line 468), not a check. If a fix folds it into the expected check-name set (34 names), or asserts `checks.get("isolation_cleaned") is True`, every real green run is rejected. On a real green run that key is absent, and the producer never emits it as `true`. The correct expected policy is that `isolation_cleaned` is not in `checks`, which exact 33-name equality implies.

## Finding 2: the r21 MEDIUM false green is not reachable from the producer's base bytes

Because the keys are literals, the producer at base emits either exactly the 33 names (green) or 33 plus `isolation_cleaned` (red). With the base producer, `len(checks) == 33` together with all values `is True` already implies exact identity. The `AttackRunnerStepResults.md` MEDIUM payload ("33 uniquely named, unrelated checks") does not come from this producer.

It is reachable in two ways:

1. Through `--rev` replay of a revision whose `cache-demonstration.py` bytes differ. The runner checks those inputs for drift (lines 610–622) but never pins their digest to an expected value.
2. Through the committed synthetic oracle that the preregistration requires.

So the repair guards against producer drift between revisions, not against the base producer. The report or lesson should say this so it does not overstate the base exposure.

A negative oracle vector built only from names the producer can emit: take the real 33 names, remove one (for example `historical_legacy_records_refused`), and add `"isolation_cleaned": true`. The result has 33 checks, all `true`, and `failed_checks: []`. The base runner accepts it (false green); the changed runner must reject it.

## Finding 3: placement of the expected names (operability, duplicate authority)

- `inventory_projection` (lines 537–552) copies `expected_summary` verbatim and compares it to the frozen r20-derived inventory (lines 600–602), which raises `Refusal`. A name list placed inside `expected_summary` makes every run refuse with "acceptance commands differ from the frozen r20 inventory". Editing `step-inventory.json` would break its `source_commit`/`source_sha256` provenance.
  - Correction: put the names in a module constant, or in a new step key that `inventory_projection` does not copy.
- There are now two authorities for the count: the frozen `"checks": 33` and the new tuple.
  - Correction: refuse if `len(CACHE_DEMO_CHECKS) != expected["checks"]`.
- Do not derive the names at runtime from the producer's AST. That would follow producer drift and restore the false green.
- `emit` uses `json.dumps(..., sort_keys=True)` (line 1107), so `checks` arrives sorted alphabetically, not in insertion order.
  - Counterexample: `list(checks) == [insertion order]` gives a false red on every real run.
  - Correction: compare as sets, or as `sorted(...)`.

## Finding 4: preserving case rows and transient paths (coverage)

These case-row fields vary on every run and must not be compared:

- `record`, `gate.command`, the `isolation.*` paths, and the `mkdtemp` base `souji-r14-cache-demo.XXXX` (lines 1151, 560, 272).
- `seconds`, `produced_at` and `observed_at` (lines 312, 501, 1000).
- `record_sha256`, which is fixed for a given revision but differs across revisions.

The existing `len(case_rows) == 4` is safe. If row content is tied at all (optional, beyond the preregistered claim), the only producer-determined row tuple on a green run is `(phase, retained, executions_after, gate_exit)`:

```
("initial-fresh",          False, 1, None)   # 596; gate None (600)
("unchanged",              True,  1, 0)      # 615
("dependency-modified",    False, 2, 1)      # 655
("legacy-no-dependencies", False, 3, 2)      # 795
```

These values follow from `make_case` (lines 557–572) and are already implied by checks such as `initial_fresh_once`, `unchanged_reused_without_producer`, `changed_dependency_producer_executed` and `legacy_producer_executed`. Compare them with exact types: `retained is True/False`, `type(x) is int`, `gate_exit is None`. JSON `false == 0` and `true == 1`, so a plain `==` check reintroduces the scalar defect for `gate_exit` 0 and 1.

## Related scalar note (for DraftScalarFix; not a Cache4 claim)

The cache branch's `payload.get("producer_executions_new_policy") == 3` (line 465) accepts both `3.0` and `True`-shaped types: the JSON decoder maps a real number to `float`, and `3.0 == 3`. `True` cannot equal 3, but `1.0`/`True` would equal a count of 1. The counter branch has the same float issue for exact JSON. Exact typing should use `type(v) is int`, not only a `bool` exclusion.

## Smallest safe correction (draft, cache-demo branch only)

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

# in the cache-demo branch, replacing the count-only conjuncts:
if len(CACHE_DEMO_CHECKS) != expected["checks"]:
    raise Refusal("cache check identity disagrees with frozen count")
check_identity = isinstance(checks, dict) and set(checks) == CACHE_DEMO_CHECKS
# demo_match: ... and check_identity
#             and all(value is True for value in checks.values()) ...
# matched_counts: add "missing_checks": sorted(CACHE_DEMO_CHECKS - set(checks or {})),
#                     "unexpected_checks": sorted(set(checks or {}) - CACHE_DEMO_CHECKS)
```

All 33 names are copied from `cache-demonstration.py` lines 880–978 at base 41553adb (blob digest above). `isolation_cleaned` is deliberately excluded. A `Refusal` raised inside `summarize_result` would abort the whole replay through `main`'s handler (line 652, exit 2) after the commands have already run. The length check is better placed beside the existing `EXPECTED_COMMANDS` inventory check (lines 597–599), so it refuses before any command runs. Leave `expected_summary`, `inventory_projection` and `step-inventory.json` unchanged. Keep `payload.get("failed_checks") == []` as it is.

## Oracle vectors

| vector | base runner | changed runner |
|---|---|---|
| Real green shape: 33 literal names, all `true`, 4 case rows with transient paths | match | match |
| `--keep` witness: 34 names incl. `isolation_cleaned: false`, `status: "red"` | reject | reject |
| Replacement: 32 real names + `isolation_cleaned: true`, otherwise green | match (false green) | reject |
| Real 33 names with one value `1` instead of `true` | reject (`is True`) | reject |

The oracle root must contain `tools/souji-evidence-cache.py`, because `summarize_result` reads it for `gate_sha` (line 454). The payload's `gate.sha256` must equal that file's digest.

## Impacted axes

- Calibration: improved by exact identity. A false-red risk exists if the fix includes `isolation_cleaned` or compares insertion order.
- Operability: a `Refusal` risk exists if the names go into `expected_summary`.
- Coverage: the real positive control is preserved as long as transient fields are not compared.
- No trade is required. F5, reap and NAMESPACE are untouched.

No tools were installed.
