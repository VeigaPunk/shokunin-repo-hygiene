# R42scribe02 — C1 register verification, chunk 2 (13 rows)

Scope: `.ufo/waves/round-42/w1/inputs/c1-chunk2.tsv` (13 `resolved` rows of `census/round-42/c1-register.tsv`). Base `bf618f6c5c09d302994871c94903abbea2deb60d`. Lane read-only: only `git show`, `git ls-tree` and `ls-tree` style reads against the base; the register was not edited; no git mutation; no candidate written outside this report.

## Method and commands run

1. `cat .ufo/waves/round-42/w1/inputs/c1-chunk2.tsv` — the 13 rows.
2. `sed -n '1,80p' census/round-42/c1-counter.py` — derivation rules R1–R4 (docstring).
3. `git -C <lane> show bf618f6c…:SCORECARD.md > sc.md`; for each line `awk 'NR<=n && /^#/ {h=NR": "$0} NR==n'` to get the line and nearest heading above it. Result: heading for lines 221 is `## Planned` (line 177, no `Round` token, so R2 cannot supply C); 314 `### Round 29`; 424 `### Round 31`; 478/487/489 `### Round 32`; 512/513 `### Round 33`; 525 `### Planned (appended at round 33)` (line 523, R1 token); 540 `### Round 34`; 666 `### Round 38`.
4. `git -C <lane> ls-tree -r --name-only bf618f6c… > tree.txt` (10436 paths) and `grep -E "(^|/)<token>$" tree.txt` per token. Result (candidate sets):
   - `git-grace-periods-and-expire-to.md`: 3 paths (`.ufo/waves/round-26/…/corpus/knowledge/…`, `census/round-26/waves/assimilation/validate/corpus/knowledge/…`, `corpus/knowledge/…`).
   - `excluded.tsv`, `symlinks.tsv`: 1 each (`census/round-26/waves/`).
   - `c3-after-c3-counter-v2.txt`, `-v3.txt`: 1 each (`census/round-31/records/`).
   - `SwarmExecutor08.md`: 5 copies (rounds 28, 29, 31, 32 w1, 32 a2w1).
   - `SwarmCritic34.md`: 1 (`census/round-32/waves/w1/`).
   - `SwarmCritic26.md`: 5 copies (rounds 30, 31 w2, 32 a2w1, 33 w1, 34 w2).
   - `c1-at-c2-repair.txt`, `c2-at-repair.txt`: 1 each (`census/round-33/records/`).
   - `make-spec-w2.py`: 5 copies (rounds 30–34 `waves/`).
   - `controls.txt`: 2 (`census/round-33/records/`, `census/round-34/records/`).
   - `c1-vacuity2.txt`: 1 (`census/round-38/records/`).
5. Read the resolved file at base (`git -C <lane> show bf618f6c…:<resolved_to>`), `grep -n` for the quoted tokens (SUMMARY lines, commit hashes, `2.56.0`, `RESULT`, `mixed`, `ignored`), and `sed -n 'Np'` for exact lines. Also `sha256sum` of the three `git-grace-periods-and-expire-to.md` copies (all `f80e8c7ee4f9593dbc6b24d41142e1c2680f70bd8c4eafcf7de196f1536727f6`).
6. Counted the wave-2 items of `census/round-33/waves/make-spec-w2.py` without writing: the script's `spec = {` write is at its line 90 and the `w2-spec.json` write is at line 91, so I exec'd only the text before `\nspec = {` in a scratch copy with a dummy `sys.argv` (4 values). Output: `n= 37 roles= {'critic': 13, 'executor': 6, 'mutation-tester': 5, 'reviewer': 5, 'sentinel': 1, 'scout': 4, 'connector': 2, 'simplifier': 1} flash= 21 attack= 23` and `C2F keys= ['O1', 'O2', 'O3', 'O4', 'O5'] ROWLINE= 5`. Confirmed `ls …/round-33/w2-spec.json` → absent (nothing was written to the lane).
7. `grep -c "exit 2" census/round-34/records/controls.txt` → `0`.

