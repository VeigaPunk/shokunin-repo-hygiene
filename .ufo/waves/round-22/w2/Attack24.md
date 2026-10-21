# Attack24 — summary/agreement-pin-check/extra (want=False)

Seat: SoujiR22.Attack24, leaf, source-only. Target code `4f83fd222ffbd8825340221a8c426550ef891191`.
Nothing was run: no oracle, runner, tests, or empirical probes. No tools installed or updated.

## STATUS

**Source-only PASS for this vector and for its paired positive.** The literal expectation `want=False` is correct under the frozen contract. The fixture actually feeds the stated input. Under the changed predicate, the vector is rejected for exactly one reason: the extra summary line. The paired positive `positive/agreement-pin-check` is accepted.

Limits:
- This vector does **not** discriminate the round-22 changes. The original runner (`ff425ab`) reaches the same `False` through unchanged code, so it guards against regression and is not calibration evidence.
- The step contract ignores any stdout that does not look like a summary line. That gap is pre-declared out of scope (see R1 below).
- No runtime evidence is claimed. L1's actual 214-vector run is authoritative.

## 1. Stored delta and reconstruction (done before reading the predicate)

Oracle case, `tests/fixtures/r22-result-oracle.json:580-585`:
`{"id":"summary/agreement-pin-check/extra","want":false,"group":"summary-control","step_name":"agreement-pin-check","stdout":"SUMMARY invalid synthetic summary\n"}`.
The only delta is `stdout`. There is no `returncode`, `stderr`, `json_set` or `stdout_nested_array_depth` key.

Pinned public original record: `census/round-21/final-out-S1.json`. It contains the single `"commands"` array at line 28 and the only `agreement-pin-check` record at line 2321. Lines 2321-2328 give `returncode: 0`, `stdout: ""`, `stderr: ""`, both sha256 equal to `e3b0c442…b855` (the empty digest), and `observed_summary: []`. Its `matched_counts` show `record_checks: 1` and `summary_lines: 0`.

Frozen inventory: `census/round-21/step-inventory.json:170-184` gives `expected_summary: ""`, `pass_pattern: null`, `pass_count: 0`, `record_checks: 1`, `kind: "summary"`. Its argv uses only `<PYTHON>` and `<ROOT>` placeholders, so `replace_revision` (`r22-result-oracle.py:40-47`) leaves this step unchanged. Line 171 is the **only** inventory step with an empty `expected_summary`, which matches `run-acceptance.py:336-337`.

Input integrity: the working-tree sha256 values equal the oracle pins. `final-out-S1.json` is `bc53a752…38fe` and `step-inventory.json` is `8b7b1cd8…1310` (oracle `r22-result-oracle.json:3-6`). `git diff --stat 4f83fd2` over all five named files is empty, so the working tree equals the pin.

The input the summarizer receives, per `r22-result-oracle.py:67-91`:

| field | value | source |
|---|---|---|
| step | inventory row 170-184, unchanged | `steps[...]` at line 59; not cache-demo, so line 84 does not apply |
| returncode | `0` | `record['returncode']` at line 88 (no case override) |
| stdout | `"SUMMARY invalid synthetic summary\n"` | `case.get('stdout')` at line 68; no json_set or depth path |
| stderr | `""` | `record['stderr']` at line 90 |

**Is the fixture actually feeding this input? Yes.** The `records` lookup is keyed by name (line 58) and there is exactly one matching record, so no duplicate-name shadowing occurs. The step name exists in both pinned inputs. All bytes are ASCII, so `surrogateescape` encoding is lossless.

**Is the expected decision correct? Yes.** With `expected_summary` set to `""`, the step contract (`run-acceptance.py:416`) means *zero* summary lines are expected. The pinned real output had zero. Adding a `SUMMARY …` line contradicts that contract, so `want=False` is right. The oracle fixes this value literally and does not read it from the implementation.

## 2. Attack on the changed predicate for this vector

Trace through `census/round-21/run-acceptance.py` at `4f83fd2`:

