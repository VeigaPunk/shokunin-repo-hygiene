# Attack16 — summary/r20-input-binding/extra (want=False)

Seat: SoujiR22.Attack16 (leaf, source-only). Code under test: 4f83fd222ffbd8825340221a8c426550ef891191 (HEAD; named files clean in `git status --porcelain`). Preregistered base: 41553adb139d06511dc386bb3ce4326aebfba675. Tools installed/updated: none.

## STATUS

PASS (source-only) for decision correctness and fixture feed, with a calibration caveat. The literal `want=False` is correct, and the fixture really does feed the mutated stdout. Tracing by hand, 4f83fd2 returns `matched=False` for this vector and `True` for its paired positive. However, the vector is **non-discriminating** for the R22 change. Base 41553adb rejects it through the identical, unchanged line-count predicate, and neither changed summary-branch predicate decides it. It is a no-harm/regression control and MUST NOT be counted as before→after calibration evidence for C1. Nothing was executed: no oracle run, acceptance run, or mutation run. L1's 214-decision run remains the runtime authority.

## 1. Stored delta reconstructed from pinned inputs (before reading the predicate)

- Oracle `r22-result-oracle.json` binds `source_receipt=census/round-21/final-out-S1.json` sha256 `bc53a752…38fe` and `frozen_inventory=census/round-21/step-inventory.json` sha256 `8b7b1cd8…1310`. Both match on-disk `sha256sum`. Oracle file sha256 `292442a6…0651`, 214 cases.
- Case keys: `{id, want, group=summary-control, step_name=r20-input-binding, stdout}`. It has no `returncode`, `stderr`, `json_set` or `stdout_nested_array_depth`.
- Pinned record `commands[name=r20-input-binding]`: returncode 0, stderr `''`, matched True, 63 stdout lines; stdout sha256 `1544ac95…2664` equals the recorded `stdout_sha256`.
- The case stdout is byte-for-byte the record stdout plus exactly one appended line: `'SUMMARY invalid synthetic summary\n'` (`case.stdout.startswith(record.stdout)` is True; the suffix is exactly that line). It is the same suffix used by all 12 `summary-control` vectors.
- Frozen inventory row `r20-input-binding` is a dict `expected_summary` (`regex` `SUMMARY\ttotal=52\tpass=52\tfail=0\tblocked=0\tinventory=exact\tbaseline_mismatches=(\d+)`, one `INVENTORY` auxiliary line, `baseline_mismatch_group=1`). It also has `pass_pattern ^CASE\tpass\t`, `pass_count 52`, `baseline_mismatch_count true` and `kind summary`, and it equals the record's `expected_summary`. It contains no `<REV>`/`<REVISION>`, so `replace_revision` is the identity here.
- Record facts that the decision depends on: `observed_summary` has 1 line; `observed_auxiliary_lines` equals the expected INVENTORY line; 8 `BASELINE_MISMATCH` lines; 52 pass lines. `returncode==0` and `matched=True` imply `failure_lines` is empty, and `failure_lines` is unchanged by R22.

## 2. Is the expected decision correct?

Yes. In the dict branch the summary contract is "exactly one SUMMARY/SELFTEST line, and it must fullmatch the regex" (`run-acceptance.py:419-423`). The string branch has the same contract (`summary_lines == [expected]`, `:416`). The appended line matches `SUMMARY_RE` (`:118`, `^(?:SUMMARY|SELFTEST)(?:\t| ).*$`, via the space alternative), so two summary lines exist. That is an ambiguous producer result and correctly not success. The preregistration requires "exact historical outcome projections", and the base produces the same False (see §4), so the literal agrees with history.

## 3. Does the fixture actually feed this input?

Yes. In `r22-result-oracle.py`:
- `:56` loads the hash-checked receipt/inventory (`inputs()` `:28-37` raises on digest mismatch); `:59-60` builds `steps` via `replace_revision`.
- `:67` `record = records['r20-input-binding']`; `:68` `stdout = case.get('stdout', record['stdout'])` → case stdout (full replacement, not a patch).
- `:69-82` skipped (no depth/json_set keys); `:84` cache-demo rewrite skipped (`kind summary`).
- `:86-91` call `summarize_result(step, 0, stdout.encode('utf-8','surrogateescape'), b'', revision, ROOT)`. Returncode and stderr come from the record (0, `''`). The text is ASCII, so the surrogateescape round-trip is exact.
- `:97` passes only if `type(observed) is bool and observed is False`.

## 4. Changed predicate, attacked for this vector (4f83fd2 line numbers)

