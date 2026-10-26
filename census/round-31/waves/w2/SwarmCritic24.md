# SwarmCritic24 — M1 carry audit, corpus/lessons/round-26.md (round 31, wave 2)

## Status

STATUS: FAIL — the appended carry of `c6108301cbf0ca0ad086ff0ece6b76adad6b74b6` is quote-exact and
complete (26/26 unique non-PASS reports, every cited line a `STATUS:` line), but its dispositions are
not honest: 7 of 26 `resolved@` bullets name a commit whose diff does not deliver what the seat said
was missing, 3 of 26 `open` bullets were in fact resolved later in the lane, and the section itself
is duplicated with an empty first block. All evidence read through `git -C <lane> show <rev>:<path>`
and read-only `python3 -B` at tip `2c16d018e40db7c23420a2c3bb546b52957bcc25`.

## Evidence

Audited bytes: `corpus/lessons/round-26.md` is byte-identical at `c6108301` and at tip
(`git diff --stat c6108301 tip -- corpus/lessons/round-26.md .ufo/waves/round-26 census/round-26/waves` → empty).

Carry completeness (independent of any gate), union at tip:
```
465 .md under .ufo/waves/round-26/ ; 494 under census/round-26/waves/ ; 29 census-only
PARTIAL-or-FAIL reports: 44 files -> 26 unique keys after pairing w<n>/<file> (18 pairs byte-identical)
carried 26, missing 0, extra 0 ; 6 FAIL + 20 PARTIAL ; dispositions 17 open + 9 resolved
```

Quote exactness: 26/26 bullets match the cited `STATUS:` paragraph exactly after joining wrapped
lines and deleting backticks/asterisks; 2 quotes had inline emphasis stripped (`*direction*`,
`*payload*`); no carry-side elision. No MISQUOTED entry.

Duplicated section (`grep -n '^## Seat-reported failures'` at M1 and tip):
```
98:## Seat-reported failures     <- intro only, no bullets
105:## Seat-reported failures    <- intro again, 26 bullets at 112-137
```
Gate impact measured, not assumed — base gate blob `9f17a1e:tools/souji-landing-gate.py`:
```
python3 -B <base gate> --root <lane> --rev c6108301 --round 26 --fleet-root <fleet>
SUMMARY findings=0 checked_reg=63 checked_changed=0 checked_pins=13 checked_measured=3
        checked_markers=18 status_lines=69 carry_heading=1 checked_reports=466   rc=0
```
reproduces `census/round-31/records/m1-after.txt` line for line (same markers=18, reports=466), so
the duplication does not fool the base gate; the 8 census-only carries are simply outside its
discovery (tip gate: markers=26, checked_reports=495).

Live residuals behind the `resolved@` verdicts, reproduced at tip:
```
python3 -B tools/souji-receipt-run.py verify --root . census/round-26/records/<r>.tsv
  c1-before, c2-before, c3-before, c1-after, c2-after -> RECEIPT-COUNTS-ABSENT
  c2-k4-base, c2-gate, c2-k4-after, c3-after -> verify=ok
python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries <both r26 entries> \
  --snapshot-dir census/round-26/sources            -> entries=2 ok=2 fail=0   (Gate sections since 33e6807)
  ... --slice-verdicts census/round-26/waves/assimilation/slice-verdicts-r26.tsv
                                                    -> FAIL slice verdict-bad-class-line-11:accepted-carried ... fail=6
python3 -B tests/fixtures/r23-locator-heading.py --entries <both r26 entries> --snapshot-dir census/round-26/sources
                                                    -> entries=2 locators=0 locators_bad=0   (Q54 vacuous)
git show tip:.ufo/waves/round-26/w1/verify-loop.sh > v.sh ; bash -n v.sh          -> rc 2 (unexpected EOF, line 320)
git show tip:census/round-26/waves/w1/verify-loop.sh > v.sh ; bash -n v.sh       -> rc 2
grep -n '^### ' SCORECARD.md -> Round 25, Round 24, Round 23, Round 26 ... (order still 25,24,23,26)
```

`tools/souji-axis-check.py` is unchanged since `c594901` (the commit the carry names as resolving
RevC3Design). Adversarial probes (seat scratch, scorecard = lane `SCORECARD.md`):
```
adv6b operability+garbage-typo (unknown surface-class)      -> claims=2 flags=0 rc=0
adv3b fixture-expansion on operability, then receipt-binding -> claims=2 flags=0 rc=0
adv4  decoy calibration block before operability/fixture-expansion -> claims=1 flags=0 rc=0
adv1  universals in claim prose after END                    -> claims=1 flags=0 rc=0
```

## Findings

1. **Duplicated carry heading with an empty first section.** `corpus/lessons/round-26.md:98-110`:
   two identical `## Seat-reported failures` headings and intros, the first with no bullet. Harm:
   calibration (a record whose own claim "26 … one bullet per STATUS paragraph" is stated twice and
   emptied once); operability exposure limited — measured: the base gate still reads 18 markers, so
   no counter is fooled by the empty section. Measured contrast: `corpus/lessons/round-27.md` and
   `round-28.md` each carry exactly one `## Seat-reported failures` heading at tip, so the
   duplication is specific to the round-26 append.
