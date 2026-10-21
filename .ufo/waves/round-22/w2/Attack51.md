# Attack51 — critic: `cache/name/changed_dependency_producer_executed` (want=False)

Target: code `4f83fd222ffbd8825340221a8c426550ef891191`, oracle `tests/fixtures/r22-result-oracle.{json,py}`.
Mode: source-only review. No tests, runner, oracle, or mutation were executed. No tools were installed or updated.

## STATUS

**Source-only PASS for this vector and its paired positive.** No concrete mismatch was found.

- The stored delta is exactly one renamed check identity applied to the pinned public record.
- The literal expected decision (`False`) is correct.
- The fixture really feeds that input to `summarize_result`.
- In the changed predicate, the only conjunct that flips is the key-identity test at `run-acceptance.py:516`.
- The base predicate (`41553adb…`) would accept this input, so the vector really separates base from changed.

Limits:
- This is not runtime evidence. L1's run of all 214 decisions is still the measurement.
- The paired positive depends on the gate-file digest in the working tree, which I did not open (it is not a named path). See C2.
- Duplicate-key smuggling is declared out of scope by this round and is not covered. See C3.

## 1. Reconstructing the delta before reading the predicate

Input bindings (sha256, read-only):
- `census/round-21/final-out-S1.json` = `bc53a752…38fe`. This equals `source_receipt_sha256` at `r22-result-oracle.json:4`.
- `census/round-21/step-inventory.json` = `8b7b1cd8…1310`. This equals `frozen_inventory_sha256` at `r22-result-oracle.json:6`.
- In the working tree, `run-acceptance.py`, `r22-result-oracle.json` and `r22-result-oracle.py` are byte-identical to `git show 4f83fd2:` of each (`00d0e9c2…`, `292442a6…`, `3c0776ae…`).

Original public record (`final-out-S1.json`, command `clean-cache-demonstration`):
- `returncode` 0 and `stderr` "" (3380–3381).
- `checks` has exactly 33 keys, all `true` (2996–3030). `changed_dependency_producer_executed: true` is at 3003.
- `measured_commit` and `harness_revision` are both `ff425ab8…` (3271, 3170).
- `failed_checks` is `[]` (3148) and `producer_executions_new_policy` is 3 (3328).
- `inputs_unchanged_during_run` is true (3245); `isolation.cleaned` is true and `isolation.residue` is `[]` (3248, 3255).
- `gate.sha256` is `dd279ba9…d6` (3164).

Frozen inventory step (`step-inventory.json:187–205`): `kind` cache-demo, `checks` 33, `cases` 4, `failed_checks` [], `producer_executions_new_policy` 3, `measured_commit` `<REV>`.

Stored vector (`r22-result-oracle.json:887–934`): `json_set [["checks"], {...}]`. Comparing it line by line with the record:
- Vector lines 898–903 equal record lines 2997–3002.
- Vector lines 904–929 equal record lines 3004–3029.
- Record line 3003 (`changed_dependency_producer_executed`) is missing from the vector.
- Vector line 930 adds `bogus_changed_dependency_producer_executed: true`.

The net delta is therefore a single rename. The key count stays 33, every value stays `true`, and no other payload field changes.

### Does the fixture actually feed it?

Yes. In `r22-result-oracle.py`:
- Line 67 selects `records['clean-cache-demonstration']`, and line 68 takes the raw record `stdout`.
- Lines 72–82 apply the delta. The path `["checks"]` has an empty `path[:-1]`, so `at = payload` and `payload['checks'] = deepcopy(value)`. This replaces the whole dict rather than merging into it, so the real key is truly absent. Line 82 then re-serializes with `json.dumps`.
- Lines 83–85 load the frozen step with `<REV>` replaced by `ff425ab…`.
- Lines 87–91 pass the record's `returncode` (0) and `stderr` ("").

Re-serialization does not change any other conjunct:
- `json.dumps` output is one line starting with `{`. It cannot trigger `failure_lines` or `SUMMARY_RE`.
- The JSON round trip preserves every value that the other conjuncts compare.

One driver detail: an exception gives `observed=None`, and `passed` requires `type(observed) is bool` (line 97). A crash therefore cannot satisfy want=False.

### Is the expected decision correct?

Yes. The producer defines the key at `cache-demonstration.py:915` as `execution_modified is not None and cases[2]["executions_after"] == 2`. That is the demo's central proof that a changed dependency forced the producer to run again. A payload that asserts an unknown name as `true` provides no evidence for that obligation.

The decision holds under either reasonable policy:
- Strict identity rejects it.
- A lenient "superset with extra fields allowed" policy also rejects it, because a required key is missing.