1. `decode_exact` (223-224) leaves the string unchanged.
2. Line 395 applies `SUMMARY_RE = ^(?:SUMMARY|SELFTEST)(?:\t| ).*$` (line 118). It matches `SUMMARY invalid synthetic summary` because a space follows `SUMMARY`, so `summary_lines = ["SUMMARY invalid synthetic summary"]`.
3. Line 396: `failure_lines` (356-359) finds no `FAIL\t`, `CASE\tFAIL\t` or `CASE\t…\tFAIL` lines, so it returns `[]`.
4. Line 410: `matched = (0 == 0) and not [] = True`.
5. Lines 415-417: `expected` is the string `""`, so `summary_match = (summary_lines == [])`, which is **False**.
6. Lines 432-436: there are no `INVENTORY\t` lines, so `[] == []` holds and `summary_match` stays False.
7. Lines 440-444 are skipped because the step has no `baseline_mismatch_count`.
8. Lines 446-450: `pass_pattern` is None, so `pass_count = 0`, which equals `0`, and `pass_match` is True.
9. Line 463: `matched = True and False and True and not ""` = **False**.
10. Line 464 does not apply (wrong step name). Line 537 returns `matched = False`.

The observed value is the bool `False` and `want` is `False`, so the comparison at oracle line 97 (`type(observed) is bool and observed is case['want']`) passes.

The rejection has a **single cause**. The exit code, failure lines, pass count, auxiliary lines and stderr all still match, so only `summary_match` flips. The vector therefore isolates the empty-expected summary branch, and no other condition could hide a regression in it.

What `4f83fd2` changed: `numeric_leaves` became iterative, and `RecursionError` is now caught at lines 469 and 496. None of this is on the `kind == "summary"` path. Across the whole of round 22 (`ff425ab..4f83fd2`), the only summary-branch changes are the `try/except ValueError` around `baseline_match.group` (lines 428-431; this step has no group) and `and not stderr` (line 463; stderr is empty). So the **original summarizer also returns False** through identical code at the old line `summary_lines == ([expected] if expected else [])`. Baseline and changed agree, and there is no harm.

## 3. Paired positive `positive/agreement-pin-check` (want=True)

Case at `r22-result-oracle.json:539-543` has no delta, so it uses the pinned record: rc `0`, stdout `""`, stderr `""`.

Trace: `summary_lines = []`, then `failures = []`, then line 416 gives `[] == []` (True), auxiliary lines `[] == []`, `pass_count 0 == 0`, and `not ""` is True. Line 463 therefore yields **True**, matching `want=True`.

The original runner also yields True, because the only round-22 addition on this path, `not stderr`, holds for empty stderr. **PASS.** The positive and the extra-summary vector differ only in the stdout bytes, so together they form a minimal pair across the branch at line 416.

## 4. Drafted mutation (not executed)

**M-A24.** Change `run-acceptance.py:416` from
`summary_match = summary_lines == ([expected] if expected else [])`
to
`summary_match = (not expected) or summary_lines == [expected]`.

- **Expected to be killed by:** `summary/agreement-pin-check/extra`. Observed would become `True`, which does not equal want `False`.
- **Survivors:** `positive/agreement-pin-check` stays True. The `exit/…` and `stderr/…` vectors for this step (oracle 545-578) still reject, through `returncode` and `not stderr`. All nonempty-expected steps are unaffected.

Because inventory line 171 is the only step with an empty expected summary, this vector is the **sole** vector in the 214-vector oracle that guards that branch. The step has exactly seven oracle cases, and the other five negatives fail for unrelated reasons. Removing this vector would leave M-A24 undetected.

## 5. Residuals (none is a mismatch for this vector)

- **R1. Accepted stdout gap (pre-declared out of scope).** For this step, any stdout that `SUMMARY_RE` misses is accepted when rc is 0, there are no FAIL lines, and stderr is empty. Examples:
  - bare `SUMMARY\n` (the regex requires a tab or space after the keyword),
  - `SUMMARYX …`,
  - ` SUMMARY …` with a leading space,
  - `ERROR: …` written to stdout.

  Each of these yields `summary_lines == []`, so the result is True. `pass_pattern` is null, so nothing else constrains stdout. `corpus/lessons/round-22.md:33` explicitly excludes "arbitrary stdout failure-marker semantics". This is not a defect in this vector, but it does mean "summary-control" only covers well-formed summary lines.
- **R2. `record_checks` is never checked.** `record_checks: 1` is only copied into `matched_counts` (line 461). No branch verifies that the agreement record check happened. This is also declared out of scope as "agreement record_checks provenance" (lessons:33).
- **R3. Calibration attribution.** This vector must not be counted as evidence for the round-22 improvement, because the baseline already decides it correctly. It counts only on the no-harm axis.

## Process disclosure

To locate the step, I ran one content grep over the `census/round-21/` directory. Its output also listed matching lines from unnamed sibling receipts (accepted-, replay-, verified-, headless-, remote-source-*, acceptance-c2-first). That breaches the "no broad grep" bound. **That output is VOID.** No finding above relies on it; every citation comes only from the named files and from `git show`/`git diff` on named paths. No other seat was contacted.
