# S90MutCounter — C1 row attack: is LD2b load-bearing and sole, and which reachable clauses stay unrowed

Seat: mutation-tester, round-90 w1, lane `souji-shokunin` (lane base bd760432, prereg commit F fd25bfc5). Read-only
in the lane: no mutating git/jj, no sibling files, no MANIFEST/.ufo/state/.scratch/watchdog. Clones, fixtures and
counter `--work` dirs lived under `/fast/scratch/hyaku/souji-r90/S90MutCounter/` (deleted before yield; receipts
copied into `.ufo/waves/round-90/w1/S90MutCounter/`).

Instruments measured (sha256 of the bytes actually read; all match the prereg):
- counter `census/round-87/c1-pointer-counter.py` = `fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b`
- battery `census/round-90/c1-clause-battery.py` = `e7265335e4458e68d2277dd0ad4f36e68999a7ba70363d60dc2155bd9cfa2d39`
- harness `census/round-90/c1-false-row-harness.py` = `c3664747ffe712fde8f61c34562df2f0e92f2a0378b151bd0b4d74e91d629cbe`
- mutants `census/round-90/c1-mutants.json` = `392522489bc6f22a9747f64d311dbde7528dd0e8b481159db15d3eb038066dd5` (16 members)
- r90 population `census/round-90/c1-false-rows.tsv` = `d64d76954daea7da5d36e6f5eda96ae343bdd37db5071ea50bd55b30a1844b45` (58 rows)
- r89 population `census/round-89/c1-false-rows.tsv` = `04570a64855978bf697af71c161fe215945da5849f2f393fee15bb0d9f21e093` (57 rows)
- r77 population `census/round-77/c2-population.tsv` = `bbc19ac66e543b0f974b5524b678985a2a755664294804dab4773953d14e889e` (35 items)
- r77 ledger `census/round-77/c2-pointer-ledger.tsv` = `011faa0e96333b28af0418df8f56a5cbb169ed71aa0e9f688ee6d97d7aa39ba5` (31 data rows, every one 4 columns)

Population delta verified independently: `cmp -n 14187` says r90's first 14187 bytes equal r89; `diff` shows a
single added line, `LD2b` (`where=ledger`, `BASE`, population `r77`, item `ZZ9`, class `-`, target `-`, expect
`LEDGER-REFUSED`/rc `1`). Nothing else in the file changed.

## 1. After and control arms (reproduced on the committed bytes)

After arm, EXIT 0 (elapsed 1005 s under wave load):

```
python3 -B census/round-90/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
  --work /fast/scratch/hyaku/souji-r90/S90MutCounter/after --only r89,r90 --expect-killed 31
ARM pristine pop=r89 rows=57 mismatches=0 errors=0 exit=0
ARM pristine pop=r90 rows=58 mismatches=0 errors=0 exit=0
...
MUTANT-PAIR m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0 | pop=r90 killed=yes mismatches=1 errors=0 exit=1
SUMMARY mutants=16 sets=r89,r90 pristine_r89=ok pristine_r90=ok killed_r89=15 killed_r90=16 killed_total=31
```

Control arm (r89 population alone), EXIT 0:

```
python3 -B census/round-90/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
  --work /fast/scratch/hyaku/souji-r90/S90MutCounter/control --only r89 --expect-killed 15
ARM pristine pop=r89 rows=57 mismatches=0 errors=0 exit=0
MUTANT-PAIR m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0
SUMMARY mutants=16 sets=r89 pristine_r89=ok killed_r89=15 killed_total=15
```

Both arms reproduce the frozen predicate exactly. Every other mutant is `killed=yes` on both populations with the
same mismatch counts (m6 1, m7 1, m8 2, m9 4, m10 1, m11 1, c7 1, m14 1, m12 1, m16 1, m17 2, m18 2, m18b 1,
m17b 1, m18d 1); the only status change between the arms is `m17c-no-malformed` (no → yes). No-work arm reaches
15/15, not 16/16 or 31: the delta really is the one row.

Per-row attribution of the kill (direct harness invocation, `attr90.txt`): m17c on the r90 population reads

```
ROW LD1   ... item=P01 expect=LEDGER-REFUSED/1 got=LEDGER-REFUSED rc=1 match=yes
ROW LD1b  ... item=P01 expect=LEDGER-REFUSED/1 got=LEDGER-REFUSED rc=1 match=yes
ROW LD2   ... item=P02 expect=LEDGER-REFUSED/1 got=LEDGER-REFUSED rc=1 match=yes
ROW LD2b  ... item=ZZ9 expect=LEDGER-REFUSED/1 got=- rc=1 match=no
SUMMARY rows=58 mismatches=1 accepted=0 refused_true=0 errors=0
```

