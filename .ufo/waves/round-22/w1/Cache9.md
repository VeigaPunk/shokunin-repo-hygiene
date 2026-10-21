STATUS: PASS — source-only critic review complete. I found a real case-container witness in the named producer and derived a minimal identity policy from it. That policy rejects every wrong-container counterexample below and accepts every valid generated run, whatever its transient paths. Nothing was executed (no runner, producer, fixture, test or probe), and no tool was installed.

Axes: calibration (the primary axis), operability and coverage. No trade is proposed: each recommended move tightens calibration and coverage without changing the verdict for any valid producer run, and without changing the frozen inventory or F5.

## Real witness: where case rows actually live (source-inferred, `census/round-14/cache-demonstration.py`)

- **The case container.** On the success path, the case container is `payload["cases"]` (line 1046). It is a `list` that `run_demonstration` builds by appending `make_case(...)` results in a fixed order. Each row is a `dict` whose identity key is `"phase"` (line 559). In order, the authoritative phase values are the literal `make_case` arguments:
  - `"initial-fresh"` (line 596);
  - `"unchanged"` (line 615);
  - `"dependency-modified"` (line 655);
  - `"legacy-no-dependencies"` (line 795).
- **Other containers that look like case rows but are not:**
  - `payload["executions"]` (line 1048) holds 3 producer rows. Their phases are `initial-fresh`, `dependency-modified` and `legacy-no-dependencies`, and an unexecuted `apply_policy` would have used `unchanged-recheck` (line 610). This is a different vocabulary and a different count from `cases`.
  - The docstring's labels (lines 12–21) say `legacy-no-deps` where the code says `legacy-no-dependencies`.
  - `blocked_payload` emits `cases_observed` (line 1078) and neither `cases` nor `checks`.
  - `unsafe_policy_control.stale_case` and `unsafe_policy_control.legacy_case` (lines 856, 868) are policy controls, not case rows.
- **Order is part of the contract.** The producer's own checks index `cases[0]` through `cases[3]` by position: `initial_fresh_once`, `unchanged_reused_without_producer`, `unchanged_retained_measured_commit`, `changed_dependency_producer_executed` and `legacy_producer_executed` (lines 880–925). A reordered list is a different producer output, even if it holds the same multiset of phases.
- **The checks container.** `payload["checks"]` (line 1051) has exactly 33 keys on any `status: ok` run (lines 879–979; I counted them by name and the list is in the draft below). The red-after-cleanup path appends a 34th key, `isolation_cleaned: False` (lines 1202–1206). The expected `isolation_cleaned: True` therefore lives in `payload["isolation"]["cleaned"]`, not in `checks`.
- **Transient fields in every valid row.** These vary from run to run:
  - `record` and every path inside `gate.command`, `gate.stdout` and `result`, because each run uses a fresh `mkdtemp` under `/var/tmp/souji-r14-cache-demo.*` (line 1151);
  - the acceptance clone root `/var/tmp/souji-r21-replay-*/src` (`run-acceptance.py` line 567), which reaches the producer through the `--gate` argument;
  - `seconds` and `produced_at`.

## Counterexamples

1. **False green today (current runner, `run-acceptance.py` lines 446–470).** The only constraint on case rows is `isinstance(case_rows, list) and len(case_rows) == 4`.
   - Witness: take a real producer payload P and set `cases = P["executions"] + [P["executions"][0]]`. That gives four genuine producer dicts with phases `[initial-fresh, dependency-modified, legacy-no-dependencies, initial-fresh]`. Every other field stays real.
   - `demo_match` is true, so the step is `matched`. The same happens with `cases = [0, 0, 0, 0]` or with `list(reversed(P["cases"]))`.
   - Impacted axes: calibration and coverage.
2. **Plausible repairs that still false-green.** Any of these checks passes the witness above, or the reversed list:
   - "every row is a dict with a `phase`";
   - "the phases are a subset of the known set";
   - "the set or multiset of phases is equal".

   Only an exact ordered sequence rejects all three. Impacted axis: calibration.
