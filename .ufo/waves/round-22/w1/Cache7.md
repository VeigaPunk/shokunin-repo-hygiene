STATUS: PARTIAL — The cache-demo gate container the base runner reads (`payload["gate"]["sha256"]`) is the producer's correct consumed-gate slot. However, the cache-demo branch crashes with an uncaught `AttributeError` on a non-dict `gate` or `isolation` container, still counts the 33 checks without identifying them, and accepts JSON `3.0` for the integer `producer_executions_new_policy`. This is a source-only review: nothing was executed, and every behaviour claim below is source-inferred unless it is labelled otherwise.

Axes: calibration, operability, coverage (no trade allowed). Base 41553adb139d06511dc386bb3ce4326aebfba675. Files read: only the six named contract files.

## Producer container map (derived from `census/round-14/cache-demonstration.py`, not invented)

On the success path, the producer emits every field the runner reads in the following places:

| runner reads | producer location | value on the success path |
|---|---|---|
| `status` | top level, line 996; `main` may flip it to `red` at 1202–1206 | `"ok"` |
| `measured_commit`, `harness_revision` | top level, 998 / 1010 | `initial_commit` (40-hex) |
| `cases` | top level, 1046; four rows from `make_case` | phases `initial-fresh`, `unchanged`, `dependency-modified`, `legacy-no-dependencies` (literals at 596, 615, 655, 795) |
| `checks` | top level, 1051; dict built at 879–979 | exactly 33 named bools (the list is below) |
| `failed_checks` | 1052 | `[]` |
| `producer_executions_new_policy` | 1049 = `len(executions)` (850) | the JSON int `3` |
| `inputs_unchanged_during_run` | set in `main`, 1216 | `true` |
| `gate.sha256` | `gate_state` from `inspect_gate(Path(args.gate))` (250–268), stored at 1020 | digest of the gate that was actually consumed (`--gate`) |
| `isolation.cleaned` / `isolation.residue` | dict at 1022–1029, merged with `cleanup()` at 1200–1201 | `true` / `[]` |

The producer actually has four gate-digest slots:
- `gate.sha256`: taken before the run.
- `gate_sha256_after`: top level, taken at the end of `run_demonstration` (1021).
- `gate.sha256_after`: taken after cleanup, in `main` (1207–1209).
- `gate.installed_default.sha256`: this is `DEFAULT_GATE = LANE/tools/...` (72, 252), not the gate that was consumed.

The blocked payload (1069–1081) also carries `gate`, but it names its rows `cases_observed`, not `cases`. Emission uses `sort_keys=True` (1107).

## Findings

### F1 (counterexample to a container move) — `gate.installed_default` is the wrong container; base `gate.sha256` is right

The runner's check at `run-acceptance.py:467`, `payload.get("gate", {}).get("sha256") == gate_sha`, reads the slot that `inspect_gate(Path(args.gate))` fills. That is the gate the demonstration actually invoked (`invoke_gate`, 271–272).

Counterexample against a repair that reads `gate.installed_default.sha256`, or that uses `matches_installed_default` as identity. The producer always fills `installed_default` from `DEFAULT_GATE` at the clone path, whatever `--gate` says. So a run with `--gate` pointing at other bytes would report:
- `gate.sha256 = <other digest>`
- `installed_default.sha256 = <clone gate digest>`, which equals the runner's `gate_sha`.

A runner reading `installed_default` would mark that run green even though the demonstration consumed a different gate.

Two other slots are also weaker than the base:
- The top-level `gate_sha256_after` alone does not bind the bytes at the start of the run.
- `checks["gate_digest_recorded_and_unchanged"]` is a claim the producer makes about itself, not a digest.

Fix: keep `gate.sha256` as the binding. Optionally, also require `gate.sha256_after == gate_sha` and `gate_sha256_after == gate_sha`. These two add coverage for a gate swapped and restored inside the step, which is the only drift the runner's before/after snapshot of `tools/souji-evidence-cache.py` (lines 610–622) cannot see. That window is a tradeoff, not a known false green.

Impacted axis: calibration (prevents a regression).

### F2 (HIGH, operability) — a malformed container crashes the runner instead of failing the step

The producer only guarantees a dict container on the real paths. The runner, however, calls `.get` on whatever the payload holds:
- `isolation = payload.get("isolation", {})` (455) returns the stored value when the key is present, so `"isolation": null` gives `None`.
- `payload.get("gate", {}).get("sha256")` (467) raises when `gate` is null, a list, a string, or a number.
- `isolation.get(...)` (468–469) has the same problem.

`main` catches only `(OSError, ValueError, RuntimeError, Refusal, KeyError)` (652). `AttributeError` is not a subclass of any of those, so it propagates uncaught.

Witness: take the real success payload shape from the map above, keep every field at its real value, and change only `"gate"` to `null` (or `"isolation"` to `[]`). Python's `and` short-circuits, so `.get` on the bad container is reached only when every earlier conjunct is true; this is that case. The uncaught `AttributeError` then:
- prints a traceback,
- exits with status 1, which collides with the runner's own "ran, not all matched" exit code (656),
- writes no record and discards all 18 step results.