`LD2b` is the ONLY red row and the only mismatch: the mutant's counter never prints a marker and dies with
`IndexError: list index out of range` at `_ledger` line 494, so the harness's `got` is `-`. LD2 (and LD1/LD1b) still
pass, which is why the r89 population scores `mismatches=0`.

## 2. Sole-killer table — pristine, m17, m17b, m17c against the LD2b ledger

Method: r77 population (35 items), frozen r77 ledger plus exactly the harness's append — `LD2` = `P02<TAB>ABSENT`,
`LD2b` = `ZZ9<TAB>ABSENT` — counter-level, command shape

```
python3 -B <counter> --root <lane> --rev e65538e73c7f1a8f7570bc24a2215da8a90043f3 \
  --fleet-root <fleet> --population census/round-77/c2-population.tsv --ledger <dup-ledger>
```

| counter | LD2 (`P02 ABSENT`, 2 col, id present) | LD2b (`ZZ9 ABSENT`, 2 col, id absent) |
|---|---|---|
| pristine | `LEDGER-REFUSED id=P02 why=unknown or duplicate id`, rc 1, `refused=1` | `LEDGER-REFUSED id=ZZ9 …`, rc 1, `refused=1` |
| `m17-duplicate-id` | marker P02, rc 1 | marker ZZ9, rc 1 |
| `m17b-target-keyed` | marker P02, rc 1 | marker ZZ9, rc 1 |
| `m17c-no-malformed` | marker P02, rc 1 — the duplicate leg fires before the store | **no stdout at all; stderr traceback; rc 1** |

The m17c traceback under LD2b (exact tail):

```
  File "/fast/scratch/hyaku/souji-r90/S90MutCounter/probe/m17c-no-malformed.py", line 494, in _ledger
    ledger[r[0]] = (r[1], r[2])
                          ~^^^
IndexError: list index out of range
```

Reading: one mutant's behaviour changes, for one reason. `m17c` drops only `len(r) < 3`, so a 2-column row whose id
is absent reaches `ledger[r[0]] = (r[1], r[2])` and raises; on LD2 the same row's id `P02` is already in the ledger,
the duplicate leg fires first, and the marker still appears. `m17` (whole duplicate leg dropped) and `m17b`
(duplicate leg keyed on target) keep the length leg and refuse `ZZ9` identically to pristine. LD2b is load-bearing
and sole for `m17c` on the frozen mutant set; it changes nothing for pristine, m17 or m17b.

## 3. Alternative spellings of the malformed guard (Q162)

Six single edits of the same guard (each `old` occurs exactly once; set filed as `spellings.json` in this seat dir,
sha256 `648b1b7e4d0283533c4cc65db916c8a46aefe477e5233693b92c198d305c9877`), scored by the unchanged battery on
BOTH populations:

```
python3 -B census/round-90/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
  --mutants .ufo/waves/round-90/w1/S90MutCounter/spellings.json \
  --work /fast/scratch/hyaku/souji-r90/S90MutCounter/spell --only r89,r90        # EXIT 0
SUMMARY mutants=6 sets=r89,r90 pristine_r89=ok pristine_r90=ok killed_r89=2 killed_r90=3 killed_total=5
```

| # | spelling (single edit of `if len(r) < 3 or r[0] in ledger:`) | r89 | r90 | behaviour vs pristine | verdict |
|---|---|---|---|---|---|
| s1 | `len(r) != 3` (exact width) | survives | survives | refuses every frozen 4-column ledger row: 31 extra `LEDGER-REFUSED` lines and rc 1 on every run | unrowed AND invisible to the harness scoring |
| s2 | `len(r) <= 2` | survives | survives | none — same predicate | unrowed (no observable difference) |
| s3 | `len(r) == 2` (refuse exactly two columns) | survives | survives | 1-column rows reach the store and crash (IndexError) | unrowed: the 1-column shape is reachable, LD2b does not reach it |
| s4 | `len(r) < 2` (threshold moved, 2-col accepted) | survives | **killed** (mismatches=1) | identical to `m17c`: 2-column absent id crashes | bound by LD2b |
| s5 | malformed row appends to `bad` BUT still stores (`continue` dropped) | killed (1) | killed (2) | crash on any 2-column row, id present or absent | already killed on r89 by LD2; LD2b only adds a second red row |
| s6 | malformed row skipped silently (no marker, no bad entry) | killed (1) | killed (2) | no `LEDGER-REFUSED` for 2-column rows; rc falls to 0 | already killed on r89 by LD2; LD2b only adds a second red row |

