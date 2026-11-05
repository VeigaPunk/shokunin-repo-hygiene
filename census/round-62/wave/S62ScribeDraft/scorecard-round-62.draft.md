Append to `SCORECARD.md` under a new heading after the `### Planned (r62)` block (append-only).

### Round 62 measurements (2026-11-05, Linux; base `16fa821fdce00e709d6895ccfc7aaffa465af195`; freeze `{{FREEZE}}`; control receipts `{{CONTROL}}`; predicate `census/round-62/preregistration.txt`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 index-flag concealment refused before a clean-tree receipt (`RECEIPT-INDEX-FLAG-CONCEALED`) | calibration 7, numeric delta 0 (no reproducible 0–10 mapping) | do-nothing (base bytes in the candidate slot): `new_forgeries={{DO_NOTHING_FORGERIES}} EXIT={{DO_NOTHING_EXIT}}` on the seven-row matrix (frozen expectation 3 and EXIT 1; measured value pasted by the L1) | `new_forgeries={{AFTER_FORGERIES}} new_honest={{AFTER_HONEST}} class_mismatches={{CLASS_MISMATCHES}} row_G={{ROW_G}} EXIT={{AFTER_EXIT}}`; r60 fixture `{{R60_FIXTURE_TALLY}}`; tool sha256 `{{TOOL_SHA}}` | `{{COUNTER_COMMAND}}` | `{{COMMIT_MEASURED}}` |

Harm check: the lane index at the base carries 17350 entries, all `H` (L1 base observation), so no honest run on today's lane is refused by the new rule. The after-measurement on the lane: `{{LANE_INDEX_CHECK}}`. Writer selftest: `{{SELFTEST_TALLY}}`. Harm over the honest rows: `{{HARM_CHECK}}`.

The numeric axis scores are unchanged (calibration 7). Named limits and routed items are in `corpus/lessons/round-62.md`.

### Planned (r63)

- MACHINE BLOCK (routed r61 defect 2; axis-check Q59): pending the operator; the L0 question `souji | round-62 | ...` asks for confirmation that `souji-axis-check.py` runs on the preregistrations. Not implemented in round 62.
- Numeric axis mapping (routed r61 defect 5): pending the operator; an L0 question asks for the reproducible 0–10 mapping or confirmation that the calibration cell stays unchanged.
- F3 matrix row (delete-and-re-add at freeze, `corpus/lessons/round-61.md` named limit): not in round 62; planned as a matrix row if the operator keeps the claim.
- Historical records (rounds 41–55 freeze records and the r60 record): carried, append-only, not rewritten.