It matches the oracle contract's "Reject … replaced cache check identities" (`r22-result-oracle.json:8`), preregistration defect 3 ("cache checks counted rather than identified"), and lesson R22-M3 (`round-22.md:17`).

## 2. Attacking the changed predicate (`run-acceptance.py:493–537`)

Each conjunct evaluated on the mutated payload:
- `isinstance(payload, dict)`, status, `measured_commit`, `harness_revision`: True (identical to the record).
- `len(case_rows) == 4`, `len(CACHE_CASE_PHASES) == 4`, phases in order (511–513): True (untouched).
- 514, `isinstance(checks, dict) and len(checks) == 33`: **True**. This is exactly the base-era hole that the rename exploits.
- 515, `len(CACHE_CHECK_NAMES) == 33`: True. The frozenset at 184–203 has 33 distinct names, matching the record's 33 keys one for one. This line also guards against silently dropping a name from the constant.
- 516, `checks.keys() == CACHE_CHECK_NAMES`: **False**, because the key sets differ in exactly one element. Comparing `dict_keys` with a `frozenset` is a real set equality: per the Python docs, key views are set-like and support `==` with any `collections.abc.Set`. It is not identity or ordering.
- 517–525: would all be True (all values are `true`, `failed_checks` is [], the count is 3, the `gate.sha256` equals the recorded value, and isolation is clean).

Result: `demo_match=False`, then `matched=False`, which equals want=False. **Line 516 is the sole deciding conjunct.** The diagnostic `matched_gate_checks` (533) reports 32/33 because it counts by name, unlike the base, which counted values.

Before/after: the base cache-demo predicate (`git show 41553adb:census/round-21/run-acceptance.py`, lines 446–470) has only `len(checks) == expected["checks"]` and `all(value is True …)` (462–463), with no identity check. On base this input yields `matched=True`, which mismatches want=False. On the changed code it yields `False`. The vector discriminates in the intended direction.

### Paired positive: `positive/clean-cache-demonstration` (`oracle.json:586–591`)

This vector has no delta and uses the raw record stdout. The key set equals `CACHE_CHECK_NAMES` exactly (all 33 names checked), so every conjunct from 506 to 526 holds and the expected result is `matched=True`. On base, the positive is also True. Because the positive and the negative share every byte except the renamed key, the pair isolates line 516, provided the positive actually passes.

## 3. Counterexamples considered

**C1 — Kill mutation.** Drafted, not executed: replace `run-acceptance.py:516` with
`and (CACHE_CHECK_NAMES - {"changed_dependency_producer_executed"}) <= checks.keys()`.
Expected kill: `cache/name/changed_dependency_producer_executed` gives observed True against want False. This should be the only vector killed, since every other `cache/name/*` vector still lacks a required name. Deleting line 516 outright should kill all 33 `cache/name/*` vectors.

**C2 — Vacuous-pass risk (a tradeoff, not a defect).** Line 503 hashes the working-tree `tools/souji-evidence-cache.py`, and line 522 compares it to the pinned record's `dd279ba…` (`final-out-S1.json:3164`). If that file drifts, the positive fails, and this negative plus all its `cache/name/*` siblings "pass" for the wrong reason (522 instead of 516).

The driver scores each vector independently (`oracle.py:97`) and does not make negatives conditional on the paired positive. It does exit 1 on any failure (line 111), so the overall receipt still fails, but a per-vector tally would be misleading.

Smallest safe correction (optional): in `oracle.py`, mark a `cache/*` negative as passing only when `positive/clean-cache-demonstration` also passed in the same run, or report the deciding conjunct. I did not verify the working-tree gate digest because that file is outside the named read set; L1's positive run settles it.

**C3 — Duplicate JSON keys (out of scope, declared).** A stdout whose `checks` contains `"changed_dependency_producer_executed": false` followed later by the same key `true` would be accepted, because `json.loads` keeps the last value. That gives 33 keys, set-equal and all `true`. This is the duplicate-key policy that `round-22.md:35` and S106 (`round-22.md:27`) explicitly exclude, and the contract disclaims malicious-producer attestation. It is not a defect against this claim, and it should not be cited as covered.

**C4 — Rename plus an extra key, giving 34 keys.** Line 514 rejects it, and line 516 rejects it independently. Both conjuncts cover it.

## Impacted axes

- **Calibration (claimed):** supported for this vector, from source only. The base would accept and the changed code rejects, decided by identity rather than count.
- **Operability:** no harm. No new exception path; `.keys()` is reached only after `isinstance(checks, dict)`.
- **Coverage:** no harm. The positive keeps its exact 33-name set. The residual risks are C2 (driver independence) and C3 (excluded scope).
