# Attack54 — critic, vector `cache/name/historical_legacy_records_refused` (want=False)

Seat: SoujiR22.Attack54, leaf, source-only. Target code 4f83fd222ffbd8825340221a8c426550ef891191; base 41553adb139d06511dc386bb3ce4326aebfba675.
Axes: calibration (claimed); operability and coverage (no-harm).

## STATUS

PASS (source-only), with one conditional dependency and two scope tradeoffs. This is not a defect.
- The expected decision `want=False` is correct.
- The fixture really feeds the intended input: exactly one key renamed, count and values preserved.
- At the pinned code, conjunct `checks.keys() == CACHE_CHECK_NAMES` is the only one this mutation can break.
- At the base, the same vector is accepted, so it is a real before→after discriminator for R22-M3.

Limits:
- Nothing was executed, so no runtime observation is claimed.
- I did not hash or read the live gate file `tools/souji-evidence-cache.py`, because it is not a named input. The paired positive therefore holds only if that file's sha256 equals the recorded `dd279ba9…`, which is [INFERENCE]. L1's 214-vector run settles this.
- I installed or updated no tools.

## 1. Reconstruction before inspecting the changed predicate

The public original record is `census/round-21/final-out-S1.json`. The entry `commands[name=clean-cache-demonstration]` has `returncode` 0 (line 3380) and `stderr` "" (line 3381). Its `stdout` (line 3383) is a JSON object whose top-level `checks` holds exactly 33 keys, all `true`. The decoded mirror at lines 2996–3030 lists them alphabetically. `historical_legacy_records_refused: true` is the 10th key (line 3006). Grep finds that name only twice in the receipt: once in `observed_json` and once in `stdout`. No `bogus_*` key exists in the receipt.

The frozen inventory is `census/round-21/step-inventory.json` lines 187–206. It fixes only the cardinality `"checks": 33`, plus `cases` 4, `failed_checks` [], `producer_executions_new_policy` 3, `inputs_unchanged_during_run` true, `isolation_cleaned` true and `measured_commit` `<REV>`. It carries no names. Name identity therefore comes from outside the frozen inventory, as the lesson's M3 row states.

The producer is `census/round-14/cache-demonstration.py` lines 880–978. It emits exactly these 33 names. Line 962 sets `historical_legacy_records_refused = historical_legacy["all_refused"]`. Lines 838–841 define that as `bool(historical_entries) and all(gate_exit==2 and findings==EXPECTED_LEGACY_FINDINGS)`, which guards against vacuous truth over an empty list. The public record has four refused records, at lines 3171–3233.

The stored delta is `tests/fixtures/r22-result-oracle.json` lines 1031–1078. `json_set` replaces the whole path `["checks"]` with a 33-key object. That object is the original 32 names in original alphabetical order (lines 1042–1073), all `true`, plus `bogus_historical_legacy_records_refused: true` (line 1074). I compared it line by line with receipt lines 2997–3029. The delta is an exact single-key rename: count stays at 33, every value stays `true`, and only the key identity changes.

Is the expected decision correct? Yes. The R22 contract (oracle line 8: "Reject … replaced cache check identities") and lesson line 7 ("exactly33 reviewed names") require rejecting any checks object whose name set differs from the reviewed 33. `want=False` is literal and correct.

Does the fixture feed that input? Yes.
- `r22-result-oracle.py` line 67 selects `records['clean-cache-demonstration']`.
- Line 68 takes its raw `stdout`.
- Lines 72–82 apply the delta. The path is non-empty, so `at = payload` and `payload['checks'] = deepcopy(value)`, then `json.dumps`.
- `returncode` and `stderr` fall back to the record values 0 and "" (lines 87–90).
- The step comes from the frozen inventory with `<REV>` replaced (lines 59–60, 40–47).
- Lines 84–85 overwrite `expected_summary.measured_commit` with the oracle revision. This is harmless because the predicate compares against the `revision` argument.
- `passed` requires `type(observed) is bool and observed is False` (line 97), so an exception (observed None) cannot pass as a rejection.

## 2. The changed predicate for this vector

`census/round-21/run-acceptance.py` lines 493–536 at the pinned commit; `git show 4f83fd22:` line numbers match the working tree (503 and 514–517). Evaluating the mutated payload conjunct by conjunct:

| line | conjunct | result | reason |
|---|---|---|---|
| 507–510 | status / measured_commit / harness_revision | true | Untouched: "ok", ff425ab…, ff425ab… (receipt stdout), equal to oracle `revision`. |
| 511–513 | cases: 4 rows, phases in order | true | Untouched: initial-fresh, unchanged, dependency-modified, legacy-no-dependencies. |
| 514 | `len(checks) == 33` | true | The rename keeps 33 keys. |
| 515 | `len(CACHE_CHECK_NAMES) == 33` | true | Constant; I counted lines 184–203 = 33. |
| 516 | `checks.keys() == CACHE_CHECK_NAMES` | **false** | `historical_legacy_records_refused` is missing and `bogus_…` is extra. |
| 517 | all values `is True` | true | All 33 values are `true`. |
| 518–526 | failed_checks, producer_executions_new_policy, inputs_unchanged, gate sha, isolation | true | Untouched. The gate-sha conjunct depends on the live file (see §3). |

