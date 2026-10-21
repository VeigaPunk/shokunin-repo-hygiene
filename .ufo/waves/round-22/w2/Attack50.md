# Attack50 — `cache/name/changed_dependency_not_reused` (want=False) and its paired positive

Seat: SoujiR22.Attack50 (critic, leaf, source-only). Target: code `4f83fd222ffbd8825340221a8c426550ef891191` (= worktree HEAD; `git diff --stat 4f83fd2 -- <named paths>` empty).

## STATUS

**PASS (source-only).** For this vector the expected decision `want=False` is correct, and the fixture really does feed the intended input. The input is the pinned S1 `clean-cache-demonstration` stdout with exactly one identity substituted: count 33, all values `true` and `failed_checks=[]` are preserved. On that input only the new identity clause (`run-acceptance.py:516`) can reject it. The base predicate (`41553adb`, lines 462–463) would have accepted it, so the vector discriminates before from after. The paired positive satisfies every cache-demo clause from the pinned bytes, with one exception: the live gate-file digest (line 503) was not read, because it is outside the named paths.

Limits:
- Nothing was run. No runner, no oracle, no mutation was executed.
- The facts come from Python `json`, `jaq` and `git` reads of the named files only. `jaq` could not parse the oracle file, so Python's decoder was used for oracle reads.
- The `observed` values below are derived by reading source. They are not runtime evidence; L1's run of all 214 decisions is authoritative.

## 1. I reconstructed the stored delta before looking at the predicate

- **Original record.** `census/round-21/final-out-S1.json` (sha256 `bc53a752…38fe`, which equals `source_receipt_sha256` in the oracle).
  - The command `clean-cache-demonstration` has `returncode=0` and `stderr=""` (lines 3380–3381).
  - Its `stdout` (line 3383) decodes to a payload equal to `observed_json` (lines 2516–3377), checked with Python and `jaq`.
  - `checks` has 33 keys, all `true` (lines 2996–3030), including `"changed_dependency_not_reused": true` (line 3002).
  - Other fields: `status="ok"` (3352), `measured_commit` and `harness_revision` both `ff425ab8…7045` (3271, 3170), `failed_checks=[]` (3148), `producer_executions_new_policy=3` (3328), `inputs_unchanged_during_run=true` (3245), `isolation.cleaned=true` with `residue=[]` (3248, 3255), `gate.sha256=dd279ba9…39d6` (3164).
  - The case phases are `initial-fresh, unchanged, dependency-modified, legacy-no-dependencies` (2625, 2732, 2819, 2926).
- **Frozen inventory.** `census/round-21/step-inventory.json` (sha256 `8b7b1cd8…d1310`, which equals `frozen_inventory_sha256`).
  - Lines 187–197 give `kind=cache-demo`, `checks: 33`, `cases: 4`, `failed_checks: []`, `producer_executions_new_policy: 3`, `inputs_unchanged_during_run: true` and `isolation_cleaned: true`.
  - `measured_commit "<REV>"` is replaced with `ff425ab…` (`r22-result-oracle.py:40-47,59-60`) and set again for cache-demo (`:84-85`).
- **Stored delta** (`r22-result-oracle.json:839-886`). A single `json_set` operation on path `["checks"]` replaces the whole object with 33 keys, all `true`.
  - Checked mechanically with Python `json`, the delta compared with the original record is: missing `changed_dependency_not_reused`, added `bogus_changed_dependency_not_reused`, nothing else.
  - No other oracle case drops this name.
  - The oracle has 214 cases in total.
- **The fixture feeds this input.** `r22-result-oracle.py:67-82` loads `record['stdout']`, parses it and applies the `json_set` (an empty `path[:-1]` means `at = payload`, so `payload['checks'] = value`). It then calls `summarize_result` with the record's `returncode=0` and `stderr=""`, and the real `root`, which is the repository.
  - `passed` requires `type(observed) is bool` (`:97`). A crash therefore cannot pass as a reject.
- **Verdict.** `want=False` is correct. A cache-demo payload that omits a reviewed obligation name, and instead carries an unreviewed name with the same cardinality, does not prove the "changed dependency not reused" obligation. Under the claim in `preregistration.txt:1` ("cache checks counted rather than identified") and `lessons/round-22.md:7,17` ("exactly 33 reviewed names"), it must reject.

## 2. Attack on the changed predicate for this vector

Predicate: `run-acceptance.py:493-536`, with names at `:184-203`.

