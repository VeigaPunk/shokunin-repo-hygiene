STATUS: PASS — source-only critique done. The base cache-demo branch already rejects a check value of integer `1` (`value is True`). The likely identity fixes would bring that false green back: dict equality against `{name: True}` (`1 == True`) and superset/subset name tests. The same branch has a separate scalar false green: `producer_executions_new_policy: 3.0` is accepted. It also has a malformed-data crash (non-dict `gate`/`isolation`). Nothing was run.

Seat: SoujiR22.Cache5 (critic, leaf). Base 41553adb139d06511dc386bb3ce4326aebfba675.
Scope: the six named files plus the public Python `json` docs URL. No other paths were read, and nothing was executed, probed, built or tested. No tool was installed or updated.

## Real witness (source-inferred from the named producer)

`census/round-14/cache-demonstration.py` `run_demonstration` builds `checks` at lines 879–979 and emits it via `json.dumps` (`emit`, lines 1106–1108). There are exactly 33 names:

`initial_fresh_once, producer_actual_subprocess_green, unchanged_gate_exit_zero, unchanged_gate_status_reusable, changed_dependency_exact_finding, legacy_exact_finding, unchanged_reused_without_producer, unchanged_retained_measured_commit, changed_dependency_gate_exit_one, changed_dependency_not_reused, changed_dependency_producer_executed, changed_dependency_fresh_digests, legacy_gate_exit_two, legacy_not_reused, legacy_producer_executed, legacy_fresh_digests, only_declared_dependency_changed, record_bytes_unchanged, gate_digest_recorded_and_unchanged, execution_log_matches_disk, isolation_confined, unsafe_control_would_retain_stale_green, unsafe_control_would_retain_legacy_green, baseline_authentic_retention, baseline_stale_green_reused, new_caller_refused_same_record_and_reexecuted, historical_legacy_records_refused, migrated_caller_reuses_unchanged, migrated_caller_refuses_stale, migrated_caller_refuses_legacy, migrated_caller_refuses_missing_revision, migrated_caller_refuses_unstable, migrated_caller_reruns_external_mutable`.

- Every right-hand side is a comparison, `is`/`not`, `bool(...)`/`all(...)`, or an `and` chain whose operands are all such booleans. Examples: `decision["reusable"]` is `exit_code == 0` (line 529). `cases[i]["retained"]` is `==` (line 569). `stale_would_retain`/`legacy_would_retain` are `is True and is not None` (line 585). `baseline_retained` is `isinstance(...) and bool(...)` (line 729). `historical_legacy["all_refused"]` is `bool(...) and all(...)` (line 837). `migrated_*["retained"]` is `is not None` (line 397). The real producer therefore emits only JSON `true`/`false` for check values; it can never emit `1` or `1.0`.
- `isolation_cleaned` is **not** one of the 33. It is added to `checks` only on the red path (lines 1202–1206), where status becomes `red` and the count becomes 34. The runner's `expected_summary` key `"isolation_cleaned": true` refers to `payload.isolation.cleaned` (`run-acceptance.py` line 468), not to a check.
- `producer_executions_new_policy` is `len(executions)`, a Python `int` (line 850). The producer never emits `3.0`.
- `cases` has four rows from `make_case`. Their `phase` values are the literal strings, in order: `initial-fresh`, `unchanged`, `dependency-modified`, `legacy-no-dependencies` (lines 594–803). Several fields vary from run to run and must stay unconstrained:
  - `record` paths and `isolation.base`/`root` under `mkdtemp("/var/tmp/souji-r14-cache-demo.*")` (line 1151)
  - `produced_at` and `observed_at` timestamps, and `seconds`
  - gate stdout/stderr embedded in `gate`
  - `measured_commit`/`record_sha256`, which follow the revision