## Per-row table

`line | token | verdict | evidence` (SC = SCORECARD.md at base; file paths are base paths)

| line | token | verdict | evidence |
|---|---|---|---|
| 221 | git-grace-periods-and-expire-to.md | agree | SC:221 (under `## Planned`, SC:177) asks to "re-verify the two remaining git-2.55.0 entries (…, `git-grace-periods-and-expire-to.md`) on 2.56.0". `corpus/knowledge/git-grace-periods-and-expire-to.md:37`: "this entry was verified on 2.55.0 and has not been re-verified on 2.56.0. Treat it as pending recheck". Derivation note: R2 cannot fire (nearest heading has no `Round`), R3 finds 3 paths, R4 picks `corpus/knowledge/`. The two round-26 copies are byte-identical (same sha256), so the pick does not change the content cited. |
| 314 | excluded.tsv | agree | SC:314 (`### Round 29`, SC:309) "ignored names accounted in `excluded.tsv`" for the r29 capture of `census/round-26/waves` (SC:314 "`census/round-26/waves` `records=1381 failed=0 uncovered=0`"). `census/round-26/waves/excluded.tsv:3`: `assimilation/validate/tools/__pycache__/souji-axis-check.cpython-314.pyc … ignored`. R2 finds no `round-29/` copy and falls to R3, which is unique. |
| 314 | symlinks.tsv | agree | SC:314 "symlinks in `symlinks.tsv`". `census/round-26/waves/symlinks.tsv:1` header `# path target`, `:2` `assimilation/validate/tests/vault/mock-cli/obsidian-cli	obsidian`; 18 lines. Same capture target as above. |
| 424 | c3-after-c3-counter-v2.txt | agree | SC:424 (`### Round 31`, SC:418) "v2 `fail=11` -> `legs=12 fail=0` (`c3-after-c3-counter-v2.txt`)". File `:14`: `SUMMARY legs=12 fail=0 f1_entries=4 rev=1baf4da02b71b012ee2426ea7c309496c0c3aca0`. |
| 424 | c3-after-c3-counter-v3.txt | agree | SC:424 "v3 `legs=13 fail=0`". File `:15`: `SUMMARY legs=13 fail=0 f1_entries=4 rev=1baf4da02b71b012ee2426ea7c309496c0c3aca0`. |
| 478 | .ufo/waves/round-32/a2w1/SwarmExecutor08.md | agree | R1 → `census/round-32/waves/a2w1/SwarmExecutor08.md` (the other four copies are other waves). SC:478 cites "two wave a2w1 full runs at the landing commit … read `pass=25 fail=2` (T12, T18)" and landing `98e5203d45b4e419a9e72801733d93303acc7ebd`. File `:7`: "C2 at its landing commit `98e5203d45b4e419a9e72801733d93303acc7ebd` re-measures **25/27 PASS, T12 and T18 FAIL** in two independent full runs". |
| 487 | SwarmCritic34.md | agree | SC:487 (`### Round 32`) "(w1 `SwarmCritic34.md`)" for the clone-local-scratch cheat. Only copy in tree is `census/round-32/waves/w1/SwarmCritic34.md`. File `:43`: "2. **Cheat A — clone-local scratch passes.** Scratch under `tools/../.selftest-scratch` inside the clone". `:21` carries `SUMMARY items=27 pass=1 fail=26`, matching SC:487. |
| 489 | SwarmCritic26.md | agree | SC:489 (`### Round 32`) "Literal-prefix: a mixed record with a `RESULT:` line passes (a2w1 `SwarmCritic26.md`)". R2 with C=32 leaves only `census/round-32/waves/a2w1/SwarmCritic26.md`. File `:83`: "near-prefix smuggling `RESULT_`, `RESULT:`, leading space, lowercase, each with one conforming `RESULT` line present → tool `bad=0` exit 0". |
| 512 | c1-at-c2-repair.txt | agree | SC:512 (`### Round 33`) names the repair commit `a7c35c24bdd8bae5cff9766ace02a81915756701` (`c1-at-c2-repair.txt`) and "`SUMMARY items=24 agree=24 mismatches=0 restated=5` at … the C2 repair commit". File `:2` `--rev a7c35c24bdd8bae5cff9766ace02a81915756701`; `:27` `SUMMARY items=24 agree=24 mismatches=0 restated=5 rev=a7c35c24bdd8bae5cff9766ace02a81915756701`. |
| 513 | c2-at-repair.txt | agree | SC:513 names repair commit `a7c35c24bdd8bae5cff9766ace02a81915756701` (`c2-at-repair.txt`). File `:14`: `SUMMARY legs=11 pass=4 fail=1 harm=1 rev=a7c35c24bdd8bae5cff9766ace02a81915756701`. Identity is right. The cell quotes no repair-commit numbers, and its `pass=3 fail=2 harm=0` belongs to the landing receipt (`c2-at-landing.txt`, not in this file). Note: the repair receipt itself reads `harm=1`; the cell does not claim otherwise. |
| 525 | .ufo/waves/round-33/make-spec-w2.py | agree | R1 → `census/round-33/waves/make-spec-w2.py` (the four other copies are rounds 30/31/32/34). SC:525 (`### Planned (appended at round 33)`) "run the 37 unrun wave-2 attack items (`.ufo/waves/round-33/make-spec-w2.py`)". Exec count (command 6 above) gives `n= 37`. Note on wording: only 23 of the 37 are attack-type roles (critic 13, reviewer 5, mutation-tester 5); the rest are executor, scout, connector, sentinel, simplifier. "attack" is a loose label for the wave, not a numeric error. |
| 540 | controls.txt | agree | R2 with C=34 (SC:535 `### Round 34 measurements`) → `census/round-34/records/controls.txt` (the round-33 copy is excluded by the round clause). File `:9`: "C2 repaired feasibility … SUMMARY legs=13 pass=9 fail=4 harm=0; rc=1", matching SC:540. Caveat: the cell's clause "CNE exit 2 at base because census/round-34 legs absent at base" does not appear in this file (`grep -c "exit 2"` → 0). Identity is right; that clause is not evidenced by the cited file. |
| 666 | c1-vacuity2.txt | agree | SC:666 (`### Round 38`) "the vacuity control reads `mismatches=9`, rc 1 (`c1-vacuity2.txt`)". File `:11`: `SUMMARY cells=10 mismatches=9`; `:1` "register row 1 expected token replaced by mismatches=99". The rc 1 is not in the file. |