The only R22 diffs in the summary branch between 41553adb and 4f83fd2 are:
- (a) `try/except ValueError` around `int(baseline_match.group(group))` (`:428-431`; base `:385`).
- (b) `and not stderr` appended to `matched` (`:463`; base `:417`).

`SUMMARY_RE` (`:118`), `summary_lines` (`:395`; base `:352`), `matched = returncode == 0 and not failures` (`:410`; base `:367`) and `summary_match = len(summary_lines) == 1` (`:419`; base `:376`) are all unchanged.

Trace for `/extra`:
- `:395` summary_lines = [real SUMMARY, `SUMMARY invalid synthetic summary`] (len 2). `:396` failures = [] (no `FAIL\t`/`CASE\tFAIL` lines; stderr empty, so no joiner). `:410` matched = True.
- `:419` summary_match = False; `:420-423` short-circuit (fullmatch is never evaluated).
- `:426` `if group is not None and summary_match` is False, so **changed predicate (a) is never reached**; reported_baseline_mismatches stays None.
- `:432-436` the auxiliary line matches, but summary_match stays False. `:440-444` stays False (also None≠8). `:446-450` pass_match True (52==52).
- `:463` `True and False and …` short-circuits at summary_match, so **changed predicate (b) is not even evaluated**. Result: matched=False. The vector passes.

Base 41553adb follows the identical path: `:376` False, so `:417` `matched and summary_match` is False. **Before = after = False.** The vector does not discriminate the R22 change, so for C1 it adds zero calibration weight and only no-harm weight.

## 5. Paired positive `positive/r20-input-binding` (want=True)

Inputs come entirely from the record (stdout 63 lines, rc 0, stderr `''`).
- `:419` len 1 → True. `:420-423` fullmatch succeeds. `:428-429` `int('8')` = 8, so (a) takes the no-exception path.
- `:435` auxiliary matches. `:441-444` 8 == 8 (`BASELINE_MISMATCH` lines). `:450` 52 == 52.
- `:463` `not ''` → (b) is True. matched = True; the positive passes on 4f83fd2.

Base: identical apart from the absent `not stderr`, so True. The recorded `matched: True` is consistent. No harm from (a) or (b) on the real output.

## 6. Mutation drafts (not executed)

- **M1, killed:** at 4f83fd2 `:419`, change `len(summary_lines) == 1` to `len(summary_lines) >= 1`. Under `/extra`, summary_lines[0] is the genuine line, fullmatch succeeds, then 8==8, 52 pass, empty stderr → matched True ≠ want False → **killed**. The positive is unchanged (True). In make_steps, `r20-input-binding` is the only summary step with a dict `expected_summary` (the other 11 summary steps use the string branch at `:416`), so `summary/r20-input-binding/extra` is the **sole** vector that kills M1. `oversized-count` has only one SUMMARY line and cannot.
- **M2, survives (coverage gap):** M1 plus `summary_lines[0]` → `summary_lines[-1]` at `:422`/`:427`. The appended invalid line is now the one checked, fullmatch fails, and the result is still False, so it is not killed. A prepended-extra variant would kill M2 but not M1. Only the append order is covered. The predicate itself is still correct; this is a gap in the oracle's mutation adequacy, not a code defect.
- A reverted-R22 mutant (delete (a) and (b)) is not killed by this vector (§4).

## 7. Concrete mismatches and limits

1. **Calibration attribution:** `/extra` (and, by the same line-count/string-equality logic, the other 11 `summary-control` vectors [INFERENCE: not traced individually]) is base-rejected. Any C1 tally that counts it as base-fail→changed-pass discrimination is wrong. It belongs to the "retain historical outcome" no-harm set.
2. **Schema wording, low severity:** lesson `round-22.md:32` says the vector schema "stores only deltas". This case stores the full 64-line replacement stdout, and `oracle.py:68` substitutes it wholesale. Only the cache stdout is deduplicated. Bytes and decision are unaffected.
3. **Out of scope:** `SUMMARY_RE` requires a tab or space after `SUMMARY`/`SELFTEST`, so variants such as a bare `SUMMARY` or `SUMMARY:` are not counted as summary lines. The claim excludes this ("arbitrary stdout failure-marker semantics", lesson `:34`); I note it without contesting the claim.
4. Not read, per contract: `tests/fixtures/r20-input-binding.py` (not a named path). Whether the real producer can emit a second SUMMARY line is unassessed; the vector is synthetic by design.

Confidence: high for §1–§5 (exact bytes, digests and line citations); medium for §6 (hand-simulated, not run).
