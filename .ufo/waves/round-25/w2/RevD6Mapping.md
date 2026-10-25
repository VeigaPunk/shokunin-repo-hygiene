# RevD6Mapping — W2 falsification: D6 slice-verdict mapping (R24-M22)

STATUS: PARTIAL — the 8-row mapping reconstructs and the three claim checks hold; the
two TSV pointer lines exist but their referent (`corpus/lessons/round-25.md § Quarantine-slice
vocabulary`) does not exist at inspection time, so the pointer confirmation fails.

## Method

Read-only, leaf seat. Absolute lane paths; lane root
`/home/vgpnk/Projects/shokunin/souji-shokunin` (HEAD `6deb53561aace9aa14a399f88cf8150da4d4f4bd`).
Sources read: `census/round-24/records/slice-verdicts.tsv` (gate), `.ufo/waves/round-24/assimilation/slice-verdicts.tsv` (detail), `census/round-22/attempt2/slice-verdicts.tsv` (r22 frozen), `corpus/lessons/round-24.md`, `corpus/SOURCES.md`, `corpus/lessons/round-24-verifier-spotcheck.md`, `tests/fixtures/r25-q57-check.sh`, `census/round-22/attempt2/sources/vendor-noreplace-probe.out`. Git history: `git log`, `git show 778747e`, `git diff 778747e 315422b`, `git diff 315422b 604cd44`, `git diff HEAD` (worktree). Structure check via Python: 8 data rows per table, identical id sets, no duplicates, gate 3 cols / detail 6 cols.

## Reconstructed D6 mapping (keyed (souji, campaign id))

| key (souji, campaign id) | r22 gate (frozen) | r24 detail register_class → verdict | map → | r24 gate | change class |
|---|---|---|---|---|---|
| S114 | accepted | payload-absent → present | accepted | accepted | unchanged; markup correction `[1]` vs `(1)` |
| S118 | unverifiable | could-not-be-fetched → present-via-mirror | accepted | accepted | **re-grade** (only one) |
| S123 | accepted | payload-absent → present (0 quote matches) | accepted | accepted | unchanged; evidence limited (digest-only) |
| S124 | accepted | payload-absent → present-quote-needs-fix | accepted | accepted | unchanged; quote correction required |
| S126 | present | payload-absent → present | accepted | accepted | **vocabulary collapse** |
| S131 | accepted | payload-absent → present (0 quote matches) | accepted | accepted | unchanged; evidence limited (digest-only) |
| S133 | accepted | payload-absent → present (0 quote matches) | accepted | accepted | unchanged; evidence limited (digest-only) |
| S138 | present | payload-absent → present | accepted | accepted | **vocabulary collapse** |

Tally: r22 5 accepted / 2 present (S126, S138) / 1 unverifiable (S118) / 0 refused; r24 gate 8/0/0/0. The class map (detail → gate) is asserted by the gate header (added at `315422b`): `present` / `present-via-mirror` / `present-quote-needs-fix` → `accepted`. Each detail row carries `appended_r24 = no`, i.e. no row was assimilated into the lane corpus.

## Verification results

1. **S118 is the only re-grade — CONFIRMED.** `git diff 778747e 315422b -- census/round-24/records/slice-verdicts.tsv` shows exactly one class-line change: S118 `unverifiable` → `accepted` (plus the vocabulary header line). At `778747e` all other rows were already `accepted`. r22→r24 class-diff rows are exactly S118 (re-grade), S126, S138 (collapse). The r22 file stays `unverifiable` (frozen history; unchanged in worktree).
2. **S126/S138 are a vocabulary collapse — CONFIRMED (with disclosed drift).** Evidence content is consistent r22→r24 (span verbatim in web docs); class changed `present`→`accepted` only via the header map, with no reason stated in the gate. Under r22 definitions both remain `present`, so the collapse hides r22's `present` class (W2Slice F4; mirrored in `corpus/lessons/round-24.md:235,238`).
3. **S123/S131/S133 evidence limitations — CONFIRMED.** Gate cells are digest/figure-only (`510722c1`, `1ac71c4f`, `a53f1e30`/`a4506492`, 8 mounts/7 paths); none asserts the quote predicate. The detail footnote (`slice-verdicts.tsv:10`, added at `315422b`) and r22 rows record 0 quote matches in the cited payloads; `accepted` rests on the wrong-source spans in git-worktree(1)/rename(2). Lane-side S124 check: `vendor-noreplace-probe.out` exists, 6 lines, each carries `NOREPLACE_new=0(ok)` alongside `NOREPLACE_existing` — consistent with the quote-drop record.
4. **Two TSV pointer lines — lines exist, referent missing.** Both files now carry a line-11 comment: gate `# r25 D6/Q57: authoritative gate table; mapping and vocabulary in corpus/lessons/round-25.md § Quarantine-slice vocabulary.`; detail `# r25 D6/Q57: scout detail, not the gate verdict; the mapping is in corpus/lessons/round-25.md § Quarantine-slice vocabulary, with census/round-24/records/slice-verdicts.tsv authoritative.` Both are **uncommitted worktree additions** (HEAD 6deb535 +1 line each). Referent `corpus/lessons/round-25.md` does not exist (35 lesson files, none round-25.md; phrase found only in w1 drafts `d5d6-drafts.md` / `quality-q57.md`).

