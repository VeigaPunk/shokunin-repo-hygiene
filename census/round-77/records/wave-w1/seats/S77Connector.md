# S77Connector: Cross-claim separation and sibling-overlap scan for round 77
### 1. Causal Separation: SEPARABLE
- Command: `git show --name-only 9b496b0883 6690cb5ad9 8bf42fc623` && `grep -hE '^(instrument=|# bind)' census/round-77/{records,controls}/*.txt`
- Output: W touches only `tools/souji-pre-report-gate.sh`; K touches 14 `.ufo/waves/{round-63,round-64}` files; L touches `c2-pointer-ledger.tsv`.
- Evidence: C1 receipts bind gate (28a51355), writer (70bbf1c2), counter (e511bd57); 0 C2 bytes read. C2 receipts bind counter (8904de85), pop (bbc19ac6), ledger (011faa0e), pointer-check (8987a95c); 0 gate bytes read. C1 verifies with K,L absent; C2 with W absent.

### 2. Other Lane Tools Calling Git Without Timeout/Guard (r77 pre-check covers gate only)
- tools/souji-receipt-write.py:159-162 `git()` no timeout: ls-files (177,273,325,587,714), check-attr (182), hash-object (302), status (364,603,715) [HIGH]
- tools/souji-verify.sh:377,421 (status), 834 (ls-files) no timeout, no nonreg guard [MEDIUM]
- tools/souji-vault-verify.sh:550,594 (status), 1033 (ls-files) no timeout, no nonreg guard [MEDIUM]
- tools/souji-record-agreement.py:114,351 (status) no timeout, no nonreg guard [MEDIUM]
- tools/souji-quarantine.sh:235,1149 (ls-files) no timeout, no nonreg guard [LOW]

### 3. Sibling Overlap: Pre-Report Gates & Uncommitted .ufo/waves Pointers
| lane | pre-report gate git status call | exposed | uncommitted .ufo/waves | exposed |
|---|---|---|---|---|
| kaidoku | tools/round-42/prefile-gate.py:109-113 (no timeout, no guard) | YES [HIGH] | 49 / 1032 | YES [MEDIUM] |
| tabi | scripts/check-selfassessment.mjs:482 (no timeout, no guard) | YES [HIGH] | 13 / 463 | YES [MEDIUM] |
| kama | tools/pre-report-gate.py:666 (60s timeout, no guard) | YES [MEDIUM] | 67 / 945 | YES [MEDIUM] |
| kasegi | corpus/instruments/r46-landing-gate.py:79 (60s timeout, no guard) | YES [MEDIUM] | 23 / 427 | YES [MEDIUM] |
| kumitate | scripts/round-gate.mjs:587 (120s timeout, no guard) | YES [MEDIUM] | 34 / 369 | YES [MEDIUM] |
| mori | tools/mori-unlanded-check.py:38 (120s timeout, no guard) | YES [MEDIUM] | 15 / 890 | YES [MEDIUM] |
| tsukuroi / kake / mado / kengaku / tameshi | no status in gate | NO | 103, 73, 43, 16, 10 | YES [MEDIUM] |
| kotodama / revenger / lore / kotoba / chousa | no status in gate | NO | 9, 8, 3, 2, 21 | YES [MEDIUM] |
| audio / game-dev-2d / game-dev-3d / kagi | no status in gate | NO | 0 (all committed/none) | NO |

Files written under seat directory: .ufo/waves/round-77/w1/S77Connector.md
