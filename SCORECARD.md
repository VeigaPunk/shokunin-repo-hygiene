# souji-shokunin — SCORECARD

Axes (fleet `AXES.md`): the lane owns **calibration, operability,
coverage**. Following the kotodama precedent, rows carry per-axis verdicts
and checkable observations plus a 0–10 score only where a reproducible
mapping from evidence to number exists. Every observation carries its
counting command and the commit it was measured against.

## Axes

| axis | score | verdict / observation | counting command | measured commit | last change |
|---|---|---|---|---|---|
| coverage | 8 | improved (C1, r3): 21/21 metadata prunes executed with receipts (lore 20→1, gd2d 6→4, lock-preserve for 3 pinned); worktree surface closed | `git -C lore-shokunin worktree list \| wc -l` → 1; `git -C game-dev-2d-shokunin worktree list \| wc -l` → 4 | r3 report | r3 |
| calibration | 6 | improved (C2, r3): 0/21 blind-pair disagreements; 96-row approval list re-verified, 0 false-SAFE; 3 blockers adjudicated pre-execution | `census/round-3/seat-57.json` disagreements:[]; `wc -l census/round-3/operator-approval-list.tsv` → 97 (hdr) | r3 report | r3 |
| operability | 7 | unchanged (no claim, r3) — souji-verify in production use by approval seats | `bash tools/souji-verify.sh --selftest; echo $?` → 0 | 9435e46 | r2 |

## Capabilities

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| fleet census (receipt taxonomy) | classify every fleet artifact into pushed / moved-to-obsidian / stale / none with per-row command evidence, at 64-seat parallelism, dry-run | `census/round-1/census-summary.json`, `census/round-1/census.tsv` (246 rows) | r1 |
| souji-verify | per-artifact SAFE/NOT-SAFE verdict from receipts, D1–D3 fixed, --selftest over F1–F10 fixtures, read-only, secrets-refusal | `tools/souji-verify.sh` (sha256 7efda63bd760…), `tests/results/INSTALL.json`, `tests/results/parent-harness-live.json` | r2 |
| worktree metadata prune | selective prune with lock-preserve of pinned registrations; receipts re-verified at act time | `census/round-3/seat-61.json` (plan), `census/round-3/seat-62.json` (lore assertions), LOG r3 | r3 |

## Planned

- **r4 (operability, capability):** Obsidian-CLI integration per
  `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md` — ledger-backed
  moved-to-obsidian verification via the official CLI (read-only vault
  access; sha256sum fallback). All session deepseek-v4.1-flash dispatches route to
  devin/deepseek-v4-1-flash-max (operator directive, post-r3; supersedes the
  hyper lane for r4/r10).
- **r5 (verification round, all axes):** audit rounds 1–4 verdicts and
  outputs for correctness and missed items, folded into the round's own
  claims. Carry-overs: the 96-row approval list awaits operator sign-off;
  the 3 pinned gd2d registrations await that lane's push; `/tmp` fixture
  residue (~2,100 r2 dirs) routed to tsukuroi/operator.

## Saturation / stagnation

Saturation line: 8 per axis; stagnation window 3 rounds. Coverage 8,
operability 7, calibration 6 — calibration lowest; r5 verification work
carries the calibration flavor.

## Retired

None.
