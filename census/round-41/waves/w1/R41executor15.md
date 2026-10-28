# R41executor15 — R1 candidate r41-drift-record-order.py

Verdict: PASS (target SUMMARY reached, exit 0).

Candidate: `.ufo/waves/round-41/w1/R41executor15/r41-drift-record-order.py`
- sha256 `3c4f0adde2be125e9b272838fd6df5daf6ade3766e84c0161331475113749e05`, 9370 bytes, 14 cases.
- Style follows tests/fixtures/r40-drift-record-branches.py (`--tool`/`--work`, `case-<name>=PASS|FAIL`, `SUMMARY cases= pass= fail=`).
- Case groups:
  - M19: 5 cases with a disagreeing TOTAL first, middle or before the rows and an agreeing last TOTAL (repos, regs, prunable variants), plus an all-agree arm.
  - M20: a fleet whose root is a git repository (UNRECORDED row reported, with and without `--skip-unrecorded`), and a plain-directory root (no UNRECORDED).
  - M21: a record row naming the root basename (measured at a git root, REGS-CHANGED at a git root, ABSENT at a plain root), and an unrelated-name row (ABSENT).

Command run (scratch `/fast/scratch/hyaku/souji-r41/R41executor15`, cwd inside it):
`bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-41/score-candidate.sh r1 /fast/scratch/hyaku/souji-r41/R41executor15 tests/fixtures/r41-drift-record-order.py=<candidate path above>`

Observed output:
```
MUTANT M11 owner=r39-drift-record-rules.py killed=yes by=r39-drift-record-rules.py failing=trailing-space
MUTANT M12 owner=r39-drift-record-rules.py killed=yes by=r39-drift-record-rules.py failing=crlf
MUTANT M13 owner=r39-drift-record-rules.py killed=yes by=r39-drift-record-rules.py failing=outside-root
MUTANT M14 owner=r39-drift-record-rules.py killed=yes by=r39-drift-record-rules.py failing=indented-comment
MUTANT M15 owner=r40-drift-record-branches.py killed=yes by=r40-drift-record-branches.py,r41-drift-record-order.py failing=total-conflicting-second
MUTANT M16 owner=r40-drift-record-branches.py killed=yes by=r40-drift-record-branches.py,r41-drift-record-order.py failing=good,total-duplicate-identical,skip-unrecorded-suppresses,invalid-utf8-in-comment
MUTANT M17 owner=r40-drift-record-branches.py killed=yes by=r40-drift-record-branches.py failing=invalid-utf8-in-repo-name
MUTANT M18 owner=r40-drift-record-branches.py killed=yes by=r40-drift-record-branches.py,r41-drift-record-order.py failing=total-repos-disagrees
MUTANT M19 owner=r41-drift-record-order.py killed=yes by=r41-drift-record-order.py failing=total-first-repos-disagrees-last-agrees,total-first-regs-disagrees-last-agrees,total-first-prunable-disagrees-last-agrees,total-middle-disagrees-first-and-last-agree,total-before-rows-disagrees-later
MUTANT M20 owner=r41-drift-record-order.py killed=yes by=r41-drift-record-order.py failing=root-repo-unrecorded-reported
MUTANT M21 owner=r41-drift-record-order.py killed=yes by=r41-drift-record-order.py failing=root-repo-unrecorded-reported,root-repo-recorded-not-unrecorded,root-basename-row-measured-at-root,root-basename-row-regs-changed-at-root
SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6 cases=14 tool_sha=b2a603cf4247 fixture_sha=3c4f0adde2be
EXIT=0
```

Notes: M15/M16/M18 are also killed by the r41 fixture; that is allowed (the retention rule only constrains the old fixtures and the novelty rule only M19-M21). Scratch dir deleted (verified absent). No tools installed. No tracked file touched.
