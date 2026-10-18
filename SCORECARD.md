# souji-shokunin — SCORECARD

Axes (fleet `AXES.md`): the lane owns **calibration, operability,
coverage**. Scores are claims: each carries its counting command and the
commit it was measured against; a score no reader can re-derive is an
opinion, not a measurement. Initial scores are 0 — nothing is claimed
before a round measures it.

## Axes

| axis | score | evidence / verdict | counting command | measured commit | last change |
|---|---|---|---|---|---|
| calibration | 0 | no false-SAFE rate measured yet | to be defined r1 (spot-check sample over census verdicts) | — | mint |
| operability | 0 | no runnable tool yet | `tools/souji-verify.sh` to land r2 | — | mint |
| coverage | 0 | surfaces = 4 known instances; census table lands r1 | census TSV row count | — | mint |

## Capabilities

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| — | none yet | — | — |

## Planned

- **r1 (coverage, calibration):** dry-run census classifying every demand
  evidence instance (b2f2efa files, conf snapshot, 24 worktrees,
  kotodama `.scratch`) with receipts; zero false-SAFE under a non-author
  spot-check of the verdict table.
- **r2 (operability):** `tools/souji-verify.sh` — per-artifact SAFE /
  NOT-SAFE verdict from the receipt taxonomy; must return NOT-SAFE on
  kotodama's unpushed/dirty state (known trap); self-test over fixtures.
- **r3 (coverage):** prune the 24 dead worktree *metadata* entries +
  deliver root-scratch removal list for operator approval.

## Saturation / stagnation

Saturation line: 8 per axis; stagnation window 3 rounds. Recorded here per
`AXES.md`; not near saturation at mint.

## Retired

None.
