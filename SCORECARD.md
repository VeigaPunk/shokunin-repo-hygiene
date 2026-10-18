# souji-shokunin — SCORECARD

Axes (fleet `AXES.md`): the lane owns **calibration, operability,
coverage**. Following the kotodama precedent, rows carry per-axis verdicts
and checkable observations plus a 0–10 score only where a reproducible
mapping from evidence to number exists; a score no reader can re-derive is
an opinion. Every observation carries its counting command and the commit
it was measured against.

## Axes

| axis | score | verdict / observation | counting command | measured commit | last change |
|---|---|---|---|---|---|
| coverage | 7 | improved (claim C1, r1): 4 evidence instances → 246 census rows: 109/109 b2f2efa files classified, 24/24 worktrees re-derived, 18 lane recon rows, kotodama set, 6 fleet dirs | `python3 -c "import csv;print(sum(1 for _ in csv.DictReader(open('census/round-1/census.tsv'),delimiter='\t')))"` → 246; `wc -l < census/round-1/census.tsv` → 247 (hdr) | 652b6f8 | r1 |
| calibration | 5 | improved (claim C2, r1): author first-pass SAFE precision 0/6; non-author catch 6/6 (critic seat) + parent re-derivation; final table 0 false-SAFE among 132 unique SAFE proposals | `python3 -c "import json;print(json.load(open('census/round-1/census-summary.json'))['author_stage'])"`; final-table check: parent loop in census-summary.json `b2f2efa_pushed_verified` 109/109 | 652b6f8 | r1 |
| operability | 0 | no runnable tool yet — planned r2 (tools/souji-verify.sh, must return NOT-SAFE on kotodama, fixture self-test) | — | — | mint |

## Capabilities

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| fleet census (receipt taxonomy) | classify every fleet artifact into pushed / moved-to-obsidian / stale / none with per-row command evidence, at 64-seat parallelism, dry-run | `census/round-1/census-summary.json`, `census/round-1/census.tsv` (246 rows) | r1 |

## Planned

- **r2 (operability):** `tools/souji-verify.sh` — verdict from the receipt
  taxonomy with defects D1–D3 fixed (default-branch resolution, worktree
  kind branch, sweep excludes census dir); must return NOT-SAFE on
  kotodama's unpushed/dirty state; fixture `--selftest`.
- **r3 (coverage):** prune the 21 SAFE(metadata-prune) worktree
  registrations (19 lore + r80-baseline + r81-frozen; commits untouched)
  + deliver the operator approval list for the 109 pushed files and 2
  root strays. The 3 gd2d named-branch worktrees stay NOT-SAFE until
  game-dev-2d pushes (cross-domain observation filed).
- **r4 (operability, capability):** Obsidian-CLI integration per
  `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md`.

## Saturation / stagnation

Saturation line: 8 per axis; stagnation window 3 rounds. Not near
saturation; operability is the lowest axis and r2 works it.

## Retired

None.
