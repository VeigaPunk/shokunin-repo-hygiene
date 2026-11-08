source: S331 (own-work wave-directory census), S332 (kernel fs/proc/array.c at v6.17); census/round-83/c1-false-rows.tsv and census/round-83/c1-false-row-harness.py
verified-at: bbffe6a0d1221766b76acbf78c649a5783ac9def (2026-11-08)
recheck: python3 -B census/round-83/c1-false-row-harness.py --counter census/round-83/c1-pointer-counter.py --lane /home/vgpnk/Projects/shokunin/souji-shokunin --fleet-root /home/vgpnk/Projects/shokunin --work <empty dir outside /tmp>

# Own-tree pointer binding — real wave shapes and a per-branch remainder (r83)

## Claim

A pointer-resolution counter that binds a MOVED ledger target inside the token's own round tree needs two
different remainder comparisons, not one. The r82 rule asked for a capture shape (`waves/`, `wave/`,
`records/wave-<w>/`) followed by the token's WHOLE path below its round-<N>, and the lane's real wave trees are
`w1/` (65 dirs), `w2/` (19), `w3/`, `a2w1/` and `assimilation/` (4) — none named `waves/` — so it refused a
genuine own-tree move into a real wave directory while keeping the harness-planted `waves/a2w1/` shape
(census/round-83/records/wave-dirs.txt; r82 amendment A2, S82Connector2 F1).

## Rule

`_owntree_ok` (census/round-83/c1-pointer-counter.py) is true when the target's path below its round-<N> is one of:

1. the token's own path (unchanged), or
2. an r82 capture shape followed by the token's whole path below its round-<N> (the r82 branch, unchanged), or
3. a real wave directory — `w[0-9]+/`, `a2w1/`, `assimilation/`, or the r82 shapes — followed by the token's path
   below its OWN first component below the round (a full suffix, in order).

Branch 2 and branch 3 are both required: with branch 3 alone the r82 capture row TF4
(`.ufo/waves/round-32/waves/a2w1/SwarmExecutor08.md`) is refused (`refused_true=1`), and with branch 2 alone the
real `w2/`/`w1/` rows TF6/TF7 are refused (`mismatches=2`, the r82 counter's control). The frozen 36-row
population carries both poles and two refused decoys: NF-J (a duplicated middle dir under a real `w1/`) and NF-K
(a flattened copy at the round-tree root). `accepted=0 refused_true=0` is the only passing summary.

## What the decoys teach

- A flattened copy at the round-tree root is exactly what a suffix-only rule accepts: the token's below-round
  path `a2w1/X` has `X` as a suffix, and `round-32/X` "keeps the suffix". The wave-dir branch refuses it because
  the shape must be a wave directory and the remainder must keep the token's directory (`X` alone loses `a2w1`).
- A duplicated middle dir (`w1/a2w1/X`) keeps the token's whole below-round path as a suffix; it is refused for
  the same reason, and it is the row that separates the identity clause from a suffix-only rule (r82 A5's
  unresolved gap, now measured).

## Limits (stated, not claimed away)

- A move into `.ufo/waves/round-<N>/records/` or the other non-wave dirs the lane has (`residual/`, `recovery/`,
  `l1/`, `final/`, `build/`, `attempt2/`, `transcripts/`) is still refused; `records/` is a record of a wave, not
  a capture of a moved artifact; the choice is conservative and reformable next round.
- Any `w[0-9]+/` is accepted, existing or not; the rule does not consult the census at run time.
- The token's first component below its round is treated as its wave directory whether or not it is one, so a token
  under `records/` or `decoy/` also gets an own-tree move case (`S83ScoutDirs` §3.4 probe `fx6`: the r83 rule returns
  MOVED where r82 refused; no row carries such a token). A token with no wave directory is therefore *not* excluded —
  the prereg's first wording said it was, and this is the corrected statement.
- Fixtures are synthetic: a row proves the rule's verdict, not that the lane really moved the file that round.
- `S331` is the lane's own directory census; `S333` corrects its provenance: `.ufo/waves/` is gitignored, so the
  counts are a working-tree census (102 dirs over 65 rounds), not a revision count (git holds 39 at `1e870403`).
- No real own-tree move of this shape exists in the lane at any rev or in any ledger row (`S83ScoutDirs` §2.3-2.4);
  TF6/TF7 prove the rule's verdict over a real layout, not a lane fact.

## Evidence

`census/round-83/records/c1-after.txt` (`SUMMARY rows=36 mismatches=0 accepted=0 refused_true=0 errors=0`,
EXIT 0) against the control `census/round-83/controls/c1-K-a-r82-counter.txt` (`mismatches=2 refused_true=2`,
EXIT 1); regressions r77 35/35 + 7/7, r78 22/22 + 12/12, r79 9/9, r80 18/18, r81 25/25, r82 harness 32/32.
