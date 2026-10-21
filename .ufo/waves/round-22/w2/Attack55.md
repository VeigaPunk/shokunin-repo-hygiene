# Attack55 — critic: oracle vector `cache/name/initial_fresh_once` (want=False)

STATUS: **PASS (source-only)**. The stored delta reconstructs exactly from the pinned public record and frozen inventory. The literal `want=False` is correct. The fixture really does feed the mutated `checks` object into `summarize_result`. At `4f83fd2`, the changed predicate rejects that input through exactly one conjunct, `checks.keys() == CACHE_CHECK_NAMES` (`census/round-21/run-acceptance.py:516`). The base predicate at `41553adb` would have accepted the same input, so the vector discriminates base from changed. No counterexample breaks this vector or its paired positive. Limits: nothing was executed. The digests of the oracle input files (`source_receipt_sha256` and `frozen_inventory_sha256`) and the live gate-file digest were not recomputed, and runtime decisions belong to L1's 214-vector run.

## Scope and identity

- I read only the files named in the contract. The only git commands were read-only: `git show`/`git diff`/`git log` on `census/round-21/run-acceptance.py`, `tests/fixtures/r22-result-oracle.json`, and `tests/fixtures/r22-result-oracle.py` at the pinned commits `4f83fd2`, `36c78ba` and `41553adb`. Each pinned file was also piped to `sha256sum` and compared with the working-tree file.
- Pinned `4f83fd222ffbd8825340221a8c426550ef891191:census/round-21/run-acceptance.py` and the working tree have the same sha256, `00d0e9c2…e080a6`. The same holds for `tests/fixtures/r22-result-oracle.json` at `292442a6…0dcd0651`. The code under review is therefore the pinned code.
- Commit `4f83fd2` only touches `numeric_leaves` and adds `RecursionError` to the JSON decode guards. Its oracle-JSON diff is insertions only (+14 lines). The vector `cache/name/initial_fresh_once` therefore dates from `36c78ba` and was not altered in the pinned commit.
- No tools were installed or updated, and no pacman transactions ran.

## 1. Stored delta, reconstructed before inspecting the predicate

Oracle entry (`tests/fixtures/r22-result-oracle.json:1079-1126`):
- `id=cache/name/initial_fresh_once`, `want=false`, `group=cache-names`, `step_name=clean-cache-demonstration`.
- `json_set=[[["checks"], {…33 keys…}]]`.

Public original (`census/round-21/final-out-S1.json`):
- The command record `name=clean-cache-demonstration` (lines 2515–3383) has `returncode 0`, `stderr ""`, and `stdout_sha256 975d4535…`.
- `observed_json.checks` (lines 2996–3029, mirrored in `stdout`) has exactly 33 keys, all `true`, sorted. `initial_fresh_once` is at line 3007.

Reconstruction (key-by-key comparison):
- The delta's first 32 keys (fixture lines 1090–1121) are exactly the original 33 keys minus `initial_fresh_once`, in the same sorted order.
- Key 33 (line 1122) is `"bogus_initial_fresh_once": true`.
- In short, the delta is the original object with one key renamed. Its size is still 33 (`len == expected 33`), every value is still `true`, and the payload's `failed_checks` stays `[]`.
- Nothing else in the payload changes. `status`, `measured_commit`/`harness_revision` (both `ff425ab…`), the four `cases` with phases in order, `producer_executions_new_policy 3`, `inputs_unchanged_during_run true`, `gate.sha256 dd279ba9…` and `isolation.cleaned true`/`residue []` all keep their public values.

Frozen inventory (`census/round-21/step-inventory.json:186-206`):
- `kind=cache-demo`.
- `expected_summary={status ok, measured_commit <REV>, cases 4, checks 33, failed_checks [], producer_executions_new_policy 3, inputs_unchanged_during_run true, isolation_cleaned true}`.

The producer confirms the name is real. `census/round-14/cache-demonstration.py:879-880` defines `checks = {"initial_fresh_once": cases[0]["executions_after"] == 1, …}`, and line 1052 derives `failed_checks` from `checks`. The public record has `cases[0].executions_after == 1`.

**Is the expected decision correct?** Yes. Under the r22 contract the cache-identity question is "exactly 33 reviewed names" (`corpus/lessons/round-22.md:7`; preregistration, defect 3: "cache checks counted rather than identified"). A result with the required `initial_fresh_once` missing and an unreviewed `bogus_initial_fresh_once` present is a renamed identity. Matching the count is the exact failure mode the claim targets, so `want=False` is the right literal.

**Does the fixture actually feed that input?** Yes. In `tests/fixtures/r22-result-oracle.py`:
- Lines 33–36 bind the receipt and the inventory to the hashes stored in the oracle (not recomputed by me).
- Line 58 sets `records[name]`, and line 68 takes `stdout` from the public record because the case has no `stdout` override.
- In lines 72–82, `path=["checks"]` is non-empty and `path[:-1]` is empty, so `payload["checks"] = deepcopy(value)` replaces the whole object, followed by `json.dumps`.
- Lines 83–85 deep-copy the frozen step and set its `measured_commit` to the oracle revision.
- Lines 87–91 call `summarize_result(step, 0, …, "", ff425ab…, ROOT)`.
- Line 97 sets `pass = observed is False`.