3. **Wrong-container repairs that false-red valid runs.** Each of these has a source-visible cause:
   - (a) A phase vocabulary taken from the docstring (`legacy-no-deps`) or from execution phases (`unchanged-recheck`) rejects every valid run.
   - (b) Applying the counter branch's exact-JSON idea (the bool/int repair) uniformly to the cache step breaks for three reasons. `expected_summary["cases"] == 4` and `["checks"] == 33` are counts, but the payload holds a list and a dict. `isolation_cleaned` is not a top-level payload key. A generic `payload[k] == expected[k]` comparison, or a type-exact one, therefore fails every valid run.
   - (c) Adding `isolation_cleaned` to the required check-name set breaks the green path, because that key is never present there.
   - (d) Exact equality on whole rows breaks because `record`, `gate`, `seconds` and `produced_at` change per run (transient path variation).

   Impacted axes: operability and calibration.
4. **Frozen-inventory regression.** `inventory_projection` copies `expected_summary` verbatim (lines 538–552), and `main` refuses on any difference from `census/round-21/step-inventory.json` (lines 600–602; the frozen cache row is at lines 187–206). If the repair adds phase or check-name lists to `expected_summary`, every replay refuses with "acceptance commands differ from the frozen r20 inventory". The planner will see this as a hard refusal, not a red result. Impacted axis: operability.
5. **The expected set must not be self-derived.** A repair could compute the expected check names by parsing `cache-demonstration.py` (for example with `ast` over the `checks` dict). That is circular: if the producer drops a check, the oracle drops it too. The preregistration requires literal, independently reviewed vectors. Impacted axis: calibration.
6. **Malformed producer data crashes instead of yielding `matched: false`.** This is source-inferred; it is adjacent to the claim, so the cache rewrite should fix it in passing. Under the line 652 refusal tuple, two cases escape:
   - If the payload is valid up to line 466 but `"gate"` is a non-dict (for example `"x"`), `payload.get("gate", {}).get` at line 467 raises `AttributeError`. That error is outside `(OSError, ValueError, RuntimeError, Refusal, KeyError)`, so the result is a traceback, exit 1 and no record.
   - A list-valued `"isolation"` fails the same way at line 468.
   - Any new row access such as `row["phase"]` on `cases: [1, 2, 3, 4]` raises an uncaught `TypeError`.

   The preregistration says "Reject malformed producer data without a crash". Impacted axis: operability.
7. **Scalar type confusion in the cache branch (same class as the counter finding).** `payload.get("producer_executions_new_policy") == 3` (line 465) accepts the JSON value `3.0`. Python's `json` module decodes a number with a fraction part to `float`, and `3.0 == 3` is true. (`True == 3` is false, so bool does not get through here.) `status`, `failed_checks`, `inputs_unchanged_during_run` and `isolation.cleaned` already compare by `==` on str or list, or by `is`, so this is the only numeric scalar affected. Impacted axis: calibration.

## Smallest safe correction (draft only; L1 integrates it)

Put the literal vectors in module constants of the runner. The runner's bytes are already bound through `INPUT_PATHS` and the committed-bytes check at lines 222–225. Keep the frozen `expected_summary` and `step-inventory.json` byte-identical, and keep the existing count checks. A mismatch between constant length and the frozen count is an inventory refusal, never a silent pass. The draft reads only `phase` from each case row; it never compares paths, digests, timings or timestamps.

```python
CACHE_CASE_PHASES = ("initial-fresh", "unchanged", "dependency-modified", "legacy-no-dependencies")
CACHE_CHECK_NAMES = frozenset((
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
```

The next block goes in the cache-demo branch, replacing lines 451–470. The surrounding `matched_counts` keys and values stay unchanged for valid runs.

```python
        payload = payload if isinstance(payload, dict) else {}
        checks = payload.get("checks")
        case_rows = payload.get("cases")
        gate = payload.get("gate")
        isolation = payload.get("isolation")
        isolation = isolation if isinstance(isolation, dict) else {}
        case_phases = ([row.get("phase") if isinstance(row, dict) else None for row in case_rows]
                       if isinstance(case_rows, list) else None)
        executions = payload.get("producer_executions_new_policy")
        demo_match = (
            bool(payload)
            and payload.get("status") == expected["status"]
            and payload.get("measured_commit") == revision
            and payload.get("harness_revision") == revision
            and case_phases == list(CACHE_CASE_PHASES)
            and isinstance(checks, dict) and set(checks) == CACHE_CHECK_NAMES
            and all(checks[name] is True for name in CACHE_CHECK_NAMES)
            and payload.get("failed_checks") == expected["failed_checks"]
            and type(executions) is int and executions == expected["producer_executions_new_policy"]
            and payload.get("inputs_unchanged_during_run") is expected["inputs_unchanged_during_run"]
            and isinstance(gate, dict) and gate.get("sha256") == gate_sha
            and isolation.get("cleaned") is expected["isolation_cleaned"]
            and isolation.get("residue") == []
        )
```

