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
| calibration | 7 | improved (V1, r5): verification round found 3 material defects (symlink false-SAFE class; local-master pushed fallback; r1 logs_tier row) — all corrected in-round with re-run evidence; 0 unresolved | `census/round-5/final-57..64.json`; lessons/round-5.md; probes in r5 report | r5 report | r5 |
| operability | 8 | improved (O1', r4): tools/souji-vault-verify.sh live — ledger+sha256 moved-to-obsidian verification, parent battery 4/4 + real-vault probe VERIFIED, self-referential rows refused | `bash tools/souji-vault-verify.sh --selftest; echo $?` → 0; `tests/results/parent-vault-battery.json` | r4 report | r4 |

## Capabilities

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| fleet census (receipt taxonomy) | classify every fleet artifact into pushed / moved-to-obsidian / stale / none with per-row command evidence, at 64-seat parallelism, dry-run | `census/round-1/census-summary.json`, `census/round-1/census.tsv` (246 rows) | r1 |
| souji-verify | per-artifact SAFE/NOT-SAFE verdict from receipts, D1–D3 fixed, --selftest over F1–F10 fixtures, read-only, secrets-refusal | `tools/souji-verify.sh` (sha256 7efda63bd760…), `tests/results/INSTALL.json`, `tests/results/parent-harness-live.json` | r2 |
| worktree metadata prune | selective prune with lock-preserve of pinned registrations; receipts re-verified at act time | `census/round-3/seat-61.json` (plan), `census/round-3/seat-62.json` (lore assertions), LOG r3 | r3 |
| ledger-verify (moved-to-obsidian receipt) | verify a ledger row's source + vault sha256 pairs read-only; refuses self-referential rows; --ledger override; obsidian-CLI probe path reserved (no usable CLI entry point on this host — banked for operator) | `tools/souji-vault-verify.sh` (sha256 d312263a…), `tests/results/parent-vault-battery.json`, LOG r4 | r4 |

## Planned

- **r4 — AMENDED by operator mid-round:** the Obsidian-CLI integration
  claim was withdrawn ("forget the obsidian integration for now"); closed
  instead on the standalone ledger-verify capability
  (`tools/souji-vault-verify.sh`, installed r4). Finding: no usable CLI
  entry point on this host — banked in
  `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md` for the operator.
  Completion-criterion obsidian-row requirement waived by the operator.
- **r5 (verification round, all axes):** audit rounds 1–4 verdicts and
  outputs for correctness and missed items, folded into the round's own
  claims (scheduled model: gpt-6-luna-max). Carry-overs: the 96-row
  approval list awaits operator sign-off; the 3 pinned gd2d registrations
  await that lane's push; `/tmp` fixture residue routed to
  tsukuroi/operator.

## Saturation / stagnation

Saturation line: 8 per axis; stagnation window 3 rounds. Scores per the
rows above: coverage 8, operability 8, calibration 7 (this prose formerly
said 6/7 — corrected r9 after the judges caught the drift).

## Tool certification (r9)

The verdict tools are PATCHED (r9 S17: 40/51/91 selftest checks) but NOT
certified for deletion authorization: r9 red-team replays still reproduce
unsafe deletions (>=16 open defect classes; see corpus/lessons/round-9.md).
Receipts are advisory until the r10 hardening closes the classes.

## Retired

None.
