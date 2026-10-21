STATUS: PASS — Assigned source-only critique of the cache-demonstration acceptance predicate is complete. It found five false-green or crash witnesses that a repair limited to check names would leave open, plus one regression trap in the frozen inventory. Nothing was executed; every decision below is inferred from source.

Scope: `census/round-21/run-acceptance.py` (cache-demo branch lines 446–480, main 596–602, 652), `census/round-21/step-inventory.json` (lines 186–205), `census/round-14/cache-demonstration.py` (lines 1–1223, read in full), `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`, `.ufo/waves/round-22/preregistration.txt`, `corpus/QUALITY.md`. No other paths, no runs, no tool installs.

## Real witness: what the named producer actually emits on green (source-derived)

**Check identity.** `checks` is one dict literal at `cache-demonstration.py:879–979` with exactly **33** keys. That count matches inventory `"checks": 33` (`step-inventory.json:192`). Sorted:

`baseline_authentic_retention, baseline_stale_green_reused, changed_dependency_exact_finding, changed_dependency_fresh_digests, changed_dependency_gate_exit_one, changed_dependency_not_reused, changed_dependency_producer_executed, execution_log_matches_disk, gate_digest_recorded_and_unchanged, historical_legacy_records_refused, initial_fresh_once, isolation_confined, legacy_exact_finding, legacy_fresh_digests, legacy_gate_exit_two, legacy_not_reused, legacy_producer_executed, migrated_caller_refuses_legacy, migrated_caller_refuses_missing_revision, migrated_caller_refuses_stale, migrated_caller_refuses_unstable, migrated_caller_reruns_external_mutable, migrated_caller_reuses_unchanged, new_caller_refused_same_record_and_reexecuted, only_declared_dependency_changed, producer_actual_subprocess_green, record_bytes_unchanged, unchanged_gate_exit_zero, unchanged_gate_status_reusable, unchanged_reused_without_producer, unchanged_retained_measured_commit, unsafe_control_would_retain_legacy_green, unsafe_control_would_retain_stale_green`.

Every value is a Python `bool`. Each is a comparison, `is`, `not`, `bool()`/`all()`, or an `and` chain whose first operand is already bool, so JSON emits `true`/`false`.

`isolation_cleaned` is **not** a green-path check. It is added only on cleanup failure, as `False`, with status forced to `red` (`:1202–1206`).

**Case rows.** There are four `make_case` calls, in this order: `:594–604`, `:612–622`, `:653–663`, `:793–803`. Each row's fields come from `:556–572`. The invariant projection below follows from code paths. It is not invented:

| phase (literal) | gate_exit | reusable | retained | producer_execution | executions_after | declared_dependency_digests_match | gate.findings |
|---|---|---|---|---|---|---|---|
| `initial-fresh` | null | null | false | index 1 | 1 | true | gate is null |
| `unchanged` | 0 | true | true | null | 1 | true | `[]` |
| `dependency-modified` | 1 | false | false | index 2 | 2 | false | `["dependency-digest-mismatch"]` |
| `legacy-no-dependencies` | 2 | false | false | index 3 | 3 | false (no `dependencies` key; `isinstance` fails at `:557`) | `["dependencies-legacy"]` |

How each column is grounded:
- **retained:** `result_origin == "retained-from-record"` (`:569`); only `apply_policy`'s reuse branch sets it (`:541`).
- **reusable:** `exit_code == 0` (`:529`).
- **executions_after:** `len(executions)` at case time. The checks at `:880`, `:904`, `:915`, `:924` assert the same values.
- **findings:** the gate's own output, which `:893–900` and `:887–888` already require to match exactly.

**Transient fields that must NOT be compared** (they vary per run or per host): `record` paths under `mkdtemp` (`:1151`), `record_sha256`, `declared`, `observed_dependencies`, `gate.command`/`stdout`/`stderr`/`seconds`/`measured_commit`, `result.producer.seconds`, `producer_execution.produced_at`/`seconds`/`command` (`sys.executable`).

## Counterexamples (strongest first)

### C1 — HIGH (calibration): renamed checks and arbitrary case rows pass
`run-acceptance.py:461–463` checks only `len(case_rows) == 4`, `len(checks) == 33` and `value is True`. So both of these pass today:
- `checks` with `initial_fresh_once` replaced by any other name;
- `cases: [1, 2, 3, 4]`.

