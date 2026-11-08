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

A rule with more than one guard per decision can leave a clause with no row for two different reasons, and the
difference decides what to do: an UNBOUND clause is one a row could bind and the population lacks that row; a
SHADOWED clause is one no row can bind, because another guard refuses every input the clause would refuse. r84
called the census-in-tree and last-component clauses "unbound by the population"; r85 measured them and found both
unbound AND reachable — each decides a row the pinned populations do not carry, so each is missing a row, not dead.

How to tell them apart, measured rather than argued (S337/S340: a suite is judged by the mutants it kills):

1. Author a single-edit mutant that drops ONLY the clause in question, and score it on every pinned population.
2. If it is killed, the clause is **bound** — the killing row is its row (the own-tree belt at
   `census/round-85/c1-pointer-counter.py:391` is bound this way: dropping it turns 7 rows red on both populations).
   A mutant that makes the counter *raise* is not a kill: the r85 wave's first basename mutant replaced the clause
   and its body and scored "killed" on an `IndentationError` — a crash, not evidence (Q133).
3. If it survives everywhere, ask whether the branch is REACHABLE: drive the branch directly through the counter's
   own `--forge` path with a hand-built row (r85: item I85R, target under `census/round-84/w1/`). If the pristine
   counter refuses with that branch's own reason and the mutant resolves the row, the clause is reachable and the
   population is missing its row → **unbound**. Build the row.
4. If no input reaches the branch — a guard above it refuses every pair the branch's guard admits — the clause is
   **shadowed**: a row cannot bind it, and it is either deleted or documented as a belt, never counted as coverage.

The last-component basename check (`:387`) and the census-in-tree branch are the r85 cases of (3): a forge row
whose target keeps the frozen bytes under a different basename is refused by the basename clause with its own
reason, and the same row falls through to the own-tree belt when the clause is dropped — reachable, deciding, and
unrowed. This section's first version got the census-in-tree branch wrong: it read the
prefix-equal own-tree belt as refusing every pair that reaches the branch. It does not — `_owntree_ok` returns True
when the target sits under a real wave directory (`OWNTREE_WAVE`), so a census-rooted token whose target is
`census/round-<N>/w1/…` passes the belt and reaches the branch, which refuses it with its own reason. The lesson is
the order of the two measurements: a mutant surviving every population is evidence about the POPULATION; only a
direct drive of the branch is evidence about reachability. `census/round-85/records/a1-c7-shadow.txt` is the
survival; `.ufo/waves/round-85/w1/S85Scribe.md` § F1 is the reachability, with a 48-row probe population in which
one added row (NF-W) kills the dropped branch.

Consequences for the claim language: "the population certifies these clauses" is a rows claim; a clause with no row
is not certified whether or not it is reachable, and a claim that counts a clause as coverage must carry its row.
r84's routed "ground it or delete it" for this branch answers "ground it" — the row is an r86 item, and nothing was
deleted on a reading that a seat falsified.

Limits: reachability was shown for one shape (a census-rooted token landing in a wave directory under its own
round), not for every shape the branch admits; the basename result rests on one forge row and the belt's on a
seven-row kill, neither of which is a committed population row yet; nothing the round examined turned out to be
shadowed, so the term is defined here from principle (a guard above that refuses every pair the branch admits) and
rests on one separate probe (`…/S85MutK4.md` m4: no conflict-while-status-clean state is constructible).

## Grounding an unbound clause: the row is the work (r86)

source: S335 (own-work clause-kill receipts), S337/S340 (mutation adequacy); census/round-86/c1-false-rows.tsv,
census/round-86/c1-mutants.json, census/round-86/c1-clause-battery.py
verified-at: 47602fa690d19bd320fc0053fbeed46a1270ff09 (2026-11-08)
recheck: python3 -B census/round-86/c1-clause-battery.py --counter census/round-86/c1-pointer-counter.py --work <empty dir outside /tmp> --only r85,r86 --expect-killed 14

r85 defined the difference between an unbound clause and a shadowed one and measured two clauses of `judge()` that
are reachable and deciding but have no row (census-in-tree at `:417-425`, the own-tree short-shape guard in
`_owntree_ok` at `:351`). r86 does the work the definition implies: each clause gets one frozen row and one
single-edit mutant that drops ONLY it, and the delta is measured on the old population as the control.

| clause | row | target (fixture rev R9) | mutant | killed on r85 47 rows | killed on r86 49 rows |
|---|---|---|---|---|---|
| census-in-tree branch | NF-W (item I85R, `census/round-84/records/c1-after.txt`) | `census/round-84/w1/c1-after.txt` | `c7-census-in-tree` | no | **yes** |
| own-tree short-shape guard | NF-Y (item I86S, `census/round-83/c1-pointer-counter.py`) | `census/round-83/waves/c1-pointer-counter.py` | `m14-short-shape` | no | **yes** |

Both rows are FALSE rows (expect REFUSED) and each is refused by exactly one clause: NF-W's target keeps the token's
last component, its round and its frozen bytes, and the own-tree belt passes it because `_owntree_ok` accepts a real
wave directory, so control reaches the census-in-tree branch; NF-Y's token sits one component below its round, so
`len(want) < 2` decides before `_capture_ok` is consulted, and dropping the guard lets `_capture_ok` accept the
one-component remainder as a suffix. Item I86S is the first population item in the lane whose token is that shallow,
which is why a new item population (and one POPS entry) was needed at all.

Measured: `census/round-86/controls/c1-before-r85-population.txt` — the same eight mutants on the r85 47 rows:
`SUMMARY mutants=8 sets=r85 pristine_r85=ok killed_r85=6`, `c7` and `m14` `killed=no`, EXIT 0.
`census/round-86/records/c1-after.txt` — `pristine pop=r85 rows=47 mismatches=0`, `pristine pop=r86 rows=49
mismatches=0`, `killed_r86=8`, EXIT 0. The six r85 mutants stay killed on both populations, so the new rows add
coverage without replacing any.

What the two rows do NOT certify (measured by the round's critic, `plans/round-86.md` A3): NF-Y exercises only the
`len(want) < 2` arm — a counter that keeps only that arm still scores 8/8 on both populations; NF-W's target is a
`w[0-9]+/` shape, so a rule that narrows the census-rooted branch to that shape also survives.

The `len(got) < 2` disjunct is not merely unrowed, it is **dead** (measured this round,
`census/round-86/records/a6-len-got.txt`): the mutant `if len(want) < 2 or len(got) < 2:` -> `if len(want) < 2:`
survives both pinned populations (`killed_r85=0 killed_r86=0`, both pristine arms green), and by construction no
(token, target) pair can flip. After the guard the expression reaches `_capture_ok`, whose `CAPTURE` needs a
non-empty remainder (so a target needs at least two components below its round), and `OWNTREE_WAVE.match(tt + "/")`
followed by `got[1:] == want[1:]`, where `want[1:]` is non-empty because the other disjunct requires
`len(want) >= 2`. A row cannot bind it, which is the third disposition this file now distinguishes: BOUND (a row kills
the mutant), UNBOUND-and-reachable (a hand-built row decides and a row is missing), and DEAD (no input flips the
verdict). The basename clause at `:387` is a fourth case with a different verdict: a row CAN make it the first
refusal (a renamed target), but no row can make its removal flip a verdict while the suffix comparisons stand, so it
is shadowed-for-verdict and a row would count coverage it does not give.
