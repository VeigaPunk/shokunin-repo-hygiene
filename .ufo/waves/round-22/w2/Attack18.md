# Attack18 — summary/r19-carry-wrap/extra (want=False)

Seat: SoujiR22.Attack18 (leaf, source-only, no run). Candidate under attack: `4f83fd222ffbd8825340221a8c426550ef891191`.
Tool installs/updates: none.

## STATUS

**PASS (source-only) for the vector itself; PARTIAL as calibration evidence.**

- The expected decision `want=False` is correct. Both the base runner (`41553adb`) and the candidate (`4f83fd2`) return `matched=False`, because the summary-equality predicate rejects the extra line.
- The fixture really does feed the stored delta, and no other part of the result contract changes. Exactly one predicate decides the outcome.
- Limits on what this vector proves:
  - It does not discriminate between base and candidate: both give False through an unchanged predicate. So it is a no-harm regression control, not evidence for the C1 calibration change.
  - All 12 `summary-control` vectors use the same append-at-end shape. Two drafted mutants of the summary predicate survive all 214 vectors (see Mutation drafts). That is an oracle coverage gap, not a defect in the candidate code.
- Everything here comes from reading source and data. Nothing was executed except read-only JSON extraction, hashing, and `git show`/`git diff` on named paths.

## 1. Stored delta, reconstructed from pinned inputs (before inspecting the predicate)

- Oracle header (`tests/fixtures/r22-result-oracle.json`) has:
  - `source_receipt=census/round-21/final-out-S1.json`, sha256 `bc53a752…38fe`
  - `frozen_inventory=census/round-21/step-inventory.json`, sha256 `8b7b1cd8…1310`
  - `revision=ff425ab8…7045`
  
  On-disk sha256 of both files matches these values, which satisfies the gate in `r22-result-oracle.py` lines 31–36.
- The pinned public record `commands[name=r19-carry-wrap]` has:
  - `returncode=0`, `stderr=""` (sha256 `e3b0c442…b855`)
  - `matched=true`, `matched_pass_lines=4`
  - `observed_summary=["SUMMARY total=4 failed=0 base_discriminating=2"]`
  - `stdout`: 8 `CASE` lines plus that single summary line, ending in `\n` (sha256 `9e1112c1…c20b`)
- The vector stores only `stdout`. It does not carry `returncode`, `stderr` or `json_set`.
- Computed relation: `vector.stdout == record.stdout + "SUMMARY invalid synthetic summary\n"`. This is an exact prefix match; the delta is one appended line.
- The frozen inventory step `r19-carry-wrap` has:
  - `kind:"summary"`
  - `expected_summary:"SUMMARY total=4 failed=0 base_discriminating=2"`
  - `pass_pattern:"^CASE\\tpass\\tchanged/"`
  - `pass_count:4`
  
  This is identical to `make_steps` in `run-acceptance.py` lines 320–322, where `kind` is implicit and defaults to `"summary"` at line 411.

## 2. Does the fixture feed that input?

Yes. Path through `r22-result-oracle.py`:

- line 67: `record = records['r19-carry-wrap']`
- line 68: `stdout = case.get('stdout', record['stdout'])`, so the delta stdout is used.
- Lines 69–82: these branches are skipped because the case has neither `stdout_nested_array_depth` nor `json_set`.
- Line 83: the step is deep-copied from the frozen inventory. `replace_revision` (lines 40–47) touches only `<REVISION>`/`<REV>` tokens, and this step has none in fields that matter.
- Line 84: the cache-demo branch is not taken.
- Lines 87–91: `returncode` falls back to the record value 0, and `stderr` falls back to the record value `""`. All text is ASCII, so `surrogateescape` has no effect.
- Line 97: the vector passes only if `observed is False`. An exception leaves `observed=None`, which also counts as a fail, so a crash cannot pass this vector.

## 3. Is want=False correct? Predicate trace in the candidate (`run-acceptance.py` at `4f83fd2`)

| Gate | Source | Value for this vector |
|---|---|---|
| summary scan | L118 `SUMMARY_RE=^(?:SUMMARY\|SELFTEST)(?:\t\| ).*$`; L395 | `["SUMMARY total=4 failed=0 base_discriminating=2", "SUMMARY invalid synthetic summary"]` (the space after `SUMMARY` matches) |
| failures | L356–359, L396 | `[]`: no line starts with `FAIL\t` or `CASE\tFAIL\t`, and no line has `FAIL` as its third field |
| rc/failures | L410 | `True` |
| summary equality | L415–416 `summary_lines == [expected]` | **False** (2 elements vs 1) |
| auxiliary | L432–436 | `[] == []`, True; `summary_match` stays False |
| baseline count | L440 | not applicable (step has no `baseline_mismatch_count`) |
| pass lines | L446–450 | 4 lines match `^CASE\tpass\tchanged/` (`wrap-unmarked`, `wrap-marked`, `wrap-complete`, `wrap-bullet-wrapped`); the appended line does not match, so True |
| stderr (new in R22) | L463 `and not stderr` | `""`, so the guard is not engaged |
| result | L463, L537 | `matched=False` |