## Findings (mismatches)

1. **HIGH — dangling pointer lines.** Both TSVs point to `corpus/lessons/round-25.md § Quarantine-slice vocabulary`, which does not exist at inspection. The mapping paragraph currently lives as an uncommitted append-only section at the tail of `corpus/lessons/round-24.md` ("Round 25 append-only correction — D6 / R24-M22"), which the pointers do not cite. `corpus/SOURCES.md:16` likewise references `corpus/lessons/round-25.md` Gate (pending). The D6 lesson deliverable is not yet landed.
2. **MEDIUM — stale tallies without superseded marks.** `SCORECARD.md:182` ("slice 7 accepted + 1 unverifiable (S118)") and `LOG.md:1692` carry the pre-re-grade tally with no `superseded by` note (append-only files; need appended notes, not edits). `corpus/lessons/round-24.md:232` (S118 cell `unverifiable`) and `:240` (7/1 tally) now have superseded notes only in the uncommitted worktree appendix.
3. **LOW — pointer-line change duplicated off-ref.** Commit `604cd44` (reachable via `--all`, not an ancestor of HEAD, on no branch/tag) already contains the identical two pointer lines plus other WIP; the same lines are now uncommitted in the worktree. A prior integration attempt appears rewritten away; nothing is on a ref.
4. **LOW — r24 verifier spot-check conflates id spaces.** `corpus/lessons/round-24-verifier-spotcheck.md:66` lists S118 class `accepted (re-graded)` with source URL `https://qiita.com/koseki/items/f1af58f1ec1693f0536a` — that is campaign S138 / lane S118's document, not campaign S118 (Broder DOI 10.1109/SEQUEN.1997.666900). Class agrees; document attribution wrong. File is non-author-owned; report-only.
5. **INFO — S138 locator drift.** r22 says qiita markdown line 11; r24 gate/detail say line 17. No table states the counting basis (W2Slice F6). Not verifiable in-lane (community web page, not snapshotted).

## Residual risk / verification gaps

- Hard bound forbids inspecting `/home/vgpnk/Projects/shokuknow`; the campaign register (`absent-defect-register.md`) was not re-read. S123/S131/S133 "0 quote matches" rests on recorded r22 rows and the detail footnote, not a fresh shokuknow probe.
- Web sources (S114/S118/S126/S138) not re-fetched; their gate cells were accepted as recorded.
- The Q57 checker fixture (`tests/fixtures/r25-q57-check.sh`) exists but is untracked; it checks tally recount + pointer presence + site classes, not a full join — the gate is not yet runnable as a committed counter.

## Attack log

- Re-read both TSVs + r22 TSV; parsed rows/cols; confirmed 8↔8 id sets, no duplicates.
- `git diff` across 778747e → 315422b → 604cd44 → HEAD → worktree for both files; pinned S118 re-grade and S126/S138 collapse to their commits.
- Checked lane SOURCES rows S117/S118/S123/S124–S126 to confirm the (souji, campaign id) key is required (campaign S118 ≠ lane S118; campaign S114 ≠ lane S117 etc.).
- Reran structure count and pointer existence; no lane edits, no git/jj mutations, no scratch writes, no tools installed.
