STATUS: PASS — Source-only critique complete. The cache-demonstration case identity in the round-21 summarizer is checked only by count, so duplicated, permuted or JSON-duplicate-key payloads can turn green. The smallest safe policy is: ordered phase-list equality, an exact check-name set, rejection of duplicate JSON object keys, and type guards so malformed input fails without a crash. Every expected value below comes from the named producer source. Nothing was executed.

Seat: SoujiR22.Cache10 (critic, leaf). Base 41553adb139d06511dc386bb3ce4326aebfba675.
Evidence class: **source-inferred** throughout. Nothing was run, built, probed or installed. The DraftCacheFix draft is not a named file, so I did not read it. The attacks below target the policy class that any count-, set- or row-literal-based fix falls into.

Files read (named only): `census/round-21/run-acceptance.py`, `census/round-21/step-inventory.json`, `census/round-14/cache-demonstration.py`, `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`, `.ufo/waves/round-22/preregistration.txt`, `corpus/QUALITY.md`.

## Real producer witness (source-derived, not executed)

`census/round-14/cache-demonstration.py` `run_demonstration` appends exactly four case rows via `make_case(phase, ...)`, in this fixed order:

| order | case `phase` (first arg to `make_case`) | source line | `gate_exit` | `reusable` | `retained` | `producer_execution` | `executions_after` | `record` file |
|---|---|---|---|---|---|---|---|---|
| 0 | `initial-fresh` | 596 | null | null | false | index 1 | 1 | `records/record.json` |
| 1 | `unchanged` | 615 | 0 | true | true | null | 1 | `records/record.json` |
| 2 | `dependency-modified` | 655 | 1 | false | false | index 2 | 2 | `records/record.json` |
| 3 | `legacy-no-dependencies` | 795 | 2 | false | false | index 3 | 3 | `records/record-legacy.json` |

These values hold only when `status == "ok"`. They are enforced by producer checks `initial_fresh_once`, `unchanged_gate_exit_zero`, `unchanged_reused_without_producer`, `changed_dependency_gate_exit_one`, `changed_dependency_producer_executed`, `legacy_gate_exit_two` and `legacy_producer_executed` (lines 880–925).

The producer's `checks` dict (lines 879–979) has exactly 33 names, and the count matches inventory `checks: 33`:

`initial_fresh_once, producer_actual_subprocess_green, unchanged_gate_exit_zero, unchanged_gate_status_reusable, changed_dependency_exact_finding, legacy_exact_finding, unchanged_reused_without_producer, unchanged_retained_measured_commit, changed_dependency_gate_exit_one, changed_dependency_not_reused, changed_dependency_producer_executed, changed_dependency_fresh_digests, legacy_gate_exit_two, legacy_not_reused, legacy_producer_executed, legacy_fresh_digests, only_declared_dependency_changed, record_bytes_unchanged, gate_digest_recorded_and_unchanged, execution_log_matches_disk, isolation_confined, unsafe_control_would_retain_stale_green, unsafe_control_would_retain_legacy_green, baseline_authentic_retention, baseline_stale_green_reused, new_caller_refused_same_record_and_reexecuted, historical_legacy_records_refused, migrated_caller_reuses_unchanged, migrated_caller_refuses_stale, migrated_caller_refuses_legacy, migrated_caller_refuses_missing_revision, migrated_caller_refuses_unstable, migrated_caller_reruns_external_mutable`.

One path adds a 34th key. `main()` lines 1202–1206 add `isolation_cleaned: False` only when cleanup fails, and also set `status: "red"`. That path is already red, so an exact 33-name set loses no valid green.