## Counts

agree=13 disagree=0 cannot-tell=0

## Derivation-rule observations (no disagreement found)

- R2 cannot fire where the nearest heading is not a `Round` heading (row 221: `## Planned`, SC:177). R3 then has 3 candidates (round-26 copies included) and falls to R4. The R4 pick is the canonical `corpus/knowledge/` entry and the copies are byte-identical, so the result is correct here, but the rule order leaves the choice to R4 by fallthrough.
- R2's "contains `round-<C>/`" clause rejects the only real target for rows 314 (`excluded.tsv`, `symlinks.tsv`), which live under `census/round-26/waves/` while the heading says Round 29. R3 is unique and correct here.
- R1 picks the round-matching copy for the `.ufo/waves/round-N/` tokens (478, 525); the R2 `/waves/` tie-break handles the SwarmCritic34/26 cases; no row resolved to a wrong round copy.

## Verdict

All 13 chunk-2 `resolved` rows name the file the SCORECARD cell means. Row 540 is agree on file identity, with its "CNE exit 2 at base" clause unevidenced in the cited file; row 525 is agree with the "attack" label being loose. No register row was edited. Lane untouched. Scratch dir `/fast/scratch/hyaku/souji-r42/R42scribe02` removed before yield.

agree=13 disagree=0 cannot-tell=0