So LD2b binds exactly one spelling class: *a 2-column row under an absent id must be refused fail-closed with the
marker and rc 1*. It does NOT bind the literal guard. Three DIFFERENT single edits survive the r90 population:
- s2 `len(r) <= 2` — logically identical, unsurprising;
- s3 `len(r) == 2` — a real narrowing (1-column rows crash) that no row reaches; a `where=ledger` row appending
  `ZZ9` alone (1 column, expect `LEDGER-REFUSED`/1) would bind it — measured: pristine marker rc 1, s3 crash;
- s1 `len(r) != 3` — a real widening-in-the-other-direction (all 4-column rows refused) that no row reaches; the
  harness cannot see it: only 5 of 58 rows assert an exit code and all five expect 1, which a reader that refuses
  everything also returns, while the ledger rows only assert that a marker with the item's id is printed (and a
  refusing reader prints one for every recorded id).

Q162 note on s5/s6: both are killed on the r89 population, i.e. by LD2 — the malformed leg itself is exercised by
LD2; what LD2 could not do was distinguish "refused through the malformed leg" from "refused through the duplicate
leg", because on LD2 both legs are true. LD2b is the row that removes that ambiguity for the drop-the-leg mutant.

## 4. Q162 probes for the r91 planned rows

Mutants (single edits, filed as `q162-probes.json` in this seat dir): `ld1c-class-keyed` (refuse only a
class-CONFLICTING duplicate — r89's `l2`), `ld1d-conflict-keyed` (refuse only a class-or-target-conflicting
duplicate, i.e. accept an identical duplicate — r89's `l1`), `nf6i2-last-occurrence` (`_whole` starts at
`line.rfind` — r89's `h4`), `nf6j-pathch-narrow` (`PATHCH` narrowed to alnum + `/` — r89's `h1`). Scored on every
pinned population r83–r90:

```
python3 -B census/round-90/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
  --mutants .ufo/waves/round-90/w1/S90MutCounter/q162-probes.json \
  --work /fast/scratch/hyaku/souji-r90/S90MutCounter/probe8b --only r83,r84,r85,r86,r87,r88,r89,r90
```

Result, EXIT 0 (elapsed 706 s). Exact lines:

```
MUTANT-PAIR ld1c-class-keyed pop=r83 killed=no mismatches=0 errors=0 exit=0 | pop=r84 killed=no mismatches=0 errors=0 exit=0 | pop=r85 killed=no mismatches=0 errors=0 exit=0 | pop=r86 killed=no mismatches=0 errors=0 exit=0 | pop=r87 killed=no mismatches=0 errors=0 exit=0 | pop=r88 killed=no mismatches=0 errors=0 exit=0 | pop=r89 killed=no mismatches=0 errors=0 exit=0 | pop=r90 killed=no mismatches=0 errors=0 exit=0
MUTANT-PAIR ld1d-conflict-keyed/same 8 cells killed=no mismatches=0 exit=0
MUTANT-PAIR nf6i2-last-occurrence/same 8 cells killed=no mismatches=0 exit=0
MUTANT-PAIR nf6j-pathch-narrow/same 8 cells killed=no mismatches=0 exit=0
SUMMARY mutants=4 sets=r83,r84,r85,r86,r87,r88,r89,r90 pristine_r83=ok pristine_r84=ok pristine_r85=ok pristine_r86=ok pristine_r87=ok pristine_r88=ok pristine_r89=ok pristine_r90=ok killed_r83=0 killed_r84=0 killed_r85=0 killed_r86=0 killed_r87=0 killed_r88=0 killed_r89=0 killed_r90=0 killed_total=0
```

(`q162.txt` carries all four full MUTANT-PAIR lines; the three abbreviated above are character-for-character the
same cells with their own ids.) All eight pristine arms were green: `pop=r83 rows=36` … `pop=r90 rows=58`, each
`mismatches=0 errors=0 exit=0`.

