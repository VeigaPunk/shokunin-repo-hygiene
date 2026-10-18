# Round 1 — census gate
Candidates: all census rows.
Admitted: C1 (coverage), C2 (calibration).
Rejected: none.
Spot-check: critic seat S63 attacked 6/6 author SAFEs (all overturned);
blind seats S54–S61 re-derived 21 targets independently; parent re-derived
all 132 unique SAFE proposals (109 pushed loop + 23 worktree/stray checks).

## Template defects found (fix before r2)

- D1: receipt procedure hardcoded `origin/main`; fleet default branch is
  `origin/master` (`git symbolic-ref refs/remotes/origin/HEAD` or
  `for-each-ref` must resolve it). Blind seats hit this and stopped at
  "pushed-unverifiable" for pushed files.
- D2: the "unreachable → NOT-SAFE" rule is for file artifacts. For
  worktree metadata seats, an absent dir + unique=0 + no dirty state IS
  the prune condition. r2's tool must branch on artifact kind.
- D3: reference sweeps (`rg -l <basename> <repo>`) must exclude
  `souji-shokunin/census/**` — the census records basenames and
  self-pollutes the zero-references condition (this falsified 5 author
  SAFEs this round).

## Calibration measurement

Author first-pass SAFE precision: 0/6. Non-author catch rate: 6/6
(critic) + parent re-derivation of the full table. Final admitted table:
0 false-SAFE among 132 unique proposals. This is the baseline the
calibration axis now measures against.