The preregistration requires rejecting malformed producer data without a crash. A related case: `json.loads` raises `RecursionError` on deeply nested input. That is a `RuntimeError`, so it is caught, but it refuses the whole run (exit 2) rather than failing one step.

Fix: replace a non-dict container with `{}`, and catch `RecursionError` locally (see the draft below).

Impacted axes: operability and calibration.

### F3 (MEDIUM, coverage) — checks counted, not identified (the known r21 defect, reconfirmed)

At lines 461–463 the runner tests only `len(checks) == 33`, that every value `is True`, and `len(case_rows) == 4`. Witness: the real payload with any one real check name renamed to an unrelated name (still `true`) passes.

The exact expected name set, derived from producer lines 879–979 (exactly 33, unique):

`initial_fresh_once`, `producer_actual_subprocess_green`, `unchanged_gate_exit_zero`, `unchanged_gate_status_reusable`, `changed_dependency_exact_finding`, `legacy_exact_finding`, `unchanged_reused_without_producer`, `unchanged_retained_measured_commit`, `changed_dependency_gate_exit_one`, `changed_dependency_not_reused`, `changed_dependency_producer_executed`, `changed_dependency_fresh_digests`, `legacy_gate_exit_two`, `legacy_not_reused`, `legacy_producer_executed`, `legacy_fresh_digests`, `only_declared_dependency_changed`, `record_bytes_unchanged`, `gate_digest_recorded_and_unchanged`, `execution_log_matches_disk`, `isolation_confined`, `unsafe_control_would_retain_stale_green`, `unsafe_control_would_retain_legacy_green`, `baseline_authentic_retention`, `baseline_stale_green_reused`, `new_caller_refused_same_record_and_reexecuted`, `historical_legacy_records_refused`, `migrated_caller_reuses_unchanged`, `migrated_caller_refuses_stale`, `migrated_caller_refuses_legacy`, `migrated_caller_refuses_missing_revision`, `migrated_caller_refuses_unstable`, `migrated_caller_reruns_external_mutable`.

Every right-hand side in that dict evaluates to a Python `bool` (each is an `==` / `is` / `bool()` / `all()` chain over bool operands), so the runner's `value is True` test is consistent with the real output. One negative control comes free: on a cleanup failure, `main` adds `isolation_cleaned: false` (1204), which makes 34 names, status `red`, and exit 1. Identity checking must keep rejecting that case, and it does.

Minimal row identity: require the ordered phase list `["initial-fresh", "unchanged", "dependency-modified", "legacy-no-dependencies"]`.

Do NOT pin any of the following, because they vary from run to run:
- `record`, `gate.path`, and `producer.command`: they contain the `mkdtemp` `souji-r14-cache-demo.<random>` and `souji-r21-replay-<random>` paths.
- `seconds`, `produced_at`, and `observed_at`.
- the gate stdout and the interpreter path.

Pinning those would reject valid generated rows. Per-row `gate_exit`, `executions_after`, and `retained` duplicate checks 1, 3, 7, 9, 11, 13 and 15. Requiring them would add forged-payload consistency, which the preregistration explicitly does not claim, so they are optional.

Impacted axis: coverage.

### F4 (MEDIUM, calibration) — the scalar-type gap reaches the cache branch too

At line 465, `payload.get("producer_executions_new_policy") == 3` accepts the JSON value `3.0`. Python's JSON decoder turns a number with a fraction into a `float`, and `3.0 == 3` is true. (`True` cannot be a witness here because `True == 1`, not 3.) The producer emits `len(executions)`, the int `3`. Witness: the real payload with only that field changed to `3.0` passes.

Fix: `type(v) is int and v == expected`.

The other cache scalars are already exact:
- `inputs_unchanged_during_run` and `isolation.cleaned` use `is True`.
- `status` and `measured_commit` are strings.
- `failed_checks` must be a list equal to `[]`.

Impacted axis: calibration.

### F5 (integration hazards that change identity) — where the repair must live

1. **Frozen inventory projection.** `inventory_projection` copies `expected_summary` whole (541–543), and lines 600–602 refuse when the projection differs from `step-inventory.json`. If the name set is added inside `expected_summary`, every replay is refused with exit 2. If `step-inventory.json` is edited to match instead, its own normalization statement ("All names/args/expectations/inventory order otherwise exact" against the r20 source at 5ff7565) becomes false provenance. The safe place is a module constant, or a new non-projected step key such as `check_names`: the projection copies only its listed keys plus `kind` and `argv`.
2. **Duplicate authority.** The literal name tuple duplicates the producer's dict. Tie it to the frozen count with `len(CACHE_DEMO_CHECKS) == expected["checks"]` and a uniqueness check, so the two cannot drift apart silently. Do not derive the names by parsing the producer: the preregistration requires literal, independently reviewed vectors.
3. **Runner self-identity.** If L1 forks the runner to a round-22 path instead of editing it, the self-binding at line 223 (`census/round-21/run-acceptance.py`), `INPUT_PATHS`, and the inventory path at 600 are hard-coded. An unchanged fork would refuse every run. Editing the r21 file in place instead changes the bytes that earlier r21 acceptance records bound. L1 must choose one of these and disclose the choice.

