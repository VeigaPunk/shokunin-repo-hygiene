STATUS: PASS — Source-only cross-axis scan complete. I found one bounded connector move. It keeps calibration, operability and coverage no-harm, and it shows that the frozen r21 step inventory can stay byte-identical. Nothing was executed (no runner, oracle, fixture, test, build or probe). Every claim below comes from reading the six contract-named files. "[INFERENCE]" marks claims that need an executed control.

## Axes (from preregistration)

- **Calibration** (claimed axis): `summarize_result` `matched` must not go green on the three admitted r21 defects. Those are JSON bool/int scalar confusion, a summary step that writes stderr, and cache checks that are counted but not identified.
- **Operability** (no harm): the runner keeps exit codes 0/1/2. A malformed producer payload is rejected and does not crash the runner. The record schema and the frozen inventory stay stable.
- **Coverage** (no harm): all 18 real acceptance steps stay positive controls, and the exact historical outcome projections stay unchanged.

## Evidence (source-read, named files only)

1. **Counter scalar equality.** `run-acceptance.py:427` compares with `observed == expected`. The subset branch (`:430-431`) uses `observed.get(key) == value`. Python's `==` treats `False` as equal to `0`, `True` as equal to `1`, and `0.0` as equal to `0`. The exact counters affected are `r13-counter-31984f4` (`F2_entry: 0`, `evidence_gate: 0`), `r13-counter-6f8ee0f` (`F2_entry: 1`, `evidence_gate: 1`), and `r14-counter-a31642d`/`552cae4` (`cache_gate`/`cache_fixture`/`boundary_fixture` set to 0 or 1). Both bool and float substitution produce false greens, and so does a substitution inside nested `tiers`/`statuses`. `numeric_leaves` (`:336-344`) excludes bools, but its count never gates `matched` (`:445`). This matches AttackRunnerStepResults HIGH-1.
2. **Summary stderr.** The summary branch (`:369-419`) never consults `stderr`. The counter branch (`:445`) and the cache branch (`:480`) both require `not stderr`. `failure_lines` (`:330-333`) only recognizes three marker spellings. This is the Q11 failure mode: "checkers test behaviour, not marker spellings". Of the 18 steps, 12 are summary steps: auditor-selftest through agreement-pin-check in `step-inventory.json`.
3. **Cache identity.** The cache branch (`:456-470`) checks `len(checks) == 33`, that every value `is True`, and `len(case_rows) == 4`. It never checks names or phases.
   - The authoritative names are source literals in `cache-demonstration.py:879-978`. I counted exactly 33 keys there.
   - The case phases are the first argument of `make_case` at `:594/:612/:653/:793`: `initial-fresh`, `unchanged`, `dependency-modified`, `legacy-no-dependencies`. The row key is `"phase"` (`:559`).
   - **Contradiction to note:** the demo's docstring (`:20`) says `legacy-no-deps`. Identity must use the code literal `legacy-no-dependencies`, not the prose.
   - `isolation_cleaned` is added to `checks` only on failure (`:1204`). That correctly turns an exact 33-name set check red.
4. **Crash path (malformed data, not covered by the admitted defects but required by the preregistration).**
   - At `:455` and `:467`, `payload.get("isolation", {})` and `payload.get("gate", {}).get("sha256")` assume dicts. If a producer emits `"gate": []` or `"isolation": "x"`, the runner raises `AttributeError`.
   - `main` catches only `(OSError, ValueError, RuntimeError, Refusal, KeyError)` (`:652`). So the base runner dies with a traceback and writes no record. The preregistration says "Reject malformed producer data without a crash."
   - [INFERENCE] The base result for such a vector is a crash, so the oracle must record a distinct `crash` outcome rather than a pass or fail.
5. **Frozen-inventory binding.** `inventory_projection` (`:537-552`) projects only the keys `name, expected_summary, pass_pattern, pass_count, record_checks, exact_json, baseline_mismatch_count, kind, argv`. `main` refuses if the projection differs from `step-inventory.json` (`:600-602`). Putting the check-name list inside `expected_summary` would force a rewrite of the frozen r21 inventory, which records its own `source_sha256` of the r20 runner. A module constant outside the projected keys does not.
6. **Self-path coupling.** `combined_snapshot` (`:222-225`) requires the running file to equal `census/round-21/run-acceptance.py`. `INPUT_PATHS` and the step-inventory path (`:600`) are hard-coded to round 21. L1's integration choice is a contract surface:
   - Editing in place changes the bytes of a filed r21 runner. Q41 forbids rewriting filed evidence. [INFERENCE] Whether the runner counts as "evidence" here is L1's call.
   - Copying to a round-22 path requires updating the self-path, `INPUT_PATHS`, the inventory path, the schema string and the temp prefix together.
