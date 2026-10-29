# R42scribe04 — C1 chunk4 verification (13 `resolved` register rows)

Scope: verify that each `resolved` row of `c1-chunk4.tsv` (SCORECARD.md at base `bf618f6c5c09d302994871c94903abbea2deb60d`) names the committed file the register's `resolved_to` points to. Read-only: no register, SCORECARD, census, corpus or tool file was edited. No git mutation was run.

## Commands run (all read-only; base blob reads only)

```
cat .ufo/waves/round-42/w1/inputs/c1-chunk4.tsv            # 13 rows (12 distinct lines; line 762 and 763 carry two tokens each)
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show bf618f6c5c09d302994871c94903abbea2deb60d:SCORECARD.md > $S/sc.md
sed -n '<L>p' $S/sc.md                                      # for L in 710 712 721 722 725 731 732 733 761 762 763
awk 'NR<=763 && /^#/' $S/sc.md                              # heading index (nearest "Round N" heading per line)
git -C <lane> ls-tree -r --name-only bf618f6c5c09d302994871c94903abbea2deb60d > $S/tree.txt   # 10436 paths
grep -E "(^|/)<token>$" $S/tree.txt                         # tree matches per token
git -C <lane> show bf618f6c5c09d302994871c94903abbea2deb60d:<resolved_to> > $S/f/<resolved_to>   # 13 record files
grep -nE 'SUMMARY|cases=|mutants=|cells=|mismatches=|legs=|items=|REFUSAL|rc' <each file>
```
(`$S` = `/fast/scratch/hyaku/souji-r42/R42scribe04`, deleted before yield; `<lane>` = `/home/vgpnk/Projects/shokunin/souji-shokunin`. No `/tmp` path is cited.)

Derivation check: the nearest `Round N` heading above each line is 706 (Round 38) for lines 710–712, 718 (Round 38) for 721–725, 729 (Round 38) for 731–733, and 757 (Round 39) for 761–763. In the tree, every token except `c1-after.txt`, `c2-before.txt`, `c2-after.txt`, `c3-before.txt`, `c3-after.txt` has exactly one match; those five have 3–6 matches across rounds 36–41, and the round-N filter of R2 leaves exactly one in each case (`census/round-39/records/...`).

## Per-row table

