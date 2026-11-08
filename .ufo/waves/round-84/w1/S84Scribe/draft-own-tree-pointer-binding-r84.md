# DRAFT — `corpus/knowledge/own-tree-pointer-binding.md`, new section (r84)

Seat: S84Scribe (drafts only; the L1 integrates). Draft file; the L1 pastes the block below into
`corpus/knowledge/own-tree-pointer-binding.md` and lands the file.

> **STATUS: superseded as an integration input.** The L1 landed its own version of this section at `4557fc71`
> under the same title, "Bounding a population, not just a rule (r84)". This draft is kept for the L1 to re-check
> or extend; where the two differ the **landed text is the lane's**. The two independently reached the same
> per-mutant kill table (NF-L; NF-L2; TF9+TF10; TF8+TF9+TF10+NF-P; NF-M) — this draft's table was measured
> row by row through the frozen harness, independently of the L1's.

## Section title

`## Bounding a population, not just a rule (r84)`

## Draft block (paste-ready)

---

## Bounding a population, not just a rule (r84)

source: S331 (own-work wave-directory census), S332 (kernel fs/proc/array.c at v6.17), S333 (the census's
corrected provenance); census/round-84/c1-false-rows.tsv, census/round-84/c1-mutants.json,
census/round-84/c1-clause-battery.py
verified-at: <the commit the L1 lands the round at> (2026-11-08)
recheck: python3 -B census/round-84/c1-clause-battery.py --counter census/round-84/c1-pointer-counter.py --work <empty dir outside /tmp> --only r84 --expect-killed 5

### The rule is one half; the population is the instrument that certifies it

A pointer counter's rule says what a verdict must be. A population says what the rule must *distinguish*. The
population is the instrument: a clause of the rule is **bound** only when some frozen row of the population would
go red under a rule that drops that clause. The r83 population (36 rows) left five of the counter's clauses
unbound, so it certified a rule it did not discriminate; the r84 population (44 rows) binds them.

### The kill view, measured

The frozen five single-edit mutants of `census/round-84/c1-pointer-counter.py` are in
`census/round-84/c1-mutants.json`; the battery is `census/round-84/c1-clause-battery.py`; a mutant is **killed**
when the harness exits non-zero on that population. Measured on the two pinned populations:

| mutant | clause it drops | r83 (36 rows) | r84 (44 rows) | the rows that kill it |
|---|---|---|---|---|
| `m6-digest-blind` | the MOVED target's bytes must equal the token's frozen digest | survives | **killed** | NF-L |
| `m7-round-blind` | the MOVED target must name the token's own `round-<N>` | survives | **killed** | NF-L2 |
| `m8-w-only-shapes` | the own-tree wave set is `w[0-9]+/` alone, without `a2w1/`/`assimilation/` | survives | **killed** | TF9, TF10 |
| `m9-basename-only` | the own-tree comparison keeps the token's whole remaining path, not a two-component shape ending in its last component | survives | **killed** | TF8, TF9, TF10, NF-P |
| `m10-records-as-wave` | a non-wave own-tree directory (`records/`) is not a capture shape | survives | **killed** | NF-M |

The r83 arm reads `SUMMARY … killed_r83=0` (five mutants at 36/36 green) and the r84 arm reads
`SUMMARY mutants=5 sets=r84 pristine_r84=ok killed_r84=5 killed_total=5`; the counter is green on **both**
populations before any mutation (`rows=36 mismatches=0`, `rows=44 mismatches=0`, `accepted=0 refused_true=0`).
The before receipt is `census/round-84/controls/c1-before-r83-population.txt` (`killed_r83=0`, EXIT 0) — the same
counter, the same battery, the same five mutants, scored on the 36-row population; it is what makes the delta
non-vacuous. The per-mutant row detail (`NF-L`, `NF-L2`, `TF9`/`TF10`, `TF8`/`NF-P`, `NF-M` — which row goes red
and which way) is in `.ufo/waves/round-84/w1/S84Scribe/receipts/c1-per-mutant-rows.txt`.

### The criterion a population has to meet

