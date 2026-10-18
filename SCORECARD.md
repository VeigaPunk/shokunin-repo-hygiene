# souji-shokunin — SCORECARD

Axes (fleet `AXES.md`): the lane owns **calibration, operability,
coverage**. Following the kotodama precedent, rows carry per-axis verdicts
and checkable observations plus a 0–10 score only where a reproducible
mapping from evidence to number exists. Every observation carries its
counting command and the commit it was measured against.

## Axes

| axis | score | verdict / observation | counting command | measured commit | last change |
|---|---|---|---|---|---|
| coverage | 7 | improved (C1, r1): 4 evidence instances → 246 census rows: 109/109 b2f2efa files, 24/24 worktrees, 18 lane recon rows, kotodama set, 6 fleet dirs | `python3 -c "import csv;print(sum(1 for _ in csv.DictReader(open('census/round-1/census.tsv'),delimiter='\t')))"` → 246 | 652b6f8 | r1 |
| calibration | 5 | improved (C2, r1): author first-pass SAFE precision 0/6; non-author catch 6/6; final table 0 false-SAFE among 132 unique SAFE proposals | `census-summary.json` `author_stage` + `final_verdicts` | 652b6f8 | r1 |
| operability | 7 | improved (O1, r2): tools/souji-verify.sh runs per spec — selftest exit 0, 5/5 live targets, winner of 8-impl × 16-runner matrix | `bash tools/souji-verify.sh --selftest; echo $?` → 0; `bash tools/souji-verify.sh /home/vgpnk/Projects/shokunin/kotodama-shokunin` → NOT-SAFE | see r2 report | r2 |

## Capabilities

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| fleet census (receipt taxonomy) | classify every fleet artifact into pushed / moved-to-obsidian / stale / none with per-row command evidence, at 64-seat parallelism, dry-run | `census/round-1/census-summary.json`, `census/round-1/census.tsv` (246 rows) | r1 |
| souji-verify | per-artifact SAFE/NOT-SAFE verdict from receipts, D1–D3 fixed, --selftest over F1–F10 fixtures, read-only, secrets-refusal | `tools/souji-verify.sh` (sha256 7efda63bd760…), `tests/results/INSTALL.json`, `tests/results/parent-harness-live.json` | r2 |

## Planned

- **r3 (coverage):** prune the 21 SAFE(metadata-prune) worktree
  registrations (19 lore + r80-baseline + r81-frozen; commits untouched) +
  deliver the operator approval list for the 109 pushed files and 2 root
  strays. The 3 gd2d named-branch worktrees stay NOT-SAFE until game-dev-2d
  pushes (cross-domain observation filed).
- **r4 (operability, capability):** Obsidian-CLI integration per
  `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md` — ledger-backed
  moved-to-obsidian verification via the official CLI (read-only vault
  access; sha256sum fallback).

## Saturation / stagnation

Saturation line: 8 per axis; stagnation window 3 rounds. Coverage and
operability at 7; calibration at 5 is the lowest axis — r3/r4 should carry a
calibration-flavored check (r5 is the scheduled verification round).

## Retired

None.