7. **Already-resolved r21 LOW.** The current bytes write `source_sample_unchanged` (`:635`), and the scope text says the samples are "not whole-source contents or cleanliness" (`:647`). AttackRunnerStepResults LOW (`source_unchanged`) does not apply to these bytes. No move is needed.

## Cross-axis overlap scan (what is ours versus the neighbouring seats)

| Surface | Owner | Boundary |
|---|---|---|
| `summarize_result` predicate correctness for the three defects plus crash-free rejection | Souji calibration (this claim) | Only `run-acceptance.py` summarizer logic. No other step semantics. |
| Oracle method: same committed fixture on base and changed, literal reviewed vectors, paired positive/negative controls | Tameshi fixture methodology (QUALITY Q22/Q39 paired-control rule; Q4 `/var/tmp`) | Calibration consumes the oracle's decisions. It must not define its own passing table. |
| F5 bytes, the 160-byte reason scope, `/proc`, process TSVs, stderr text retained in the record | Kagi privacy (Q42/Q46/Q49) | The move does not touch F5 or `/proc`. Synthetic oracle stderr must be fabricated, never captured from live tools. |
| Exit codes, refusal without crash, record/inventory stability, real-step greens | Mori health/operability | The blanket summary-stderr rule is the only place this move could harm operability (see risk R1). |

## Proposed move (one, bounded): a single strict JSON comparator and unprojected cache identity constants

Use one recursive type-exact comparator for all three JSON scalar sites:

- the counter exact comparison,
- the counter subset comparison,
- the cache-demo scalar fields.

Put the cache identity, meaning the 33 check names and the 4 ordered phases, in module constants outside the projected step keys. Then:

- the frozen `step-inventory.json` and its projection stay byte-identical, so coverage and historical projections are unchanged;
- the identity is still bound, because the runner's own bytes are in `INPUT_PATHS` and are digest-checked;
- the same comparator also closes the `gate`/`isolation` crash path, because non-dict values become mismatches.

The summary-stderr fix is one conjunct. This is a synthesis of the DraftScalarFix and DraftCacheFix lanes: one predicate replaces three ad-hoc `==` sites, rather than two parallel patches.

```python
CACHE_DEMO_PHASES = ("initial-fresh", "unchanged", "dependency-modified", "legacy-no-dependencies")
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


def json_equal(observed, expected) -> bool:
    if isinstance(expected, dict):
        return (isinstance(observed, dict) and observed.keys() == expected.keys()
                and all(json_equal(observed[key], value) for key, value in expected.items()))
    if isinstance(expected, list):
        return (isinstance(observed, list) and len(observed) == len(expected)
                and all(json_equal(item, want) for item, want in zip(observed, expected)))
    return type(observed) is type(expected) and observed == expected
```

These are the changed sites (draft only; L1 integrates):

```python
# summary branch, replacing the final conjunction
        matched = matched and summary_match and pass_match and not stderr
# counter branch
        if step["exact_json"]:
            json_match = json_equal(observed, expected)
        else:
            json_match = (isinstance(observed, dict)
                          and all(key in observed and json_equal(observed[key], value)
                                  for key, value in expected.items()))
# cache-demo branch
        gate = payload.get("gate") if isinstance(payload, dict) else None
        isolation = payload.get("isolation") if isinstance(payload, dict) else None
        demo_match = (
            isinstance(payload, dict)
            and payload.get("status") == expected["status"]
            and payload.get("measured_commit") == revision
            and payload.get("harness_revision") == revision
            and isinstance(case_rows, list) and len(case_rows) == expected["cases"]
            and tuple(row.get("phase") if isinstance(row, dict) else None
                      for row in case_rows) == CACHE_DEMO_PHASES
            and isinstance(checks, dict) and len(checks) == expected["checks"]
            and checks.keys() == CACHE_DEMO_CHECKS
            and all(value is True for value in checks.values())
            and json_equal(payload.get("failed_checks"), expected["failed_checks"])
            and json_equal(payload.get("producer_executions_new_policy"),
                           expected["producer_executions_new_policy"])
            and payload.get("inputs_unchanged_during_run") is expected["inputs_unchanged_during_run"]
            and isinstance(gate, dict) and gate.get("sha256") == gate_sha
            and isinstance(isolation, dict)
            and isolation.get("cleaned") is expected["isolation_cleaned"]
            and json_equal(isolation.get("residue"), [])
        )
```