The values below vary between runs and **must not** be compared as literals:
- **Paths:** `record` paths are under `mkdtemp(prefix="souji-r14-cache-demo.", dir="/var/tmp")`. The `gate.command` and `producer_execution.producer.command` fields carry `sys.executable`, the clone root `/var/tmp/souji-r21-replay-*/src/...` and the fixture root.
- **Timings:** `produced_at` and `seconds`.
- **Rows 0–2:** these rows have the same `record` path and the same `record_sha256`. This is required by producer check `record_bytes_unchanged`.
- **Rows 2–3:** `declared_dependency_digests_match` is `false` in both rows on a valid run. Row 2 is stale by design, and row 3 is legacy with no dependencies.

## Findings

### F1 MEDIUM — Duplicate or permuted case identity passes (base defect; also defeats any count- or membership-based draft)

Evidence: `run-acceptance.py:461` checks only `isinstance(case_rows, list) and len(case_rows) == expected["cases"]`. No row content is read.

Counterexample: take the real ok payload and replace `cases` with four copies of the real row 0 (`initial-fresh`). Alternatively use `[initial-fresh, unchanged, unchanged, legacy-no-dependencies]`. Every other field stays the same as producer output.
- Base: `demo_match` is True, so `matched` is True (false green).
- A per-row membership draft (`all(row["phase"] in ALLOWED ...)`) is also True (false green).
- A `set(phases) == ALLOWED` draft combined with `len == 4` rejects duplicates but accepts any permutation. That still contradicts the order-dependent `executions_after` sequence 1, 1, 2, 3.

Smallest safe correction: ordered list equality on the extracted phase list: `phases == ["initial-fresh", "unchanged", "dependency-modified", "legacy-no-dependencies"]`. It rejects both duplicates and permutations. The real producer is deterministic (one `cases.append` per phase, in source order), so no valid generated row set is lost.

### F2 MEDIUM — Duplicate JSON object keys collapse identity before any identity check runs

Evidence: `run-acceptance.py:448` uses plain `json.loads(stdout)`. Python's `json` documentation ([Repeated Names Within an Object](https://docs.python.org/3/library/json.html#repeated-names-within-an-object)) says the decoder does not raise on repeated names and ignores all but the last name-value pair. RFC 8259 §4 says names SHOULD be unique, and receivers disagree on duplicates.

Counterexamples (malformed producer output; no attestation claimed):
- `"checks": {..., "legacy_exact_finding": false, ..., "legacy_exact_finding": true}` has 34 pairs and 33 distinct names. After parsing, the result has 33 keys and all values are `True`. An exact-name-set fix passes it, although the producer emitted two values for one check identity.
- Top-level `"status": "red", ..., "status": "ok"` parses as `"ok"`, while a first-wins consumer sees red.

The real producer cannot emit duplicates. `emit()` uses `json.dumps(payload, sort_keys=True)` over Python dicts with string keys. Mixed-type keys would raise `TypeError` under `sort_keys`, so no `1`/`"1"` collision can occur. Rejecting duplicates therefore preserves every valid output.

Smallest safe correction: pass `object_pairs_hook` that raises `ValueError` on a repeated key. The existing `except (ValueError, TypeError): payload = None` at lines 449–450 already turns that into a non-crashing mismatch. The hook applies at every nesting level, so case rows are covered too.

### F3 LOW–MEDIUM (operability) — Malformed producer data can crash the runner instead of failing the step

Evidence: `run-acceptance.py:467` evaluates `payload.get("gate", {}).get("sha256")`, and line 455 together with lines 468–469 evaluates `isolation.get(...)`. If the key exists with a `null` or list value, `.get` returns that value and the next `.get` raises `AttributeError`. `main()` catches only `(OSError, ValueError, RuntimeError, Refusal, KeyError)` (line 652), so the result is an uncaught traceback and no record is written.

Counterexample: the real ok payload with `"gate": null`. Every earlier `and` term holds, so evaluation reaches line 467.

Draft trap: a phase check written as `{row["phase"] for row in case_rows}` adds two more failure modes:
- `TypeError` for `"phase": []` (unhashable) or for a non-dict row. This is also uncaught, so the runner crashes.
- `KeyError` for a missing `phase`. This is caught by `main()` and becomes exit 2 "refused with no new result" rather than a recorded failed step.

