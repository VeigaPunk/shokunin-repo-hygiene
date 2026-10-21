# Attack53 — cache/name/gate_digest_recorded_and_unchanged (want=False)

Seat: SoujiR22.Attack53 (critic, leaf, source-only). Target code `4f83fd222ffbd8825340221a8c426550ef891191` (= HEAD; the working-tree `census/round-21/run-acceptance.py` matches the committed blob, sha256 `00d0e9c2…e080a6`). No tests, oracle runs, or probes were executed. I installed nothing.

## STATUS

**PASS (source-only).** The literal expectation `want=False` is correct. The oracle feeds the intended input: the pinned public stdout with exactly one check identity replaced. The changed predicate rejects the vector at exactly one conjunct, `checks.keys() == CACHE_CHECK_NAMES` at run-acceptance.py:516. The base predicate would have accepted it, so the vector discriminates between base and changed code.

Limits:
- **Positive-vector condition [INFERENCE].** The paired positive passes only if the working-tree `tools/souji-evidence-cache.py` still has sha256 `dd279ba9…08939d6`. That file is outside the read contract, so I did not check it. L1's run of `positive/clean-cache-demonstration` must confirm it.
- **Semantic gap (accepted tradeoff, not a C1 defect).** The runner trusts the producer's `gate_digest_recorded_and_unchanged` boolean. It never re-checks the post-run gate digest. See the counterexample below.

## 1. Stored delta, reconstructed from the public record before reading the predicate

Inputs and their sha256 digests, matching `oracle.source_receipt_sha256` and `oracle.frozen_inventory_sha256`:
- `census/round-21/final-out-S1.json` = `bc53a752…738fe`
- `census/round-21/step-inventory.json` = `8b7b1cd8…7d1310`
- Committed oracle JSON at `4f83fd2` = `292442a6…0dcd0651` (same as the working tree)

**Original record** (`final-out-S1.json`, clean-cache command at :2515):
- `returncode` 0 (:3380) and `stderr` "" (:3381).
- `stdout` (:3383) has sha256 `975d4535…6db40` (:3384).
- Its decoded `checks` object (mirrored in `observed_json`, :2996–3029) has 33 keys, all `true`, including `"gate_digest_recorded_and_unchanged": true` (:3005).
- Other top-level fields the predicate reads:
  - `status` is `"ok"` (:3352) and `failed_checks` is `[]` (:3148).
  - `producer_executions_new_policy` is 3 (:3328) and `inputs_unchanged_during_run` is `true` (:3245).
  - `gate.sha256`, `gate.sha256_after` and `gate_sha256_after` all equal `dd279ba9…` (:3164, :3165, :3169).
  - `isolation.cleaned` is `true` and `isolation.residue` is `[]` (:3248, :3255).
  - `measured_commit` and `harness_revision` are both `ff425ab8…` (:3271, :3170).
  - The `cases` rows (:2606) carry the phases initial-fresh, unchanged, dependency-modified and legacy-no-dependencies, in that order (:2625, :2732, :2819, :2926).

**Frozen inventory** (`step-inventory.json`:187–206): `kind: cache-demo`, with `expected_summary` = {status ok, measured_commit `<REV>`, cases 4, checks 33, failed_checks [], producer_executions_new_policy 3, inputs_unchanged_during_run true, isolation_cleaned true}.

**Oracle vector** (`r22-result-oracle.json`:984–1030): `json_set = [[["checks"], {…}]]`. The value lists 32 of the original keys in sorted order with `gate_digest_recorded_and_unchanged` omitted (between :1001 and :1002), then adds `"bogus_gate_digest_recorded_and_unchanged": true` (:1026). I counted every key: 32 originals plus 1 bogus key = 33, all `true`. This is a same-cardinality identity swap, so it isolates exactly the preregistered defect "cache checks counted rather than identified" (preregistration.txt:1; lesson R22-M3, round-22.md:17).

**Is the expected decision correct?** Yes. The contract (oracle :8; lesson :7) says "Cache identity means exactly33 reviewed names". A checks object that is missing a reviewed obligation and carries an unreviewed one must not match.

**Does the fixture actually feed this input?** Yes. Walking `r22-result-oracle.py` in order:
- `records[case['step_name']]` selects the clean-cache record (:58, :67). Because the case has no `stdout` override, `stdout = record['stdout']` is the raw public string, not `observed_json` (:68).
- The `json_set` path `["checks"]` is non-empty, so `path[:-1]` is empty and `payload["checks"]` is replaced wholesale with a deepcopy (:72–82). No other field changes.
- `returncode` (0) and `stderr` ("") come from the record (:88–90).
- The step comes from the frozen inventory with `<REV>` replaced, and `measured_commit` is forced to `oracle.revision` = `ff425ab8…` (:59–60, :84–85). This matches the stdout's `measured_commit` and `harness_revision`.
- `passed` requires `observed is False`, and an exception counts as a failure (:97). The delta has no dead or unreached part.

