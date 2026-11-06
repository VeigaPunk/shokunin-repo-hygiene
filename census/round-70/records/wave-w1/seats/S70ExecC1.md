# S70ExecC1 — post-landing falsification of C1 (pathspec-variable scrub)

Verdict: **C1 REPRODUCED byte-for-byte** from committed bytes; every frozen number re-derived independently. No finding against C1. One LOW lane-hygiene note.

1) **C1 candidate** (cwd lane; `python3 -B census/round-70/c1-counter.py --root <lane> --matrix census/round-70/c1-matrix.tsv --base-rev e063a2fc --rev 93a051b2 --tool tools/souji-receipt-write.py --work <scratch>/c1`):
`SUMMARY matrix=59 base_forgeries=4 base_honest=13 new_forgeries=0 new_honest=15 class_mismatches=0 new_echo=0 errors=0 regress=PASS` / `EXIT=0`; `REGRESS base=PASS new=PASS` (both slots cases=8 pass=8 fail=0); 0 `new=error` rows.
Named rows (base->new, finding): LA acc->acc; LD acc->ref RECEIPT-INDEX-FLAG-CONCEALED; LN4 acc->ref same; LU1 ref->ref RECEIPT-INDEX-UNMERGED; LG1 acc->ref RECEIPT-GITLINK-CONCEALED; LA9 acc->ref RECEIPT-INDEX-CONCEALED-ABSENT; GA ref->acc; GD ref->ref FLAG-CONCEALED; NGA acc->acc; NGD ref->ref FLAG-CONCEALED; ICA ref->acc; ICD ref->ref FLAG-CONCEALED. Only GA and ICA were base over-refusals.

2) **`--new-tool` runs** (base.py = `git show e063a2fc:tools/souji-receipt-write.py`, sha256 b811ee2a…):
```
do-nothing    EXIT=1 new_forgeries=4 new_honest=13 class_mismatches=5 new_echo=0 errors=0 regress=PASS
F1            EXIT=1 new_forgeries=0 new_honest=11 class_mismatches=8 new_echo=0 errors=0 regress=PASS
F2            EXIT=1 new_forgeries=0 new_honest=13 class_mismatches=0 new_echo=0 errors=0 regress=PASS
```
F1 over-refuses LA/GA/NGA/ICA ("RECEIPT-ENV-PATHSPEC-SET"); its 8 class mismatches are LD LN4 LU1 LG1 LA9 GD NGD ICD. F2 leaves GA/ICA over-refused.

3) **Diffs of `^(CASE|REGRESS|SUMMARY|EXIT=)` lines vs receipts**: candidate vs `census/round-70/records/c1-after.txt` IDENTICAL (59 CASE + REGRESS + SUMMARY + EXIT); base vs `controls/c1-do-nothing.txt` IDENTICAL; F1 vs `controls/c1-F1-refuse-on-presence.txt` IDENTICAL; F2 vs `controls/c1-F2-literal-only-scrub.txt` IDENTICAL; candidate re-run at tip `feb283ee` (knowledge-file recheck form) vs c1-after.txt IDENTICAL.

4) **Independent recount** from CASE lines × `c1-matrix.tsv` (verdict + klass-in-stderr, not the counter's counters): cand `4/13/0/15 cm=0 echo=0 err=0`; base `4/13/4/13 cm=5` cm_rows=LD LN4 LU1 LG1 LA9; F1 `4/13/0/11 cm=8` cm_rows=LD LN4 LU1 LG1 LA9 GD NGD ICD; F2 `4/13/0/13 cm=0`, rows=59 each. Every SUMMARY field reproduces from the emitted rows.

5) **Chronology** (all rc=0): `git merge-base --is-ancestor` 0243af04->93a051b2, 93a051b2->e84f691, e84f691->0d8ce29, 0d8ce29->feb283ee. `git log --format='%H %ci' -1`: base 2026-11-05 17:34:21; freeze 11-06 15:49:38; candidate 15:50:28; after-arms 15:54:09; r69 mirror 15:54:29; tip 15:56:41 (-0300). `git diff --quiet e063a2fc 0243af04 -- tools/souji-receipt-write.py` rc=0; `git diff --quiet 0243af04 e84f691 -- census/round-70/{c1-counter.py,c1-matrix.tsv,c2-harness.py}` rc=0. Candidate commit touches only `tools/souji-receipt-write.py` (42+/1-, `PATHSPEC_ENV` scrub in `git()` + selftest `case_38_pathspec_env_scrubbed`); after-arms adds only the 4 receipts.
Hashes: counter 3f684c3e…bada, matrix 1607e4f8…7536, `srcs/git-manual.html` 534c674f…f9d1 (= S304's stated sha256), base writer b811ee2a…a725 (= prereg), candidate writer 118597e0…e71f (= c1-after `slot new`). Matrix has 59 data rows; rows 2..48 byte-identical to `census/round-69/c1-matrix.tsv` rows 2..48 (47 carried + 12).

6) **Mechanism confirmed outside the counter** (git 2.56.0; fixture toplevel verified == fixture dir): `ls-files -v -z ':(top)'` with a skip-worktree entry prints `S tools/instr.sh` under ambient/GLOB/NOGLOB/ICASE but **nothing under GIT_LITERAL_PATHSPECS=1 (rc 0)**; `ls-tree --name-only HEAD -- <path>` rc=0 ambient/LITERAL, rc=128 under GLOB and ICASE ("pathspec magic not supported"). Direct writer runs (base vs candidate, `--out` in scratch): LITERAL+skip-worktree base rc=0 receipt written (the forgery) / cand rc=2 FLAG-CONCEALED no receipt; GLOB and ICASE honest-clean base rc=2 "cannot read tree" / cand rc=0 receipt written; LITERAL and NOGLOB honest-clean accept on both — the fix removes both failure modes and adds no refusal. `--selftest`: `SELFTEST cases=29 pass=29 fail=0`, EXIT=0 (matches `records/counter-selftest.txt`).

## Findings
- **LOW (lane hygiene, outside C1):** lane worktree dirty during the wave — `git status --porcelain` = ` M SCORECARD.md`, `?? census/round-70/records/pointer-check-r70.txt` (earlier `?? tools/souji-pointer-check.py`). Not mine, untouched; SCORECARD.md is the L1's write set, so the L1 should confirm that tracked edit is intended before committing.
- No HIGH/MEDIUM finding: all five pred numbers, both control verdicts and the do-nothing verdict reproduce; no narrowing needed.

Commands: the preregistration's four counter invocations (+ `--selftest`, + one candidate re-run at `feb283ee`); `git merge-base --is-ancestor`, `git log --format='%H %ci' -1`, `git diff --quiet`, `git diff --name-status`, `git show <rev>:tools/souji-receipt-write.py | sha256sum`, `sha256sum`, `diff <(grep -E '^(CASE|REGRESS|SUMMARY|EXIT=)' …)`; fixture: `git -C "$D" init -q`, `update-index --skip-worktree`, `ls-files`/`ls-tree` probes, and a driver running base vs candidate writer with `--allow-outside` and `--out` in scratch. No lane tracked file edited, no git/jj mutation, no pacman, no tool installed.

Files written: `.ufo/waves/round-70/w1/S70ExecC1.md`; `.ufo/waves/round-70/w1/S70ExecC1/receipts/{c1-candidate-lines.txt,c1-base-summary.txt,c1-f1-summary.txt,c1-f2-summary.txt,independent-recount.txt,diff-results.txt,chronology.txt,mechanism-probe.txt}`.