| candidate | mutant scored (single edit) | killed | verdict | row shape it needs (or killer row) |
|---|---|---|---|---|
| LD1c | `ld1c-class-keyed` — refuse only a class-CONFLICTING duplicate (r89 `l2`) | no on all 8 (killed_total=0) | survives every pinned population → **needs a row** | `where=ledger`, item `P02`, append `P02<TAB>ABSENT<TAB>census/nowhere/ld1c` (3 col, class `ABSENT` equal to the frozen P02 class, different target). Counter-level: l2 no marker rc0 (red); l1 still refuses → LD1c isolates l2. |
| LD1d | `ld1d-conflict-keyed` — accept an identical duplicate (r89 `l1`) | no on all 8 (killed_total=0) | survives → **needs a row** | append `P01<TAB>FLEET<TAB>-` (identical class+target). Counter-level: l1 AND l2 both no marker rc0 → this single row kills both spellings. |
| NF6i2 | `nf6i2-last-occurrence` — `_whole` starts at `line.rfind(needle)` (r89 `h4`) | no on all 8 | survives → **needs a row** | fixture rev R13: the R12 twice-token line reversed, whole occurrence FIRST (`tests/…/.git and xtests/…/.git`), target a fresh leaf. Pristine resolves it (QUARANTINED); rfind examines only the suffix occurrence and refuses → row red. |
| NF6j | `nf6j-pathch-narrow` — `PATHCH = alnum + "/"` (r89 `h1`) | no on all 8 | survives → **needs a row** | fixture rev R13: one declaration carrying the token after each of `. _ @ + ~ -` (e.g. `.tests/…; _tests/…; @tests/…; +tests/…; ~tests/…; -tests/…`), fresh leaf target. Pristine refuses (all six are path bytes); the narrowed guard sees at least one occurrence whole → resolves → red. The prereg's limit ii calls NF6h's `/` predecessor "one of the eight PATHCH classes, not the set", so this row is the carried narrowing, still worth a row under Q162 because the mutant survives. |