| line | token | verdict | evidence |
|---|---|---|---|
| 710 | c2-after5.txt | agree | SCORECARD:710 "`c2-after5.txt` (`cases=12 pass=12 fail=0 base_cases=12 base_fail=6`"; `census/round-38/records/c2-after5.txt:4` "SUMMARY cases=12 pass=12 fail=0 base_cases=12 base_fail=6 behavioral_fail=3"; file header names 4bda5f67 = SCORECARD:706 measurement revision |
| 712 | c3-after4.txt | agree | SCORECARD:712 "`c3-after4.txt` (`cases=10 pass=10 fail=0`; `mutants=4 killed=4 survived=0 pristine=ok"; `census/round-38/records/c3-after4.txt:2` "SUMMARY cases=10 pass=10 fail=0"; `:8` "SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0" |
| 721 | c1-vacuity6.txt | agree | SCORECARD:721 ends "`c1-vacuity6.txt`", SCORECARD:722 "(`mismatches=9`, rc 1)"; `census/round-38/records/c1-vacuity6.txt:2` "SUMMARY cells=10 mismatches=9", `:3` "rc=1"; header = cb5737a6 (SCORECARD:718 block) |
| 722 | c2-after6.txt | agree | SCORECARD:722 "`c2-after6.txt` (`cases=12 pass=12 fail=0 base_cases=12 base_fail=6`"; `census/round-38/records/c2-after6.txt:4` "SUMMARY cases=12 pass=12 fail=0 base_cases=12 base_fail=6 behavioral_fail=3", `:5` "rc=0" |
| 725 | a7-counter-fixes2.txt | agree (caveat: cell quotes no number) | SCORECARD:725 "`a7-counter-fixes2.txt` (the three counter first-falsifications refused at this revision)"; `census/round-38/records/a7-counter-fixes2.txt:1` header "A7 evidence (final) at cb5737a6 — the three counter first-falsifications"; three non-zero runs: `:4` SUMMARY cells=1 mismatches=2 + `:5` rc=1; `:8` SUMMARY cells=1 mismatches=2 + `:9` rc=1; `:10` "REFUSAL USAGE: register ... is not a regular file" + `:11` rc=2. Note: the file holds four `MISMATCH` lines in two failing runs, so "three" counts the three refused runs, not the MISMATCH lines |
| 731 | c1-after8.txt | agree | SCORECARD:731 "`c1-after8.txt` (`cells=10 mismatches=0`, rc 0)"; `census/round-38/records/c1-after8.txt:1` "# C1 after (filed) at 99efe0676f439309a52f001b71bf0ba2ed8af47f", `:2` "SUMMARY cells=10 mismatches=0", `:3` "rc=0" |
| 732 | c2-after7.txt | agree | SCORECARD:732 "`c2-after7.txt` (`cases=12 pass=12 fail=0 base_cases=12 base_fail=6 behavioral_fail=3`, rc 0)"; `census/round-38/records/c2-after7.txt:3` same SUMMARY, `:4` "rc=0"; header 99efe067 = SCORECARD:729 "Final tip 99efe06" |
| 733 | c3-arms-filed.txt | agree | SCORECARD:733 "`c3-arms-filed.txt` (`cases=10 pass=10 fail=0`; `mutants=4 killed=4 survived=0 pristine=ok"; `census/round-38/records/c3-arms-filed.txt:2` "SUMMARY cases=10 pass=10 fail=0", `:3` "SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0" |
| 761 | c1-after.txt (census/round-39/records/c1-after.txt) | agree | SCORECARD:761 "`SUMMARY items=16 open=0 register_cells=6 register_mismatches=0 commit_distinct=6` rc 0 (`c1-after.txt`)"; `census/round-39/records/c1-after.txt:20` "SUMMARY items=16 open=0 register_cells=6 register_mismatches=0 commit_distinct=6", `:21` "# rc=0" |
| 762 | c2-before.txt (census/round-39/records/c2-before.txt) | agree | SCORECARD:762 "`SUMMARY legs=6 pass=2 fail=4 harm=0` rc 1 (`c2-before.txt`)"; `census/round-39/records/c2-before.txt:10` same SUMMARY, `:11` "# rc=1" |
| 762 | c2-after.txt (census/round-39/records/c2-after.txt) | agree | SCORECARD:762 "`SUMMARY legs=6 pass=6 fail=0 harm=0` rc 0 (`c2-after.txt`)"; `census/round-39/records/c2-after.txt:9` same SUMMARY, `:10` "# rc=0" |
| 763 | c3-before.txt (census/round-39/records/c3-before.txt) | agree | SCORECARD:763 "`SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10` rc 1 (`c3-before.txt`"; `census/round-39/records/c3-before.txt:8` same SUMMARY, `:9` "# rc=1" |
| 763 | c3-after.txt (census/round-39/records/c3-after.txt) | agree | SCORECARD:763 "`SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7` rc 0 (`c3-after.txt`)"; `census/round-39/records/c3-after.txt:7` same SUMMARY, `:8` "# rc=0" |

## Derivation-rule finding

No row disagrees. For all 13 rows the frozen R2 rule (nearest `Round N` heading, then the unique tree path ending in `/<token>` that contains `round-N/`) names the same file the SCORECARD cell quotes. Every one of the five ambiguous round-39 tokens (`c1-after.txt`, `c2-before.txt`, `c2-after.txt`, `c3-before.txt`, `c3-after.txt`) has 3–6 same-name files in other rounds, so R2 is the rule doing the disambiguation there. The round-38 tokens have a single tree match each. No rule defect surfaced in this chunk.

## Verdict

13 of 13 `resolved` rows in chunk4 are AGREE with the cited base-blob evidence. Caveat on line 725 only: the cell names the file by its claim, not by a number, and I judged it on the file's header and three refused runs.

agree=13 disagree=0 cannot-tell=0
