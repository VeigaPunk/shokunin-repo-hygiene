# R42scribe03 — C1 chunk 3 verification (scribe)

Base: `bf618f6c5c09d302994871c94903abbea2deb60d`. Input: `.ufo/waves/round-42/w1/inputs/c1-chunk3.tsv` (13 `resolved` rows). Register not edited.
Scope: for each row, does SCORECARD.md line `<line>` at the base name the committed file `<resolved_to>` (agree), another same-name file (disagree), or can the cell not be tied to a file (cannot-tell)?

## Commands run and observed output

```
$ cat .ufo/waves/round-42/w1/inputs/c1-chunk3.tsv
line	token	class	resolved_to
666	c1-after2.txt	resolved	census/round-38/records/c1-after2.txt
667	c2-after2.txt	resolved	census/round-38/records/c2-after2.txt
667	c2-after2.txt	resolved	census/round-38/records/c2-after2.txt
668	c3-before.txt	resolved	census/round-38/records/c3-before.txt
668	c3-after2.txt	resolved	census/round-38/records/c3-after2.txt
668	c3-after2.txt	resolved	census/round-38/records/c3-after2.txt
673	consumers-after2.txt	resolved	census/round-38/records/consumers-after2.txt
699	c1-vacuity4.txt	resolved	census/round-38/records/c1-vacuity4.txt
700	c2-after4.txt	resolved	census/round-38/records/c2-after4.txt
701	c3-after3.txt	resolved	census/round-38/records/c3-after3.txt
702	consumers-after4.txt	resolved	census/round-38/records/consumers-after4.txt
702	a7-counter-fixes.txt	resolved	census/round-38/records/a7-counter-fixes.txt
709	c1-vacuity5.txt	resolved	census/round-38/records/c1-vacuity5.txt

$ git -C <lane> show bf618f6c…:SCORECARD.md | wc -l          -> 839
$ (per line n) awk 'NR<=n && /^#/ {h=NR": "$0} NR==n' SCORECARD.md
   666,667,668,673 -> nearest heading 662 "### Round 38 measurements (...)"  (C=38)
   699,700,701,702 -> nearest heading 695 "### Round 38 receipt pointer update (appended after wave 1, 2026-10-28)"  (C=38)
   709             -> nearest heading 706 "### Round 38 final receipt pointers (appended after wave 2)"  (C=38)

$ for t in <11 distinct tokens>; do grep -E "(^|/)$t\$" tree.txt; done   # tree = git ls-tree -r --name-only BASE
   every token: exactly one committed path in census/round-38/records/, except c3-before.txt:
   census/round-37/records/c3-before.txt, census/round-38/records/c3-before.txt, census/round-39/records/c3-before.txt
   (rule R2 keeps only the round-38 one, since the nearest heading is "Round 38")

$ sed -n '<line>p' SCORECARD.md   (token occurrences per line)
   666: c1-after2.txt x1 | 667: c2-after2.txt x2 | 668: c3-after2.txt x2, c3-before.txt x1
   673: consumers-after2.txt x1 | 699: c1-vacuity4.txt x1 | 700: c2-after4.txt x1
   701: c3-after3.txt x1 | 702: consumers-after4.txt x1, a7-counter-fixes.txt x1 | 709: c1-vacuity5.txt x1
   (matches the 13 chunk rows; c1-items.tsv carries the same 13 rows at 666..709 with result mismatch:path-absent)

$ git show bf618f6c…:census/round-38/records/c1-vacuity4.txt | cat -n | tail -3
   11 SUMMARY cells=10 mismatches=9
   12 rc=1
$ (head -1 of each receipt, at the base)
   c2-after4.txt : "# C2 after at 6949319e9e4dd6fa38c9c9f9d68bea09b6fde1cf (post-A4 drift tool)"
   c3-after3.txt : "# C3 after at 6949319e9e4dd6fa38c9c9f9d68bea09b6fde1cf (post-A5/A6)"
   a7-counter-fixes.txt : "# A7 evidence at 9b4432000f51ea28caa21e8f92df23e9a5d9a01e — ..."
```

The SCORECARD line text and the receipt text were read in full with `sed -n` and `git show … | cat -n`; the verdicts below rest on those reads. The frozen counter was not run; this is a per-row content check, not a counter result.

## Per-row table

Receipt pointers are `census/round-38/records/<file>:<line>` at the base.