Q162 minimality note on the pair: LD1d's shape kills BOTH `l1` and `l2`, while LD1c's shape kills only `l2`. Neither mutant
is killed by any pinned population, so neither proposed row is padding in Q162's stated sense (already-killed), but if
r91 adds both, LD1c adds no killed mutant beyond LD1d — the pair is redundant while a lone LD1d row would bind both
spellings. The two mutants are distinct readings; one row (LD1d's identical-duplicate shape) suffices for coverage.

All four probes survive the r90 population too, so LD2b does not absorb any r91-planned clause.

Row-shape measurements at counter level (r77 ledger + one appended row; `M:` = `LEDGER-REFUSED id=`):

| appended row | pristine | l2 class-keyed | l1 conflict-keyed |
|---|---|---|---|
| `P02 ABSENT census/nowhere/ld1c` (3 col, same class, diff target — LD1c shape) | M:P02 rc1 | **no marker rc0** | M:P02 rc1 |
| `P01 FLEET -` / `P01 FLEET - note` (identical duplicate — LD1d shape) | M:P01 rc1 | **no marker rc0** | **no marker rc0** |
| `P01 ABSENT -` (LD1) | M:P01 rc1 | M:P01 rc1 | M:P01 rc1 |
| `P01 ABSENT census/nowhere/ld1b` (LD1b) | M:P01 rc1 | M:P01 rc1 | M:P01 rc1 |
| `P02 ABSENT` (LD2) / `ZZ9 ABSENT` (LD2b) | marker rc1 | marker rc1 | marker rc1 |

Consequence for the planned pair: the identical-duplicate shape (LD1d) kills BOTH `l1` and `l2`, while the
same-class-different-target shape (LD1c) kills only `l2`. If r91 adds both, LD1c is redundant kill coverage; if it
adds only one, LD1d alone binds both spellings. This is the Q162 "score before the row" result, not a claim change.

## 5. Unrowed clauses this seat can reach

Measured, not inferred (counter-level matrix over the r77 ledger; full receipts in the seat dir):

1. **1-column ledger row** (prereg limit ii names it). Reachable: pristine prints `LEDGER-REFUSED id=ZZ9` rc 1; an
   `== 2` reader (s3) crashes with no marker. A `where=ledger` row appending `ZZ9` alone would bind it. Unrowed.
2. **The ledger's width acceptance itself.** A reader that refuses every 4-column row (`len(r) != 3`) survives r89
   and r90 because no row asserts that a recorded ledger entry is accepted: the five rc-asserting rows all expect
   1 (which the over-refusing reader also exits) and the four ledger rows only check that a marker with their item's
   id appears — the over-refusing reader prints one for every recorded id. Unrowed, and not bindable by another
   `where=ledger` row of the same shape; it needs a row that asserts an item RESOLVED THROUGH its ledger entry.
3. **4+-column and CRLF-wrapped rows** (limit ii). Measured: a new-id 4-column row behaves exactly like the 3-column
   one (unknown-id leg, same marker, same rc; a 4-column duplicate behaves like the 3-column duplicate); CRLF leaves
   `\r` on the last cell and changes no verdict. No distinction a row can assert.
4. **Blank-line / header rows.** `_ledger` skips both; every spelling measured identical. Equivalent, cannot bind
   (matches r89 F8).
5. **Class-keyed duplicate** (`l2`) and **identical duplicate** (`l1`): measured, both survive all eight pinned
   populations (8/8, `killed_total=0`); counter-level row shapes above. Need LD1c / LD1d; a single LD1d-shaped row
   kills both.
6. **Occurrence order in `_whole`** (`rfind`, last-occurrence-only): measured, survives all eight. Needs NF6i2
   (R13, twice-token line with the whole occurrence FIRST).
7. **The six PATHCH punctuation predecessors** (`. _ @ + ~ -`): measured, survives all eight (the `/` predecessor
   alone is bound by NF6h). Needs NF6j (R13, one declaration carrying the token after each class).
8. **`line.isdigit()` / `0 < line <= len(blob)`** (`q1`/`q1b`): unrowable from the current population — the line is
   read from the pinned items file, so an `ERROR` row over a malformed item plus a new items pin is needed
   (r89 F7; not re-measured here, no new instrument).
9. **`_capture_ok`'s `len(want) <= len(have)`** (`m19`): not reached by any false row (r85/r89 carry it); this seat
   did not create a new fixture to reach it, so it is named, not measured.

What I could NOT check: the r83–r88 populations for the six spelling mutants (only r89/r90, as the task requires —
the four Q162 probes were scored on all eight). I did not run C2 (outside this seat). I did not measure the lane's
real ledgers (the populations are fixtures, as the prereg's limits state). I did not build a new fixture to reach
`m19` or `q1`/`q1b`; they are named as carried, not measured here.

## 6. Verdict

- **LD2b is load-bearing and sole for m17c on the frozen mutant set.** After arm reproduces
  `killed_r89=15 killed_r90=16 killed_total=31` EXIT 0; control arm reproduces `killed_r89=15` with m17c alive,
  EXIT 0; the only row that goes red for m17c on r90 is LD2b (`got=-`, `SUMMARY rows=58 mismatches=1`), and the
  mechanism is the stated one (IndexError at `_ledger`, no marker).
- **LD2b binds ONE spelling class, not the literal guard.** It binds "a 2-column row under an absent id is refused
  fail-closed with `LEDGER-REFUSED` and rc 1" (`s4 < 2` dies on r90; `s5`/`s6` already die on r89 via LD2).
  Three different single edits survive the r90 population: `len(r) <= 2` (equivalent), `len(r) == 2` (1-column
  rows crash — reachable but unrowed), `len(r) != 3` (all 4-column ledger rows refused — unrowed AND invisible to
  the harness scoring because no row asserts a resolution through a ledger entry).
- **The r91 planned rows are all justified on the pinned bytes** (each mutant survives 8/8): LD1c
  (`l2`, same-class different-target duplicate), LD1d (`l1`, identical duplicate), NF6i2 (`h4`, occurrence order),
  NF6j (`h1`, the six PATHCH punctuation predecessors). No killer row exists for any of them; none is killed by
  LD2b. One caveat for the planner: LD1d's shape alone kills both `l1` and `l2`, so the LD1c+LD1d pair is
  redundant coverage if both are added.

## 7. Receipts and scratch

Seat dir `.ufo/waves/round-90/w1/S90MutCounter/`:
- `spellings.json` — six spelling members (sha256 `648b1b7e…`, in the battery header of `spellings.txt`)
- `q162-probes.json` — four Q162 members (sha256 `62093ba3…`, in the battery header of `q162.txt`)
- `after.txt`, `control.txt`, `spellings.txt`, `q162.txt`, `attr90.txt` — the raw battery/harness outputs quoted
  above; sha256 `d584dabb…` (after), `d0e06880…` (control), `b05e45ff…` (spellings), `011ecb3f…` (q162),
  `f07f8bfb…` (attr90)
- `probe-matrices.txt` — the counter-level shape × counter matrix and the exact m17c traceback (regenerable; the
  traceback names the scratch path `…/probe/m17c-no-malformed.py`, built by the filed one-line replacement)

Scratch `/fast/scratch/hyaku/souji-r90/S90MutCounter/` (fixtures, mutant files, work dirs) is deleted at yield; no
scratch is left behind. No mutating git/jj command was run anywhere: the batteries' fixtures are their own clones
under the scratch dir and the harness asserts the fixture toplevel before committing. No tool was installed or
upgraded this seat.

