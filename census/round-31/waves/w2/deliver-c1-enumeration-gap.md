# C1 enumeration gap: count statements the frozen rule does not see (routing input for round 32)

Seat SwarmScout08, round 31 wave 2. Not a claim attack: the frozen rule (`census/round-31/c1-cells.tsv` header) counts only
`cases=N pass=N` or `N/M` literals in the third cell of capability-table rows at base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc
(lines 147-175, 313-314, 354-355). Everything below is outside that notation or outside that cell.

Method: lines 13-15 and the three row ranges were read at base 9f17a1ef (SCORECARD lines 1-359 are byte-identical at tip
2c16d018e40db7c23420a2c3bb546b52957bcc25, which only appends 47 lines). Each cell was split on the table pipes, committed-path
tokens, hashes, S-ids and `rNN` tags were masked, and every remaining digit run or number word was read by hand with its
neighbours. Each candidate was then looked up in committed bytes with `git show`/`git grep` against the tip (read-only).
Codes: **REC** = a committed record file states or reproduces it (path:line); **CMD** = a committed command/fixture/tool prints
or recomputes it; **PROSE** = only prose or a LOG sentence backs it, no mechanical check; **OUT** = lives outside the lane;
**STALE** = a committed check disagrees with the statement today. "In row?" says whether the SCORECARD row itself names the
check. Nothing here was run through a lane counter; the re-derivations are git/python reads of committed bytes (commands
given in the report).

Totals: 40 statements (G01-G40). Counter-visible items in the same lines: 41 (L01-L41). Of the 40: 10 in the `what it can now
do` column (A), 14 in other notations of the evidence column (B), 16 in the axes table rows 13-15 (C).

## A. `what it can now do` column (C1 never reads it)

| id | line | text | code | check (committed) | in row? |
|---|---|---|---|---|---|
| G01 | 147 | `at 64-seat parallelism` | REC | `census/round-1/census-summary.json` line 5 `"fragments": "64/64"` | no |
| G02 | 165 | `secret patterns and160-byte bounds` | REC | `census/round-21/reason-after.txt` SUMMARY `max_reason_bytes=160` | partly (cites reason-after.txt) |
| G03 | 166 | `strict branch keeps five pinned replay verdicts` | PROSE | comment `tools/souji-landing-gate.py:122` ("so the five pinned historical replays keep their") and `corpus/lessons/round-19.md:18`; no command counts the pins | no |
| G04 | 170 | `replay18 frozen r20 predicates` | REC | `census/round-21/step-inventory.json` key `steps` has 18 entries; `census/round-21/accepted-matrix.json` `scenarios=3 summaries_equal=True` | no |
| G05 | 173 | `re-derive four declared-vs-observed keys` | CMD | fixture case `repaired` asserts `keys=4` (`tests/fixtures/r23-record-agreement.py:472`); tool prints `keys=K` | no |
| G06 | 173 | `reject an always-zero emitter on eight of nine fixture cases` | **STALE** | fixture `CASES` at tip holds 15 entries, 12 flagged control, 3 not (counted from `tests/fixtures/r23-record-agreement.py` lines 525-541); docstring line 38 still says "Cases 2-8 are the always-zero control". The supersession row L32 corrects only the evidence cell (9/9 -> 15/15); this sentence in the same row keeps the old 9 | no |
| G07 | 174 | `fixture claim over 8 frozen cases` | REC (qualified) | `tests/fixtures/r24-size-census.py` docstring: frozen 8-case set extended by r25 with cases 9-12; fixture now prints `cases=12` (L33 row). True as "8 frozen", ambiguous beside the row's restated `cases=12` | no |
| G08 | 175 | `its fixture fails the always-zero emitter on all nine cases` | CMD | `tests/fixtures/r24-coverage-agreement.py` builds Case 1..9 (grep `Case(\d` = 9); L35 row binds `cases=9 pass=9` | no |
| G09 | 175 | `grounded entries only (6 of 13 at 778747e)` | REC | `census/round-24/records/c2-after.tsv` `grounded=6 mapped=6` at rev 778747eb; `git ls-tree --name-only 778747eb corpus/knowledge/` shows 13 `.md` | row names the tsv |
| G10 | 355 | `it surfaced round 29's seven uncarried seat failures` | REC | `census/round-30/records/m1-r29-carry-red-before.txt` first rev block `SUMMARY findings=7` (7 `LG-SEAT-UNCARRIED` lines) | yes (cited) |

