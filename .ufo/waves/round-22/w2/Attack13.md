# Attack13 — `summary/auditor-selftest/extra` (want=False) vs code 4f83fd2

Seat: SoujiR22.Attack13 (leaf, source-only). HEAD = `4f83fd222ffbd8825340221a8c426550ef891191`; all named paths clean in the working tree.

## STATUS

**PASS (source-only) for this vector, with one coverage gap that does not block C1.**

- The expected decision `want=False` is correct.
- The fixture really feeds the mutated input to `summarize_result`.
- The changed code rejects the input for exactly one reason: the summary-line equality at `run-acceptance.py:416`.

The vector does not discriminate R22's change. The predicate that rejects it is byte-identical in the base commit `41553adb` (base lines 118/352/373), so the vector is a no-harm regression control, not calibration evidence.

Evidence: I read the named source files and ran `git show`/`git diff` on named paths only. I also ran byte comparisons over the named JSON files with `python3 -B -c`; these only load JSON and never import or run the runner or the oracle script. I did not run the oracle, the runner, any test or any mutation. All runtime decisions below are `[INFERENCE]` from source.

## 1. Stored delta, reconstructed before reading the predicate

- Oracle case: `tests/fixtures/r22-result-oracle.json:51-57`.
  - Fields: `id=summary/auditor-selftest/extra`, `want=false`, `group=summary-control`, `step_name=auditor-selftest`, plus a full `stdout` override.
  - It has no `returncode`, `stderr`, `json_set` or `stdout_nested_array_depth` fields.
- Public original record: `census/round-21/final-out-S1.json:208-217`.
  - Values: `returncode 0`, `stderr ""`, stdout of 119 lines (118 `PASS\t…` lines plus `SELFTEST\tpass=118\tfail=0`).
  - The stdout SHA-256 recomputes to the stored `stdout_sha256` `68f8b35f…d93e`.
  - The receipt file SHA-256 is `bc53a752…38fe`, which equals `source_receipt_sha256` in the oracle.
- Reconstruction: the case stdout is the original stdout plus exactly one appended line, `'SUMMARY invalid synthetic summary\n'`, giving 120 lines. Nothing else changes.
- Frozen inventory step: `census/round-21/step-inventory.json:7-19`.
  - Values: `expected_summary "SELFTEST\tpass=118\tfail=0"`, `pass_pattern ^PASS\t`, `pass_count 118`, `kind summary`.
  - The file SHA-256 is `8b7b1cd8…1310`, which equals the value the oracle pins.
  - The step has no `baseline_mismatch_count`.
- Stability: the case is identical in 36c78ba (212 vectors) and HEAD (214 vectors). 4f83fd2 only added `malformed/cache-demo/decoder-depth` and `malformed/r13-counter-31984f4/decoder-depth`; no case changed or was removed.
- Independence: I could not confirm from Git that the vector was frozen before the implementation, because the oracle and the code landed together in 36c78ba. `bindings-before.json` is outside my read contract. This remains an unresolved gap, not a mismatch.

## 2. Is the expected decision correct?

Yes. The step's contract is exactly one summary line, equal to `SELFTEST\tpass=118\tfail=0`. A second summary-shaped line asserting a different (invalid) summary makes the output's self-report ambiguous, so accepting it would be a false green. `want=False` follows from the frozen `expected_summary` alone and is not derived from the code under test.

## 3. Does the fixture actually feed that input?

Yes (`tests/fixtures/r22-result-oracle.py`):

- `:67` takes the record from the public receipt.
- `:68` applies the case's `stdout` override.
- `:69-82` are skipped because the case has no depth or `json_set` keys.
- `:83` deep-copies the frozen step; `replace_revision` at `:59` has no placeholder to change in this step's fields.
- `:84` is skipped because the step is not cache-demo.
- `:87-91` pass `returncode=0` and `stderr=""` from the record, and encode stdout as UTF-8 with surrogateescape.
- `:97` requires the observed value to be the literal bool `False`.

## 4. Changed predicate on this vector

