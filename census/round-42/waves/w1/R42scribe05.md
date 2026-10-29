# R42scribe05 — C1 register chunk 5 verification (13 resolved rows)

Seat: R42scribe05 (role scribe). Input: `.ufo/waves/round-42/w1/inputs/c1-chunk5.tsv`.
Base: `bf618f6c5c09d302994871c94903abbea2deb60d` (SCORECARD.md and tree read at base only).
Register `census/round-42/c1-register.tsv` was not edited. No candidate files written. No frozen file touched.

## Commands run and observed output

1. `cat .../inputs/c1-chunk5.tsv` — 13 data rows, lines 772, 773, 792 (x3), 793 (x2), 811 (x2), 821, 822, 823, 832.
2. `git -C <lane> show bf618f6c…:SCORECARD.md | sed -n '<n>p'` for n in 772 773 792 793 811 821 822 823 832 — each line carries the item's token (exact-count check below).
3. Nearest heading above each line (awk over base SCORECARD.md):
   - 772, 773 <- line 767 `### Round 39 capability rows (appended)`
   - 792, 793 <- line 787 `### Round 40 measurements (...)`
   - 811 <- line 809 `### Round 40 finality correction (...)`
   - 821, 822, 823 <- line 817 `### Round 41 measurements (...)`
   - 832 <- line 828 `### Round 41 capability rows (appended)`
4. `git -C <lane> ls-tree -r --name-only bf618f6c…` filtered by `/<token>$` — candidate sets:
   - `c2-after.txt`: rounds 36, 37, 38, 39, 40, 41 (six matches; R2 round selection is load-bearing)
   - `c3-after.txt`: rounds 36–41 (six matches; same)
   - `fixtures-after.txt`, `c2-after-d.txt`, `c3-after-d.txt`, `c2-after-h.txt`, `c3-after-h.txt`, `tip-remeasure.txt`: one match each
   - `controls/c1-control.txt`: `census/round-41/controls/c1-control.txt` only. (`census/round-40/records/c1-control.txt` and `census/round-41/waves/w2/R41w2scribe02/receipts/c1-control.txt` exist but do not end in `/controls/c1-control.txt`.)
   - `controls/c2-control.txt`, `controls/c3-control.txt`: one match each under round-41/controls.
5. `git -C <lane> show bf618f6c…:<resolved_to> | cat -n` and `grep -n` for SUMMARY/numeric lines in each resolved file (outputs below).
6. Per-token occurrence count on the SCORECARD line (`sed -n '<n>p' | grep -o -F <token> | wc -l`):
   772 c2-after.txt 1; 773 c3-after.txt 1; 792 fixtures-after.txt 1; 792 c2-after-d.txt **2**; 793 c3-after-d.txt **2**; 811 c2-after-h.txt 1; 811 c3-after-h.txt 1; 821 controls/c1-control.txt 1; 822 controls/c2-control.txt 1; 823 controls/c3-control.txt 1; 832 tip-remeasure.txt 1.
   Two-count rows match the register's two identical rows for 792 and 793.
7. Scratch `/fast/scratch/hyaku/souji-r42/R42scribe05` removed with `rm -rf`; follow-up `ls | grep -c R42scribe05` printed `0`. No tool installed; no PATH or ~/.local/bin change.

## Per-row table

Evidence: `path:line` quotes are from the base tree file; `SC<n>` = SCORECARD base line n.

