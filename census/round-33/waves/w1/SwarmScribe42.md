# SwarmScribe42 — r33 w1, `## Mistakes` rows (M1, M2)

## Status

STATUS: PASS — M1 (five C1 capability cells: stale-from round, rounds stale, captured-by, fix) and M2 (one class mined from the r30-r32 closures) are drafted as paste-ready `## Mistakes` rows in the named delivery file. Everything below comes from read-only `git -C <lane> log/show/blame/cat-file/merge-base` and file reads on the lane; no clone, work tree or scratch dir was created, no counter was run, no tool was installed, and nothing in the lane (index, jj, refs) or in the fleet was mutated.

## Evidence

| command | output excerpt | revision |
|---|---|---|
| `sed -n '1,200p' census/round-33/preregistration.txt` | "Allowed self-assessment change: appended rows in `### Round 33 capability currency`"; target `mismatches=0` | preregistration `2d9bca55a9f042a2c9ed60a797a8069e74c41f46` |
| `cat census/round-33/c1-items.tsv` | K04 line 155, K05 line 158, K16 line 173, K17 line 174, K18 line 175 | frozen list |
| `git show 6017a48:SCORECARD.md` rows 155,158,173,174,175 | stated literals `5/5`, `18/18`, `9/9`, `cases=8 pass=8`, bare `python3 tests/fixtures/r24-coverage-agreement.py` | base `6017a482…` |
| `grep -n` over `census/round-33/records/feasibility.txt` | `ITEM K04 MISMATCH … last=selftest=PASS ids=7/7` (:37), `K05 … last=SELFTEST pass=65 fail=0` (:38), `K16 … last=selftest=15/15` (:47), `K17 … last=cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` (:48), `K18 rc=2 … required: --tool` (:49), `SUMMARY items=24 agree=19 mismatches=5 restated=0` (:139) | r33 feasibility, base |
| `grep -n` over `census/round-30/records/c1-before.txt` | `ROW R04 SCORECARD.md:155 stated=5/5 … MISMATCH kind=value` (:4), `R05 :158` (:5), `R14 :173` (:14), `R15 :174` (:15), `R16 :175` (:16) | r30, base `9420341` |
| `git blame -s -L 155,175 6017a48 -- SCORECARD.md` | `:155` `23014d4` (r13), `:158` `163158a` (r16), `:173` `4765250` (r23), `:174` and `:175` `07f83e6` (r26) | base |
| `git log --format='%h %ad %s' -- <row tool/fixture>` | `r13-repo-structure.sh`: 6ed10a7, 728b2ce, 98e5203; `souji-landing-gate.py`: … ddb7347 (r17) …; `r23-record-agreement.py`: 4765250, 1dd8b1e, c872eec, 728b2ce; `r24-size-census.py`: 1efe406, 679e2d0; `r24-coverage-agreement.py`: 1efe406 | lane history |
| `git show 728b2ce -- tests/fixtures/r13-repo-structure.sh` | removes `selftest=PASS ids=5/5 (--probe mode)`, adds `ids=7/7`; case list grows by linked-common-dir and colocated-vs-plain | r25 |
| `git show <rev>:tests/fixtures/r23-record-agreement.py` + case-list count | CASES 9 at 4765250, 11 at 1dd8b1e, 12 at c872eec, 15 at 728b2ce | r23-r25 |
| `git show 07f83e6:tests/fixtures/r24-size-census.py` | `CASES` list has 12 entries (`clean` … `partialClone-only`) → `cases=12`; the r26 row states 8 | r26 |
| `git show 1efe406:tests/fixtures/r24-coverage-agreement.py` | `ap.add_argument("--tool", required=True)` at :331 | r24 |
| `git show <rev>:tools/souji-landing-gate.py` + `grep -c '^ *check("'` | 14 at a6ec781 (r16), 23 at ddb7347 (r17) | r16/r17 |
| `git merge-base --is-ancestor` | 4765250 ⊂ 1dd8b1e ⊂ c872eec ⊂ 728b2ce; 679e2d0 ⊂ 07f83e6 — all yes | lane history |
| `grep -n 'R30-CORRECTION' SCORECARD.md` | 13 lines, `:325` `:155 R04 … observed=selftest=PASS ids=7/7`, `:326` `:158 R05`, `:333` `:173 R14`, `:334` `:174 R15`, `:335` `:175 R16 cmd=… --tool …` | base |
| `grep` over `census/round-31/records/c1-after-a4.txt` | `ITEM L05 SCORECARD.md:155 literal=ids=7/7 superseded binding=run MATCH` (:6), L06 (:7), L32 (:33), L33 (:34), L35 (:36) | r31 |
| `sed -n '128,140p' corpus/lessons/round-32-verifier-spotcheck.md`; `grep` | D2 at :34 — "No committed tip run states `findings=0`"; routed item 3 at :135 — "Do not report `findings=0` without a run"; `census/round-32/records/final-tip-measure.txt:164-166` reads `SUMMARY findings=2 …`, `exit=1` at `4ea897f` | r32 closure |
| `awk '/^## Mistakes/,/^## [^M]/'` over `corpus/lessons/round-3[0-2].md` | classes: landing, reference-drift, stale-premise, vacuous, scope / landing, record, instrument, contract, disposition / contract, enumeration, anchor-selection, instrument, harm, misroot, flaky anchor — no unrun-reading class | r30-r32 |