## 2. Attack on the changed predicate for this vector

These are lines 493–537 of `run-acceptance.py`, evaluated for this vector:
- The `matched` seed is true: `returncode == 0` and there are no failure lines (:410).
- `payload` is a dict, and `checks`, `cases`, `gate` and `isolation` all have the expected types (:498–501).
- `status`, `measured_commit` and `harness_revision` all match (:508–510).
- There are 4 case rows, and the phases equal `CACHE_CASE_PHASES` in order (:511–513).
- `len(checks) == 33` and `len(CACHE_CHECK_NAMES) == 33` (:514–515). I counted the constant at :184–203: 33 names, the same set as the public keys.
- **`checks.keys() == CACHE_CHECK_NAMES` → False (:516).** The key set has `bogus_gate_digest_recorded_and_unchanged` instead of `gate_digest_recorded_and_unchanged`. A `dict_keys` view compares as a set against a `frozenset`, so key order is irrelevant.
- The remaining conjuncts are true: all values are `True`, `failed_checks` is `[]`, the counts match, `gate.sha256` equals the gate digest (given the condition in the STATUS section), and isolation is clean (:517–526).
- So `demo_match` is False, `matched` is False, and `observed` is False, which equals `want`. No exception path is reachable.
- The diagnostic `matched_gate_checks` is 32 (:533). It does not feed `matched`.

**Base comparison.** Both `ff425ab8…` and preregistered base `41553adb…` use `len(checks) == expected["checks"]` plus `all(value is True …)` with no identity conjunct (base :462–463, gate sha :454/:467). The base therefore observes True, which is wrong. The vector discriminates base from changed code.

**Single point of kill.** Line 516 is the only conjunct that rejects this vector. Cardinality and truthiness are both preserved by design.

### Paired positive: `positive/clean-cache-demonstration` (want=True, oracle :587–591)

The positive takes the unmodified record and passes every conjunct above, including :516, given the gate-digest condition. It guards the other side of the predicate: a typo or omission of `gate_digest_recorded_and_unchanged` in `CACHE_CHECK_NAMES`, or a constant with 32 or 34 names, would flip the positive to False and kill the mutation.

**Confound [INFERENCE, not executed].** `gate_sha` is read from the oracle's `ROOT` working tree (:503; oracle :17, :91), not from revision `ff425ab8`. If `tools/souji-evidence-cache.py` changed after `ff425ab8`, the positive fails. Every `cache/*` negative would then pass vacuously, because the oracle records only the final boolean and not which conjunct rejected. This vector's evidence is therefore only meaningful together with a passing positive. L1 must confirm that the positive passes in the same run.

## 3. Counterexample beyond the claim (semantic gap)

This stdout is accepted by the changed predicate:
- Take the public stdout and keep `checks.gate_digest_recorded_and_unchanged: true`.
- Set `gate.sha256_after` and top-level `gate_sha256_after` to `"0"*64`.

The producer computes that check as `bool(gate_state["sha256"]) and gate_sha_final == gate_state["sha256"]` (cache-demonstration.py:933–935), and it publishes both after-digests (:1021, :1207). The runner compares only `gate.sha256` against disk (:522), so this self-contradictory payload yields `matched=True`.

This is out of scope for C1 by its own text: "not a proof that each producer assertion executed" (round-22.md:7) and "No … complete producer validation" (oracle :8). It is a tradeoff, not a defect against the admitted claim.

**Smallest safe correction (optional, separate claim).** Add `gate.get("sha256_after") == gate_sha and payload.get("gate_sha256_after") == gate_sha` beside :522. The public positive still passes, because all three digests are equal (:3164, :3165, :3169). Pair it with a want=False vector that mutates only `gate_sha256_after`.

## 4. Drafted mutations (not executed)

- **M-a.** Delete the `and checks.keys() == CACHE_CHECK_NAMES` line (:516).
  - Expected killed: `cache/name/gate_digest_recorded_and_unchanged` (observed True vs want False) and every sibling `cache/name/*` swap.
- **M-b (per-name specificity).** Replace :516 with `and (CACHE_CHECK_NAMES - {"gate_digest_recorded_and_unchanged"}) <= checks.keys()`.
  - Expected killed: only this vector. The siblings still reject, because their swaps remove a different name.

## Axes

| Axis | Effect |
|---|---|
| Calibration (claimed) | Supported for this vector: correct literal expectation, real input feed, base→changed flip located at :516. |
| Operability (no-harm) | No harm found: there is no exception path for this input, and the type guards at :498–501 hold. |
| Coverage (no-harm) | No harm found. The gate after-digest gap existed before this change and is explicitly declared out of scope. |