## 2. Changed predicate against this vector

Code at `4f83fd2` (`census/round-21/run-acceptance.py`):
- **Lines 184–203:** `CACHE_CHECK_NAMES` is a frozenset literal. I counted 33 distinct names. They are set-equal to the 33 public keys (each checked), and the set does not contain `bogus_initial_fresh_once`.
- **Lines 506–526:** the conjunction `demo_match`, evaluated on the mutated input:
  - Lines 507–513: payload is a dict, status `ok`, revision equality, four cases, and the phase tuple equals `CACHE_CASE_PHASES` (all from public values). **True.**
  - Line 514: `checks` is a dict with `len == 33`. **True**, because the mutation keeps the count.
  - Line 515: `len(CACHE_CHECK_NAMES) == 33`. **True.**
  - **Line 516:** `checks.keys() == CACHE_CHECK_NAMES`. **False.** A dict key view is set-like, so `==` against a frozenset compares the two sets by size and membership. The view contains `bogus_initial_fresh_once`, which is not in the frozenset, and lacks `initial_fresh_once`, which is.
  - Line 517 (all values `is True`) and lines 518–525 (typed `failed_checks`/count, inputs, gate digest, isolation) would be True, but the `and` chain already stops at line 516.
- **Line 536:** `matched = returncode==0 and not failures and demo_match and not stderr`, which gives **False**, so `observed is False` and the vector passes.

**Base `41553adb` (counterfactual, from `git show`).** The cache-demo predicate only had `len(checks) == expected["checks"] and all(value is True …)`, with no identity conjunct. Every other conjunct holds for this input, so the base gives `matched=True`, and the vector fails on base as preregistered. Line 516 is the **sole** killer. That makes the vector a genuine before/after discriminator for defect 3, not one that passes for some unrelated reason.

**Paired positives.**
- `positive/clean-cache-demonstration` (fixture lines 587–591) feeds the unmodified record. The key set equals `CACHE_CHECK_NAMES`, so line 516 is True and the other conjuncts hold on the public values. Expected `matched=True`, which agrees with `want=true`.
- `positive/cache-transient-path-and-time` (lines 4055–4075) changes only `cases[0].record` and `observed_at`. Neither is read by `demo_match`, and the phase/count conjuncts at lines 504–513 are unaffected. Expected True, which agrees.

## 3. Strongest counterexamples tried (none breaks this vector)

1. **Duplicate JSON keys.** Input like `{"initial_fresh_once": false, …, "initial_fresh_once": true}` decodes to the last value, `true`, and would be accepted. The lesson already lists this outside the claim (`round-22.md:35`, "Duplicate JSON keys … remain outside this claim"). It is a tradeoff, not a defect, and it is unrelated to this vector, which uses `json.dumps` output.
2. **Semantic forgery.** A producer could keep the name `initial_fresh_once: true` while `cases[0].executions_after == 2`, and the runner would accept it, because it never re-derives check values from case rows. This is a disclosed limit ("not a proof that each producer assertion executed", `round-22.md:7`), so the judge should not count it against C1.
3. **Superset or alias input** (34 keys including both names). Line 514 rejects it on length and line 516 rejects it on identity.
4. **Non-hermetic gate conjunct (attribution risk, not a mismatch).** Line 503 hashes the **live** `ROOT/tools/souji-evidence-cache.py`, and line 522 requires it to equal the record's `gate.sha256 dd279ba9…`. If that live file drifts, every cache-demo vector returns `matched=False`. All 33 `cache/name/*` negatives would then pass vacuously while both cache positives fail. The oracle receipt records only a boolean per vector, not which conjunct failed. The kill is therefore attributable to line 516 only if both cache positives pass **in the same receipt**. I did not recompute the live gate digest; it is not a named path.

## 4. Impacted axes

- **Calibration (claimed):** supported for this vector. It is a literal, correctly reconstructed negative, and line 516 alone kills it, with a demonstrated base→changed flip.
- **Operability and coverage (no-harm):** no harm seen. The identity conjunct is a pure comparison on already-decoded data and does not change the paired positives.

## 5. Smallest safe correction

Nothing needs to change for this vector. One recommended L1 integration guard, which needs no code change: count `cache/name/*` negatives as evidence only when `positive/clean-cache-demonstration` and `positive/cache-transient-path-and-time` pass in the same oracle receipt. That closes the attribution gap from line 503 in counterexample 4. An optional later hardening, not required for C1, would have `summarize_result` emit the first failing conjunct name, so each negative's receipt names its killer directly.

Report: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/w2/Attack55.md