The only reason this vector is rejected is the summary-list equality at line 416. That is the correct literal expectation: the contract requires exactly one summary line, equal to the expected text, and a trailing invalid `SUMMARY` line is an extra summary.

**Base comparison.** `git show 41553adb:census/round-21/run-acceptance.py` (sha256 `11418399…aa2b`) contains the same line 118 regex, the same `failure_lines` (lines 330–333), and the same line 373 `summary_lines == ([expected] if expected else [])`. Its line 417 is `matched = matched and summary_match and pass_match`, without the stderr guard. The receipt runner `ff425ab` (sha256 `6a395c13…a560`, equal to the receipt's recorded `census/round-21/run-acceptance.py` digest) has the same summary path. So base and candidate both give False.

Across `41553adb`→`4f83fd2`, the diff on the summary path contains only the stderr guard at line 463 and the `ValueError` guard at lines 428–431, which applies only to the regex branch. Neither affects this vector.

## 4. Paired positive: positive/r19-carry-wrap (want=True)

This vector uses the unmodified record (rc 0, stderr `""`):

- `summary_lines == [expected]`, True
- pass count 4 == 4
- no failures, auxiliary `[]`
- the new line 463 `not stderr` is True

So `matched=True` in both base and candidate. This agrees with the receipt's recorded `matched:true` and `matched_counts`. The stderr guard does no harm to this positive.

## 5. Attacking the predicate for this vector: mutation drafts (drafted, not executed)

Each mutant targets line 416 of `run-acceptance.py` and touches only the string `expected_summary` branch.

| ID | Mutation at L416 | This vector | Positive | Other oracle vectors | Verdict |
|---|---|---|---|---|---|
| M-A | `summary_match = expected in summary_lines` (any-match) | observed True ≠ want False | True | — | **killed** by this vector (and by the other 10 non-empty string-summary `extra` vectors) |
| M-B | `summary_match = summary_lines[:1] == ([expected] if expected else [])` (first-line) | True ≠ False | True | — | **killed** |
| M-C | `summary_match = summary_lines[-1:] == ([expected] if expected else [])` (last-line) | False = want | True | Every `extra` vector appends at the end, so the last line is always the invalid one. `agreement-pin-check/extra`: `["SUMMARY invalid…"] != []`, False. | **SURVIVES all 214** (source trace) |
| M-D | `summary_match = set(summary_lines) == ({expected} if expected else set())` (deduplicating) | `{exp, invalid}`, False | True | No vector repeats the expected summary line | **SURVIVES all 214** (source trace) |
| M-E | L463 drop `summary_match` from the conjunction | True ≠ False | True | — | **killed** |

How I established the survival of M-C and M-D: I enumerated every oracle case whose step kind is summary and whose stdout is altered. That gives the 12 `summary-control/extra` vectors, all `append:'SUMMARY invalid synthetic summary\n'`, plus `summary/r20-input-binding/oversized-count`, which takes the regex branch (lines 418–431) and so is unaffected by M-C or M-D. No vector prepends, interleaves or duplicates a summary line.

**Concrete inputs that the candidate rejects correctly but the oracle never feeds:**

- `record.stdout` for r19-carry-wrap with `SUMMARY invalid synthetic summary\n` **prepended**. Candidate: False. M-C: True.
- `record.stdout + "SUMMARY total=4 failed=0 base_discriminating=2\n"`, a **duplicated expected summary**. Candidate and base: False. M-D: True.

Proposed literal additions, which would kill the survivors: `summary/r19-carry-wrap/prepend` (want False) and `summary/r19-carry-wrap/duplicate` (want False). Both expectations match the existing base and candidate semantics at line 416, so they would not change any decision. This is a coverage recommendation only; I did not edit the oracle.

## 6. Other observations (outside this vector, flagged, not claimed)

- **Inconsistent line splitting.** `summary_lines` and `failure_lines` use `str.splitlines()` (lines 395 and 357), which also splits on `\r`, `\x0b`, `\x0c`, `\x1c`–`\x1e`, `\x85`, `\u2028` and `\u2029`. `pass_pattern` uses `re.findall(..., re.MULTILINE)` (line 447), where `^` anchors only after `\n`. The two counters can therefore disagree on producer bytes that contain these separators. No oracle vector exercises this, and it is unchanged from base. [INFERENCE: no current producer emits such bytes.]
- **Undetected summary spellings.** `SUMMARY_RE` requires `SUMMARY`/`SELFTEST` at the start of the line, followed by a tab or space. Indented or punctuated variants (` SUMMARY …`, `SUMMARY:…`) are not counted as extra summaries. This is unchanged from base, and the lessons file lists arbitrary marker semantics as out of scope.

## Remaining unknowns

- I made no runtime observation. That the candidate and base actually return False and True as traced is left to L1's 214-decision run.
- I did not attempt to decide whether the C1 claim needs this vector to discriminate. By construction it is a no-harm control, and the lessons file (line 7) describes the 18 positives and the extra-field control as "remain valid".