Exit codes (`exit 2` at L157 x2, L174; `exit 0` at L152) and example values (`garbage: 1`, `alternates>0`) were read and excluded:
they are not counts of anything the row measures.

## B. Evidence column, notations the rule misses

| id | line | text | code | check (committed) | in row? |
|---|---|---|---|---|---|
| G11 | 147 | `(246 rows)` | REC+CMD | `census/round-1/census-summary.json` `"rows_total": 246`; `git show <rev>:census/round-1/census.tsv \| wc -l` = 247 (header + 246) | no |
| G12 | 151 | `baseline 33 rows, mined=16 queued=15 rejected=2 at 31984f47...` | CMD (git at rev) | at 31984f47: S-row regex count = 33, status cells mined 16 / queued 15 / rejected 2 (derived this run). The record the row cites, `census/round-13/verification.json`, shows rows 37 and mined 20 (a later census), so the cited path does not reproduce the figures; only a command at the named revision does | no command in cell |
| G13 | 159 | `oracle2372 keys over192 files, tp3/fp0/fn0` | REC | `census/round-21/oracle-acceptance.json`: `labelled 2372`, `files 192`, `tp 3`, `fp 0`, `fn 0`; `.txt` line 6 `ORACLE tp=3 fp=0 fn=0 labelled=2372` | yes (cited) |
| G14 | 159 | `all401 old tuples identical` | REC (count only) | same json: `prior_verdicts` has 401 entries plus `prior_verdicts_sha256`; "identical" is the record's claim, not a count | yes (cited) |
| G15 | 161 | `(5fa6017 tools: 13 fail)` | REC | `census/round-17/jj-receipts-base5fa6017.txt`: 13 `CASE ... FAIL` lines, `SUMMARY total=33 failed=13 skipped=2` (note total 33 vs the cell's 35) | row cites `jj-receipts-*.txt` |
| G16 | 165 | `leaks19→0` | REC | `reason-oracle-before.txt` `leaks=19`; `reason-after.txt` `leaks=0 base_leaks=19` | yes (cited) |
| G17 | 168 | `final r21 18-step receipts` | REC | `census/round-21/step-inventory.json` `steps` = 18 | no |
| G18 | 168 | `r19-seat-audit-shapes17/0 (base12)` | REC | `census/round-21/acceptance-c2-first.json:804` `base_discriminating=12`; step-inventory same | no |
| G19 | 168 | `r20-audit-contract78/0 (base11)` | REC | `acceptance-c2-first.json:416` `base_discriminating=11` | no |
| G20 | 175 | `c2-control-base.tsv (2 at base)` | REC | tsv stdout `grounded=4 mapped=2 dangling=0 mismatches=2` at rev a65fac98 | yes (path) |
| G21 | 175 | `c2-after.tsv (0)` | REC | tsv stdout `grounded=6 mapped=6 dangling=0 mismatches=0` | yes (path) |
| G22 | 313 | `base mismatches=10 -> 0` | REC | `census/round-29/records/controls.tsv:2` `mismatches=10`; `final-tip-measure-2.txt:4` `mismatches=0` | no (records not cited) |
| G23 | 314 | `records=1381 failed=0 uncovered=0` | REC | `census/round-29/records/final-tip-measure.txt:5` `r26 records=1381 failed=0 uncovered=0`; row names `census/round-26/waves`, not the record | no |
| G24 | 354 | `k1=13` -> `k1=0` | REC | `census/round-30/records/c1-before.txt:29` `k1=13`; `c1-after-a3.txt:30` `k1=0` | yes (cited) |

Already seen by the rule and therefore not listed: `12/9 failed →12/0` (L13-14), `stub control 4/8` (L34), `base gate 3/7` (L41),
`cases=N pass=N` forms (L36, L38, L40). `S035/S036/S037` and `S045–S047` are source ids, not counts (`N/M` needs digits both sides).

## C. Axes table, rows 13-15 (outside lines 147-175 entirely)

| id | line | text | code | check (committed) | in row? |
|---|---|---|---|---|---|
| G25 | 13 | `cmd+reason2/2` | PROSE | `corpus/lessons/round-21.md:9` "cmd-only1/2 → cmd+reason2/2"; no counter | no |
| G26 | 13 | `same27-case oracle6/27→27/27` | REC | `reason-oracle-before.txt` SUMMARY `total=27 pass=6`; `reason-after.txt` `total=27 pass=27` | no (row cites receipts generally) |
| G27 | 13 | `leaks19→0/max454→160` | REC | before `leaks=19 max_reason_bytes=454`; after `leaks=0 max_reason_bytes=160` | same |
| G28 | 13 | `160-byte synthetic-only scope` | REC | `max_reason_bytes=160` in `reason-after.txt` | same |
| G29 | 13 | `Numeric delta0` | PROSE | no command: derived from the statement that no reproducible 0-10 mapping exists | no |
| G30 | 13 | `MANIFEST rounds[408]` | OUT | fleet `MANIFEST.json` (not opened, out of bounds); only echoed at `LOG.md:1342` | no |
| G31 | 14 | `assertions=55 resolved=52 skipped=33 mismatches=3` | REC | `census/round-22/attempt2/declared-evidence-before-final.tsv` prints exactly that | yes (cited) |
| G32 | 14 | `assertions=63 resolved=63 skipped=40 mismatches=0` | CMD+REC | command in the row's counting cell (`souji-declared-evidence.py ... --rev 9301d98c... --format counts`); `census/round-23/records/declared-evidence-after.tsv` | yes |
| G33 | 14 | `(55→63)` | REC | derived from G31 and G32 | yes |
| G34 | 14 | `67/67/40/0` (wider span-inclusive reading) | **UNBOUND, contradicted** | no committed record states it; `.ufo/waves/round-23/w1/RevRecords.md:134` says "is unbound and contradicted by the receipted wider reading"; the same file puts the receipted reading at 66/66/40/0. Row text unchanged at tip, no correction appended | no |
| G35 | 14 | `2 of 3 repairs address a real path` | PROSE | judged by hand | no |
| G36 | 14 | `the pre-hardening instrument's 56/53 reading` | REC | `census/round-22/attempt2/declared-evidence-before.tsv` `assertions=56 resolved=53 skipped=33 mismatches=3` | yes |
| G37 | 14 | `--selftest 8/8` | CMD | `python3 tools/souji-declared-evidence.py --selftest`; same literal as L30 (run-bound there), but this occurrence is not an enumerated item | yes |
| G38 | 15 | `three source shapes3/3, each18/18 original predicates` | REC | `census/round-21/accepted-matrix.json` `scenarios 3`, `summaries_equal True`; 18 = steps in step-inventory | no |
| G39 | 15 | `remote-ref-only/unborn HEAD18/18` | REC | `census/round-21/remote-source-after.json` (L29 binds the same literal in the capability row) | no |
| G40 | 13-15 | score column `8` / `7` / `8`, `Numeric delta0` (L15), `rounds[408]` (L15) | PROSE/OUT | SCORECARD L307 states no reproducible 0-10 mapping exists; rounds[408] as G30 | no |

## D. What the numbers say for routing

1. Mechanical share: of 40 statements, 32 are checkable from committed bytes today by REC or CMD: A 8 (G01, G02, G04, G05, G07-G10), B 14 (G11-G24), C 10 (G26-G28, G31-G33, G36-G39). The other 8: PROSE G03, G25, G29, G35, G40; OUT G30; unbound and contradicted G34; STALE G06 (checkable, and the check disagrees).
2. Highest-value routing target: G06 (and G07). The L1 supersession rows L32 and L33 fix the cell's evidence counts (9/9 -> 15/15, 8/8 -> 12/12) but the same row's `what` text keeps the old nine/eight, so a row can pass `unbound=0 mismatches=0` while contradicting itself. A sibling-count rule (when a run row restates a cell's count, scan the whole line for other counts) closes this class.
3. G34 is an axes-row count that a prior round (r23 RevRecords C1-c) already refuted and that is still in the row at tip: the axes table was never in any enumeration.
4. A rule that would have seen most of group B: `key=value` integers (`k1=13`, `mismatches=10`, `records=1381`, `base12`), glued `<word><int>` forms (`read32`, `oracle2372`, `all401`, `leaks19→0`), parenthesised `(N at base)`, and number words in the `what` column ("four", "five", "seven", "eight of nine", "all nine"). Hash prefixes, S-ids, `rNN` and exit codes need an explicit exclusion list.
5. Scope note: only the three ranges the brief names were read. SCORECARD lines 18-141 and 178-348 (Round 28/29/30 measurement tables) carry more counts and were not enumerated.
