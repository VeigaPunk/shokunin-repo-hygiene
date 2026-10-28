# R41w2mutationtester04 — R1 mutant extension (falsify)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin · tip 1d41c13574db80fdd9a4bde490b712da7ce2a85f
Target: `tools/souji-worktree-drift.py` (pristine sha256 b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6, matches `PRISTINE_SHA256`)
Fixtures scored separately: r39 `tests/fixtures/r39-drift-record-rules.py`, r40 `tests/fixtures/r40-drift-record-branches.py`, r41 `tests/fixtures/r41-drift-record-order.py` (all read from tip with `git show`, read-only).
Kill contract (r1-counter.py): fixture `SUMMARY cases=… fail>0`, exit 1, no Traceback on fixture stderr.
Tools used: python 3.14.8, git 2.56.0 (no installs). No candidate was written into tests/, tools/, census/, corpus/, SKILL.md or any tracked file. Scratch `/fast/scratch/hyaku/souji-r41/R41w2mutationtester04` is deleted after copying receipts.

## Helpers (seat dir)
- `mutate-r1.py` — 24 single-line mutants (X01–X24) of the pristine tool; anchors checked for exactly one occurrence; each mutant compiled; run against r39, r40, r41 separately. Table of anchors/replacements is in its `MUTANTS` list.
- `probe-survivors.py` — for each survivor, a scratch fleet that exercises the mutated line; compares pristine vs mutant (rc + output). Distinguishes equivalent mutants from coverage gaps.
- `receipts/` — `run-final.txt` (24-mutant × r39/r40/r41 run), `results.json` (per-fixture rc/cases/fail/failing names), `probe-final.txt`, `r1-counter-tip.txt`, `prior-run.txt` (same mutants vs r36/r37/r38a/r38b), `SHA256SUMS`.

## Commands run (exact) and output
1. `git -C …/souji-shokunin show <tip>:tools/souji-worktree-drift.py` (inside harness) → pristine sha match=True.
2. `python3 -B …/.ufo/waves/round-41/w2/R41w2mutationtester04/mutate-r1.py --scratch /fast/scratch/hyaku/souji-r41/R41w2mutationtester04` →
   ```
   pristine tool sha256=b2a603cf…3ab3e34dc6 match=True
   PRISTINE r39:cases=7,fail=0,rc=0,clean=True r40:cases=8,fail=0,rc=0,clean=True r41:cases=12,fail=0,rc=0,clean=True
   SURVIVE-ALL-THREE X01,X02,X03,X08,X09,X10,X11,X12,X13,X14,X18,X19,X21,X22,X24
   KILLED-COUNT 9/24
   ```
   (full table: receipts/run-final.txt)
3. `python3 -B …/probe-survivors.py --scratch …` → receipts/probe-final.txt (14 of the 15 survivors distinguished; X24 not).
4. `python3 -B …/census/round-41/r1-counter.py --root <lane> --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f --scratch …` → exit 0,
   `SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6 cases=12 tool_sha=b2a603cf4247 fixture_sha=a2880a914106` (receipts/r1-counter-tip.txt). This reproduces the frozen R1 target, so the harness kill semantics agree with the counter.
5. Same mutants against the prior drift fixtures (r36, r37, r38-record, r38-write-envelope): receipts/prior-run.txt. NOTE: that run's column headers are hard-coded `r39/r40/r41`; the cells there are r36/r37/r38a. The `by` column is authoritative.

## Kill matrix (24 mutants; kill = contract above)
| id | mutant (tool line at tip) | killed by |
|---|---|---|
| X04 | repo_path direct branch returns None (L211) — positive control | r39, r40, r41 |
| X05 | `if not args.skip_unrecorded` inverted (L377) | r40, r41 |
| X06 | discovery `if name not in recorded` → always (L379) | r39, r41 |
| X07 | `live_recorded += 1` dropped (L370) — SUMMARY live_repos | r41 |
| X15 | RECORD-EMPTY refusal removed (L175) | r39 |
| X16 | TOTAL regs checked with `<` (L179) | r41 |
| X17 | TOTAL repos checked with `>` (L177) | r40, r41 |
| X20 | REGS-CHANGED only when live > record (complement of X10; L373) | r41 |
| X23 | root-basename fallback returns None (L213) | r41 |
| X01, X02, X03, X08, X09, X10, X11, X12, X13, X14, X18, X19, X21, X22, X24 | — | **none** |

Killed by the trio: 9/24. Survive all three: 15/24.