| line | token | verdict | evidence |
|---|---|---|---|
| 772 | c2-after.txt | agree | SC772 cell: `-> legs=6 pass=6 fail=0 harm=0` (`c2-after.txt`). `census/round-39/records/c2-after.txt:9`: "SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484". Heading SC767 "Round 39". Round-39 is the only round the cell's heading selects. |
| 773 | c3-after.txt | agree | SC773 cell: `mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7` (`c3-after.txt`). `census/round-39/records/c3-after.txt:7`: "SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5". Exact. |
| 792 | fixtures-after.txt | agree | SC792 cell: "`SUMMARY cases=9 pass=6 fail=3` (`fixtures-after.txt`; the r39 control misses `--root` on the continuation line)". `census/round-40/records/fixtures-after.txt:34`: "SUMMARY cases=9 pass=6 fail=3". Line 28: "case-frozen-pairs-present=FAIL missing=['RECORD-OUTSIDE-ROOT(--root)']", matching the note. |
| 792 | c2-after-d.txt (1st) | agree | SC792 cell: "`SUMMARY legs=7 pass=7 fail=0 harm=0` (`c2-after-d.txt`)". `census/round-40/records/c2-after-d.txt:11`: "SUMMARY legs=7 pass=7 fail=0 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741". The cell's "fixture joined 9/9, one-line control 6/9" is in `fixtures-after.txt:23` ("SUMMARY cases=9 pass=9 fail=0") and `:34`, not in c2-after-d.txt. |
| 792 | c2-after-d.txt (2nd) | agree | Second mention on SC792 is the closure commit receipt "`549d9ec…` (`c2-after-d.txt`)". Same file, same line 11 evidence. |
| 793 | c3-after-d.txt (1st) | agree | SC793 cell: "`SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8` rc 0 (`c3-after-d.txt`)". `census/round-40/records/c3-after-d.txt:8`: "SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e". Exact. |
| 793 | c3-after-d.txt (2nd) | agree | Second mention on SC793 is the closure receipt "(`c3-after-d.txt`)". Same file, same line 8. |
| 811 | c2-after-h.txt | agree | SC811 text: "`c2-after-h.txt` (`legs=7 pass=7 fail=0 harm=0`)". `census/round-40/records/c2-after-h.txt:11`: "SUMMARY legs=7 pass=7 fail=0 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741". Exact. The `-d` and `-h` files carry identical numbers; the token is an exact basename, so the `-h` file is named. |
| 811 | c3-after-h.txt | agree | SC811 text: "`c3-after-h.txt` (`mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8`)". `census/round-40/records/c3-after-h.txt:8`: "SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8". Exact. |
| 821 | controls/c1-control.txt | agree | SC821 cell: "`items=3 mismatched=3 corrected=0 uncorrected=3 junk=0` (do-nothing), junk lesson `junk=3` (`controls/c1-control.txt`)". `census/round-41/controls/c1-control.txt:6`: "SUMMARY items=3 mismatched=3 corrected=0 uncorrected=3 junk=0 rewritten=0 sourced=0". `:13`: "SUMMARY items=3 mismatched=3 corrected=0 uncorrected=3 junk=3 ...". Exact. Round-40 homonym `census/round-40/records/c1-control.txt` (FORGE-TOKEN receipt) is not the match: heading is Round 41. |
| 822 | controls/c2-control.txt | agree | SC822 cell: "tool absent: `pass=0`; always-clean stub `pass=2` of 21". `census/round-41/controls/c2-control.txt:4`: "SUMMARY cases=21 pass=0 fail=21 ... tool_sha=absent". `:31`: "SUMMARY cases=21 pass=2 fail=19 control_clean=REJECTED ...". Exact. |
| 823 | controls/c3-control.txt | agree | SC823 cell: "fixture absent; all-PASS stub survives 19/19". `census/round-41/controls/c3-control.txt:4`: "... fixture_sha=absent" with "survived=19". `:8`: "PRISTINE ok rc=0 probes=21 ... summary=(21, 21, 0)" (all-PASS stub). `:28`: "SUMMARY sites=19 probes=21 pristine=ok killed=0 survived=19 ...". Exact. |
| 832 | tip-remeasure.txt | agree (weak: name-only) | SC832 cell "freeze check" row, evidence "`census/round-41/records/c2-after-hardened.txt`; `tip-remeasure.txt`", quotes no number. `census/round-41/records/tip-remeasure.txt:14-15`: "== freeze-check real" / "SUMMARY claims=3 findings=0". The file is the only tree path with that basename, and it has a freeze-check section. The match rests on name plus section label, not a quoted number. |

## Counts

Derivation rules: no disagree row, so no derivation-rule defect in chunk 5.
Load-bearing: rule R2 (round selection from the nearest `Round N` heading) is required for `c2-after.txt` and `c3-after.txt` (six candidates each across rounds 36–41). Without it, rule R3 yields an ambiguous set. Rules R1 and R4 do not apply to these rows.

## Verdict

All 13 rows resolve to the file the SCORECARD cell names. Calibration of this chunk: PASS. The one soft spot is 832, which quotes no number; its agreement rests on the unique filename and a freeze-check section.

agree=13 disagree=0 cannot-tell=0
