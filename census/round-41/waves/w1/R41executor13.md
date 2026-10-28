# R41executor13 — R1 candidate r41-drift-record-order.py

Candidate: .ufo/waves/round-41/w1/R41executor13/r41-drift-record-order.py
sha256: a2880a91410611c7ed8bd6c472957f88745e3c61d9044e1ba3ff53386a47d234
bytes: 8226

## Cases (12)
M19 (TOTAL order): total-agreeing-pair (pos), total-first-bad-repos, total-first-bad-regs, total-first-bad-prunable, total-middle-bad, total-before-rows-then-bad
M20 (root dropped from discovery): root-unrecorded-reported, root-unrecorded-suppressed-by-flag (pos), root-recorded-not-unrecorded (pos)
M21 (root-basename row): root-basename-row-measured, root-basename-row-live-figure, other-basename-absent (pos: fallback is exact)
Root arms use a --root that is itself a git repo (basename `rootrepo`) holding child `alpha`; no r39/r40 fixture uses a repo root.

## Command
cd /fast/scratch/hyaku/souji-r41/R41executor13 && bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-41/score-candidate.sh r1 /fast/scratch/hyaku/souji-r41/R41executor13 tests/fixtures/r41-drift-record-order.py=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41executor13/r41-drift-record-order.py

## Output (key lines)
MUTANT M19 killed=yes by=r41-drift-record-order.py failing=total-first-bad-repos,total-first-bad-regs,total-first-bad-prunable,total-middle-bad,total-before-rows-then-bad
MUTANT M20 killed=yes by=r41-drift-record-order.py failing=root-unrecorded-reported
MUTANT M21 killed=yes by=r41-drift-record-order.py failing=root-unrecorded-reported,root-recorded-not-unrecorded,root-basename-row-measured,root-basename-row-live-figure
(M15, M16, M18 are also killed by the r41 fixture; allowed: only M19-M21 novelty is gated and old_fixtures_killed_new=0.)
SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6 cases=12 tool_sha=b2a603cf4247 fixture_sha=a2880a914106
EXIT=0

## Verdict
PASS: target SUMMARY reached, exit 0. Scratch dir removed. No tools installed. Frozen files untouched.