The inventory guard goes once in `main`, beside the existing `EXPECTED_COMMANDS` check at line 598, and reads the frozen values.

```python
            cache_step = next(step for step in steps if step.get("kind") == "cache-demo")
            if (len(CACHE_CASE_PHASES) != cache_step["expected_summary"]["cases"]
                    or len(CACHE_CHECK_NAMES) != cache_step["expected_summary"]["checks"]):
                raise Refusal("cache identity vectors disagree with the frozen inventory")
```

Notes for integration:

- **Why valid runs still pass.** This rests on the producer source only. Every valid `status: ok` run has phases built from the four literal `make_case` arguments, 33 checks with exactly the names above, all `True` (checks are bool expressions, so they serialize as JSON `true`), and `producer_executions_new_policy = len(executions)`, which is an `int`. Paths, digests and timings are not read.
- **Malformed data.** With `payload = {}`, a missing or non-dict `gate`/`isolation`, or non-dict rows, the step yields `matched: false` instead of raising.
- **Optional extra coverage (not in the preregistered claim).** On every valid run, the per-phase rows also satisfy `(gate_exit, retained, executions_after)` = `(None, False, 1)`, `(0, True, 1)`, `(1, False, 2)`, `(2, False, 3)`. Each value follows from the producer's own checks (lines 880–925) and from `make_case` (`gate_exit` is `None` when there is no decision; `retained` comes from `result_origin`). If L1 adopts this, compare by `type(v) is int` / `is`, not `==`. I do not recommend it as part of the minimal fix.
- **`matched_counts` [INFERENCE].** I kept the existing keys and semantics, because `replay-matrix.sh` (not a named file, so not read this round) reportedly hashes `matched_counts`, according to AttackRunnerStepResults.md line 31. If identity diagnostics are wanted, they belong in a separate result key.

## Oracle vectors for the committed synthetic fixture (base vs. changed; all derived, none executed)

In this table, "base" means the current `run-acceptance.py` and "changed" means the draft above. P is a structurally valid synthetic payload assembled from the source-derived fields above. Its paths are arbitrary placeholders under `/var/tmp`, so no real producer values are invented. A fixture that builds P must supply a root containing `tools/souji-evidence-cache.py`. Without it, `read_regular` at line 454 raises `Refusal` before any verdict.

| vector | base | changed |
|---|---|---|
| P as is | match | match |
| P with different `/var/tmp/souji-r14-cache-demo.*` and clone-root paths in `record` and `gate` | match | match |
| `cases = executions + [executions[0]]` | match (false green) | reject |
| `cases = reversed(P.cases)` | match (false green) | reject |
| `cases = [0, 0, 0, 0]` | match (false green) | reject, no crash |
| one check renamed, still 33 and all `true` | match (false green) | reject |
| `checks` plus `isolation_cleaned: true` (34 keys) | reject | reject |
| `producer_executions_new_policy: 3.0` | match (false green) | reject |
| `gate: "x"` | uncaught `AttributeError` | reject, no crash |
| blocked payload (`cases_observed: []`, no `cases`) | reject | reject |

## Limits

- Everything above is inferred from the source of the named files. No run of the acceptance or the producer confirms it.
- The real producer stdout was not observed this round.
- I did not read `replay-matrix.sh` or the gate's source, because neither is a named file.
- F5 code, the frozen inventory, and the reap/NAMESPACE holds are untouched by these recommendations.

Files read: `census/round-21/run-acceptance.py`, `census/round-21/step-inventory.json`, `census/round-14/cache-demonstration.py`, `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`, `.ufo/waves/round-22/preregistration.txt`, `corpus/QUALITY.md`.
Report: `.ufo/waves/round-22/w1/Cache9.md`