Both violate the preregistration's "Reject malformed producer data without a crash".

Smallest safe correction: use `isinstance(..., dict)` guards for `gate`, `isolation` and each row. Extract phases with `row.get("phase") if isinstance(row, dict) else None`. Compare with list equality, which works on unhashable values.

### F4 TRADEOFF/TRAP — Plausible identity sources that false-red the real producer (the judge must reject these)

Each of these alternatives is derived from the named files and turns a real green into red:
- **Docstring names:** lines 12–21 call case 4 `legacy-no-deps`, but the code emits `legacy-no-dependencies` (line 795).
- **Policy-phase names:** the `apply_policy` phase for case 1 is `unchanged-recheck` (line 610), but the case row's phase is `unchanged` (line 615).
- **`executions[*].phase`:** this list contains only three phases (`initial-fresh`, `dependency-modified`, `legacy-no-dependencies`) and cannot identify four cases.
- **Uniqueness of `record` or `record_sha256`:** rows 0–2 share both on a valid run.
- **All rows matching:** requiring `declared_dependency_digests_match` to be true for every row fails on rows 2 and 3.
- **Frozen whole rows:** comparing full case rows to a literal fails on the varying values listed above (mkdtemp paths, `sys.executable`, `produced_at`, `seconds`).

Correction: identity is the `phase` field taken from the `make_case` first arguments, and nothing else. Optional extra projections (`gate_exit`, `reusable`, `retained`, `executions_after`) are consistent with the table above. They are not needed for the identity claim, and they only repeat facts the payload already reports about itself, so I do not require them.

### F5 TRADEOFF — Where the identity expectation lives

`inventory_projection` (lines 537–552) copies `expected_summary` verbatim and compares it to the frozen `census/round-21/step-inventory.json` `steps` (lines 600–602). Adding `case_phases` or `check_names` inside `expected_summary` makes every replay refuse with "acceptance commands differ from the frozen r20 inventory". Fixing that would mean editing the frozen inventory and its r20 provenance note, which breaks the "exact historical outcome projections" requirement.

Smallest safe correction: keep `expected_summary` byte-identical. Put the identities in module constants in the runner. That file is in `INPUT_PATHS` and is self-checked against committed bytes (lines 222–225), so the constants are byte-bound. Add a startup consistency refusal so the frozen counts and the constants cannot drift apart. Put diagnostics under a new result key rather than changing `matched_counts` keys, so historical `matched_counts` projections stay unchanged. Recording the identity outside the frozen inventory is a disclosed limit, not a weakening: the frozen 4/33 counts still apply as well.

## Expected decision vectors (literal; L1 to execute against base and changed code)

Every vector is the real ok payload with exactly one mutation. "Real ok" means the L1 acceptance's own positive control; no producer values are invented.

| id | mutation | base `matched` | changed `matched` | changed process |
|---|---|---|---|---|
| V0 | none (real `clean-cache-demonstration` step output) | true | true | exit per all-matched |
| V1 | `cases` = 4 × real row 0 | **true** (false green) | false | no crash |
| V2 | `cases` rows 1 and 2 swapped | **true** | false | no crash |
| V3 | `cases` = rows [0, 1, 1, 3] | **true** | false | no crash |
| V4 | `checks`: one real name replaced by `bogus_check: true` (the r21 finding) | **true** | false | no crash |
| V5 | `checks`: 34 pairs, `legacy_exact_finding` repeated false then true | **true** | false (parse rejected) | no crash |
| V6 | top level: `"status":"red"` followed by `"status":"ok"` | **true** | false (parse rejected) | no crash |
| V7 | `"gate": null` | **crash** (`AttributeError`) | false | no crash |
| V8 | `"isolation": null` | **crash** (`AttributeError`) | false | no crash |
| V9 | row 2 `"phase": ["dependency-modified"]` | **true** | false | no crash |
| V10 | row 3 replaced by the JSON string `"legacy-no-dependencies"` (not an object) | **true** | false | no crash |
| V11 | `record`/`gate.command`/`produced_at` changed to another mkdtemp path and timestamp | true | true | preserves path variation |

