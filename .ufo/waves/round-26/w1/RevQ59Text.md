# RevQ59Text — review of the Q59 axis-of-surface criterion draft

Reviewer: `RevQ59Text`. Reviewed artifact: `.ufo/waves/round-26/w1/axis-check-docs.md` (ScribeAxisDocs deliverable, unlanded), Q59 row at :30. Lane HEAD at close: `d6fe8a1125a9723e7593df7b8b90ee6c05cdf9ff`. Scratch: `/var/tmp/souji-r26-RevQ59Text` (removed).

## Status

STATUS: PARTIAL — the Q59 draft correctly captures the declared-axis-vs-surface-class rule, cites the right lesson intents (r25 C2 axis misattribution + this round's R26-M1), avoids overreach, and does not contradict Q58; but it is not landable as-is: the check column's discriminator conjunct has no executable carrier in committed bytes, and the motivating-evidence anchor `corpus/lessons/round-26.md R26-M1` does not exist yet in the committed lesson file.

## Evidence

All commands `python3 -B`; copies of lane files run in `/var/tmp/souji-r26-RevQ59Text` only (lane writes: none, this report only). Lane HEAD `d6fe8a1`; landed tool blob `14bc9632e88ef58f18108011f6645bd970cd825d0ffc1664369dc60b0d579332`, landed fixture blob `2ffc18289fc82b9075ad3580cb9bec6a80384061c7d294b5aa17dbf9ca93c8da`, w1 12-case fixture `220eed2e15f3154d8a6909cac57f325862d0d472a4e3bab6d88ce48776e1d88d` (git show HEAD:... matches working bytes for all three).

- E1 — tool on the round's own prereg (Q59 check-cell first conjunct, C3 K1 shape): `python3 -B tool/souji-axis-check.py --prereg prereg.txt --scorecard scorecard.md` → `claims=3 flags=0`, rc 0. Executable.
- E2 — C3 fixture command, LANDED fixture: `python3 -B tests/fixtures/r26-axis-check.py` → `cases=11 pass=11`, rc 0, no `control=`. line in normal mode; `--stub` arm → `cases=11 pass=4` / `control=FALSE-GREEN-REJECTED`, rc 1. The frozen K2 literal `cases=12 pass=12 control=FALSE-GREEN-REJECTED` is not producible by committed bytes (matches divergence 1 and ExecAxisSelftest F6).
- E3 — `--tool PATH` is ignored by the landed fixture: `tests/fixtures/r26-axis-check.py:204` `tool = TOOL`; `TOOL` is derived from the fixture's own path (:41-42), `--tool` never parsed. Confirmatory artifact: running the copied fixture with `--tool tool/souji-axis-check.py` (tool elsewhere) made every case exit 2 (`cases=11 pass=1`); relocating the tool to `tools/souji-axis-check.py` restored 11/11 — proof the arg played no role.
- E4 — C3 fixture command against the w1 12-case fixture (ExecAxisFixture deliverable, unlanded): `python3 -B fixture/r26-axis-check-12case.py --tool tool/souji-axis-check.py` → `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, rc 0. Case 1 is `r25-c2-replica-fixture-expansion-on-operability`; expectation `rc=1 flags=2 rules=R2,R3` (the replica fires R2 and R3).
- E5 — motivating evidence: read `corpus/lessons/round-25.md:10` this run: "W2 review shows the change is coverage of edge classes, not a change to runnable operability" (17 words, no `|`); verdict cell "**unprovable on the declared axis**". Correct r25 locus (R25-M1 is number-drift, R25-M2 is duplicate dispatch — neither is the axis misattribution).
- E6 — motivating evidence: `corpus/lessons/round-26.md` (committed `ea0bbe6`, in current HEAD lineage) has sections Gate / Findings / Residuals / Receipts only — no `## Mistakes`, no R26-M1. Repo-wide grep for `R26-M1` hits only wave specs (`make-spec.py:168`, `w1-dispatch.json`, `w1-spec.json`, `w1-validate.out`) and wave reports (ScribeAxisDocs.md:135, c1-append-note.md:132), never the lesson file.
- E7 — Q58 read: `corpus/QUALITY.md:142` — "A preregistered numeric target is derived at the named base revision, not copied from a prior round's different base... a mismatch is a preregistration defect, not license to weaken the counter after scoring." Distinct subject (numeric targets) with the same pre-data defect posture.

## Findings

1. **Check column, second conjunct, has no executable carrier (medium).** The Q59 check cell says "the r25-C2 replica (fixture-expansion declared on operability) exits 1 with an R2 FLAG line". No command in the cell constructs or points at such a replica; the only committed executable that carries the replica is the fixture's case 1, and the committed fixture does not contain it (E2: 11 cases, case 1 = R1 axis-not-owned per unit docstring :16; E3: `--tool` ignored). The 12-case fixture that does carry it is unlanded (E4). As written, a grader cannot execute the second conjunct against committed bytes. Fix: name the C3 K2 fixture command as the carrier (its case 1 is the discriminator) and sequence the row with the 12-case fixture landing; or specify a synthetic replica prereg + tool invocation.
2. **Dangling motivating-evidence anchor `round-26.md R26-M1` (medium).** The row's motivating evidence cites "corpus/lessons/round-26.md R26-M1"; the committed lesson file has no such row (E6). The draft's own landing precondition 2 only requires the file to exist (LG-DANGLING-PTR checks path presence), so the missing anchor would pass that gate silently. Must land the R26-M1 mistakes row (ScribeLessonR26 deliverable / L1) with or before the Q59 row, and the citation should pin the final landed row id (c1-append-note.md:132 notes a second r26 mistake row id is pending; if the mined-mistake numbering shifts, the citation must follow).
3. **Under-specification of the discriminator expectation (low).** The 12-case fixture's case 1 expects exactly `{R2,R3}` (E4: `flags=2 rules=R2,R3`) — the replica also trips R3 because the synthetic axes table has no calibration-declared claim. The cell's wording ("exits 1 with an R2 FLAG line") is true but partial; a reader could implement an R2-only oracle and fail the suite. Suggest "exits 1 with an R2 FLAG line (fixture case 1 = R2+R3)" or defer entirely to the named fixture.
4. **Residual, not a draft defect (info).** Neutral surface classes (`receipt-binding`, `measurement`) are outside the Q59 taxonomy and bypass R2 (`tools/souji-axis-check.py:41`; ExecAxisSelftest A1). Q59 faithfully mirrors frozen R2, so this is an instrument gap, not a criterion overreach; the draft correctly lists exactly the five frozen classes.

## Positive findings

- Capture: the criterion text ("every frozen claim declares a surface class, and the class fixes the axis it may be declared on — `bookkeeping-file` on calibration, `knowledge-entry` and `registry-append` on coverage, `fixture-expansion` on coverage, `instrument-acquisition` on operability") matches the frozen R2 map verbatim (`preregistration.txt`, C3 R2). Correct.
- Lessons: right intents on both sides — r25 C2 claim row (E5) for the historical shape; R26-M1 for this round's mined mistake (preregistration.txt:227 "The mined mistake: R26-M1 = the round-25 C2 axis misattribution"). The two citations point at the same incident captured twice, which is what the wave spec asked for (make-spec.py:167-168).
- Overreach: none. The cell explicitly excludes R1/R3/R4 ("separate predicates of the same instrument and are not claimed by Q59"); the criterion checks declared-vs-surface class only, never semantic correctness.
- Q58: no contradiction. Q59's "Extends Q58's re-derivation rule to axis attribution" is accurate framing: Q58 is numeric targets re-derived at base; Q59 is axis/surface binding pre-freeze; both share the "defect before after-data, never a licence to weaken/relabel after scoring" posture (E7).
- Table shape: header `| id | criterion | applies to | check | motivating evidence |` mirrors the Round 25 block (`QUALITY.md:139`); no literal or escaped `|` inside cells.

## Attack log

Not an attack item. No predicate, target or case set is challenged; findings 1-3 are landing-sequencing/carrier fixes within the frozen contract.

## Residuals for the integrator

- Land the 12-case fixture (`w1/r26-axis-check.py` → `tests/fixtures/r26-axis-check.py`, overwriting the 11-case committed fixture) before this row's check cell is executable; keep the frozen K2 literal in sync.
- Land the R26-M1 mistakes row in `corpus/lessons/round-26.md` before or with the Q59 row.
- Neutral-surface bypass (finding 4) stays an instrument-level decision (ExecAxisSelftest A1), out of Q59's row scope.