The `matched_counts` diagnostics and the record schema stay unchanged, so the replay-matrix signature fields are unchanged.

L1 may also add a structural guard in `main`, next to the existing `EXPECTED_COMMANDS` check: refuse when `len(CACHE_DEMO_CHECKS)` differs from the cache step's `expected_summary["checks"]`, or when `len(CACHE_DEMO_PHASES)` differs from `["cases"]`. It is optional. It keeps the constants and the frozen counts from drifting apart.

## Risks

- **R1 (operability/coverage).** [INFERENCE] The blanket `not stderr` rule on the 12 real summary steps assumes they emit no stderr today. The named files do not show their real stderr. If any of them emits a benign warning, this move turns a real positive red. **Gate:** before adopting the blanket rule, L1 checks that every summary command in the base acceptance record has `stderr_sha256 == e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. If any step does not, use a reviewed per-step expected-stderr literal for that step instead of `""`. Never weaken the rule globally.
- **R2 (calibration scope).** `json_equal` also rejects int/float confusion (`0.0` versus `0`). That is inside "JSON scalar type equality" (the round goal), but it goes beyond the literal bool/int wording in the preregistration. The oracle needs an explicit float vector, or the claim must say bool/int only.
- **R3 (oracle contract).** The same oracle drives both base and changed bytes only if the signature `summarize_result(step, returncode, stdout_bytes, stderr_bytes, revision, root)` stays identical. The cache branch reads `root/tools/souji-evidence-cache.py`.
  - The oracle should pass the real checkout as `root`, read-only, and compute `gate_sha` from it. Then it creates no scratch files, which avoids Q4 entirely.
  - The base runner raises `AttributeError` on non-dict `gate`/`isolation`. The oracle must catch per-vector exceptions and record `crash` as a literal expected base outcome.
- **R4 (integration path).** Evidence item 6 is unresolved by this seat: in-place edit versus a round-22 copy. Either way, every round-21 literal in `combined_snapshot`, `INPUT_PATHS` and the `:600` path must move together, or the runner refuses.
- **Held, not in this claim.**
  - The `record_checks: 1` field on `agreement-pin-check` is echoed from the step definition (`:415`) and never observed. An exit-0 run with no output passes that step. This is the same counted-not-identified class, but it was not admitted.
  - `json.loads` keeps the last of any duplicate keys and accepts `NaN`. Duplicate keys can mask a value. This is outside the preregistered defects.
  - Route both items to the next round. Do not fix them here, because the preregistration says "No additional axis claim."

## Required positive and negative controls (for L1/Tameshi; none executed here)

1. **Real acceptance positive controls.** The changed runner reports all 18 steps `matched` at the integrated revision (`matched_command_count == 18`). The `inventory_projection` equality still passes. `step-inventory.json` is byte-identical to base.
2. **Paired oracle vectors**, on the same fixture for base and changed. For each target vector, include its sibling positive with correct types, empty stderr and the correct names, green on both.
   - Exact counter `F2_entry: false` (r13-31984f4). Base green, changed red.
   - Nested `tiers.C: true` (r13-6f8ee0f; base 1). Base green, changed red.
   - `cache_gate: 1.0` (r14-552cae4). Base green, changed red (float; see R2).
   - Subset counter `admitted_entries: 6.0`. Base green, changed red.
   - `auditor-selftest` exact stdout plus stderr `ERROR: self-test could not complete`. Base green, changed red.
   - Cache payload with 33 all-true checks where one real name is replaced by a bogus name. Base green, changed red.
   - Cache payload with phases permuted, or one phase spelled `legacy-no-deps`. Base green, changed red.
   - Cache `producer_executions_new_policy: 3.0`. Base green, changed red.
   - Cache `"gate": []` and `"isolation": "x"`. Base crash (`AttributeError`), changed red with no exception.
3. **Precondition for R1.** Summary-step stderr is empty in a real base record.
4. **No-harm.** F5 production bytes, including the 160-byte synthetic-only reason scope, are byte-identical to base 41553adb. The oracle reads no `/proc`, process TSVs or live census output (preregistration; Q42/Q49).

## Verification performed

Source reading only:

- `run-acceptance.py:1-659`, all of it;
- `step-inventory.json:1-339`, all of it;
- `cache-demonstration.py:1-300, 556-623, 653-664, 793-804, 860-1223`, plus two exact-pattern greps scoped to that single named file;
- AttackRunnerStepResults, the preregistration and QUALITY in full.

Nothing was executed and nothing was installed. I wrote no files other than this report.

Report: .ufo/waves/round-22/w1/ConnectScope.md
