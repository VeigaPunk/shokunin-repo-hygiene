# SwarmScout08 — round 31 wave 2: count statements the C1 enumeration does not see

## Status

STATUS: PASS — all three ranges, the `what` column and axes rows 13-15 were read and every candidate count (40, G01-G40) is listed with line, text and a checkability code in `deliver-c1-enumeration-gap.md`; 32 are checkable from committed bytes, 8 are not (one stale, one contradicted, one out of lane, five prose). Nothing here attacks a claim.

## Evidence

Reading rev: tip 2c16d018e40db7c23420a2c3bb546b52957bcc25; SCORECARD lines 1-359 are identical to base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc (`git show HEAD:SCORECARD.md | head -359 | diff - base` printed no difference; `git diff --stat base tip -- SCORECARD.md`: 47 insertions, 0 deletions).

Commands (all read-only git/python against committed bytes, scratch under `/fast/scratch/hyaku/souji-r31/w2-c1-enumeration-gap/`):
- table scan: a python tokenizer over cells of lines 147-175, 313-314, 354-355 and 13-15 (masks paths, hashes, S-ids, `rNN`; lists remaining digit runs and number words with context).
- `git show 2c16d018:census/round-1/census.tsv | wc -l` -> 247 (header + 246); `census-summary.json` `"rows_total": 246`, `"fragments": "64/64"`.
- `git show 31984f47:corpus/SOURCES.md` S-row count -> 33; status cells mined 16, queued 15, rejected 2. Cited record `census/round-13/verification.json` shows `"rows": 37` and `"mined": 20` (later census).
- `census/round-21/oracle-acceptance.json`: `labelled 2372`, `files 192`, `tp 3`, `fp 0`, `fn 0`, `prior_verdicts` 401 entries.
- `census/round-17/jj-receipts-base5fa6017.txt`: 13 `CASE ... FAIL` lines, `SUMMARY total=33 failed=13 skipped=2`.
- `census/round-21/reason-oracle-before.txt` `SUMMARY total=27 pass=6 fail=21 leaks=19 base_leaks=19 max_reason_bytes=454`; `reason-after.txt` `total=27 pass=27 leaks=0 base_leaks=19 max_reason_bytes=160`.
- `census/round-21/step-inventory.json` `steps` = 18; `acceptance-c2-first.json:804` `base_discriminating=12`, `:416` `base_discriminating=11`.
- `tests/fixtures/r23-record-agreement.py` lines 525-541: `CASES` has 15 entries, 12 flagged control (True), 3 not; docstring line 38 "Cases 2-8 are the always-zero control".
- `tests/fixtures/r24-size-census.py` docstring: "frozen 8-case set, extended by r25 C2 with the refusal-surface cases 9-12"; `tests/fixtures/r24-coverage-agreement.py` builds Case 1..9.
- `census/round-24/records/c2-control-base.tsv` `mismatches=2` (rev a65fac98); `c2-after.tsv` `mismatches=0`, `grounded=6` at rev 778747eb; `git ls-tree --name-only 778747eb corpus/knowledge/` -> 13 `.md`.
- `census/round-29/records/controls.tsv:2` `mismatches=10`; `final-tip-measure-2.txt:4` `mismatches=0`; `final-tip-measure.txt:5` `r26 records=1381 failed=0 uncovered=0`.
- `census/round-30/records/c1-before.txt:29` `k1=13`; `c1-after-a3.txt:30` `k1=0`; `m1-r29-carry-red-before.txt` first block `findings=7`.
- axes: `census/round-22/attempt2/declared-evidence-before-final.tsv` `assertions=55 resolved=52 skipped=33 mismatches=3`; `census/round-23/records/declared-evidence-after.tsv` `assertions=63 resolved=63 skipped=40 mismatches=0` (rc=0, rev 9301d98c); `declared-evidence-before.tsv` `assertions=56 resolved=53`.
- `git grep -E '67/67/40/0|resolved=67|assertions=67' 2c16d018`: only SCORECARD.md:14, `.ufo/waves/round-23/w1/RevRecords.md:89,134` and a round-26 capture; no census record.

Not run: no counter, fixture or selftest was executed (unrun checks have not passed); every CMD classification means a committed command exists that prints the figure, with the printed figure read from the committed record or fixture source, not re-run.

## Findings

Routing inputs, not claim attacks. Axis harmed in each case: calibration.

1. **G06, L173 `what` column: "reject an always-zero emitter on eight of nine fixture cases" is stale.** The fixture has 15 cases (12 control). The L1's supersession row L32 restates only the evidence cell (9/9 -> 15/15); the same row's `what` sentence keeps eight of nine and the fixture docstring still says "Cases 2-8". The counter reads `unbound=0` for that row while the row contradicts itself. A same-line sibling-count rule would see it. L174 `8 frozen cases` (G07) is the same shape but literally true as "frozen 8" (fixture now `cases=12`).
2. **G34, L14 axes: `67/67/40/0` is unbound and was refuted in round 23, still uncorrected.** `.ufo/waves/round-23/w1/RevRecords.md:134`: "is unbound and contradicted by the receipted wider reading". SCORECARD line 14 is unchanged at tip; no append-only correction exists. The axes table (lines 13-15, 16 statements) is outside every C1 enumeration.
3. **Evidence-column counts in other notations: 14 statements (G11-G24), all checkable from committed records or git-at-rev.** Missed notations: `key=value` (`k1=13`, `mismatches=10`, `records=1381`, `mined=16 queued=15 rejected=2`), glued word-digit (`oracle2372`, `all401`, `leaks19→0`, `(base12)`), parenthesised `(N at base)`, `(246 rows)`, `(13 fail)`. Two rows cite a record that does not hold the figure: L151 cites `census/round-13/verification.json` (37 rows, mined 20, a later census) for `baseline 33 rows, mined=16 ...` (derivable only at 31984f47); L313/L314 name no record for `mismatches=10 -> 0` and `records=1381`.
4. **`what` column: 10 statements (G01-G10), 8 checkable (REC/CMD), 1 prose (G03 `five pinned replay verdicts`), 1 stale (G06).**
5. **Prose or out-of-lane only: G03, G25, G29, G35, G40 (prose), G30 (fleet MANIFEST `rounds[408]`, not opened).** Scores 8/7/8 and `Numeric delta0` carry the SCORECARD's own statement that no reproducible 0-10 mapping exists.
6. Observation (not a defect): L161 `35/0 (5fa6017 tools: 13 fail)` — the cited base record has `total=33` with 2 skipped, so the base run and the 35-case tip run are different case sets.

## Attack log

- Tried to find counts in the `name` column: only round tags and `attempt 2` (ordinals), no counts.
- Tried the `S035/S036/S037` and `S045–S047` tokens against the `N/M` rule: not matched (digits needed both sides), excluded as source ids.
- Tried exit codes (`exit 2`, `exit 0`) and `garbage: 1`: excluded, not measured counts.
- L162, L169, L148-L150, L156, L171-L172 `what`/evidence cells: no unseen counts.
- L363+ (Round 31 block) and lines 18-141, 178-348: out of the assigned ranges; named in the deliverable's scope note.
- Did not open `MANIFEST.json` (G30 stays OUT); did not run any fixture; no lane mutation. I ran `mkdir -p` on the existing `.ufo/waves/round-31/w2/` (already present).

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w2/deliver-c1-enumeration-gap.md` (40-row inventory G01-G40 with line, text, checkability code, committed check, in-row flag; routing notes).
- This report.
