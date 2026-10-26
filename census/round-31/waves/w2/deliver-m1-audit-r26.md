# M1 carry audit — corpus/lessons/round-26.md (round 31, wave 2, seat SwarmCritic24)

Scope: the 26 bullets appended by `c6108301cbf0ca0ad086ff0ece6b76adad6b74b6` under
`## Seat-reported failures` at the end of `corpus/lessons/round-26.md` (lines 98-137 at
that commit and at tip `2c16d018e40db7c23420a2c3bb546b52957bcc25`; the file and both
report trees are byte-unchanged between the two commits: `git diff --stat c6108301 tip
-- corpus/lessons/round-26.md .ufo/waves/round-26 census/round-26/waves` is empty).

All report bytes were read through `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show
<rev>:<path>` at tip; all lane instruments were run read-only at tip with `python3 -B`.

## Verdict tally

| verdict | count |
|---|---|
| OK | 16 |
| SHOULD-BE-RESOLVED | 3 |
| WRONG-RESOLVED | 7 |
| MISQUOTED | 0 |

## Quote exactness (26/26)

Every cited `path:line` resolves to a line that begins `STATUS:` in the cited file, and every
quoted paragraph equals the report's STATUS paragraph exactly after (a) joining the wrapped
lines with single spaces and (b) deleting backticks and asterisks. Two quotes had inline
emphasis stripped (`*direction*`, `*payload*`); no words were dropped or added. No quote
contains a carry-side elision marker (the one `…` in `ScribeLogR26.md:8` is the seat's own).

## Per-entry ledger

`R` = report path as cited (relative to lane root). `disp` = bullet disposition. Verdict and
evidence per entry; correction names the commit that actually delivered the fix.

| # | R:line | disp | verdict | evidence |
|---|---|---|---|---|
| 1 | .ufo/.../w1/CritAmendNeed.md:5 | open | OK | finding (b) still true at tip: `census/round-26/c2-counter.sh` is 10 lines with no base revision (`grep -n base` = no match), so `rows 127 -> 132` is still not an append-only predicate. |
| 2 | .ufo/.../w1/CritCoverageCredit.md:5 | open | OK | K2 red and the two absent receipts were fixed (see #15), but `python3 -B tools/souji-receipt-run.py verify --root . census/round-26/records/c2-before.tsv` still returns `RECEIPT-COUNTS-ABSENT` (same for c2-after), and `corpus/README.md:39` still reads `frontier, entries held` at tip, so the coverage-credit finding stands. |
| 3 | .ufo/.../w1/CritQ54Gate.md:3 | open | OK | K2 now `entries=2 ok=2 fail=0`, but Q54 is still vacuous on the admitted entries: `python3 -B tests/fixtures/r23-locator-heading.py --entries <both> --snapshot-dir census/round-26/sources` → `entries=2 locators=0 locators_bad=0`, and `tools/souji-gate-check.py:42` only string-matches `LOCATOR_RE`, it resolves nothing. |
| 4 | .ufo/.../w1/CritSourcedClaim.md:5 | open | OK | the two missing receipts now exist, but the §2b per-row lesson attestation is still absent: `grep -c 'https\?://'` over the lesson `## Gate` block (lines 9-30) = 0. |
| 5 | .ufo/.../w1/ExecC1Surgery.md:4 | resolved@07f83e6 | OK | `git show 07f83e6 -- SCORECARD.md` appends the two missing rows (`debris census (r24)`, `coverage-map agreement (r24)`) after the record-agreement row, exactly the amendment-2 item 5 omission the seat named. |
| 6 | .ufo/.../w1/LabReceiptVerify.md:5 | open | OK | reproduced at tip: c1-before, c2-before, c3-before all return `RECEIPT-COUNTS-ABSENT` (only c2-k4-base was `verify=ok` when the seat wrote; at tip c2-gate, c2-k4-after and c3-after also verify ok, but every red-before receipt is still unverified). |
| 7 | .ufo/.../w1/LabSourcesCensus.md:9 | open | OK | the ticket-level clause is permanent (the assignment's CORPUS.md lane path does not exist at any revision). The five-row fleet-registry clause was not re-derived here ([INFERENCE] — fleet registry out of seat scope). |
| 8 | .ufo/.../w1/RevC1Counter.md:2 | open | OK | `git log --oneline -- census/round-26/c1-counter.sh` shows one commit (`12fd90b`); the K1 marker-prefix-count predicate the seat attacked is unchanged at tip. |
| 9 | .ufo/.../w1/RevC3Design.md:4 | resolved@c594901 | **WRONG-RESOLVED** | c594901 fixes only findings 1 and 5 (R4 in-block scan; 12-case fixture — `python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py` → `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, rc 0). Findings 2, 3, 4, 6, 7 are live at tip (tool bytes unchanged since c594901), reproduced below. |
| 10 | .ufo/.../w1/RevEntryDrafts.md:2 | resolved@50443f5 | **WRONG-RESOLVED** | the demanded correction (Entry B must cite S132 at source-line level) is present from the entry's first commit, `0833de9` (`git log --diff-filter=A -- corpus/knowledge/git-auto-maintenance-trigger-set-r23.md` → 0833de9; its front matter already carries `source: S132 — lanes/souji/round2/evidence/r23-worktree-census.out`). 50443f5's hunk `@@ -3,11 +3,11 @@` leaves every `source:` line untouched and rewrites only `verified-at:`. Correction: `resolved@0833de9…` (or drop, since the committed entry never carried the defect). |
| 11 | .ufo/.../w1/RevQ59Text.md:7 | resolved@50443f5 | **WRONG-RESOLVED** | both missing pieces landed at `166baa1` (Q59 row with the executable carrier, `corpus/QUALITY.md:143`; R26-M1 row, `corpus/lessons/round-26.md:96`). 50443f5 does not touch `corpus/QUALITY.md` at all (`git show --stat --format='' 50443f5` — the only non-mirror paths are `corpus/SOURCES.md`, `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md`, `corpus/lessons/round-26.md`). Correction: `resolved@166baa1…`. |
| 12 | .ufo/.../w1/RevR25Residuals.md:2 | open | OK | D4 is operator-owned; nothing in the lane log claims it. |
| 13 | .ufo/.../w1/ScribeAxisDocs.md:5 | open | **SHOULD-BE-RESOLVED** | the premise ("the landed fixture cannot produce the frozen K2 literal — 11 cases, `--tool` ignored") died at c594901: fixture prints `cases=12 pass=12 control=FALSE-GREEN-REJECTED` and takes `--tool`. At tip `git grep -l 'r26-axis-check'` lists only `.ufo/waves/round-26/` paths — no `SKILL.md` row pins any r26 axis-check literal. |
| 14 | .ufo/.../w1/ScribeGateDraft.md:5 | open | **SHOULD-BE-RESOLVED** | the stated blocker ("C2's frozen K2 fails … both entries have no `## Gate` heading") was removed at `33e6807` (Gate sections; receipt `census/round-26/records/c2-gate.tsv` → `entries=2 ok=2 … fail=0`, `verify=ok`), and the lesson adopted the 12-case fixture. Its second clause (lesson Gate refusal reason vs prereg) was not re-derived ([INFERENCE]). |
| 15 | .ufo/.../w1/ScribeLessonR26.md:5 | resolved@50443f5 | **WRONG-RESOLVED** | the two missing arms were delivered earlier: `33e6807` (K2 `entries=2 ok=2 fail=0`) and `c594901` (`cases=12 pass=12`). 50443f5's own diff changes neither. Correction: `resolved@33e6807…` for the K2 arm and `resolved@c594901…` for the fixture arm (a single hash cannot cover both). |
| 16 | .ufo/.../w1/ScribeLogR26.md:8 | resolved@50443f5 | **WRONG-RESOLVED** | same two arms as #15, same earlier commits; additionally its third clause ("Wave/dead-seat totals … remain RECEIPT-PENDING") is still unmet: the lesson's headings at tip are Gate, Findings, Residuals, Receipts, Mistakes table, Seat-reported failures — there is no Wave section. |
| 17 | .ufo/.../w1/ScribeScorecardR26.md:5 | resolved@50443f5 | **WRONG-RESOLVED** | same as #15: K2 red fixed at 33e6807, 11→12 case set at c594901, neither delivered by 50443f5. |
| 18 | .ufo/.../w1/SentBounds.md:3 | open | OK | the receipt-instrumentation clause is still true at tip (c1/c2/c3-before `RECEIPT-COUNTS-ABSENT`); the C3 case-set clause was fixed at c594901. Partial resolution, core alive. |
| 19 | census/.../w1/CritEntryB.md:12 | resolved@50443f5 | OK | 50443f5's entry hunk replaces "All four commands prune" with the fetch-only measurement, adds `MEASURED IN THE CAMPAIGN, NOT BY THIS LANE`, names fixture `:146`, `:153`, `:161`, and edits the S131 registry cell to `only the fetch 2 -> 1 arm is isolated measurement`. Direct delivery. |
| 20 | census/.../w1/CritNoHarm.md:9 | open | OK | `grep -n '^### ' SCORECARD.md` at tip yields `Round 25 … Round 24 … Round 23 … Round 26 append-only corrections … Round 26 measurements`, i.e. 25, 24, 23, 26 — the ordering defect is still live. (Its c1-after-pre-tip clause was fixed at `ba8b54b`.) |
| 21 | census/.../w1/ExecVerifyLoop.md:5 | open | OK | both committed copies are still syntactically broken at tip: `bash -n` on `.ufo/waves/round-26/w1/verify-loop.sh` and on `census/round-26/waves/w1/verify-loop.sh` → rc 2 each (`line 320: unexpected EOF while looking for matching '"'`). |
| 22 | census/.../w1/RevAssimRules.md:4 | resolved@50443f5 | **WRONG-RESOLVED** | the two named missing receipts landed at `9a6e0f1` (`c2-gate.tsv`, `c2-k4-after.tsv`, both present and `verify=ok` at tip) and the Gate sections at `33e6807`; 50443f5 adds no `census/round-26/records/` path and no `## Gate`. Correction: `resolved@33e6807…` / `resolved@9a6e0f1…`. |
| 23 | census/.../w1/RevC2Scope.md:9 | open | OK | reproduced at tip: `c2-before.tsv` and `c2-after.tsv` still `RECEIPT-COUNTS-ABSENT`; the counter's output shape still cannot match the verifier's counts-line grammar. |
| 24 | census/.../w1/ScoutAssimRegister.md:5 | open | OK | reproduced at tip: `tools/souji-gate-check.py:48` `CLASSES = {present, accepted, unverifiable, refused}`; the r26 artifact `census/round-26/waves/assimilation/slice-verdicts-r26.tsv` carries 6 `accepted-carried` rows, and the gate prints `FAIL slice verdict-bad-class-line-11:accepted-carried` … `fail=6`. |
| 25 | census/.../w1/ScoutF1Gap.md:5 | open | **SHOULD-BE-RESOLVED** | the confounded-evidence clause was delivered at 50443f5 (entry claim 2 "The pull, merge and rebase rows are confounded and are NOT attributions"; S131 cell rewritten). The separate "numerator stale at tip" observation is not a defect of the admit set. |
| 26 | census/.../w1/ScoutRegroundDocs.md:3 | open | OK | F3 still reproduced at tip (`locators=0` for both entries); 50443f5 does not touch `corpus/knowledge/git-auto-maintenance-trigger-set.md` at all, so the F4/F5 quote defects (its L22-24, L30-35, L75) are untouched. |

## Reproduced live defects behind the WRONG-RESOLVED verdict on #9

`tools/souji-axis-check.py` at tip is byte-identical to c594901 (`git log --oneline -- tools/souji-axis-check.py`
→ c594901, 0833de9). Probes written under the seat scratch dir, scorecard = lane `SCORECARD.md`:

```
adv6b (C1 calibration/bookkeeping-file + C2 operability/garbage-typo)  -> claims=2 flags=0  rc=0   [finding 2]
adv3b (C2 operability/fixture-expansion then surface-class: receipt-binding) -> claims=2 flags=0 rc=0 [finding 3]
adv4  (decoy CALIBRATION block, then operability/fixture-expansion)     -> claims=1 flags=0  rc=0   [finding 4]
adv1  (universals in claim prose after END)                             -> claims=1 flags=0  rc=0   [finding 1 remnant]
```

adv4 hides a definite R2 violation (`fixture-expansion` on `operability`) behind a decoy block,
exactly the ADV8 shape the seat called the strongest adversarial input. Since `corpus/QUALITY.md:143`
(Q59) names this tool as the criterion's executable carrier, the hole reaches the calibration axis,
not only the round-26 record.

## Section-level defect

`corpus/lessons/round-26.md` carries **two** `## Seat-reported failures` headings (lines 98 and 105
at M1 and at tip) with identical 4-line intros, and the first section has **zero** bullets. Reading
`c6108301:corpus/lessons/round-26.md` by line number: 98 heading / 100-103 intro / 105 same heading /
107-110 same intro / 112-137 the 26 bullets. Measured gate impact: the base gate blob
(`9f17a1e:tools/souji-landing-gate.py`) at `--rev c6108301 --round 26` prints
`SUMMARY findings=0 … checked_markers=18 status_lines=69 carry_heading=1 checked_reports=466`,
reproducing `census/round-31/records/m1-after.txt` — so the duplication does not fool the base gate,
but the file's own claim ("26 … one bullet per STATUS paragraph") is stated twice with an empty
section first, and any first-section reader gets 0 carried entries.

## Carry completeness (independent of the gate)

Union at tip: 465 `.md` under `.ufo/waves/round-26/`, 494 under `census/round-26/waves/`, 29 of the
latter census-only. Reports whose `STATUS:` is PARTIAL or FAIL: 44 files, 26 unique once the trees
are paired by `w<n>/<file>` (18 pairs byte-identical). The carry holds exactly those 26 keys, zero
missing, zero extra, 6 of them FAIL and 20 PARTIAL.