- **One false row per clause the rule enforces.** The 44-row population adds five false rows, one per unbound
  clause: **NF-L** (a real `w3/` copy whose bytes differ from the token's frozen digest — the digest clause),
  **NF-L2** (a byte-equal copy in *another* round's wave tree, `round-33/w2/`, while the token is a `round-32`
  move — the round clause), **NF-M** (a non-wave `records/` directory under the token's own round tree — the
  shape clause), **NF-P** (the deep token flattened one component, same basename, same real `w2/` — the
  suffix-depth clause) and **NF-Q** (a real `w2/` prefix alone is not enough — the token's suffix is not kept).
- **One true row per real shape the rule names.** The population adds three true rows for the shapes the rule
  enumerates but the r83 population never exercised: **TF8** (a deep token — two components below its wave
  directory — kept under a real `w2/`), **TF9** (`a2w1/`) and **TF10** (`assimilation/`). Those directory names
  are the lane's own: the working-tree census `census/round-83/records/wave-dirs.txt` counts `w1/` 65, `w2/`
  19, `assimilation/` 4, `w3/` 1, `a2w1/` 1 (S331; S333 corrects the provenance — the census is a working-tree
  count, not a revision count, because `.ufo/waves/` is gitignored). A rule that names a shape no row exercises
  is prose, not calibration: the r83 own-tree rule named `a2w1/` and `assimilation/` and carried no row on
  either, so a `w[0-9]+/`-only mutant passed all 36 rows (r83 Q152, r83 A2 route).
- **Both poles.** The population must keep the real shapes *and* reject the near-misses, and the counter reports
  `accepted` (a false row accepted) and `refused_true` (a true row refused) beside `mismatches`, so a rule that
  refuses everything cannot read green: `accepted=0 refused_true=0` is the only passing summary.

### Why the mutation view is the right view

A rule can be wrong in a direction the population does not measure, and a population can be green while the rule
is wrong — unless the population is checked against rules that differ from it. The mutation view is that check:
it asks, of the rule under test, *which rows distinguish it from a cheaper rule*. `m9-basename-only` is exactly
the r83 critic's A2 rule (`len(got)==2 and got[1]==want[-1]`), which passed all 36 r83 rows — because every
own-tree token in that population sat exactly one component below its wave directory (r83 A2). Adding the deep
token **TF8** and its flattened decoy **NF-P** is what makes the suffix clause load-bearing: `m9` now refuses the
true row TF8 and accepts the false row NF-P, so it is killed 4 rows deep. The same reasoning applies to the
shape set (`m8`, killed by the `a2w1/`/`assimilation/` true rows TF9/TF10), the digest clause (`m6`, killed by
NF-L), the round clause (`m7`, killed by NF-L2) and the non-wave clause (`m10`, killed by NF-M).

### Limits (stated, not claimed away)

- A population proves **discrimination on its own rows**, not the rule's correctness on the world. A clause with
  no row is invisible to the population, which is exactly the failure the r83 population had.
- The NF rows are **byte-equal copies of the token's byte source by construction** (except NF-L, whose differing
  copy is a synthetic file, not a real divergent artifact), so they test **location binding, not content
  identity**; NF-L tests that the rule consults the frozen digest at all, on a synthetic input.
- TF9 and TF10 use `a2w1/` and `assimilation/` directories the lane has (the census above) but **no recorded
  ledger move has used those layouts** (r83 A4), so they are **shape rows, not move rows**: they prove the rule's
  verdict over a real layout, not a lane fact.
- The five mutants are **hand-written single edits, not a generated battery**; a kill shows that one clause is
  load-bearing on the rows that carry it, not that the clause is the only possible one.
- A kill is `harness EXIT != 0`, which **cannot distinguish a row mismatch from a harness error**; the receipt
  prints both (`mismatches=` and `errors=` beside each mutant line).
- The population is **pinned by sha256** inside the harness and the battery
  (`POP_PINS` in `census/round-84/c1-false-row-harness.py`; the battery refuses any other file), so editing a
  population row kills the claim rather than changing it.

## Grounding map for the L1

| draft sentence | grounded in |
|---|---|
| r83 36 rows left five clauses unbound; the five mutants | `census/round-84/preregistration.txt` C1; `census/round-84/c1-mutants.json` |
| kill rule (harness exit non-zero), both populations green, `killed_r83=0` | `census/round-84/controls/c1-before-r83-population.txt`; `census/round-84/c1-clause-battery.py` |
| `killed_r84=5`, `rows=44 mismatches=0` | `census/round-84/records/c1-reference-prefreeze.txt`; `census/round-84/records/c1-after.txt`; my re-run in `.ufo/waves/round-84/w1/S84Scribe/receipts/c1-battery-r84.txt` |
| which row kills which mutant | `.ufo/waves/round-84/w1/S84Scribe/receipts/c1-per-mutant-rows.txt` (re-measured row by row through the frozen harness) |
| the eight added rows and their notes | `census/round-84/c1-false-rows.tsv` (rows TF8, TF9, TF10, NF-P, NF-L, NF-L2, NF-M, NF-Q) |
| `w1/` 65, `w2/` 19, `assimilation/` 4, `w3/` 1, `a2w1/` 1 | `census/round-83/records/wave-dirs.txt` (S331); provenance corrected by S333 |
| "a rule that names a shape no row exercises is prose" | `corpus/QUALITY.md` Q152; `plans/round-83.md` A2 |
| m9 = the r83 critic's A2 rule, 36/36 green before | `plans/round-83.md` A2; `census/round-84/c1-mutants.json` (m9's `note`) |
| TF9/TF10 are shape rows, not move rows | `census/round-84/preregistration.txt` C1 "Stated limits (frozen)" |
| NF rows are byte-equal copies by construction; NF-L is synthetic | `census/round-84/preregistration.txt` C1 "Stated limits (frozen)" |
| a kill is `harness EXIT != 0` and cannot distinguish mismatch from error | `census/round-84/c1-clause-battery.py` docstring; `census/round-84/preregistration.txt` |
| populations pinned by sha256; editing a row kills the claim | `census/round-84/c1-false-row-harness.py` `POP_PINS`; `census/round-84/preregistration.txt` |

### Open points for the L1 (not draft sentences)

1. `verified-at:` is a placeholder for the commit at which the L1 lands the round.
2. The section names **S331, S332, S333** because those rows are committed and citable today. The r84 source rows
   the round's source seat lands (whatever ids it assigns) should be added to the `source:` line by the L1 — the
   draft deliberately does not invent an id for a row that does not exist yet.
