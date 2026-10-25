# Round 26 (2026-10-25) — calib/census integration, gate decision

Round 26 ran three claims: C1 (calibration) integrated the r24 scaffold
payloads into SCORECARD.md; C2 admitted two grounded F1 knowledge entries and
registry rows S128-S132; C3 built `tools/souji-axis-check.py` with a
11-case FALSE-GREEN-controlled fixture. This file records the gate decision,
the re-grounding receipts, and the fixable residuals left for later rounds.

## Gate

The r25 registry's staged S-language-edition row (zh/ja docs, a vendor page)
was checked against the build's edition boundaries. What passed: the en
`git-fetch(1)` manual (opened from `git-scm.com/docs/git-fetch`), the
v2.56.0 tag sources (fetched snapshots in `census/round-26/sources/`, bound
by `SHA256SUMS`), and the en `git(1)` pages already in the corpus. What was
refused: the zh/ja docs (their version alignment with 2.56.0 on the mirrors
was not provable and the pages' own build stamps were ambiguous) and the
vendor page (it quoted an older 2.16.x-era workflow; parsing it to an
argument would have silently changed the claim's public surface).

Admitted rows instead re-ground the *en* single source of truth: S128
(`git-fetch(1)` § OPTIONS switches), S129 (five v2.56.0 call sites of
`run_auto_maintenance`), S130 (`builtin/pull.c` spawns `fetch`, so pull
inherits fetch's trigger), S131 (the campaign's measured prune fixture,
re-grounded byte-for-byte by sha256) and S132 (the fleet worktree census,
0 prunable / 5 registrations). S131/S132 are own-work tier A per the source
registry contract: the lane's re-runnable gate output, re-run in r26 by
sha256 verification rather than by re-executing the campaign fixture.

## Findings

- The r25 "0 prunable, 3 locked" fleet census is history: S132 re-checks to
  **5 registrations, 0 prunable, 0 locked** even at `--expire=now`. The
  fleet is *currently* unexposed — but the mechanism (fetch/pull/merge/
  rebase auto-maintenance) is live on five surface commands.
- The r24 scaffold's Round 24 measurements block was never landed (the r24
  attempt was cut off). The r25 heading order therefore violated the file's
  own newest-first contract; C1 landed the block and reordered headings to
  round-25 < round-24 < round-23.
- Replacement "C1 kill-rule vs positional line numbers": the frozen claim's
  kill rule named base line ranges, but the integration the K2 counter
  demands moves the protected byte spans. Amendment 2 (accepted pre-data in
  session) clarified the regions are byte-content spans, and the post-edit
  byte-diff of each protected span against the committed base is empty. The
  counter (`census/round-26/c1-counter.sh`) verifies the *order* of the
  headings; the margin of C1 is the byte-diff, recorded in the report.
- The R3 receipt-label pitfall (from the r25 gate): the receipt's `tool`
  binds the labelled file's committed bytes *and* the argv label. The c3
  counter's `--stub` arm is a separate labelled file commit, so the control
  receipt's `tool_sha256` legitimately differs from the main receipts';
  each receipt's label is its own argv element, so
  `receipt-run --tool` accepts all three.

## Residuals

- R-r26-1: `git maintenance run` strategy/task scope (which tasks run under
  which strategy) remains unmeasured; only the trigger and the per-command
  opt-out are held. The recheck command for S128 is in the entry's
  `recheck:` line and re-greps the call sites at the next host git tag.
- R-r26-2: the two stage candidate rows remain un-cited (see Gate). If the
  edition boundary of the zh/ja mirrors becomes provable on a later release,
  the S-language row can be reconsidered; it must then be cited with the
  version-stamp evidence rather than as a paraphrase.
- R-r26-3: keep-ref expiry (the `keep` ref option) is still not measured —
  the trigger set covers expiry via `gc.worktreePruneExpire`, not via the
  keep-ref guarantee. See `git-auto-maintenance-trigger-set.md` for the
  claim boundary.

## Receipts

- `census/round-26/records/c1-after.tsv` (a529c76, markers=0, order
  17<44<78) + byte-diff annex in the round report.
- `census/round-26/records/c2-before.tsv` (base 89e0fce: F1=0, rows=127),
  `c2-after.tsv` (d6c13b0: F1=2, rows=132), real gate rc=0.
- `census/round-26/records/c3-before.tsv` (tool absent), `c3-after.tsv`
  (flags=0 at tip d2e6253), `c3-control.tsv` (FALSE-GREEN-REJECTED, rc=1).
