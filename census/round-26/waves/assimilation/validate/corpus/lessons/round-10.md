# Round 10 — gate record
Declared: close the r9 defect classes and certify the toolchain.
Outcome: **REJECTED on O1 — 3 residual unsafe outcomes (one class:
census --compare accepts empty/near-empty prior censuses); certification
NOT granted.** Delta: >=16 open classes at r9 close -> 1 class at r10
close; 121 conservative refusals across 15 corpora.

## What landed

- tools/cand-merge-* composed from 7 cluster pairs (A-G) and INSTALLED
  over the S17 tools (selftests 40/51/91 green). All r9 fix classes
  verified closed by the certifier except the census-compare contract.
- The certifier ran 15 corpora/reproducer suites (S05..S24, final-21..24,
  selftest, fresh variants): unsafe 3, all census-contract, originals
  preserved in every case (contract violation, not data loss).
- Hyper lane tested for the operator: functional but ~14 min/agent —
  functionally unusable for batch work; r10 completed on
  devin/deepseek-v4-1-flash-max per the session fallback.

## r11 carry

Fix the census --compare empty-prior contract (refuse empty/near-empty
with exit != 0), re-run the certifier's 15 suites, and only then flip
the SCORECARD certification to CERTIFIED.