- Python authority (opened this seat: https://docs.python.org/3/library/json.html, JSONDecoder conversion table and the "Repeated Names Within an Object" section):
  - JSON `true` decodes to `True`, a number (int) to `int`, and a number (real) to `float`.
  - Repeated object names are accepted, and the last value wins.
  - `bool` is an `int` subclass, so `1 == True` and `1.0 == True`. This is standard Python semantics, cited from language knowledge and not re-opened here: [INFERENCE] for the citation, not for the semantics.

## Counterexamples (synthetic oracle rows; derived from the real green shape with one mutation)

The "base" column comes from reading `summarize_result` at lines 446–481. "Naive fix" means a plausible identity repair.

| # | mutation of a real green payload | base | naive fix | required |
|---|---|---|---|---|
| C1 | `checks.initial_fresh_once: 1` | reject (`1 is True` false) | **accept** if `checks == dict.fromkeys(NAMES, True)` or `checks[n] == True` | reject |
| C2 | same with `1.0` | reject | **accept** (same reason) | reject |
| C3 | one real name replaced by bogus `zz: true` (still 33) | **accept** (count only) | reject | reject |
| C4 | 34 keys: the 33 plus `isolation_cleaned: true` | reject (count) | **accept** if `NAMES <= checks.keys()` | reject |
| C5 | 32 real names plus `isolation_cleaned: true` | **accept** (count 33) | reject if exact set | reject |
| C6 | `producer_executions_new_policy: 3.0` | **accept** (`3.0 == 3`, line 465) | accept unless the scalar helper also covers the cache branch | reject |
| C7 | `cases` = 4 rows with reordered or arbitrary `phase` | **accept** (`len == 4` only) | — | reject |
| C8 | `gate: "x"` (or `isolation: null` / `[]`), everything else valid | **crash**: `AttributeError` at line 467/468; `main` catches only `OSError, ValueError, RuntimeError, Refusal, KeyError` (line 652) | — | reject, no crash |
| C9 | duplicate `"initial_fresh_once": false, … "initial_fresh_once": true` | accept (last wins) | accept | tradeoff (see below) |
| P1 | real green with different `/var/tmp/souji-r14-cache-demo.*` paths, timestamps, `seconds`, gate stdout | accept | must stay accept | accept |
| P2 | real red path: `checks` has 34 keys with `isolation_cleaned: false`, status `red` | reject | must stay reject | reject |

Impacted axes:
- **Calibration:** C1–C7 are false greens.
- **Operability:** C8 is a crash. Also, putting the identity set into the step's `expected_summary` would break the run.
- **Coverage:** P1, P2 and the 18 real positive controls must hold.

## Hidden regressions to reject in the proposed fix

1. **Dict equality on check values (C1/C2).** Replacing `all(value is True …)` with `checks == {n: True …}` reopens the exact bool/int confusion this round is repairing. Keep `is True`. JSON `true` decodes to the singleton `True` per the docs table.
2. **Identity set placed in `expected_summary`.** `inventory_projection` projects `expected_summary` verbatim and compares it with the frozen `census/round-21/step-inventory.json` steps (lines 538–552, 600–602). Changing `"checks": 33` to a name list makes every run refuse with exit 2 ("acceptance commands differ from the frozen r20 inventory"). That loses all 18 positive controls. Editing the frozen inventory to compensate falsifies its recorded `source_commit`/`source_sha256` normalization claim (inventory lines 2–5): this is false provenance. The name set belongs in a runner constant, cross-checked against the frozen count.
3. **Adding `isolation_cleaned` to the name set (C4/P2 confusion).** That makes the real green (33 keys) fail, so the clean-cache-demonstration positive control regresses.
4. **Constraining case-row content beyond `phase`.** Any comparison of `record`, `record_sha256`, `gate`, `seconds` or timestamps against a literal breaks P1, the run-to-run path variation.
5. **A second strictness authority.** If the counter-branch scalar fix adds a strict JSON equality helper, the cache branch must reuse that same helper for `producer_executions_new_policy` (C6). It must not grow its own ad hoc `type(x) is int` variant.

## Smallest safe correction (draft for L1; `census/round-21/run-acceptance.py` cache branch only)

```python
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
    "unsafe_control_would_retain_stale_green",
    "unsafe_control_would_retain_legacy_green", "baseline_authentic_retention",
    "baseline_stale_green_reused", "new_caller_refused_same_record_and_reexecuted",
    "historical_legacy_records_refused", "migrated_caller_reuses_unchanged",
    "migrated_caller_refuses_stale", "migrated_caller_refuses_legacy",
    "migrated_caller_refuses_missing_revision", "migrated_caller_refuses_unstable",
    "migrated_caller_reruns_external_mutable",
))
CACHE_CASE_PHASES = ["initial-fresh", "unchanged", "dependency-modified",
                     "legacy-no-dependencies"]
```

```python
    elif kind == "cache-demo":
        try:
            payload = json.loads(stdout)
        except (ValueError, TypeError):
            payload = None
        if not isinstance(payload, dict):
            payload = None
        checks = payload.get("checks") if payload is not None else None
        case_rows = payload.get("cases") if payload is not None else None
        gate = payload.get("gate") if payload is not None else None
        isolation = payload.get("isolation") if payload is not None else None
        expected = step["expected_summary"]
        gate_sha = sha256_bytes(read_regular(root / "tools/souji-evidence-cache.py"))
        demo_match = (
            payload is not None
            and payload.get("status") == expected["status"]
            and payload.get("measured_commit") == revision
            and payload.get("harness_revision") == revision
            and isinstance(case_rows, list) and len(case_rows) == expected["cases"]
            and [row.get("phase") if isinstance(row, dict) else None
                 for row in case_rows] == CACHE_CASE_PHASES
            and len(CACHE_CHECK_NAMES) == expected["checks"]
            and isinstance(checks, dict) and checks.keys() == CACHE_CHECK_NAMES
            and all(value is True for value in checks.values())
            and payload.get("failed_checks") == expected["failed_checks"]
            and <shared strict JSON equality>(payload.get("producer_executions_new_policy"),
                                              expected["producer_executions_new_policy"])
            and payload.get("inputs_unchanged_during_run") is expected["inputs_unchanged_during_run"]
            and isinstance(gate, dict) and gate.get("sha256") == gate_sha
            and isinstance(isolation, dict)
            and isolation.get("cleaned") is expected["isolation_cleaned"]
            and isolation.get("residue") == []
        )
```

Notes on the draft:
- `<shared strict JSON equality>` is whatever single helper the scalar seat lands for exact counters (type-exact recursion: `type(observed) is type(expected)` before `==`). If none lands, `type(x) is int and x == expected` is the minimal local form. Do not add a second helper.
- The `str`/`list[str]` comparisons (`status`, commits, phases, `failed_checks == []`) cannot hit bool/int confusion, so they stay `==`. The phase comparison is `list == list` of strings and cannot crash on non-dict rows.
- `dict_keys == frozenset` is set equality. It rejects C3, C4 and C5 and accepts P1.
- `expected_summary` and the frozen inventory stay byte-identical, so `inventory_projection` is unaffected (constants are not projected).
- For the identity set to be visible in the record, optionally set `matched_counts["matched_gate_checks"]` to `sum(checks.get(n) is True for n in CACHE_CHECK_NAMES)` when `checks` is a dict. This is observability only, not a gate.

Required oracle vectors for the committed synthetic fixture:
- Reject: C1, C2, C3, C4, C5, C6, C7, C8. For C8, assert `matched is False` and no exception.
- Accept: P1.
- Reject: P2.
- Real acceptance: the 18 real steps unchanged, including `clean-cache-demonstration` matched.
- Fixture note: `summarize_result` reads `root/tools/souji-evidence-cache.py` (line 454). The oracle must supply a regular file there and set `gate.sha256` to its digest, or the positive control false-reds.

## Bounded findings / tradeoffs

- **C9 (duplicate keys):** fixable with `object_pairs_hook` rejecting repeated names, but it only defends against a malicious or hand-forged payload. The real producer serializes a `dict` and cannot emit duplicates. The round's preregistration disclaims malicious-producer attestation, so this is out of claim scope. If adopted, it must apply to both counter and cache parsing through one loader. It is not required for this claim.
- **Location identity (not a defect):** editing `census/round-21/run-acceptance.py` in place is pinned by `combined_snapshot` (line 223) and INPUT_PATHS. Historical r21 records stay bound to their own `measured_commit` bytes, so no filed evidence is rewritten. Reports must not describe r21 acceptance records as having used the repaired predicate.
- **F5, the 160-byte synthetic-only scope, and reap/NAMESPACE/historical holds:** untouched by this critique. The draft changes only the cache-demo branch of the acceptance runner.

## Source-inferred vs executed

- **Source-inferred:** every base/naive/required decision in the table, from reading `run-acceptance.py` lines 330–481, 538–552, 600–602 and 652, and `cache-demonstration.py` lines 397, 529, 569, 585, 729, 837, 850, 879–979, 1106–1108 and 1151–1218.
- **Executed:** none. One public URL was fetched (Python `json` docs).
- **Installs:** none.