References are to `census/round-21/run-acceptance.py`. For this input:

- `:395` with `:118` (`SUMMARY_RE = ^(?:SUMMARY|SELFTEST)(?:\t| ).*$`) gives `summary_lines = ["SELFTEST\tpass=118\tfail=0", "SUMMARY invalid synthetic summary"]`. The second line qualifies through the space alternative.
- `:396` with `:356-359` gives `failures = []`. No line starts with `FAIL\t` or `CASE\tFAIL\t`, and stderr is empty, so nothing is joined.
- `:410` gives `matched = True`.
- `:416` gives `summary_match = (two lines == [expected])`, which is **False**.
- `:432-436`: there are no `INVENTORY\t` lines, so `[] == []` holds and does not change the result.
- `:440` is skipped.
- `:447-450`: `pass_count = 118` equals 118, so `pass_match` is True.
- `:463`: `matched and False and True and not ""` gives **False**, so `matched` is False at `:537`.

The rejection depends on one cause only (`:416`), so the vector cleanly isolates the summary-equality predicate. The only R22 change on this path is `and not stderr` at `:463`, which is neutral here because stderr is empty. The base code (`41553adb:…:417`, `matched = matched and summary_match and pass_match`) also yields False.

**Paired positive** (`positive/auditor-selftest`, oracle `:10-15`, `want=True`): with the unmodified record, `summary_lines` is `[expected]`, `pass_count` is 118, failures and auxiliary lines are empty, and stderr is empty. The result is True on both the base and the changed code. There is no mismatch.

## 5. Attacks and gaps

These are drafted only and were never executed.

1. **Mutation that this vector kills.** Change `:416` to `summary_match = (expected in summary_lines) if expected else not summary_lines`, or to `summary_lines[:1] == [expected]`. On this vector the result becomes True, so the vector catches the mutation (killed vector: `summary/auditor-selftest/extra`). A `SUMMARY_RE` mutation to tab-only `(?:\t)` would also flip this vector to True and be killed.
2. **Mutation that survives the whole oracle (coverage gap).** Change `:416` to `summary_match = summary_lines[-1:] == ([expected] if expected else [])`.
   - All 12 `summary-control` deltas append the extra line after the real summary (checked against the receipt).
   - No summary-kind vector places an extra summary line *before* the real one (checked: zero such cases).
   - The other summary-kind groups (stderr 49, exit 12, positive 12, malformed 1) do not depend on summary-line ordering. The single malformed vector, `summary/r20-input-binding/oversized-count`, uses the dict-regex branch at `:418-431`, not the string branch.
   - `[INFERENCE]` This "last summary line wins" mutation would therefore pass all 214 vectors.
   - This is an oracle coverage gap about summary-line identity and position. It is not a C1 falsification: the predicate is unchanged from base, and C1 claims nothing about summary ordering.
3. **Residual false green the predicate cannot see** (same on base and changed code). An appended `SUMMARY\n` or `SELFTEST\n` with no separator, `SUMMARY:x`, a leading-space ` SUMMARY x`, or lowercase `summary x` fails `SUMMARY_RE` (`:118`). The line is not counted, so the output would still be accepted. `FAIL x` with a space instead of a tab also escapes `failure_lines` (`:356-359`). Both fall within the lesson's declared exclusion "arbitrary stdout failure-marker semantics" (`corpus/lessons/round-22.md:35`), so they are not a C1 mismatch.
4. **Naming hazard only.** The contract phrase "subset extra-field control" (oracle `:8`, lesson `:7`) refers to `positive/subset-extra-fields` (oracle `:4020`, `want=True`, a counter `json_set`). It does not refer to this `summary/*/extra` family, which has `want=False`. The decisions are consistent; the shared word "extra" is the only confusion.

## Remaining unknowns

- I could not verify the independent pre-implementation freeze of this vector (see section 1).
- The actual base and changed oracle observations are pending the L1 run of all 214 decisions and the 18-step acceptance.

## Tools

No tools were installed or updated, and no pacman transaction was made.