This confirms the r21 MEDIUM finding (`AttackRunnerStepResults.md:17–20`).

Note the claim's wording: "exact cache check identity" covers only half of that finding. A repair that identifies checks but leaves case rows counted keeps the "cases counted rather than identified" defect, and the r21 finding names case content explicitly. Either repair case rows too (C3), or the round wording must say case rows stay count-only.

### C2 — HIGH (calibration): scalar type confusion in the cache branch
The bool/int defect is not counter-only:
- `payload.get("producer_executions_new_policy") == 3` (`:465`) accepts `3.0`, because Python `json` decodes `3.0` to `float` and `3.0 == 3` is true.
- Any case-row repair written with `==` would accept `"gate_exit": false` for `0`, and `true`/`1.0` for `executions_after: 1`.

A repair that only excludes `bool` (for example `not isinstance(x, bool)`) still accepts floats. Exact JSON equality must compare `type(observed) is type(expected)` recursively. One helper should serve both the counter and cache branches; two separate type-equality rules would be duplicate authorities.

### C3 — MEDIUM (coverage): docstring phase names differ from emitted phase names
The docstring lists `legacy-no-deps` (`cache-demonstration.py:20`). The emitted phase is `legacy-no-dependencies` (`:795`).

The execution-phase label `unchanged-recheck` (`:610`) is never emitted on green, because no producer runs for that case.

Any expected-phase table copied from the docstring false-reds the real positive control. Phases must be taken from the `make_case` call sites.

### C4 — MEDIUM (operability): malformed producer data crashes the runner
The preregistration requires that malformed producer data be rejected without a crash.
- With every earlier conjunct true, `"gate": null` makes `payload.get("gate", {})` return `None`, and `.get("sha256")` raises `AttributeError` (`:467`).
- `"isolation": []` (or any non-dict) fails the same way at `:468`, because `:455` returns the non-dict as-is.

`main`'s handler catches only `(OSError, ValueError, RuntimeError, Refusal, KeyError)` (`:652`). The traceback therefore propagates, no record is written, and the process exits 1. That is the same exit code as an ordinary red result [INFERENCE: standard CPython uncaught-exception status].

### C5 — MEDIUM (calibration): null-member shortcuts in a naive row check
If the row check reads `row.get("producer_execution", {}).get("execution_index")`, then an `unchanged` row with `"producer_execution": {}` yields `None` and matches the expected null.

Likewise `initial-fresh` with `"gate": {"findings": null}` matches "gate is null".

The projection must tell apart "container is null" and "container is a dict whose member is X".

### C6 — HIGH (hidden regression): editing `expected_summary` triggers a refusal
`main` compares `inventory_projection(steps…)` against frozen `step-inventory.json` (`:600–602`).

Putting the name set or case table into the step's `expected_summary` (in `make_steps:312–317`) makes every run refuse with "acceptance commands differ from the frozen r20 inventory". Rewriting the frozen inventory instead breaks the preregistered "exact historical outcome projections".

The constants must live outside `expected_summary`, tied to it by a startup equality check against its counts `33` and `4`.

### C7 — LOW (operability, optional): duplicate JSON keys collapse before identity is checked
`json.loads` keeps the last duplicate key, so `{"initial_fresh_once": false, "initial_fresh_once": true, …}` decodes as all-true.

The honest producer cannot emit duplicates, because it serializes a dict with `json.dumps(sort_keys=True)` (`:1107`). So a duplicate-rejecting `object_pairs_hook` on the cache decode costs no positive control.

This is not required by the claim, since no malicious-producer attestation is claimed. If added, it must be fail-closed (treated as not matched), not a raised exception.

## Rejected inference (for SOURCES)
I considered deriving the expected check names at runtime by AST-parsing or importing `cache-demonstration.py`. **Rejected**: that would make the producer its own oracle. Renaming or dropping a check would silently update the expectation, which is false provenance.

I also rejected comparing exact row key sets, `record_sha256` or observed digests. They add no independent semantics and violate the preservation of transient path variation.

## Smallest safe correction (draft; L1 integrates; `expected_summary` and frozen inventory stay byte-identical)

