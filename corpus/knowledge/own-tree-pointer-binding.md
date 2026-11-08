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

## Bounding a population, not just a rule (r84)

source: S335 (own-work clause-kill receipts), S331/S333 (the wave-directory census and its provenance); census/round-84/c1-false-rows.tsv,
census/round-84/c1-mutants.json, census/round-84/c1-clause-battery.py
verified-at: 1f49b3a7824e7f4e65c33358ee24a6afaf8ca50d (2026-11-08)
recheck: python3 -B census/round-84/c1-clause-battery.py --counter census/round-84/c1-pointer-counter.py --work <empty dir outside /tmp> --only r84 --expect-killed 5

A rule says what a verdict must be; a population says what the rule must **distinguish**. A clause of the rule is
bound only when some frozen row would go red under a rule that drops that clause. The r83 population (36 rows, the
r83 section above) left five clauses unbound: it certified a rule it did not discriminate.

Measured with the frozen five single-edit mutants (`census/round-84/c1-mutants.json`) over two pinned populations
(`c1-false-row-harness.py` `POP_PINS`: r83 `c9a6d58c…` 36 rows, r84 `4795f009…` 44 rows):

| mutant | clause it drops | r83 (36) | r84 (44) | rows that kill it |
|---|---|---|---|---|
| `m6-digest-blind` | target bytes must equal the token's frozen digest | survives | killed | NF-L |
| `m7-round-blind` | target must name the token's own `round-<N>` | survives | killed | NF-L2 |
| `m8-w-only-shapes` | wave set is `w[0-9]+/` alone, without `a2w1/`/`assimilation/` | survives | killed | TF9, TF10 |
| `m9-basename-only` | the remainder is the whole path, not a two-component shape ending in its last component | survives | killed | TF8, TF9, TF10 (refused_true=3), NF-P (accepted=1) |
| `m10-records-as-wave` | a non-wave own-tree dir (`records/`) is not a capture shape | survives | killed | NF-M |

Both arms keep the unmutated counter green (`rows=36 mismatches=0`, `rows=44 mismatches=0`, `accepted=0
refused_true=0`): the r84 arm reads `killed_r84=5` (`census/round-84/records/c1-after.txt`, EXIT 0), the r83 arm
reads `killed_r83=0` (`census/round-84/controls/c1-before-r83-population.txt`, EXIT 0) — same counter, same battery,
same mutants, so the delta is the population, not the rule.

The criterion: one FALSE row per clause **the population claims to bind** (digest, round, shape set, suffix depth,
non-wave dir) and one TRUE row per real shape the rule names (`a2w1/`, `assimilation/`, a deep two-component
remainder under a real `wN/`). What the population does NOT bind, measured (S84Sentinel F1/F2, its
`c1_clause_coverage.py`): the census-in-census clause (a `census/round-<N>/` target must be a wave capture keeping
the token's full suffix) and the last-component clause are green under a dropped-clause mutant on both pinned
populations; the census-in-census one is the dangerous gap — the mutant resolves a wrong file (two enumerated
targets) and both populations still pass, because no population item has a token under `census/round-<N>/` (the
only census-token items name no round). Limits: a population proves discrimination on its own rows, not the rule's
correctness; the NF rows are byte-equal copies by construction (location binding, not content identity); the five
mutants are hand-written single edits, not a generated battery; a "kill" is a non-zero harness exit, which does not
by itself separate a row mismatch from a harness error (every observed kill was a real `match=no`, `errors=0`).

## A shadowed clause is not an unbound clause (r85)

r84 read the sentinel's per-clause battery as "the census-in-census and last-component clauses are unbound by the
population" and routed a row for each. r85 measured that the sentence is wrong in a way that matters: an UNBOUND
clause is one a row could bind; a SHADOWED clause is one no row can bind, because another belt refuses every input
the clause would refuse.

The census-in-tree branch of `judge()` in `census/round-85/c1-pointer-counter.py` (the branch
`elif kr and target[:tr.start(0)] == "census" and token[:kr.start(0)] == "census" and not _capture_ok(...)`) is
shadowed, not unbound. To reach it a call must have `target[:tr.start(0)] == "census"` and
`token[:kr.start(0)] == "census"`; the branch immediately above it fires on `target[:tr.start(0)] ==
token[:kr.start(0)]` and refuses the same input through `_owntree_ok`. When the token's root is not `census`, the
branch's second condition is false and the `target[:tr] == "census" and token[:kr] != "census"` belt above it
applies. The branch therefore cannot be the first refusing branch for any pair.

How to tell the two apart, measured rather than argued: author a single-edit mutant that drops ONLY the clause in
question and score it on every pinned population (S337: a suite is judged by the mutants it kills, not by the rows
it carries; S340 is the paper-backed form of the same criterion).

- Survives everywhere, and the branch order shows a belt above catches every input it would catch → **shadowed**:
  delete it (dead code that reads like protection) or leave it as a documented belt; a row cannot bind it.
  `census/round-85/records/a1-c7-shadow.txt` reads `killed_r84=0 killed_r85=0` with both pristine arms green.
- Survives everywhere but the branch IS reachable → **unbound**: a row is missing (r84's five clauses, closed by the
  44-row population).
- Killed by some population → bound; the killing row is the clause's row.

Consequences for the claim language. "The population certifies five clauses" is a claim about rows; "the counter's
rule is certified" is a claim about the rule, and it is false whenever a branch is shadowed — the belt is what
protects, and the dead branch is a reader trap. The r85 round therefore reports the census-in-tree branch as
shadowed with its probe, adopts r84's routed "ground it or delete it" as "delete" (landed in a later round; a
claim's rule is never changed after a seat has scored), and does not count it as coverage.

Limits: the shadow argument is branch-order reasoning over one function, checked by one mutant pair, not a proof
over all inputs; a second belt can be shadowed by a third (this round only shows the first-order pair); the
last-component basename check is shadowed in the same way for every MOVED row measured (a basename change fails the
suffix comparisons that follow), and no probe was run for it.
