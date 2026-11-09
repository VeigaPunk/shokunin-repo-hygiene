# R93MutC1 — C1 attack: alternative spellings, kill rule, LD5/LD6 attribution

Seat dir: `.ufo/waves/round-93/w1/R93MutC1/` under `/home/vgpnk/Projects/shokunin/souji-shokunin/`.
All harness/search runs used the frozen r93 instruments against the pristine lane counter
(`census/round-87/c1-pointer-counter.py`, sha256 `fd0a8e24…220b`), harness
`census/round-93/c1-false-row-harness.py` (sha256 `1868a570…04a4`), population
`census/round-93/c1-false-rows.tsv` (sha256 `d6439f65…88e`, 66 rows). Each scored mutant is a fresh
copy of the counter in this seat dir (`*.py`) scored by the frozen harness on the frozen population
(`*.out.txt`, one work tree per run, never more than 2 at once; scratch deleted after copying
receipts in). Every `ROW`/`SUMMARY` line below is verbatim from those files; `verdicts.txt` is the
full machine-readable sweep.

## 0. Baseline: the prereg predicates re-derive

- Pristine harness: `SUMMARY rows=66 mismatches=0 accepted=0 refused_true=0 errors=0`, EXIT 0
  (`pristine-out.txt`). LD5 line: `ROW LD5 where=ledger-drop rev=BASE item=P04 class=- expect=UNRESOLVED/1 got=UNRESOLVED rc=1 match=yes`; LD6: `ROW LD6 where=ledger-trim rev=BASE item=P04 class=- expect=MOVED/0 got=MOVED rc=0 match=yes`.
- Official search (`search-out.txt`): `SEARCH-SUMMARY generated=2 ambiguous=0 uncompiled=0 hung=0 scored=2 errored=0 killed=2 survived=0`, EXIT 0, with `SEARCH h-ok-admits-one line=552 killed=yes rc=1` and `SEARCH a491c22-<-to-<= line=491 killed=yes rc=1`.

## 1. Spelling table (task §1)

Same counter, same 66-row population. Each mutant = one `old`→`new` replacement of the pristine bytes
(anchors verified unique, all files compile). "Killed by" names the single `match=no` row (each run
produced exactly one unless it survived).

| # | mutant file | edit (pristine → mutant) | verdict (r93 search semantics) | killing row |
|---|---|---|---|---|
| m1 | `m1_gt_len_minus_2.py` | 552 `resolved == len(pop)` → `resolved > len(pop) - 2` | **killed** (harness EXIT 1, `SUMMARY rows=66 mismatches=1 accepted=0 refused_true=0 errors=0`) | LD5: `expect=UNRESOLVED/1 got=UNRESOLVED rc=0 match=no` |
| m2 | `m2_ge_len_minus_2.py` | 552 → `resolved >= len(pop) - 2` | **killed** (same SUMMARY as m1) | LD5, same line |
| m3 | `m3_res_unres_sum.py` | 552 → `resolved + counts['unresolved'] == len(pop)` | **killed** (same SUMMARY) | LD5, same line |
| m4 | `m4_unres_le_1.py` | 552 → `unresolved <= 1 and resolved >= len(pop) - 1` | **killed** (same SUMMARY) | LD5, same line |
| m5 | `m5_plus_unknown_sub.py` | 552 → `resolved == len(pop) - len(unknown) and not unknown` | **SURVIVES** (EXIT 0, `SUMMARY rows=66 mismatches=0 … errors=0`) | — none |
| m6 | `m6_ge_len_minus_unknown.py` | 552 → `resolved >= len(pop) - len(unknown) and not unknown` | **SURVIVES** (EXIT 0, same clean SUMMARY) | — none |
| g1 | `g1_lt_4.py` | 491 `len(r) < 3` → `len(r) < 4` | **killed** (`mismatches=1`) | LD6: `expect=MOVED/0 got=UNRESOLVED rc=1 match=no` |
| g2 | `g2_not_in_3_4.py` | 491 → `len(r) not in (3, 4)` | **SURVIVES** (EXIT 0, clean SUMMARY) | — none |
| g3 | `g3_ne_4.py` | 491 → `len(r) != 4` | **killed** (`mismatches=1`) | LD6, same line |

Two semantic identities matter for attribution naming: on integers `resolved > n-2` ≡ `resolved >= n-1`
so **m1 is byte-different but behaviorally the HAND edit `h-ok-admits-one`**; likewise `len(r) < 4` ≡
`len(r) <= 3`, so **g1 is the HAND edit `a491c22-<-to-<=` in another spelling**. The exact HAND bytes
(`h-ok-admits-one.py`, `a491c22-<-to-<=.py`) were written from `search.gen()` and their full-population
scores are the official SEARCH lines above; m1/g1 give the per-row breakdown (LD5 vs LD6 respectively).