Line 516 alone forces `demo_match` false, so `matched` is False (line 536). The observed value equals `want=False` and the vector passes for the right reason.

`dict_keys == frozenset` compares as a set (order-insensitive). I confirmed this by opening the Python 3 stdtypes documentation: "Keys views are set-like since their entries are unique and hashable." The rename is therefore detected regardless of the insertion position of `bogus_…`.

The same vector at base 41553adb (`git show` lines 456–470) checks only `len(checks) == expected["checks"]` and that all values are True. It would return True there, so at the base the vector fails against `want=False`. It is a genuine before→after flip. It is not padding.

The diagnostic at line 533, `matched_gate_checks`, would report 32/33 here. It does not feed `matched`.

## 3. Paired positive: `positive/clean-cache-demonstration` (want=True)

The positive is at oracle lines 587–591 and has no delta. The record satisfies every conjunct:
- status "ok";
- measured_commit and harness_revision ff425ab… (stdout top level);
- four phases in `CACHE_CASE_PHASES` order;
- exactly the 33 names in `CACHE_CHECK_NAMES`, all true;
- `failed_checks` [] and `producer_executions_new_policy` 3, both type-exact;
- `inputs_unchanged_during_run` true;
- isolation `cleaned` true and `residue` [] (lines 3246–3258);
- no `FAIL\t` line starts in the JSON stdout;
- stderr "".

The one exception is gate sha (line 522), which compares the recorded `gate.sha256 = dd279ba95eebd13a6674f79983cec286fd856aa6d7e0719bf551ae0fc08939d6` (lines 3164, 3242) with `sha256(ROOT/tools/souji-evidence-cache.py)`, read live (line 503).

Counterexample (the strongest available locally): that live file is not among the oracle's SHA-bound inputs; `inputs()` at lines 31–36 binds only the receipt and the inventory. If the gate file changes after ff425ab, the positive turns False and every cache negative, including this one, also turns False, but through line 522 instead of line 516. The negative would then pass for the wrong reason.
- In a full run, the positive's failure exposes this: `fail ≥ 1` and exit code 1. No hidden regression.
- With `--case cache/name/historical_legacy_records_refused` alone (oracle.py line 53), the run would report pass with no discrimination. Impacted axis: calibration evidence quality for single-case runs only.

Disposition: a fixable reporting tradeoff, not a judge-rejection defect. Smallest safe correction (no production edit required): L1 cites cache-negative discrimination only from full runs where `positive/clean-cache-demonstration` passes in the same invocation and the same ROOT. An optional fixture change is to bind the gate sha into the oracle header next to the receipt and inventory digests.

## 4. Other attacks attempted

- **Value type.** Replacing the renamed key's value with `1` or `"true"` is caught by line 517 (`is True`). The `cache/value/int-one` vector covers this.
- **Count drift.** Dropping the key without adding one is caught by line 514. The changed code also checks the name set, so a 33-key relabel cannot pass.
- **Vacuous producer truth.** A producer that emits `historical_legacy_records_refused: true` with `historical_legacy.records == []` would pass acceptance. Line 516 checks only the name and value; it never cross-checks `payload.historical_legacy.all_refused` or the record count. The genuine producer cannot emit this (lines 838–841 require `bool(historical_entries)`). The lesson already disclaims it (line 7: "not a proof that each producer assertion executed"; line 35 rejects claiming malicious-producer attestation). This is a tradeoff inside the declared boundary, not a defect.
- **Duplicate JSON keys.** For example `"historical_legacy_records_refused": false, …, "historical_legacy_records_refused": true`. `json.loads` keeps the last value, so this would be accepted. The lesson (line 35) and S106 explicitly place duplicate keys outside the claim. Not a defect for C1.
- **Provenance.** The S105 URL `https://docs.python.org/3/builtins/stdtypes.html` resolves with HTTP 200 and serves the Python 3.15.1 "Built-in Types" page, including the bool subclass paragraph. No false provenance found.

## 5. Drafted mutation (not executed)

- **Mutation M-A54:** delete line 516 (`and checks.keys() == CACHE_CHECK_NAMES`) at 4f83fd22.
  - Expected killed vector: `cache/name/historical_legacy_records_refused`. Observed becomes True against want False, so it fails. All 33 `cache/name/*` vectors would die the same way.
  - Expected survivors: `positive/clean-cache-demonstration` stays True.
- **Narrower variant:** replace line 516 with `and "historical_legacy_records_refused" in checks`. This should kill only this vector among the 33 name vectors, which shows the vector pins this specific identity.

## Impacted axes

- **Calibration:** supported for this vector. The conditional in §3 applies.
- **Operability:** no harm. The mutated shape is type-guarded; there is no `.get` on a non-dict, and lines 498 and 514 guard first.
- **Coverage:** no harm. The single-case caveat is a reporting note.

Report: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/w2/Attack54.md
