# Round 33 — `## Mistakes` rows (draft, paste-ready)

Read at base `6017a482e7068d5afb7617640198fbb0fe743357` on 2026-10-26 by SwarmScribe42 (r33 w1).
Two rows: **M1** (this round's data, five C1 items) and **M2** (one class mined from the r30-r32 closures).
Every quoted output line below is verbatim from committed bytes opened this run (`census/round-33/records/feasibility.txt`,
`census/round-30/records/c1-before.txt`, `census/round-32/records/final-tip-measure.txt`); cell text carries no pipe characters.

## Rows (paste verbatim into `corpus/lessons/round-33.md` `## Mistakes`)

| class | evidence pointer | captured-by | fix |
|---|---|---|---|
| capability-currency | five capability cells state a count their named command does not print at base `6017a48`: `SCORECARD.md:155` states `5/5`, the row's own argv prints `selftest=PASS ids=7/7`; `:158` states `18/18`, prints `SELFTEST pass=65 fail=0`; `:173` states `9/9`, prints `selftest=15/15`; `:174` states `cases=8 pass=8`, prints `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`; `:175` carries a bare argv that exits 2 with `r24-coverage-agreement.py: error: the following arguments are required: --tool`. Readings: `census/round-33/records/feasibility.txt:37,38,47,48,49` (items K04 K05 K16 K17 K18), first committed at r30 in `census/round-30/records/c1-before.txt:4,5,14,15,16`. Stale from, by the row's own tool or fixture log: `:155` r25 `728b2ce` (the fixture's documented final line moved 5/5 to 7/7); `:158` r17 `ddb7347`, where the K05 restatement seat executed the break at 18 to 28 (`deliver-c1-K05.md`) and the gate's `check(` case count in the diff grows 14 to 23; `:173` r23 `1dd8b1e` (9 to 11 cases, 15 by `728b2ce`); `:174` at write r26 `07f83e6`, which copied `cases=8` after `679e2d0` (r25) had extended the fixture to 12; `:175` at write r26 `07f83e6`, whose bare argv had failed since `1efe406` (r24) made `--tool` required. Stale rounds at the r32 closure: 8, 16, 10, 7, 7 — 48 row-rounds | Q23 (r15) should have caught each one before r30: capability wording must match the exercised boundary, and its own test is to inspect the cited observation's output; no instrument did. Q63 (r30) then did catch all five — `census/round-30/records/c1-before.txt:4,5,14,15,16` read MISMATCH — but Q63's repair is an appended `R30-CORRECTION` line with "the cell stays" (`SCORECARD.md:325-327,333-335`), and Q67 (r31) restated them as `superseded` (`census/round-31/records/c1-after-a4.txt:6,7,33,34,36`, section text "the cell text stays as written"); no criterion after r31 re-read the cells | the C1 currency counter as a standing gate at every landing commit and at the tip: `python3 -B census/round-33/c1-counter.py --root <lane> --rev <full40> --list-rev <prereg-commit> --scratch <dir>`, target `mismatches=0`. Shown able to fail: the do-nothing base control prints `SUMMARY items=24 agree=19 mismatches=5 restated=0` (`census/round-33/records/feasibility.txt:139`), and a junk restatement (a true output line under a non-causal commit) is refused as BAD-CAUSE |
| unrun-reading | the r32 closure report says the landing gate reads `findings=0` for round 32 at the tip, while the only committed run is at `4ea897f` and reads (fields tab-separated, shown collapsed) `SUMMARY findings=2 checked_reg=74 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=18 status_lines=80 carry_heading=1 checked_reports=103` with two `LG-DANGLING-PTR` findings pointing at the receipt itself (`census/round-32/records/final-tip-measure.txt:164-166`); re-derived and routed at `corpus/lessons/round-32-verifier-spotcheck.md:34` (D2) and `:135` item 3. Not mined in the r30-r32 `## Mistakes` tables, whose classes are landing, reference-drift, stale-premise, vacuous, scope, record, instrument, contract, disposition, enumeration, anchor-selection, harm, misroot and flaky anchor; the nearest precedent is the r15 rejection for unrun checks (`corpus/lessons/round-15-verifier-spotcheck.md:7`) | Q24 (r15): unrun checks never pass, and a report must carry the actual named command, output and revision it claims; Q55 (r23) also makes a count quoted in a lane record a record defect unless a receipt binds the revision and the sha256 of the bytes. Neither was applied to a closure's own gate sentence, so `findings=0` stood unbacked | a closure-receipt counter: for every `<field>=<n>` gate SUMMARY literal quoted in the round's lesson and closure text, require a committed run capture whose bytes contain that exact line at the cited revision, exiting 1 with the claim's file:line and the nearest committed reading otherwise. Can fail: run on the r32 closure bytes it must refuse (`findings=0`, no committed tip run, only `findings=2` at `4ea897f`); run on a tree that commits the tip run it passes. Design only here — this seat did not execute it |

## Per-item detail (not part of the paste; one line per stale cell)

| item | row | stated | observed at base | stale from | rounds stale | cause |
|---|---|---|---|---|---|---|
| K04 | `SCORECARD.md:155` | `5/5` | `selftest=PASS ids=7/7` | r25 | 8 (r25-r32) | `728b2ce` (fixture probe cases 5 to 7) |
| K05 | `SCORECARD.md:158` | `18/18` | `SELFTEST pass=65 fail=0` | r17 | 16 (r17-r32) | `ddb7347` (gate selftest 18 to 28) |
| K16 | `SCORECARD.md:173` | `9/9` | `selftest=15/15` | r23 | 10 (r23-r32) | `1dd8b1e` first growth 9 to 11; 15 by `728b2ce` |
| K17 | `SCORECARD.md:174` | `cases=8 pass=8` | `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` | r26 at write | 7 (r26-r32) | `679e2d0` (r25) extended 8 to 12; the r26 row copied 8 |
| K18 | `SCORECARD.md:175` | `9/9` | exit 2, `r24-coverage-agreement.py: error: the following arguments are required: --tool` | r26 at write | 7 (r26-r32) | argv correction: `--tool` required since `1efe406` (r24) |

Counting convention: a cell is stale from the round whose closure first read it wrong, through the r32 closure
(r33 is the round that restates). Rows `:174` and `:175` did not exist before `07f83e6` (r26); the cause of
`:174`'s false literal is the r25 fixture change it was copied from.

## Paste notes

- Insert both rows under `## Mistakes` in `corpus/lessons/round-33.md`, before `## Receipts`; keep M1 first.
- M1 quotes the counter's whitespace-collapsed line (`SELFTEST pass=65 fail=0`); the raw bytes are tab-separated,
  and the counter collapses both sides, so either spelling judges alike (same reading as `deliver-c1-K05.md`).
- If the L1 prefers to restate K17 as an argv correction instead of a value drift, `07f83e6` is the commit that
  wrote the row and the row's own argv already fails there; `679e2d0` is the commit that moved the fixture.
  `[INFERENCE]` both routes satisfy the counter's cause rule as written in `census/round-33/c1-counter.py`; neither
  route was executed by this seat.
- No number in either row is a promise about the C1 target: the target stays `mismatches=0` at the landing commit
  and at the tip, and only the L1's run can show it.

## How each fix can fail

- **M1** — observed, twice over: the do-nothing base control reads `mismatches=5` (`feasibility.txt:139`), and the
  r30 instrument's red-before file reads the same five MISMATCH lines (`c1-before.txt:4,5,14,15,16`). A green run
  with the five cells left alone is impossible without the appended section, and a restatement with a non-causal
  commit is refused as BAD-CAUSE (`census/round-33/records/preregistration.txt`, Controls).
- **M2** — the red arm is the r32 closure text: no committed run anywhere states `SUMMARY findings=0` for round 32
  at the tip, and the only committed reading is `findings=2` at `4ea897f` (`final-tip-measure.txt:164-166`), so the
  proposed counter refuses that claim. The green arm is any tree whose committed run contains the quoted line.
  Unexecuted by this seat; stated as a design, not as a passing check.