## Draft correction (report-only; not applied)

```python
CACHE_CASE_PHASES = ("initial-fresh", "unchanged", "dependency-modified", "legacy-no-dependencies")
CACHE_CHECK_NAMES = frozenset((
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


def unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON object key: " + key)
        obj[key] = value
    return obj
```

```python
    # main(), beside the existing fixed-inventory refusal:
    cache_step = next(step for step in steps if step.get("kind") == "cache-demo")
    if (len(CACHE_CASE_PHASES) != cache_step["expected_summary"]["cases"]
            or len(CACHE_CHECK_NAMES) != cache_step["expected_summary"]["checks"]):
        raise Refusal("cache identity constants disagree with the frozen inventory counts")
```

```python
    elif kind == "cache-demo":
        try:
            payload = json.loads(stdout, object_pairs_hook=unique_pairs)
        except (ValueError, TypeError):
            payload = None
        if not isinstance(payload, dict):
            payload = None
        checks = payload.get("checks") if payload else None
        case_rows = payload.get("cases") if payload else None
        gate = payload.get("gate") if payload else None
        isolation = payload.get("isolation") if payload else None
        phases = ([row.get("phase") if isinstance(row, dict) else None for row in case_rows]
                  if isinstance(case_rows, list) else None)
        case_identity = phases == list(CACHE_CASE_PHASES)
        check_identity = isinstance(checks, dict) and set(checks) == CACHE_CHECK_NAMES
        # ... existing terms unchanged, plus:
        #   and case_identity and check_identity
        #   and isinstance(gate, dict) and gate.get("sha256") == gate_sha
        #   and isinstance(isolation, dict) and isolation.get("cleaned") is expected["isolation_cleaned"]
        #   and isolation.get("residue") == []
        result["cache_identity"] = {
            "expected_case_phases": list(CACHE_CASE_PHASES),
            "observed_case_phases": phases,
            "case_identity_match": case_identity,
            "check_names_match": check_identity,
            "missing_check_names": sorted(CACHE_CHECK_NAMES - set(checks)) if isinstance(checks, dict) else None,
            "unexpected_check_names": sorted(set(checks) - CACHE_CHECK_NAMES) if isinstance(checks, dict) else None,
        }
```

The existing `matched_counts` keys and their values stay unchanged. The `.get` calls in `matched_counts` must use the narrowed `payload`, which is `None` or a dict.

## Impacted axes

- **Calibration:** V1–V6, V9 and V10 are false greens on base (F1, F2).
- **Operability:** V7 and V8 are crashes on base, and a set-based draft adds a `TypeError` crash and a `KeyError` refusal (F3).
- **Coverage:** the 33 check names and 4 case phases are now identified rather than only counted (F1, F2).

No axis trade is needed: V0 and V11 keep real output green, and F5 keeps the frozen inventory and historical projections byte-identical. Out of scope and untouched: F5 production code (byte-identical), the 160-byte synthetic-only repair, and the reap, NAMESPACE and historical-assessment holds.

## Adjacent (not this seat's claim)

`unique_pairs` belongs on the counter branch too (`run-acceptance.py:422`). Otherwise `{"F2_entry": 5, "F2_entry": 0}` passes `observed == expected` the same way. This is separate from the scalar-type fix, which the scalar seat owns.

## Verification gaps

- Every finding is source-inferred. Base `matched` values and crash outcomes in the vectors table come from reading control flow, not from execution.
- L1 must run V0–V11 against base and changed code, plus the 18-step acceptance.
- The checks-name list was transcribed from lines 879–979. L1 should confirm it against an actual ok payload's `checks` keys.
- No tools were installed or updated.

Report: .ufo/waves/round-22/w1/Cache10.md