Impacted axes: operability and calibration.

## Smallest safe correction (draft for L1; not applied, not run)

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
    "unsafe_control_would_retain_legacy_green", "baseline_authentic_retention",
    "baseline_stale_green_reused", "new_caller_refused_same_record_and_reexecuted",
    "historical_legacy_records_refused", "migrated_caller_reuses_unchanged",
    "migrated_caller_refuses_stale", "migrated_caller_refuses_legacy",
    "migrated_caller_refuses_missing_revision", "migrated_caller_refuses_unstable",
    "migrated_caller_reruns_external_mutable",
)
CACHE_DEMO_PHASES = ("initial-fresh", "unchanged", "dependency-modified",
                     "legacy-no-dependencies")


def exact_int(value, expected: int) -> bool:
    return type(value) is int and value == expected
```

```python
    elif kind == "cache-demo":
        try:
            payload = json.loads(stdout)
        except (ValueError, TypeError, RecursionError):
            payload = None
        if not isinstance(payload, dict):
            payload = {}
        def container(key):
            value = payload.get(key)
            return value if isinstance(value, dict) else {}
        checks = payload.get("checks")
        case_rows = payload.get("cases")
        expected = step["expected_summary"]
        if (len(set(CACHE_DEMO_CHECKS)) != expected["checks"]
                or len(CACHE_DEMO_PHASES) != expected["cases"]):
            raise Refusal("cache-demo identity vectors disagree with frozen counts")
        gate_sha = sha256_bytes(read_regular(root / "tools/souji-evidence-cache.py"))
        gate = container("gate")
        isolation = container("isolation")
        phases = [row.get("phase") if isinstance(row, dict) else None
                  for row in case_rows] if isinstance(case_rows, list) else None
        demo_match = (
            payload.get("status") == expected["status"]
            and payload.get("measured_commit") == revision
            and payload.get("harness_revision") == revision
            and phases == list(CACHE_DEMO_PHASES)
            and isinstance(checks, dict) and set(checks) == set(CACHE_DEMO_CHECKS)
            and all(value is True for value in checks.values())
            and payload.get("failed_checks") == expected["failed_checks"]
            and exact_int(payload.get("producer_executions_new_policy"),
                          expected["producer_executions_new_policy"])
            and payload.get("inputs_unchanged_during_run") is expected["inputs_unchanged_during_run"]
            and gate.get("sha256") == gate_sha
            and isolation.get("cleaned") is expected["isolation_cleaned"]
            and isolation.get("residue") == []
        )
```

Notes on the draft:
- In `matched_counts`, keep the existing fields and add `"matched_check_names": len(set(checks) & set(CACHE_DEMO_CHECKS)) if isinstance(checks, dict) else 0`. Replace each `payload.get(...) if isinstance(payload, dict)` guard with the normalized `payload`.
- The two optional `sha256_after` conjuncts from F1 are left out of the minimum on purpose.
- `make_steps` and `step-inventory.json` stay byte-identical, so the projection equality at line 601 still holds.

## Required oracle vectors (literal, for the shared result-oracle fixture)

Each vector starts from the real success shape in the map above and changes exactly one field. Expected decisions for the base runner and the changed runner:

| # | single change from the real shape | base | changed |
|---|---|---|---|
| 1 | none (positive control) | matched | matched |
| 2 | one check renamed `x_unrelated: true` | matched (false green) | not matched |
| 3 | `producer_executions_new_policy: 3.0` | matched (false green) | not matched |
| 4 | `gate: null` | crash, uncaught `AttributeError`, exit 1, no record | not matched, no crash |
| 5 | `isolation: []` | crash, as in row 4 | not matched, no crash |
| 6 | case phases reordered | matched (false green) | not matched |
| 7 | `gate.sha256` changed while `gate.installed_default.sha256 == gate_sha` | not matched | not matched (guards against the F1 container move) |
| 8 | `isolation_cleaned: false` added (34 checks, status red, exit 1) | not matched | not matched |
| 9 | `record`, `gate.path` and `observed_at` given different `/var/tmp/...<random>` / timestamp values | matched | matched (transient variation preserved) |

## Verification gaps

- Every decision above is inferred from the source: no runner, producer, fixture, or acceptance step was executed, as the contract requires. The crash-versus-catch claims rest on Python's exception hierarchy (`AttributeError` and `TypeError` sit outside `(OSError, ValueError, RuntimeError, KeyError)`; `RecursionError` is a `RuntimeError`). The `3.0 == 3` witness rests on the documented JSON-to-float conversion and numeric equality.
- I did not check that the 33-name list matches any committed r21 acceptance output. L1's run is the only executed confirmation.
- No tools were installed. No peers were contacted. The only file written is this report.