```python
_ABSENT = object()


def json_equal(observed, expected) -> bool:
    if type(observed) is not type(expected):
        return False
    if isinstance(expected, dict):
        return (observed.keys() == expected.keys()
                and all(json_equal(observed[key], expected[key]) for key in expected))
    if isinstance(expected, list):
        return (len(observed) == len(expected)
                and all(json_equal(item, want) for item, want in zip(observed, expected)))
    return observed == expected


CACHE_DEMO_CHECKS = frozenset((
    "baseline_authentic_retention", "baseline_stale_green_reused",
    "changed_dependency_exact_finding", "changed_dependency_fresh_digests",
    "changed_dependency_gate_exit_one", "changed_dependency_not_reused",
    "changed_dependency_producer_executed", "execution_log_matches_disk",
    "gate_digest_recorded_and_unchanged", "historical_legacy_records_refused",
    "initial_fresh_once", "isolation_confined", "legacy_exact_finding",
    "legacy_fresh_digests", "legacy_gate_exit_two", "legacy_not_reused",
    "legacy_producer_executed", "migrated_caller_refuses_legacy",
    "migrated_caller_refuses_missing_revision", "migrated_caller_refuses_stale",
    "migrated_caller_refuses_unstable", "migrated_caller_reruns_external_mutable",
    "migrated_caller_reuses_unchanged", "new_caller_refused_same_record_and_reexecuted",
    "only_declared_dependency_changed", "producer_actual_subprocess_green",
    "record_bytes_unchanged", "unchanged_gate_exit_zero", "unchanged_gate_status_reusable",
    "unchanged_reused_without_producer", "unchanged_retained_measured_commit",
    "unsafe_control_would_retain_legacy_green", "unsafe_control_would_retain_stale_green",
))
# None: the container itself is null; [value]: the container is an object holding value.
# phase, gate_exit, reusable, retained, producer_execution.execution_index,
# executions_after, declared_dependency_digests_match, gate.findings
CACHE_DEMO_CASES = (
    ("initial-fresh", None, None, False, [1], 1, True, None),
    ("unchanged", 0, True, True, None, 1, True, [[]]),
    ("dependency-modified", 1, False, False, [2], 2, False, [["dependency-digest-mismatch"]]),
    ("legacy-no-dependencies", 2, False, False, [3], 3, False, [["dependencies-legacy"]]),
)
CACHE_CASE_FIELDS = ("phase", "gate_exit", "reusable", "retained")


def _member(row: dict, field: str, key: str):
    container = row.get(field, _ABSENT)
    if container is None:
        return None
    if isinstance(container, dict) and key in container:
        return [container[key]]
    return _ABSENT


def cache_cases_match(rows) -> bool:
    if not isinstance(rows, list) or len(rows) != len(CACHE_DEMO_CASES):
        return False
    for row, expected in zip(rows, CACHE_DEMO_CASES):
        if not isinstance(row, dict):
            return False
        observed = (
            *(row.get(field, _ABSENT) for field in CACHE_CASE_FIELDS),
            _member(row, "producer_execution", "execution_index"),
            row.get("executions_after", _ABSENT),
            row.get("declared_dependency_digests_match", _ABSENT),
            _member(row, "gate", "findings"),
        )
        if not all(json_equal(got, want) for got, want in zip(observed, expected)):
            return False
    return True
```

Replace the cache branch's `demo_match` (lines 455–470). Keep `matched_counts` byte-identical. Per `AttackRunnerStepResults.md:30`, the replay matrix tuple includes `matched_counts` [INFERENCE: `replay-matrix.sh` was not readable in scope]. Put identity diagnostics in a new sibling key:

