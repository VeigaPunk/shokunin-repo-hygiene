# R41executor14 — R1 candidate fixture (executor)

Candidate: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41executor14/r41-drift-record-order.py`
sha256 `fd10972f0a4f60e6b556bfdebb0f84cb92b96a1b510eb0f3c9b0a15e6b99b6b3`, 10387 bytes, 20 cases, `--tool/--work` protocol of r40 (`case-<name>=PASS|FAIL`, `SUMMARY cases= pass= fail=`, exit 0 iff fail=0).

## Cases (each with paired present/absent arm)
- M19 (every TOTAL checked): total-first-disagrees-last-agrees / total-first-agrees-last-agrees; total-middle-disagrees / total-three-agree; total-last-disagrees; total-before-rows-disagrees-last-agrees / total-before-rows-agrees / total-only-before-rows-agrees; total-between-rows-prefix-only / total-between-rows-superseded / total-after-all-rows-agree-three.
- M20 (root repo discovered): root-repo-unrecorded-reported / root-repo-unrecorded-suppressed (--skip-unrecorded) / root-repo-and-absent-recorded-name; absence arms plain-root-not-reported, plain-root-unrecorded-child-only. Forbidden-token checks assert nothing extra is reported.
- M21 (root basename row measured): root-basename-row-measured, root-basename-row-regs-changed; absence arms root-other-name-absent (ghost -> ABSENT), plain-root-basename-row-absent (non-git root -> ABSENT).

## Command run
`cd /fast/scratch/hyaku/souji-r41/R41executor14 && bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-41/score-candidate.sh r1 /fast/scratch/hyaku/souji-r41/R41executor14 tests/fixtures/r41-drift-record-order.py=<candidate>`

Observed (verbatim tail):
```
MUTANT M19 owner=r41-drift-record-order.py killed=yes by=r41-drift-record-order.py failing=total-first-disagrees-last-agrees,total-middle-disagrees,total-before-rows-disagrees-last-agrees,total-between-rows-prefix-only,total-between-rows-superseded
MUTANT M20 owner=r41-drift-record-order.py killed=yes by=r41-drift-record-order.py failing=root-repo-unrecorded-reported,root-repo-and-absent-recorded-name
MUTANT M21 owner=r41-drift-record-order.py killed=yes by=r41-drift-record-order.py failing=root-repo-unrecorded-reported,root-repo-and-absent-recorded-name,root-basename-row-measured,root-basename-row-regs-changed
SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6 cases=20 tool_sha=b2a603cf4247 fixture_sha=fd10972f0a4f
EXIT=0
```
M11-M14 killed only by r39, M17 only by r40 fixture; M15/M16/M18 also red in the r41 candidate (allowed: retention requires the owner kills; novelty only constrains M19-M21).

## Notes
Scratch dir removed. No tooling installed. Nothing under tests/, tools/, census/ touched.

## Verdict
PASS: target SUMMARY met, exit 0.
