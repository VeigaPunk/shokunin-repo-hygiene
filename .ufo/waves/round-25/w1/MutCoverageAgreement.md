# MutCoverageAgreement — C1 coverage-agreement tool clause mutants

Seat: L1Souji25.MutCoverageAgreement (mutation-tester, wave 1). Item: mutate the
coverage-agreement tool clauses; score each mutant against the r24 fixture (9 cases) and the
draft r25 fixture (16 cases incl. k1–k7); report the survivor set after the kill-rule arm lands;
check the always-zero emitter control. Drafts scored: ExecC1's `w1/souji-coverage-agreement.py`
(sha256 `bb506469…d12f27f`) and `w1/r25-coverage-agreement.py` (`2a65d8c…225a0407`). Baseline:
committed tool bytes at a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe (extracted via `git show`,
sha256 `71b89eb3…b8f28897`, 160 lines). Scratch `/var/tmp/souji-r25-MutCoverageAgreement/`
(git/python3/sha256sum/diff only; no tools installed, no pacman).

## Status
STATUS: PASS — 14 single-clause mutants scored against both fixtures; 12 killed by at least one
fixture; survivors after the kill-rule arm lands = **M04, M06** (r25 16/16 on both). Always-zero
emitter control and veto-less control both rejected (`FALSE-GREEN-REJECTED`) in every run.

## Evidence
All commands run from the lane root; fixture runner `python3 -B <fixture> --tool <path>`, rc +
last line captured. Result files in `/var/tmp/souji-r25-MutCoverageAgreement/results/`.

- Baseline vs r24: rc 0, `cases=9 pass=9 control=FALSE-GREEN-REJECTED`.
- Draft vs r24: rc 0, `cases=9 pass=9 control=FALSE-GREEN-REJECTED` (no regression).
- Draft vs r25: rc 0, `cases=16 pass=16 control=FALSE-GREEN-REJECTED`.
- Baseline vs r25 (red arm): rc 1, `cases=16 pass=9`; k1–k7 all FAIL (`counts_lines=0 exit=2`
  — old tool refuses `--base-rev`).
- Always-zero emitter control (r25 fixture `CONTROL_SRC`): every `control case=N … -> FAIL`
  (16/16, incl. `case=9 exits=[0,0,0]`) → `FALSE-GREEN-REJECTED`; same in r24 (9/9).
  Veto-less control (k7) rejected on k1/k2 (`counts_lines=0 exit=0` → not-ok → rejected).
- Mutant generation: exact-string substitution on the draft, each replacement asserted to occur
  exactly once; per-mutant sha256 prefixes: M01 5fdf8cca, M02 2ba01a8c, M03 ebb8af3b,
  M04 1f4b6cf0, M05 decc00f5, M06 3e1e2f80, M07 69d5d366, M08 803929a8, M09 8bd5e399,
  M10 dd44a086, M11 78357277, M12 1954bc96, M13 9438cd4e, M14 c3d1f3f0.

### Kill table (mutant | clause defect | r24 kills? | r25 kills? | failing cases)
| Mutant | Defect | r24 (9) | r25 (16) | Failing cases |
|---|---|---|---|---|
| M01 | drop FRONT_GROUND front-matter parse (never matches) | YES 1/9 | YES 1/16 | r24: 1–8; r25: 1–8,k1–k7 |
| M02 | drop GROUND_TOKEN map-row prefix match (never matches) | YES 1/9 | YES 2/16 | r24: 1–8; r25: 1–8,k2–k7 |
| M03 | GROUND_TOKEN boundary: drop end-of-string alternative (`F7` bare cell not a token) | YES 8/9 | YES 15/16 | 6 (both) |
| M04 | swap mapped/mismatch counting (`mapped += len(missing)`) | NO 9/9 | NO 16/16 | — survivor |
| M05 | drop DANGLING-MAP-PATH check | YES 8/9 | YES 15/16 | 5 (both) |
| M06 | break kill-rule existence clause (`kind != "blob"` → never) | NO 9/9 | NO 16/16 | — survivor |
| M07 | break same-F clause (`not base_ks <= got` → never) | NO 9/9 | YES 14/16 | k2,k5 |
| M08 | ignore extra ground lines (subset → equality) | NO 9/9 | YES 15/16 | k6 |
| M09 | exit 0 ignores `kill_violations` | NO 9/9 | YES 13/16 | k1,k2,k5 |
| M10 | `kill_tested` counts violated entries, not base-grounded | NO 9/9 | YES 12/16 | k3,k4,k6,k7 |
| M11 | base knowledge tree read at `--rev` instead of `--base-rev` | NO 9/9 | YES 9/16 | k1–k7 |
| M12 | drop `knowledge/` path constraint (any trailing token is a knowledge path) | YES 2/9 | YES 9/16 | 1,2,3,5,6,7,8 (both) |
| M13 | map detection: every 3-column table is a coverage map (header check dropped) | YES 8/9 | YES 15/16 | 2 (both) |
| M14 | accept non-full-40-hex revisions (refusal check dropped) | YES 8/9 | YES 15/16 | 9 (both) |

Kill = fixture rc ≠ 0 / `pass < C`; survivors = full-pass (rc 0).

## Findings
1. **Survivor M04 — `mapped` is unasserted by both fixtures.** Both `Case.expect_text`
   implementations emit `mapped=*` (r24 fixture `tests/fixtures/r24-coverage-agreement.py`,
   `expect_text` `mapped=*`; draft `w1/r25-coverage-agreement.py` `Case.expect_text`
   `mapped=*`). A wrong-direction mapped counter (M04 changes `mapped` from 1 to 0 on clean
   cases) passes r24 9/9 and r25 16/16. The counters line carries the value but no frozen case
   checks it; a future tool could ship a wrong `mapped` silently.
2. **Survivor M06 — the kill-rule existence clause is not independently enforced.** Dropping
   `if kind != "blob"` (M06) leaves k1 still detected because the same-F subset branch fires
   when a deleted entry's rev-ground set is empty (`base_ks <= got` false). The only observable
   lost is the MISMATCH detail text (`rev=absent` vs `lost=F2 rev_grounds=none`), which
   `score()` discards (it compares class + basename + counts). k1–k7 all pass under M06.
   If the existence clause is contractual (distinct row semantics), the frozen fixture cannot
   discriminate its removal; a detail assertion or a case where only the detail differs would.
3. **Kill-rule arm value confirmed.** All kill-clause mutants (M06–M11) are invisible to r24
   (9/9) and killed by r25 except the two survivors above; baseline (no `--base-rev`) fails all
   seven k-cases. The arm adds exactly the kill-specific discrimination it claims.
4. M03/M05/M13/M14 are detected by both fixtures; M12 (knowledge-path constraint) is the only
   mutant where the r25 arm adds no new detection over r24 (same failing case set).

## Attack log
None proposed. The two survivors are coverage findings, not contracts to change; no predicate,
target or case set is suggested for re-specification (C1 kill rule: no case dropped or
re-specified after scoring — respected; these runs were read-only against the lane).
