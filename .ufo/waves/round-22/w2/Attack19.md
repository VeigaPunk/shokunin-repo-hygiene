# Attack19 — `summary/landing-gate-selftest/extra` (want=False) + paired positive

Seat: SoujiR22.Attack19 (leaf, source-only). Code under attack: `4f83fd222ffbd8825340221a8c426550ef891191` (HEAD; `git diff --stat 4f83fd22 --` on all five named runner/oracle/inventory/receipt paths is empty). Base per preregistration: `41553adb139d06511dc386bb3ce4326aebfba675`.

## STATUS

**PASS (source-only), with one calibration-attribution caveat.** The expected decision `want=False` is correct, and the fixture really does feed the intended input. The vector does **not** exercise any round-22 predicate change: base `41553adb` and changed `4f83fd22` reach the same `False` through the unchanged summary-list equality. It is a no-harm/preservation control and MUST NOT be counted as C1 calibration-improvement evidence. Paired positive `positive/landing-gate-selftest` (want=True) is also correct and unchanged across base→changed.

Limits: no execution of the oracle, runner, or mutations. The only commands were JSON byte extraction and comparisons on the named pinned files, plus `git show`/`git diff`/`git log` on the named runner path. No tool installs.

## 1. Stored delta reconstructed from the pinned public record (before the predicate)

- The oracle input hashes match the stored values: `final-out-S1.json` sha256 `bc53a752…38fe` and `step-inventory.json` sha256 `8b7b1cd8…1310`, both equal to `source_receipt_sha256` / `frozen_inventory_sha256` in `r22-result-oracle.json`.
- Record `commands[name=landing-gate-selftest]` (measured_commit `ff425ab8…`) has `returncode=0`, `stderr=''`, `matched=True`, `observed_summary=['SELFTEST\tpass=65\tfail=0']`, and `failure_lines=[]`. Its stdout sha256 recomputes to the stored `stdout_sha256` `fa10064c…7c14`. The stdout has 66 lines: 65 `CASE\tpass\t…` lines plus 1 `SELFTEST\tpass=65\tfail=0` line. It contains no non-ASCII bytes and no line separators other than `\n`.
- Frozen inventory step: `expected_summary='SELFTEST\tpass=65\tfail=0'`, `pass_pattern='^CASE\\tpass\\t'`, `pass_count=65`, `kind='summary'`. This is identical to runner `make_steps` at `run-acceptance.py:323-324`.
- Vector (`r22-result-oracle.json:339-345`): its only override is `stdout`, and `case.stdout == record.stdout + 'SUMMARY invalid synthetic summary\n'` holds exactly. There is no `returncode`, `stderr`, `json_set`, or depth override.
- Sibling consistency: all 12 `summary-control` vectors use the same single key (`stdout`), all have want=False, and all use the identical appended tail.

## 2. Does the fixture actually feed that input?

Yes, as traced through `r22-result-oracle.py`:

- `:67-68` resolves the record by `step_name`, then `stdout = case.get('stdout', record['stdout'])` takes the mutated stdout.
- `:84` builds `step` from the frozen inventory after `replace_revision`. This step has no `<REVISION>` token, and `kind` is not `cache-demo`.
- `:87-91` passes `returncode` and `stderr` through from the record (`0` and `''`). Stdout is encoded with `surrogateescape`, which round-trips through `decode_exact` (`run-acceptance.py:223-224`).
- `:97` sets `pass` only when `type(observed) is bool and observed is want`, so an exception cannot pass the vector.

## 3. Predicate trace for this vector at 4f83fd22

- `SUMMARY_RE` (`:118`) is `^(?:SUMMARY|SELFTEST)(?:\t| ).*$`. The injected line matches through the space alternative, so `summary_lines` becomes `['SELFTEST\tpass=65\tfail=0', 'SUMMARY invalid synthetic summary']` (`:395`).
- `failure_lines` (`:356-359`) returns `[]`. No line starts with `FAIL\t` or `CASE\tFAIL\t`, and no case-name field equals `FAIL`.
- `:410`: `matched = (0 == 0) and not []`, which is True.
- `:416`: `summary_lines == [expected]` is **False** because there are two summary lines and the expected list has one.
- `:432-435`: there are no `INVENTORY\t` lines, so `[] == []` holds. `baseline_mismatch_count` is absent (`:440`). `pass_count` is 65 == 65 (`:446-450`).
- `:463`: `matched = True and False and True and not ''`, which gives **False**. This equals the literal `want=False`, so the expected decision is correct.

## 4. Attack on the changed predicate

- Base `41553adb` vs changed (`git diff 41553adb 4f83fd22 -- census/round-21/run-acceptance.py`): `SUMMARY_RE` (base `:118`), `decode_exact`, `failure_lines`, and the string-expected branch `summary_lines == ([expected] if expected else [])` (base `:373`, changed `:416`) are byte-unchanged. The only change in the `summary` kind that this vector reaches is `:463`, which adds `and not stderr`.
- This vector has `stderr == ''`, so the added conjunct is a no-op here. Base `:417` (`matched and summary_match and pass_match`) also yields False.
- **Concrete mismatch (attribution, not a decision error):** the vector gives the same decision on base and changed, so it gives no evidence for C1's improvement claim ("summary stderr accepted despite success"). The stderr fix is guarded only by `stderr/landing-gate-selftest/{error,blank,pass,warning}`, plus `exit/…` for returncode.

## 5. Paired positive `positive/landing-gate-selftest` (want=True)

This vector uses the unmodified record: `rc=0`, `stderr=''`, `summary_lines == [expected]`, no auxiliary lines, `pass_count=65`, and `failure_lines=[]`. That gives **True** at both `:463` (changed) and base `:417`, which matches `want=True` and the historical `matched=True`. It is correct, but it is a preservation control only.

## 6. Drafted mutations (NOT executed)

- **M19-A** (`:416`): `summary_match = summary_lines == ([expected] if expected else [])` becomes `summary_match = expected in summary_lines`. Expected result: **killed** by `summary/landing-gate-selftest/extra` (False→True, `pass=false`), while `positive/landing-gate-selftest` survives (True).
- **M19-B** (`:118`): `(?:\t| )` becomes `\t`. The injected space-separated line would no longer be collected, so the extra vector is **killed** (False→True). Space-separated summary positives (for example `r19-carry-wrap`, `SUMMARY total=4 …`) would also flip True→False. The landing-gate positive is unaffected.
- **M19-C** (`:463`): revert `and not stderr`. The extra vector **survives** (still False). This confirms it does not guard the round-22 change. The expected killers are the `stderr/landing-gate-selftest/*` vectors.

## 7. Residual unknowns / gaps

These are inferences, outside the declared claim.

- `SUMMARY_RE` requires a tab or space after the token. An appended bare `SUMMARY` or `SELFTEST` line, or a variant like `SELFTEST:`, would not be collected, so `summary_lines` would be unchanged and the result would be `matched=True`. No oracle vector covers this. The round-22 lesson does not claim it either: it excludes arbitrary stdout marker semantics.
- `pass_count` counts `^` matches under `re.MULTILINE`, which only breaks on `\n`. `summary_lines` uses `str.splitlines()`, which also breaks on `\r`, `\x0b`, `\x0c`, `\x1c`–`\x1e`, `\x85`, `\u2028`, and `\u2029`. The divergences I can see make the check stricter, not more permissive, for this step. No vector probes them.
- Naming hazard: the lesson's "subset-extra-fields control" (want=True) is a different control from this `summary/…/extra` (want=False). Reviewers should not conflate them.