| line | token | verdict | evidence |
|---|---|---|---|
| 666 | c1-after2.txt | agree | SCORECARD:666 cell `SUMMARY cells=10 mismatches=0`, rc 0, rev `2843805d…` ↔ `c1-after2.txt:3` "SUMMARY cells=10 mismatches=0", `:4` "rc=0", `:1` header "at 2843805d…". |
| 667 | c2-after2.txt (1st) | agree | SCORECARD:667 cell `SUMMARY cases=12 pass=12 fail=0 base_cases=12 base_fail=6`, rc 0 ↔ `c2-after2.txt:21` identical, `:22` "rc=0"; base arm FAIL lines `:15`–`:20` (six). Mechanism words (O_NONBLOCK, S_ISREG, JSON-IS-RECORD) are not in the receipt; not checked. |
| 667 | c2-after2.txt (2nd) | agree | Same line, second mention of the token; same file, same evidence. Two items, one path. |
| 668 | c3-before.txt | agree | SCORECARD:668 cell `mutants=4 killed=0 survived=4 pristine=ok` ↔ `c3-before.txt:7` "SUMMARY mutants=4 killed=0 survived=4 pristine=ok", `:8` "rc=1". The round-37 and round-39 same-name files are different receipts; the cell's heading is Round 38 (SCORECARD:662), so the round-38 file is the one named. |
| 668 | c3-after2.txt (1st) | agree | SCORECARD:668 cell `cases=10 pass=10 fail=0` and `mutants=4 killed=4 survived=0 pristine=ok base_killed=0`, rc 0 ↔ `c3-after2.txt:13`, `:19` identical, `:20` "battery_rc=0"; header `:1` at 2843805d. |
| 668 | c3-after2.txt (2nd) | agree | Same line, second mention; same file, same evidence. |
| 673 | consumers-after2.txt | agree | SCORECARD:673–674 cell "16/16, 14/14, 12/12, 6/6, 12/12 with base_fail=9 escapes=9, 21/21, 10/10" ↔ `consumers-after2.txt:3` 16/16, `:6` 14/14, `:9` 12/12, `:12` 6/6, `:15` "base_fail=9 escapes=9", `:18` 21/21, `:21` 10/10 (all `pass=…fail=0`). |
| 699 | c1-vacuity4.txt | agree | SCORECARD:699 cell `mismatches=9` ↔ `c1-vacuity4.txt:11` "SUMMARY cells=10 mismatches=9", `:12` "rc=1"; header `:1` rev 78ea25a, same as the cell's rev. |
| 700 | c2-after4.txt | agree (path); rev claim contradicted | SCORECARD:700 cell `cases=12 pass=12 fail=0 base_cases=12 base_fail=6 behavioral_fail=3` ↔ `c2-after4.txt:4` identical. But SCORECARD:697–698 says "every final receipt was re-measured at 78ea25a…"; `c2-after4.txt:1` says "at 6949319e…". Path correct, rev claim false. |
| 701 | c3-after3.txt | agree (path); rev claim contradicted | SCORECARD:701 cell `cases=10 pass=10 fail=0` and `mutants=4 killed=4 survived=0 pristine=ok base_killed=0` ↔ `c3-after3.txt:2` and `:8` identical, `:9` battery_rc=0. Header `:1` says "at 6949319e…", not 78ea25a as SCORECARD:697–698 claims. |
| 702 | consumers-after4.txt | agree | SCORECARD:702 names it; `consumers-after4.txt:1` "at 78ea25a… (final)" matches the cell rev; all SUMMARY lines `:3`–`:24` are pass/0 fail. The cell quotes no numbers. |
| 702 | a7-counter-fixes.txt | agree (path); rev claim contradicted | Unique path, SCORECARD:702 names it; the cell quotes no numbers. Header `a7-counter-fixes.txt:1` says "A7 evidence at 9b443200…", not the 78ea25a rev that SCORECARD:697–698 claims for "every final receipt". |
| 709 | c1-vacuity5.txt | agree | SCORECARD:709 cell `(mismatches=9)` ↔ `c1-vacuity5.txt:2` "SUMMARY cells=10 mismatches=9", `:3` "rc=1"; header `:1` rev 4bda5f67 matches the SCORECARD:708 sentence "Every claim was re-measured at 4bda5f67…". |

## Verdict on the derivation

- No row disagrees. Rule R2 (nearest heading round + unique path match) gives the file the cell names in all 13 rows. The one name with same-basename siblings (`c3-before.txt`, round-37 and round-39 copies) is resolved correctly because the nearest heading is "Round 38" (SCORECARD:662, and SCORECARD:668 below it).
- The derivation checks only that a path exists, not what the cell says about it. Three rows (700, 701, 702/a7) pass the derivation while their cells claim a revision that the receipts' own headers contradict (`6949319e…` and `9b443200…` versus the `78ea25a…` the SCORECARD states). These are calibration findings for the L1, not register disagreements. The counter is not built to catch them.

## Findings for L1

1. No `disagree` rows in chunk 3; the register's `resolved_to` values for these 13 rows are the files the cells name.
2. The SCORECARD:697–698 sentence ("every final receipt was re-measured at 78ea25a…") is false for three of the five receipts it lists (`c2-after4`, `c3-after3`, `a7-counter-fixes`), per their own headers. This is outside the path-resolution rule and is a content issue for the scorecard owner.
3. The `c2-after2` mechanism words in SCORECARD:667 (O_NONBLOCK, S_ISREG, JSON-IS-RECORD) do not appear in the receipt. I did not check them against the tool, so that part is unverified.

## Result

| line | token | verdict | evidence |
|---|---|---|---|
| 666 | c1-after2.txt | agree | see above |
| 667 | c2-after2.txt | agree | see above |
| 667 | c2-after2.txt | agree | see above |
| 668 | c3-before.txt | agree | see above |
| 668 | c3-after2.txt | agree | see above |
| 668 | c3-after2.txt | agree | see above |
| 673 | consumers-after2.txt | agree | see above |
| 699 | c1-vacuity4.txt | agree | see above |
| 700 | c2-after4.txt | agree | see above (rev claim contradicted) |
| 701 | c3-after3.txt | agree | see above (rev claim contradicted) |
| 702 | consumers-after4.txt | agree | see above |
| 702 | a7-counter-fixes.txt | agree | see above (rev claim contradicted) |
| 709 | c1-vacuity5.txt | agree | see above |

agree=13 disagree=0 cannot-tell=0

Verdict: all 13 chunk-3 `resolved` rows name the committed file the derivation picked. Three rows carry a revision claim that their receipts' own headers contradict; that is a finding for the scorecard, not a register disagreement. No tools were installed. The frozen counter was not run here.