## Survivors of r39/r40/r41 — observability (probe-final.txt)
| id | survivor | probe: pristine vs mutant | observable? |
|---|---|---|---|
| X01 | symlinked child skip removed (L225-228) | pristine `SUMMARY … drift_rows=0`; mutant `DRIFT UNRECORDED ext`, drift_rows=1, rc 0/1 | yes — gap |
| X02 | worktree-style `.git` file not discovered (L231) | pristine `UNREACHABLE wt`, rc 1; mutant no row, rc 0 | yes — gap |
| X03 | direct branch ignores `.git` file (L210) | pristine `UNREACHABLE wt`; mutant `ABSENT wt` | yes — gap |
| X08 | live_regs takes record figure (L371) | pristine live_regs=1; mutant live_regs=5 | yes — gap |
| X09 | PRUNABLE-CHANGED never emitted (L375) | pristine `DRIFT PRUNABLE-CHANGED alpha record=1 live=0`; mutant none | yes — gap |
| X10 | REGS-CHANGED only when live < record (L373) | live=2 record=1: pristine `REGS-CHANGED`; mutant none | yes — gap (direction) |
| X11 | `worktree list` rc ignored (L195) | shim-fails-list: pristine `UNREACHABLE:list-rc=1`; mutant `REGS-CHANGED live=0` | yes — gap (probe uses PATH shim in scratch) |
| X12 | `worktree prune --dry-run` rc ignored (L202) | shim-fails-prune: pristine `UNREACHABLE:prune-rc=1`; mutant `PRUNABLE-CHANGED record=0 live=1` | yes — gap (PATH shim) |
| X13 | drift rows not sorted (L391) | pristine ABSENT zeta before REGS-CHANGED alpha; mutant reverse | yes — gap |
| X14 | duplicate REPO name accepted (L161) | pristine rc 2 RECORD-MALFORMED; mutant rc 0 | yes — gap |
| X18 | SUMMARY drift_rows subtracts unreachable (L401) | pristine drift_rows=2; mutant drift_rows=1 | yes — gap |
| X19 | SUMMARY record_regs sums prunable (L396) | pristine record_regs=1; mutant record_regs=0 | yes — gap |
| X21 | live_prunable not accumulated (L372) | pristine live_prunable=1; mutant 0 | yes — gap |
| X22 | RECORD-OUTSIDE-ROOT gitdir refusal disabled (L316) | pristine rc 2 `RECORD-OUTSIDE-ROOT: esc gitdir…`; mutant rc 1 with UNRECORDED alpha | yes — gap (documented refusal class, docstring L51) |
| X24 | root inserted at end of discovery (L234) | identical output | **no — equivalent** (drift is sorted before printing) |

Result: 14 non-equivalent survivors of the trio, all distinguished by a concrete scratch fleet.

## Cross-check vs prior committed fixtures (prior-run.txt)
Killed by r36/r37/r38 among the 15 trio-survivors: X02, X03, X08, X09, X14, X18, X19, X21 (X02/X03/X08/X09/X18/X19/X21 by r36/r37; X14 by r38-record). Survive r36–r41 (all committed fixtures): **X01, X10, X11, X12, X13, X22** (+ X24 equivalent). X17 is killed only by r40/r41 (it survives r36–r38); X23 is killed only by r41 (it survives r36–r38).

## Prediction record (falsification)
Predictions were written before the first run. Mismatches: X06 (predicted r41; r39 also kills — its `good` case reports the two recorded repos as UNRECORDED), X10 (predicted r41; the battery has no live>record REGS-CHANGED case, only the complement X20 is killed). All other 22 predictions matched. The 5 mutants added after the first run (X20–X24) were predicted before their run and all five matched; X24 is equivalent (predicted none, observed none; probe identical).

## Verdict
- Harness verdict: PASS. Pristine is clean on all three fixtures; the control X04 is killed by all three; the counter's own target SUMMARY reproduces on the tip; every mutant compiles and changes the file (anchor count 1).
- Coverage verdict (the falsification): the record/discovery/measure region is NOT covered by the frozen r39–r41 trio. 14 observable, non-equivalent single-defect mutants survive it (X01, X02, X03, X08, X09, X10, X11, X12, X13, X14, X18, X19, X21, X22), and 6 survive every committed fixture r36–r41 (X01, X10, X11, X12, X13, X22). Most consequential: X22 (the documented gitdir RECORD-OUTSIDE-ROOT containment refusal has no assertion anywhere) and X01 (symlink skip, a documented r37 A2.7 guard).
- This does not falsify the frozen R1 counter target (it measures M11–M21 only); it bounds what R1 claims. No admission-blocking finding for C1–C3 from this item.
- [INFERENCE] X11/X12 are scored on a PATH-shim git (scratch only); a real-git failure that exercises those branches was not constructed.
