# Attack23 — summary/r19-revision-pin-fixture/extra (want=False) + positive/r19-revision-pin-fixture

Seat: SoujiR22.Attack23 (scout, leaf, source-only). Candidate code 4f83fd222ffbd8825340221a8c426550ef891191; oracle revision ff425ab835614f38205426330b9cdb93fd267045.

## Identity of inputs read (sha256, observed)

| file | working tree | pinned |
|---|---|---|
| census/round-21/run-acceptance.py | 00d0e9c2…e080a6 | equals `git show 4f83fd2:` blob; `git show ff425ab:` = 6a395c13…ca560 (the digest recorded in final-out-S1 input_sha256 for this file) |
| tests/fixtures/r22-result-oracle.json | 292442a6…0651 | equals `git show 4f83fd2:` |
| tests/fixtures/r22-result-oracle.py | 3c0776ae…a604 | equals `git show 4f83fd2:` |
| census/round-21/final-out-S1.json | bc53a752…38fe | equals oracle `source_receipt_sha256` |
| census/round-21/step-inventory.json | 8b7b1cd8…1310 | equals oracle `frozen_inventory_sha256` |

## 1. Stored delta, reconstructed before inspecting the predicate

Pinned public record `final-out-S1.json` → `commands[name=r19-revision-pin-fixture]`: returncode 0, stderr `""`, stdout_sha256 b9660531…ac77c (recomputed from stored stdout: identical), 855 chars, 20 lines, ending in `\n`. Lines 1–19 are `CASE\t…`. Thirteen of them match `^CASE\tpass\t`, six are `CASE\tdiscriminates\t…`, and line 20 is `SUMMARY total=13 failed=0 base_discriminating=6`. No line matches FAIL or INVENTORY. Record says matched=true, observed_pass_lines=13.

Frozen inventory step `r19-revision-pin-fixture`: kind `summary`, expected_summary `SUMMARY total=13 failed=0 base_discriminating=6`, pass_pattern `^CASE\tpass\t`, pass_count 13. There is no `baseline_mismatch_count`, and `<ROOT>/<PYTHON>` appear only in argv. This matches `make_steps` (run-acceptance.py:333–335).

Vector stdout is 889 chars. It equals the pinned stdout as an exact prefix, plus the suffix `SUMMARY invalid synthetic summary\n`. As a unified diff that is `@@ -20,0 +21 @@`, a single appended line. The vector has no `returncode`, `stderr`, `json_set` or `stdout_nested_array_depth` keys.

## 2. Does the fixture actually feed that input? YES

r22-result-oracle.py:67–68 uses `stdout = case.get('stdout', record['stdout'])`, so the vector stdout replaces the pinned one. Lines 86–91 inherit `returncode=0` and `stderr=""` from the record, and stdout is encoded utf-8/surrogateescape (ASCII only here, so it round-trips through `decode_exact`, run-acceptance.py:223–224). The step comes from the frozen inventory after `replace_revision` (lines 59–60), which changes only argv. Kind is not cache-demo, so lines 84–85 do not apply. Decision (lines 92, 97): `observed = result['matched']`, and the vector passes only if `observed is False`.

## 3. Is want=False correct? YES

Hand trace on the candidate (4f83fd2 run-acceptance.py):
- Line 395: `SUMMARY_RE` (line 118, `^(?:SUMMARY|SELFTEST)(?:\t| ).*$`) matches both line 20 and the appended `SUMMARY invalid…` line (prefix `SUMMARY` followed by a space). `summary_lines` therefore has two entries.
- Line 396: `failure_lines` is empty, and line 410 gives `matched = True`.
- Line 416: `summary_lines == [expected]` is false, because the list has two elements.
- Lines 432–435: there are no INVENTORY lines, so `auxiliary_match` is true. Line 440 has no `baseline_mismatch_count`. Line 447: pass_count is 13, so `pass_match` is true.
- Line 463: `matched = True and False and True and not ""`, which is **False**.

The kill has a single cause: summary-line list equality. It is not pass-count, failure-line or stderr.

Paired positive `positive/r19-revision-pin-fixture` (want=True). It uses the pinned stdout, rc 0 and stderr `""`. `summary_lines == [expected]` is true, auxiliary is `[] == []`, pass is 13 == 13 and stderr is empty, so the result is **True**. This agrees with the recorded matched=true. Correct.

## 4. Attack on the changed predicate for this vector

- **The predicate that decides this vector did not change.** In the pinned ff425ab version, the decisive comparison is line 373 `summary_match = summary_lines == ([expected] if expected else [])`, with the combination at line 417 `matched = matched and summary_match and pass_match`. On the candidate the same text is at lines 416 and 463. In the diff, the only change on this vector's path is the conjunct `and not stderr` (line 463), and it is vacuous here because stderr is `""`. The other summary-branch change, the `try/except ValueError` at 428–431, is unreachable because expected_summary is a string.
- **Consequence:** both the original and the changed summarizer give False for this vector and True for its positive. The vector does not discriminate the R22 repair. It is a no-harm, preservation control and carries **zero calibration weight** for C1, whose R22-M2 repair is exercised by the `stderr/*` group and not by `summary-control`. If any report counts it toward calibration (the "repaired" axis), that would be a concrete mismatch. The oracle `contract` string and lessons line 7 do not claim it as repair evidence, so there is no mismatch in the artifacts read.
- **Coverage gap, not a decision error.** All 12 `summary-control` vectors, this one included, append the same non-matching line *after* the real SUMMARY line. No vector in the 214 overrides stdout for a string-expected summary step in any other way; the only other summary stdout override is `summary/r20-input-binding/oversized-count`, which goes through the regex/dict branch. So the string-equality clause is never tested with:
  - an extra line placed before the real one,
  - a duplicated *exact* expected line, or
  - a line-order swap.

### Drafted mutations (not executed)

- **M-survivor.** Change line 416 to `summary_match = summary_lines[-1:] == ([expected] if expected else [])` (last-line-only).
  - This vector: `['SUMMARY invalid synthetic summary'] != [expected]`, so the result is False and it passes. Positive: True, passes.
  - [INFERENCE] It is not killed by any of the 214 vectors, because every control appends.
  - `set(summary_lines) == {expected}` survives the same way for the duplicate-line case.
  - Killing these would need a vector that prepends a stray SUMMARY line, or one that duplicates the exact expected line.
- **M-killed.** Change line 416 to `summary_match = (expected in summary_lines) if expected else not summary_lines`.
  - Expected killed vector: `summary/r19-revision-pin-fixture/extra` gives observed True against want False.
  - The other 11 `*/extra` controls are killed the same way.

## STATUS: PASS (source-only), with a coverage limit

What passes:
- The stored delta reproduces exactly from the pinned record: a single appended line, with rc and stderr inherited.
- The fixture feeds that input.
- want=False is correct, and the paired positive want=True is correct.

Limits:
- The decisive predicate is unchanged between ff425ab and 4f83fd2, so this vector supports operability/no-harm only, not calibration.
- A last-line-only or set-equality mutant of line 416 would survive this vector and, by inference, the whole 214-vector oracle.
- No runner or oracle execution was performed. Line counts and the diff were computed directly over stored JSON data. All observed/expected values above are hand traces.

Scope note: one `ls … | grep -c` on this lane directory returned only an entry count (2) to confirm the directory exists. No names were viewed or used. No tools were installed and nothing else was modified.