Quote fidelity (`grep -Fc`, each 1): `the cell stays and an` (QUALITY.md, Q63), `unrun checks never pass` (Q24), `A quoted count without such a binding is a record defect, not a measurement` (Q55), `the cell text stays as written` (SCORECARD.md:361 section), `an unrun check has not passed` (round-15-verifier-spotcheck.md:7).

## Findings

1. **The five r33 mismatches are five cells the lane already detected and already restated beside themselves, not a blind spot.** r30 enumerated the same rows and read MISMATCH on all five (`census/round-30/records/c1-before.txt:4,5,14,15,16`); its repair was 13 appended `R30-CORRECTION` lines (`SCORECARD.md:324-336`), under Q63's rule "the cell stays and an `R30-CORRECTION SCORECARD.md:<line> <row-id> [cmd=<argv>] rc=<n> observed=<line>` line follows the base bytes". r31 then superseded the same literals as `superseded … MATCH` with executed runs (`census/round-31/records/c1-after-a4.txt:6,7,33,34,36`), the section stating "the cell text stays as written" (`SCORECARD.md:361`). Consequence for the landing prose: r33's `mismatches=5` measures **cell text** that Q63 and Q67 both deliberately leave unchanged; the honest framing is "already restated beside the cell at r30/r31, now restated in the r33 section under the stricter executed-cause rule", not "the lane never noticed". Not raised as an ATTACK: the frozen target stays reachable and the new rule is stricter-only (each restatement's cause is executed), and I propose no change to any frozen predicate, item or leg.

2. **M1 attribution, per cell** (paste detail in the delivery file): `:155` stale from r25 (`728b2ce`, fixture probe cases 5→7), 8 rounds; `:158` stale from r17 (`ddb7347`, where the gate selftest breaks — the K05 restatement seat executed 18→28 at that commit in `.ufo/waves/round-33/w1/deliver-c1-K05.md`, and the gate's `check(` case count in the diff grows 14→23), 16 rounds; `:173` stale from r23 (`1dd8b1e` 9→11 cases, 15 by `728b2ce`), 10 rounds; `:174` shipped stale at write in r26 (`07f83e6` copied `cases=8` after `679e2d0`, r25, had extended the fixture to 12), 7 rounds; `:175` shipped broken at write in r26 (the fixture has needed `--tool` since `1efe406`, r24), 7 rounds. Total 48 row-rounds. Counting convention: stale from the round whose closure first read it wrong through the r32 closure; r33 is the correcting round.

3. **`:174` and `:175` are born-stale rows, not value drift into an existing row.** Both entered `SCORECARD.md` at `07f83e6` ("round-26 C1 fix: append the two r24 capability rows … wave ExecC1Surgery found omission"). For the counter this matters: a value-drift restatement for K17 must name a cause that touches `tests/fixtures/r24-size-census.py` (the natural one is `679e2d0`, r25, which is an ancestor of the list-rev and moves 8 cases to 12), while an argv-correction restatement must name `07f83e6`. `[INFERENCE]` — read from the counter docstring and the item row, not executed by this seat; the sibling C1 seats own those restatements.

4. **K18's argv never worked**: `tests/fixtures/r24-coverage-agreement.py:331` at `1efe406` already reads `ap.add_argument("--tool", required=True)`, and the row's bare invocation exits 2 with `r24-coverage-agreement.py: error: the following arguments are required: --tool`. Any framing of `:175` as drift is wrong; it is an argv correction from birth.

5. **M2 class confirmed un-mined and grounded**: `unrun-reading` (a closure reporting a gate verdict it did not run at the claimed revision). Evidence `corpus/lessons/round-32-verifier-spotcheck.md:34` (D2) plus the committed reading `census/round-32/records/final-tip-measure.txt:164-166` (`findings=2` at `4ea897f`, both `LG-DANGLING-PTR` to the receipt itself); routed at `:135` item 3. Absent from the r30-r32 `## Mistakes` tables (the class list is the last row of the Evidence table). Captured-by is Q24 (r15) "unrun checks never pass", reinforced by Q55's count-receipt rule; the class previously sank the r15 closure (`round-15-verifier-spotcheck.md:7`, "an unrun check has not passed"), so this is a recurrence of a criterion the lane has held since r15.

6. **Write-scope self-correction (disclosed).** This seat's first `write` used a lane-relative path and, because seat tools start at the fleet root, created `/home/vgpnk/Projects/shokunin/.ufo/waves/round-33/w1/deliver-mistakes.md` plus its `w1/` directory (the parent `round-33/` and its `falsify/` child pre-existed, mtime 2026-10-25 15:08). Corrected in the same minute: the file was `mv`-ed to `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-33/w1/deliver-mistakes.md` and the empty `w1/` removed; `ls` of the fleet `round-33/` now shows only the pre-existing `falsify/`. No fleet file content existed before or after; only that directory's mtime moved. This is the r32 "misroot" shape (`corpus/lessons/round-32.md` `## Mistakes`), reproduced and repaired inside one seat.

7. **Table hygiene**: the two paste rows each carry exactly five pipe characters (four columns), verified by `awk`; no cell contains a pipe, so the rows drop into `corpus/lessons/round-33.md` `## Mistakes` without escaping.

## Deliveries

- `.ufo/waves/round-33/w1/deliver-mistakes.md` — M1 and M2 rows, per-item detail table, paste notes, and a "how each fix can fail" paragraph.
- `.ufo/waves/round-33/w1/SwarmScribe42.md` — this report.

No scratch tree was created and none is left behind; no tool was installed or upgraded.
