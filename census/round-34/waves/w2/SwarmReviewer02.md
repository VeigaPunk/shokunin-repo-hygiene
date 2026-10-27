## Status
W1's proposed G11 restatement is **not valid under the frozen cause rule**. The G11 base mismatch is reproduced by the committed do-nothing receipt; the proposed correction is contradicted by W1's own independent parent reading in its mismatch-classification report. I did not execute a new fixture/counter run.

## Evidence
- Frozen row: `census/round-34/c1-items.tsv:27` pins exit 0 and `SUMMARY total=36 pass=36 fail=0` for `python3 tests/fixtures/r20-input-binding.py`.
- Frozen cause rule: `census/round-34/preregistration.txt:48-53` requires a value-drift cause to be full-40, ancestor of `--list-rev`, executed, with original holding at cause parent and failing at cause. Q76 prior correction rule is at lines 55-57.
- Committed do-nothing receipt `.../w1/deliver-c1-do-nothing-check.txt:16` records G11 MISMATCH at base: `SUMMARY total=45 pass=45 fail=0 ...` (rc=0); lines 2-3 identify base/list revision and counter digest.
- W1's proposed restatement in `.../w1/deliver-c1-G11.md` cites cause `4f30f23e26bff29dfc18807298300402bc148cae` and says its parent is `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`.
- Crucially, W1's `.../w1/deliver-c1-mismatch-classification.md:82-88` records direct fixture readings: at that parent output is `SUMMARY total=36 pass=32 fail=4 ...` with rc 1; at cause it is `SUMMARY total=45 pass=45 fail=0 ...` with rc 0. Thus the frozen original predicate and exit are false at the parent as well as changing at the cause. This fails the required True/False value-drift transition.
- No pre-existing G11 binding is shown by W1's base SCORECARD grep in `.../w1/deliver-c1-G11.md` (the four reported counts are zero); no Q76 alternative is evidenced.

## Findings
**Actionable — W1's G11 restatement claim is contradicted by its own evidence.** The 36-case parent result is not a passing 36/36 result: it is 36 total, 32 pass, 4 fail, rc 1. Therefore `same` argv cannot honestly restate the frozen row using `SUMMARY total=45 pass=45 fail=0...` with that cause: the original does not hold at cause parent, as expressly required by preregistration lines 48-53. This is not a benign line-number discrepancy (W1 notes the actual fixture row is line 235 rather than frozen `SKILL.md:234`); the same-argv branch avoids inspecting that line, but does not waive cause execution/transition requirements.

The purported successful throwaway validation in `deliver-c1-G11.md` (ITEM AGREE / `restated=1`) is insufficient and conflicts with the counter's required transition: its displayed result proves only acceptance of the appended row, not that the recorded parent run satisfies the frozen original. On available evidence this looks like a counter/measurement inconsistency or invalid acceptance, not an honest route. I did not reproduce the scratch acceptance independently; this is a source/evidence-level finding, not a claim of new execution.

## Attack log
1. Read frozen preregistration, G11 census row, G11 W1 deliverable, do-nothing receipt, and W1 mismatch-classification evidence.
2. Compared proposed cause/parent criteria and same-argv restatement against the recorded parent output. No separate frozen clause provides an escape; Q76 is inapplicable absent a prior binding row.
3. Did not run a new counter, fixture, or scratch probe; therefore no new execution output is claimed.

## Deliveries
Scoped report: `.ufo/waves/round-34/w2/AttackG11.md` (also copied to `SwarmReviewer02.md`).