2. **Seven false-provenance `resolved@` dispositions.** Location: r26 carry bullets at
   `corpus/lessons/round-26.md:120` (RevC3Design), `:121` (RevEntryDrafts), `:122` (RevQ59Text),
   `:126` (ScribeLessonR26), `:127` (ScribeLogR26), `:128` (ScribeScorecardR26), `:133`
   (RevAssimRules). Each cited commit's own diff does not deliver the named fix: `50443f5`'s
   non-mirror paths are only `corpus/SOURCES.md`, `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md`
   and `corpus/lessons/round-26.md`; `c594901` changes the fixture case set and R4 only. The real
   deliveries are `33e6807` (Gate sections, `entries=2 ok=2`), `9a6e0f1` (c2-gate/c2-k4-after
   receipts), `c594901` (12-case fixture), `166baa1` (Q59 row + R26-M1 row), `0833de9` (Entry B
   already cites S132 at its first commit). Harm: calibration — the carry is the lane's own failure
   ledger and it now asserts resolutions at revisions that did not resolve them.
3. **Three stale `open` dispositions.** Location: `:124` (ScribeAxisDocs — the "fixture cannot
   produce the literal" premise died at c594901: `cases=12 pass=12 control=FALSE-GREEN-REJECTED`,
   `--tool` honoured; no r26-axis-check row remains in `SKILL.md`), `:125` (ScribeGateDraft — its
   stated blocker "both entries have no `## Gate` heading" ended at 33e6807), `:136` (ScoutF1Gap —
   the confounded pull/merge/rebase evidence is disclosed in the entry and in S131's cell at
   50443f5). Harm: calibration.
4. **A `resolved@` that hides four live holes in the named instrument.** `tools/souji-axis-check.py`
   at `:120` (RevC3Design → resolved@c594901) still returns rc 0 for an unknown surface-class, for a
   repeated `surface-class:` line (last-wins at `:74`), for a decoy first MACHINE BLOCK (first-match at
   `:56`) and for universals in claim prose. Location: `tools/souji-axis-check.py:56,74,110-114,121`.
   `corpus/QUALITY.md:143` (Q59) names this tool as the criterion's executable carrier, so the hole
   reaches the calibration axis, not only the round-26 record.
5. **M1's "after" reading measures presence, not resolution.** `census/round-31/records/m1-after.txt`
   reaches LG-SEAT-UNCARRIED 0 by counting carried bullets (the frozen target, met); the receipt is
   silent on whether the carried failures were closed. Of the 26 carried entries, 12 describe defects
   that still reproduce at tip — ledger items 1, 2, 3, 4, 6, 8, 18, 20, 21, 23, 24, 26 — each scored
   OK above only because its `open` disposition is honest. Location: the M1 claim
   and its receipt. Harm: calibration — the receipt reads like a closure certificate while the
   underlying failures are live.

## Attack log

- A1 union completeness: enumerated 465 `.ufo` + 494 `census` md, paired duplicates by `w<n>/<file>`,
  compared to the 26 carried keys → 0 missing, 0 extra. Attack failed; carry is complete.
- A2 quote exactness: per-bullet paragraph extraction at the cited line, normalized comparison →
  26/26 exact (only markdown delimiters and line joins differ). Attack failed.
- A3 disposition falsification: `git show --stat` + targeted hunks on `50443f5`, `c594901`,
  `07f83e6`, `166baa1`, `0833de9`, `33e6807`, `9a6e0f1`, `ba8b54b`, `2706527` → 7 wrong, 2 right
  (`07f83e6`, `50443f5`→CritEntryB). Attack succeeded.
- A4 later-resolution sweep: `git log` over the whole lane plus tip runs of the receipt verifier,
  the gate, the locator fixture, the slice-vocabulary check, `bash -n` on both verify-loop copies,
  `SCORECARD.md` heading order → 3 stale `open`s. Attack succeeded.
- A5 gate-duplication impact: ran the base gate blob at the M1 commit; markers=18, findings=0 —
  identical to the committed receipt. The empty first section does not blind it. Attack failed.
- A6 adversarial probes against the "resolved" C3 instrument: 4 shapes, all rc 0. Attack succeeded.
- A7 slice-class reproduction: `accepted-carried` still outside `CLASSES`; gate prints 6 FAIL lines
  on the r26 verdict artifact. Attack succeeded (confirms ScoutAssimRegister's `open`).
- Read-only respected: no git/jj mutation in the lane, no writes outside this seat's report,
  delivery and `/fast/scratch/hyaku/souji-r31/w2-SwarmCritic24/` (removed). No tool install needed.

## Deliveries

- `.ufo/waves/round-31/w2/deliver-m1-audit-r26.md` — per-entry ledger (26 rows), verdict tally
  (16 OK / 3 SHOULD-BE-RESOLVED / 7 WRONG-RESOLVED / 0 MISQUOTED), corrections, reproduced probes.