**Why the survivors survive (named limits / row shapes).**

- **m5/m6 (sub/super tolerated by unknown count).** `LD5` runs with `unknown` empty, so
  `len(pop) - len(unknown) = len(pop)` and the mutants coincide with the pristine test on the LD5 run
  (`rc=1 match=yes`) and on every all-resolved `rc=0` row. A row that separates them needs, in one run,
  ≥1 unknown id **and** the resolved count not equal to the full population by a *different* amount
  than the unknown count — e.g. a ledger run with an unknown id (counts `refused`) **plus** exactly one
  `UNRESOLVED` item, so pristine `ok = (35-1 == 35) = false` but m6 `ok = (34 >= 35-1) = true`.
  No existing row has that shape: every ledger row (`LD1/LD1b/LD2/LD2b/LD1c/LD3`) has `resolved = len(pop)`
  (no unresolved item), and `LD5` has no unknown id. m5 is the stricter equality sibling; m6 the
  `>=` sibling. **This is a genuine clause-level survivor: the population binds the HAND edit, not
  every `resolved`-threshold spelling** — consistent with prereg stated limit (i) ("Two edits are
  bound, not their clauses"). No C1 sentence is refuted by this (see §4).
- **g2 (`len(r) not in (3, 4)`).** It *accepts* width 3, so it behaves like the pristine guard on every
  frozen ledger (all real rows are 4 wide; verified: r77 31×4, r78 19×4, r85/r86/r87 2×4 each) and on
  `LD6` (width-3 row kept, P04 resolves `MOVED`, `rc=0 match=yes`). It differs from pristine only at
  widths the population never shows: 5+-column real ledger rows (refused by g2, accepted by pristine)
  and width-1/2 acceptance is identical (both refuse). Wait — it refuses width 1/2, exactly like
  pristine, and refuses 4? No: `not in (3,4)` is false for 3 and 4, so it keeps 3 and 4 and refuses
  1, 2, 5+. On every run in the population (widths 1, 2, 3, 4 only) g2 is **behaviorally identical to
  pristine**. A separating row needs a genuine ≥5-column ledger row for an item that must resolve,
  or a 1/2-column row under a *duplicated* id where acceptance vs refusal interacts with the duplicate
  leg (current `LD2/LD2b/LD3` reach the guard leg for both). This is the same class of limit as m5/m6:
  the guards' agreed domain on the frozen population is {1,2,3,4}; outside it they diverge unobserved.
- **g3 (`len(r) != 4`)** is killed for the same reason g1 is: it refuses the width-3 trim row. Note g3
  would *also* refuse a hypothetical 5-column row, but the population contains none, so LD6 is the
  sole killer; a ≥5-column row would kill it a second time.

**Suggested row shapes (for the L1; not filed as claims).** R1: ledger run with P04 dropped *and* ZZ9
appended as a refused unknown (one unresolved + one unknown). R2: ledger run with a genuine 5-column P04
row (extra trailing comment column). Both would kill the three survivors above; R1 kills m5/m6, R2 kills
g2 (and g3 twice).

## 2. Kill-rule probe (task §2)

`verdict()` in `census/round-93/c1-survivor-search.py:86-93` was exercised directly, and two crash
mutants were scored through the real harness on the r93 population, and one through the search's own
`score()` (the search only generates token-swap + HAND ids, so a `/tmp`-free, name-free hand mutant
must go through `score()` or the harness directly).

Verdict truth table (rc, harness stdout) → verdict:

| rc | content | verdict |
|---|---|---|
| 0 | anything (even `match=no` lines) | `no` |
| 1 | ≥1 line ending ` match=no` | `yes` (killed) |
| 1 | `match=error`-only rows | `errored` |
| 1 | no ROW lines | `errored` |
| 2 | `match=no` text present | `errored` |

- **k1 (`k1_ld5_crash.py`)**: returns 2 only when `--ledger` ends `/ledger-LD5.tsv` (the LD5 run).
  Harness: EXIT 1, `SUMMARY rows=66 mismatches=0 accepted=0 refused_true=0 errors=1`,
  `ROW LD5 … got=- rc=2 match=error`. Through the search's `score()`: **`errored`, rc=1** — the
  harness exits 1 (one `match=error` row) and the search reads `errored`, exactly as the r93 kill rule
  states. A harness exit 2 is impossible here: the harness maps subprocess rc=2 to `match=error` and
  itself exits 0/1/2 (2 only for setup errors). An `errored` verdict is therefore reached via
  rc=1 + error-only rows, which is what k1 exercises.
- **k2 (`k2_import_crash.py`)**: raises at import. Harness: EXIT 1,
  `SUMMARY rows=66 mismatches=10 accepted=0 refused_true=0 errors=56` → **read as KILLED (`yes`), not
  errored**. Mechanism: the harness only turns subprocess rc=2 into `match=error`; this mutant dies
  with a Python traceback (rc=1) and prints no ITEM/FORGE line, so the 10 ledger-family rows
  (`LD1/LD1b/LD2/LD2b/LD1c/LD3/LD4/LD4r/LD5/LD6`, the `g4` branches at harness lines 458-472, 519-533)
  compare `got='-'` against the expected status and print `match=no`, while the 56 forge-branch rows
  print `match=error`. Ten `match=no` lines make the verdict `yes`. **The r93 kill rule as stated does
  not classify an import-time crash as `errored`; it classifies it as killed.** No C1 sentence claims
  otherwise (the rule's wording — "a mutant is killed only when the harness exits 1 AND prints at
  least one `ROW … match=no` line" — is exactly what happens). Recorded here as the measured
  behavior, not as a refutation.

## 3. One-row attribution (task §3)

Scratch populations with one of the two r93 rows removed, pinned in scratch harness copies
(`harness-pop-no-ld5.tsv` sha `b608b7e8…8c5`, `harness-pop-no-ld6.tsv` sha `c4f0615c…9f`, each
`rows=65`; underivable from `POP_PINS` — passing them to the frozen harness exits 2,
`a1-hok-nold5-fullpop.out.txt`).

- **h-ok-admits-one without LD5** (`a1-hok-nold5.out.txt`): `SUMMARY rows=65 mismatches=0 accepted=0 refused_true=0 errors=0`, EXIT 0 → **survives**. **LD5 alone carries the kill** for h-ok (the full population kills it; dropping LD5 un-kills it). With LD6 still present, no other row kills the mutant.
- **a491c22 without LD6** (`a2-a491-nold6.out.txt`): `SUMMARY rows=65 mismatches=0 …`, EXIT 0 → **survives**. **LD6 alone carries the kill** for a491c22. With LD5 still present, no other row kills it.
- Cross-check consistent: on the full population, m1's only mismatch is LD5 and g1's only mismatch is LD6 (§1 table).

## 4. Falsification check

**NO-FALSIFICATION.** Nothing in this probe refutes a sentence of the C1 claim as stated. In
particular:

- §1's survivors (m5/m6, g2) are consistent with stated limit (i) ("Two edits are bound, not their
  clauses" — the prereg claims two named *edits*, and the alternative spellings above are exactly the
  kind the limit reserves). None of the claimed predicates (the two SEARCH-SUMMARY lines, the control
  `killed=0 survived=2`, the LD5/LD6 pristine lines) fails.
- The import-crash reading (k2 = killed via ten `match=no` lines) is the kill rule's stated behavior,
  not a counterexample to it; the rule's exit-2/error-only arm was exercised by k1 and behaves as
  written.
- The population and row-type descriptions (LD5 = one unresolved, exit 1; LD6 = 3-column row accepted,
  exit 0) reproduced exactly.

Attempted and survived (coverage findings, not falsifications): `resolved == len(pop) - len(unknown)`,
`resolved >= len(pop) - len(unknown)`, and `len(r) not in (3, 4)` — each needs a row shape the r93
population lacks (named in §1: R1 = one-unresolved-plus-one-unknown ledger run; R2 = genuine
≥5-column ledger row). No artifact of this seat falsifies any C1 sentence; therefore there is no
`FALSIFIES-WORDING` or `FALSIFIES-NUMBER` entry and no amendment for plans/round-93.md from R93MutC1.

## Reproducibility

Every mutant + harness output pair is in this seat dir (`*.py`, `*.out.txt`); `verdicts.txt` sweeps all
of them through `search.verdict`. One harness run ≈ 15 s; score a mutant with:

```
python3 -B census/round-93/c1-false-row-harness.py --counter <mutant>.py \
  --lane . --fleet-root /home/vgpnk/Projects/shokunin \
  --work <empty scratch, NOT /tmp> --population census/round-93/c1-false-rows.tsv
```

## Tooling

No tools installed (none needed; `uv`/pacman untouched). Nothing was written outside this seat dir
and the report plus deleted scratch under `/fast/scratch/hyaku/souji-r93/R93MutC1/` (removed before
yield; receipts copied to this dir first). The frozen instruments, `census/`, `tests/fixtures/`,
`tools/`, `corpus/`, MANIFEST/state files were read only.