The clauses evaluate as follows on the delta input:
- `status`, `measured_commit`, `harness_revision`, the four cases and the phase order (lines 508–513) pass.
- `len(checks)==33` (514) passes.
- `len(CACHE_CHECK_NAMES)==33` (515) passes. The 33 names extracted from `:184-203` equal the original record's key set exactly, compared mechanically.
- **`checks.keys() == CACHE_CHECK_NAMES` (516) fails**, because the missing and bogus names differ.
- All values `True` (517) passes.
- `json_exact` on `failed_checks` and on `producer_executions_new_policy` (518–520) passes.
- The `inputs_unchanged`, `gate` and `isolation` clauses (521–525) pass, assuming the gate digest is unchanged (see section 3).

The result is `demo_match=False`, so `matched=False`, which agrees with `want`.

Semantics: `dict_keys` compared with `==` against a `frozenset` uses set equality. In CPython, `dictview_richcompare` accepts any set, and the [dictionary view docs](https://docs.python.org/3/library/stdtypes.html#dictionary-view-objects) say keys views are set-like. I did not re-open that page this round. `matched_gate_checks` (533) now counts by reviewed name, giving 32 for this input. That is diagnostic only and does not affect the decision.

Base discrimination: the base commit `41553adb` has no change to this file up to `1957154` (`git diff --stat` is empty). Its predicate is only `len(checks)==expected["checks"]` plus all-`True` (base lines 462–463). That gives `matched=True` for this input, so the base fails this vector and the changed code passes it. I found no counterexample inside this vector's scope.

**Strongest counterexample found** (a tradeoff, not a C1 defect). The predicate checks name identity only, not the payload's own evidence for that name. In the pinned payload, `cases[2]` (dependency-modified) has `reusable=false`, `retained=false`, `gate_exit=1`, `result.result_origin="fresh-execution"` and `executions_after=2`. The producer derives the check from exactly those fields (`cache-demonstration.py:912-914`).

Consider this synthetic input, drafted but **not executed**:

```
json_set [[["cases",2,"reusable"],true],[["cases",2,"retained"],true],[["cases",2,"result","result_origin"],"retained-from-record"]]
```

It contradicts `changed_dependency_not_reused=true` inside the same payload, yet the current predicate would return `matched=True` (derived from source).

This is outside the C1 claim, which is disclosed in `lessons/round-22.md:7` ("not a proof that each producer assertion executed") and in the oracle `contract` ("No … complete producer validation"). The Rust judge should therefore treat it as a declared tradeoff. It is not grounds to reject C1, but it must not be described as obligation verification. Smallest safe correction, for a future round only: cross-check the `dependency-modified` row (`reusable is False and retained is False and result.result_origin == "fresh-execution"`) against the claimed check, and add the draft above as a `want=False` vector.

## 3. Paired positive `positive/clean-cache-demonstration` (want=True)

This case has no delta (`r22-result-oracle.json:587-591`). Every pinned-byte clause in section 2 holds for the unmodified stdout, and line 516 holds because the key set equals `CACHE_CHECK_NAMES` exactly. `failure_lines` (356–359) is empty because `stdout` is one JSON document with no lines starting `FAIL\t` or `CASE\tFAIL\t`.

One clause is outside the pinned bytes. Line 503 hashes the live `ROOT/tools/souji-evidence-cache.py` and compares it to the recorded `dd279ba9…39d6`. That path is not in my named read set, so it is unverified. If the gate file has drifted:
- the positive reports `matched=False`, which is visible as a failure;
- every cache-name negative, including this one, would still "pass" for the wrong reason.

The oracle does not attribute which clause rejected an input, so the positive is the only guard against that masking. L1 should check that the positive passes in the same run before crediting this vector.

## 4. Drafted mutation (not executed)

Delete `run-acceptance.py:516` (`and checks.keys() == CACHE_CHECK_NAMES`). This restores the base's counted-not-identified behaviour.

- Expected killed vector: `cache/name/changed_dependency_not_reused` (observed `True`, want `False`). All 32 sibling `cache/name/*` vectors should be killed too.
- Expected survivor: `positive/clean-cache-demonstration` (still `True`).

## Impacted axes

- **calibration** (claimed): supported for this vector.
- **operability / coverage**: no harm found. The coverage gap is the declared tradeoff in section 2.

## Tooling

No installs or updates. `jaq` 3.1.1 (already installed as `jq`) failed to parse the oracle JSON at byte offset 164988, so Python's stdlib `json` was used for oracle reads.

Report: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/w2/Attack50.md