```python
        gate_state = payload.get("gate") if isinstance(payload, dict) else None
        isolation = payload.get("isolation") if isinstance(payload, dict) else None
        checks_identified = (isinstance(checks, dict)
                             and checks.keys() == CACHE_DEMO_CHECKS
                             and all(value is True for value in checks.values()))
        cases_identified = cache_cases_match(case_rows)
        demo_match = (
            isinstance(payload, dict)
            and json_equal(payload.get("status", _ABSENT), expected["status"])
            and json_equal(payload.get("measured_commit", _ABSENT), revision)
            and json_equal(payload.get("harness_revision", _ABSENT), revision)
            and isinstance(case_rows, list) and len(case_rows) == expected["cases"]
            and isinstance(checks, dict) and len(checks) == expected["checks"]
            and checks_identified and cases_identified
            and json_equal(payload.get("failed_checks", _ABSENT), expected["failed_checks"])
            and json_equal(payload.get("producer_executions_new_policy", _ABSENT),
                           expected["producer_executions_new_policy"])
            and payload.get("inputs_unchanged_during_run") is expected["inputs_unchanged_during_run"]
            and isinstance(gate_state, dict) and json_equal(gate_state.get("sha256", _ABSENT), gate_sha)
            and isinstance(isolation, dict)
            and isolation.get("cleaned") is expected["isolation_cleaned"]
            and json_equal(isolation.get("residue", _ABSENT), [])
        )
        result["cache_identity"] = {
            "missing_checks": sorted(CACHE_DEMO_CHECKS - set(checks)) if isinstance(checks, dict) else sorted(CACHE_DEMO_CHECKS),
            "unexpected_checks": sorted(set(checks) - CACHE_DEMO_CHECKS) if isinstance(checks, dict) else [],
            "cases_identified": cases_identified,
        }
```

In `main`, right after the inventory comparison (line 602):

```python
            cache_expected = next(step["expected_summary"] for step in steps
                                  if step.get("kind") == "cache-demo")
            if (cache_expected["checks"] != len(CACHE_DEMO_CHECKS)
                    or cache_expected["cases"] != len(CACHE_DEMO_CASES)):
                raise Refusal("cache identity constants disagree with the frozen inventory")
```

The counter branch's exact path (line 427) should call the same `json_equal`. That closes the bool and float variants through one authority. Seats owning the counter claim should take note.

## Oracle vectors for the shared synthetic fixture (expected decisions are source-inferred)

P is the positive template:
- the 33 names above, each `true`;
- four rows exactly as in the case table;
- `status "ok"`; `measured_commit` and `harness_revision` equal to the rev; `failed_checks []`; `producer_executions_new_policy 3`; `inputs_unchanged_during_run true`;
- `gate.sha256` equal to the fixture root's `tools/souji-evidence-cache.py` digest; `isolation {cleaned: true, residue: []}`;
- return code 0, empty stderr;
- transient fields filled with obvious placeholders and never compared.

| id | mutation of P | base `matched` | changed `matched` |
|---|---|---|---|
| V1 | none | true | true |
| V2 | different `/var/tmp/souji-r14-cache-demo.*` paths, `record_sha256`, `seconds`, `produced_at`, `gate.stdout` | true | true |
| V3 | `initial_fresh_once` renamed to `bogus_check` | **true (false green)** | false |
| V4 | add a 34th `isolation_cleaned: true` | false | false |
| V5 | row 4 phase `legacy-no-deps` | **true** | false |
| V6 | `cases: [1,2,3,4]` | **true** | false |
| V7 | `unchanged.gate_exit: false` | **true** | false |
| V8 | `unchanged.producer_execution: {}` | **true** | false |
| V9 | `producer_executions_new_policy: 3.0` | **true** | false |
| V10 | `gate: null` | **crash (AttributeError, :467)** | false, no crash |
| V11 | `isolation: []` | **crash (:468)** | false, no crash |
| V12 | `initial-fresh.gate: {"findings": null}` | **true** | false |

V4 is the control showing the constant must not include `isolation_cleaned`.

The 18 real acceptance steps remain the positive controls. On green, the real producer's rows and checks satisfy the projection: each column is pinned by the producer's own checks or by deterministic code (see the case table), so changed V1/V2 have no false red.

## Impacted axes
- **Calibration:** C1, C2, C5, V3–V12.
- **Coverage:** C1 (case-row half), C3.
- **Operability:** C4 (crash instead of a recorded red), C6 (whole-run refusal regression if `expected_summary` is edited).

No tradeoff is required: every correction preserves V1/V2 and the frozen inventory bytes.

## Verification
Not executed: no runner, producer, fixture, test, build or formatter was run. All base and changed decisions above are inferred from the cited source lines. L1 runs the shared oracle and the 18-step acceptance after integration. No tools were installed or updated.

Report: .ufo/waves/round-22/w1/Cache11.md
