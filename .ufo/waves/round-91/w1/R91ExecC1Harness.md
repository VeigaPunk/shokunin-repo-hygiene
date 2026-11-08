# R91ExecC1Harness — C1 population + harness hand-drive audit (souji round 91, wave 1)

Seat: R91ExecC1Harness (leaf executor). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Contract read first: `census/round-91/preregistration.txt` (commit F a703bcb7…), lane base
681f6c72b242d410d0e8654efadb2a1553fb111d. Instruments are frozen; this seat modified nothing under `census/`,
`tests/fixtures/`, `tools/` or `corpus/` (other seats' working-tree edits to `corpus/` visible in `git status`
are not this seat's). Scratch `/fast/scratch/hyaku/souji-r91/R91ExecC1Harness/` was used for fixtures/counter
copies and deleted before yield; receipts were copied to `receipts/` beside this file.
No git/jj mutation was performed anywhere; every fixture git call named `-C <fixture>` and the fixture
toplevel was asserted (`git -C … rev-parse --show-toplevel` →
`/fast/scratch/hyaku/souji-r91/R91ExecC1Harness/work-r91/fixture`).

## 0. Instrument hashes observed (prereg pins in parentheses)

```
fdc3d23839527fc1b67ef78945d0e537811ba28a8a2156fb9c598946a02bc460  census/round-91/c1-false-rows.tsv   (pin fdc3d238…)
5c6a1cf9825689a964a7ff104be2a7124095b03eba7727ec7c3ebe7026f601fc  census/round-91/c1-false-row-harness.py (pin 5c6a1cf9…)
5f717a1bf162f4ca26b1a8e25dab21d52564787118547156ead5e58fde541b0e  census/round-91/c1-clause-battery.py  (pin 5f717a1b…)
3c26051e2b18e387bb267ec68630d34b781ed3f064b0c05c7943520c04ef6ad9  census/round-91/c1-mutants.json       (pin 3c26051e…)
fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b  census/round-87/c1-pointer-counter.py  (pin fd0a8e24…)
d64d76954daea7da5d36e6f5eda96ae343bdd37db5071ea50bd55b30a1844b45  census/round-90/c1-false-rows.tsv    (r90 control)
```
All six match the preregistration byte-for-byte.

Counter "BYTE-UNCHANGED" proof (independent of the sha pin): the worktree blob, the lane-base blob and HEAD agree,
and the r90 receipts name the same sha:

```
$ git hash-object census/round-87/c1-pointer-counter.py
243c34bc805fa5e5bbd448aa10bfd6268be3393d
$ git rev-parse 681f6c72b242d410d0e8654efadb2a1553fb111d:census/round-87/c1-pointer-counter.py
243c34bc805fa5e5bbd448aa10bfd6268be3393d
$ git diff --stat 681f6c72… HEAD -- census/round-87/c1-pointer-counter.py   # empty
$ git diff --stat -- census/round-87/c1-pointer-counter.py                  # empty
$ grep -h fd0a8e24 census/round-90/records/c1-after.txt | head -1
# counter path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-87/c1-pointer-counter.py sha256=fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b
```

Instrument lineage verified by diff against the previous round (so the prereg's "the r90 X plus …" wording is
literally true, not merely asserted):
- `census/round-90/c1-false-row-harness.py` → r91 harness diff is exactly: docstring, the r91 population pin,
  the R13 fixture block, `R13` added to the accepted rev labels, `ledger-resolve` added to the row-type set and
  its BASE-row classification, the LD1c/LD3 append shapes, the `ledger-resolve` row branch, and
  `last-stub`/`pathch-stub` added to the fixture leaf list. No judgement code changed.
- `census/round-90/c1-clause-battery.py` → r91 battery diff is exactly: docstring, the r90 pin path fix
  (`HERE` → `census/round-90/…`), the r91 pin, and the battery's own sha256 print.
- `census/round-90/c1-mutants.json` → r91: first 16 members byte-identical (`all(x==y for x,y in zip(a,b[:16]))`
  → `True`), 22 members, six new ids, all unique.

## 1. Pristine r87 counter on the r91 population — receipt

Command (cwd = lane):

```
python3 -B census/round-91/c1-false-row-harness.py \
  --counter census/round-87/c1-pointer-counter.py \
  --lane /home/vgpnk/Projects/shokunin/souji-shokunin \
  --fleet-root /home/vgpnk/Projects/shokunin \
  --work /fast/scratch/hyaku/souji-r91/R91ExecC1Harness/work-r91 \
  --population census/round-91/c1-false-rows.tsv
```

Receipt: `receipts/harness-r91.out` (68 lines: 4 header + 63 ROW + SUMMARY), stderr empty. Exit **0**.

```
# harness sha256=5c6a1cf9825689a964a7ff104be2a7124095b03eba7727ec7c3ebe7026f601fc base=e65538e73c7f1a8f7570bc24a2215da8a90043f3
# population path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-91/c1-false-rows.tsv sha256=fdc3d23839527fc1b67ef78945d0e537811ba28a8a2156fb9c598946a02bc460
# counter path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-87/c1-pointer-counter.py sha256=fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b
# fixture F0=6436db6a8ea2d9d0deea6f57cbc160fafa4c6c23 R1=f28736a936699bdbb3653630a130648512ead31a R2=afc4ceb7bc9340b1847d705e6b3bce9e0e24bce6 R3=bdea7114f6afc467a4b35d1546e3fc190c2656c1 R4=0440ea312278b7888d9f0d984a60f9c0d62ea236 R5=d1ed98f40cf657ffbf0c6220ebefe5351c99d521 R6=fd1b8083966fd7a3e0cfee4de02d70d61b4f3675 R7=afc36569eff0a59cfbc863718e7ffc19e76acddf R8=db68908dd7641e582bd9a79560b7b52c3d94caa3 R9=351bdd54903d80748687f4dee04d92d880617b8b R10=e5c9ebc53d7e86fb391286be2e618af801d33f99 R11=b38e92848933a106a61dba00663cfa29bd0cc948 R12=655d1893ae7dfccd5494642c3c5719e37a4a119e R13=8a61ecf4e4f494cac85cfd80d8170c3666818766
ROW LD1c where=ledger rev=BASE item=P01 class=- expect=LEDGER-REFUSED/1 got=LEDGER-REFUSED rc=1 match=yes
ROW LD3 where=ledger rev=BASE item=ZY8 class=- expect=LEDGER-REFUSED/1 got=LEDGER-REFUSED rc=1 match=yes
ROW LD4 where=ledger-resolve rev=BASE item=P04 class=- expect=MOVED/- got=MOVED rc=0 match=yes
ROW NF6i2 where=fixture rev=R13 item=L06 class=QUARANTINED expect=QUARANTINED/- got=QUARANTINED rc=1 match=yes
ROW NF6j where=fixture rev=R13 item=L06 class=QUARANTINED expect=REFUSED/- got=REFUSED rc=1 match=yes
SUMMARY rows=63 mismatches=0 accepted=0 refused_true=0 errors=0
```

All 63 ROW lines read `match=yes` (`grep -c 'match=yes'` = 63, `grep -c '^ROW '` = 63); no row is an error.
The five r91-new rows are exactly the five quoted above. NOTE ON THE BRIEF: the r91 population delta is **five**
rows, not eleven — the only eleven new objects this round are five rows + six new mutant members; the receipt
itself has 63 ROW lines (58 r90 + 5). All 63 are in `receipts/harness-r91.out`.

## 2. Pristine counter on the r90 population — the 58-row control

```
python3 -B census/round-91/c1-false-row-harness.py … --work …/work-r90 --population census/round-90/c1-false-rows.tsv
```

Receipt: `receipts/harness-r90.out` (4 header + 58 ROW + SUMMARY). Exit **0**.

```
SUMMARY rows=58 mismatches=0 accepted=0 refused_true=0 errors=0
```

58 ROW lines, all `match=yes`. The same harness accepts the r90 pin (58) and the r91 pin (63); the r90
population is the do-nothing control and stays green.

## 3. Population delta: r91 = r90 + exactly five rows

```
r90_size=14628  r91_size=16134
$ cmp -n 14628 census/round-90/c1-false-rows.tsv census/round-91/c1-false-rows.tsv
(no output)  → PREFIX-IDENTICAL: the first 14628 bytes of r91 are r90 byte-for-byte
$ diff census/round-90/c1-false-rows.tsv census/round-91/c1-false-rows.tsv
@@ -58,3 +58,8 @@
+LD1c  ledger          BASE r77 P01 - - LEDGER-REFUSED 1  r91 C1: the `_ledger` duplicate-id refusal for an IDENTICAL duplicate (same class and target). …
+LD3   ledger          BASE r77 ZY8 - - LEDGER-REFUSED 1  r91 C1: the malformed guard's ONE-COLUMN reach: the appended row is `ZY8` alone. …
+LD4   ledger-resolve  BASE r77 P04 - - MOVED            -  r91 C1: the ledger WIDTH-ACCEPTANCE clause: with the frozen 4-column ledger unchanged, item P04 resolves MOVED only if a recorded 4-column entry is accepted; …
+NF6i2 fixture         R13  r78 L06 QUARANTINED .ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/last-stub   QUARANTINED -  r91 C1: `_whole` examines occurrences left to right. R13 carries the token WHOLE first and as a suffix later; …
+NF6j  fixture         R13  r78 L06 QUARANTINED .ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/pathch-stub REFUSED     -  r91 C1: the six PATHCH punctuation predecessors `. _ @ + ~ -`; …
```

`diff | grep -c '^>'` = **5**. The five additions are the last five rows (file lines 61–65; 63 rows + 2 comment
lines = 65 lines). No r90 row changed, none was reordered. sha256 of the whole file is the prereg pin
`fdc3d238…`. (In the quote above tabs are rendered as spaces and the long source notes elided with `…`; the raw
`diff -u` and the `cmp`/size proof are filed at `receipts/population-delta.txt`.)

## 4. R13 fixture block and leaves

Harness source (`census/round-91/c1-false-row-harness.py:346-352`) writes exactly these two declaration lines
(quoted from the harness source; `q6` = `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/`):

```
f.write(f"\n- retired copy: tests/vault/vadv54-run/p/p6repo/.git and xtests/vault/vadv54-run/p/p6repo/.git; "
        f"quarantine slot `{q6}last-stub`.\n".encode())
f.write(f"- path predecessors: .tests/vault/vadv54-run/p/p6repo/.git; _tests/vault/vadv54-run/p/p6repo/.git; "
        f"@tests/vault/vadv54-run/p/p6repo/.git; +tests/vault/vadv54-run/p/p6repo/.git; "
        f"~tests/vault/vadv54-run/p/p6repo/.git; -tests/vault/vadv54-run/p/p6repo/.git; "
        f"quarantine slot `{q6}pathch-stub`.\n".encode())
```

As committed at fixture rev R13 (`8a61ecf4e4f494cac85cfd80d8170c3666818766`, `corpus/lessons/round-79-collision.md`):

```
- retired copy: tests/vault/vadv54-run/p/p6repo/.git and xtests/vault/vadv54-run/p/p6repo/.git; quarantine slot `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/last-stub`.
- path predecessors: .tests/vault/vadv54-run/p/p6repo/.git; _tests/vault/vadv54-run/p/p6repo/.git; @tests/vault/vadv54-run/p/p6repo/.git; +tests/vault/vadv54-run/p/p6repo/.git; ~tests/vault/vadv54-run/p/p6repo/.git; -tests/vault/vadv54-run/p/p6repo/.git; quarantine slot `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/pathch-stub`.
```

Leaf check on the fixture disk (`work-r91/fixture/.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/`):
both fresh leaves exist and are **disk-only** (not in the R13 tree, so the declaration is the only binding):

```
-rw-r--r-- 22 Nov  8 13:20 last-stub      → "r80 fixture last-stub"
-rw-r--r-- 24 Nov  8 13:20 pathch-stub    → "r80 fixture pathch-stub"
$ git -C $FX ls-tree -r --name-only R13 | grep -E 'last-stub|pathch-stub'
NOT-TRACKED: last-stub and pathch-stub are disk-only
```

`git grep -h -F -I -e <target> R13 -- corpus` returns exactly one line per target — the two declarations above —
so each row's quarantine leaf is bound by exactly one committed line. (Leaf body text says "r80 fixture …" for
every leaf, inherited from the r80 writer; cosmetic only, no claim depends on leaf content.) The full check
(toplevel assertion, leaf listing/contents, `ls-tree`, `git grep`) is filed at `receipts/r13-fixture-check.txt`;
the fixture itself was scratch and is deleted.

## 5. Hand-drive: NF6i2 and NF6j at R13 (one-row forge, pristine + the two Q162 probes)

Driver: `receipts/handdrive.py` (recreates the counter copies from the filed mutants JSON with
`src.count(old) == 1` asserted, writes the forge TSV the harness writes, runs the counter at the R13 commit).
Receipt: `receipts/handdrive.out`. Forge rows (exactly the harness's `{rid}\t{item}\t{cls}\t{target}\tREFUSED`):

```
NF6i2	L06	QUARANTINED	.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/last-stub	REFUSED
NF6j	L06	QUARANTINED	.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/pathch-stub	REFUSED
```

| drive | counter | FORGE line (verbatim) | exit |
|---|---|---|---|
| NF6i2 | pristine r87 (`fd0a8e24…`) | `FORGE NF6i2 item=L06 class=QUARANTINED expect=REFUSED got=QUARANTINED match=no` | 1 |
| NF6i2 | `nf6i2-last-occurrence` (`87942593…`) | `FORGE NF6i2 item=L06 class=QUARANTINED expect=REFUSED got=REFUSED match=yes` | 1 |
| NF6i2 | `nf6j-pathch-narrow` (`ab015cde…`) | `FORGE NF6i2 item=L06 class=QUARANTINED expect=REFUSED got=QUARANTINED match=no` | 1 |
| NF6j | pristine r87 | `FORGE NF6j item=L06 class=QUARANTINED expect=REFUSED got=REFUSED match=yes` | 1 |
| NF6j | `nf6i2-last-occurrence` | `FORGE NF6j item=L06 class=QUARANTINED expect=REFUSED got=REFUSED match=yes` | 1 |
| NF6j | `nf6j-pathch-narrow` | `FORGE NF6j item=L06 class=QUARANTINED expect=REFUSED got=QUARANTINED match=no` | 1 |

Reading: the harness compares `got` to the row's `expect_got`, so NF6i2 binds `nf6i2-last-occurrence` only
(pristine and nf6j both resolve QUARANTINED), and NF6j binds `nf6j-pathch-narrow` only (pristine and nf6i2 both
refuse). The mutant `nf6i2` is not killed by NF6j and `nf6j` is not killed by NF6i2 — no cross-binding.
Exit is 1 on every arm because the r78 population itself carries two refused items
(`SUMMARY items=22 resolved=20 … refused=2`), not because of the forge; the row's `expect_rc` is `-`, so the
harness asserts only `got`, as the prereg says.

## 6. Hand-drive: LD1c, LD3, LD4 (ledgers built in scratch, pristine + four ledger mutants)

Ledgers: `receipts/ledger-LD1c.tsv` = frozen r77 ledger + `P01<TAB>FLEET<TAB>-<TAB>r91 LD1c identical duplicate…`;
`receipts/ledger-LD3.tsv` = frozen r77 ledger + `ZY8` alone; LD4 runs the frozen r77 ledger unchanged
(`sha256 011faa0e…`). Population = `census/round-77/c2-population.tsv` (35 items), root = lane, rev = BASE
`e65538e73c7f1a8f7570bc24a2215da8a90043f3` (the counter refuses `--rev BASE`; the harness substitutes the commit).

### LD1c — identical duplicate

| counter | marker line | exit | row verdict |
|---|---|---|---|
| pristine | `LEDGER-REFUSED id=P01 why=unknown or duplicate id` | 1 | pass (expected marker+1) |
| `ld1c-class-keyed` | *(none)*; `SUMMARY items=35 resolved=35 … refused=0` | 0 | **red → killed** |
| `ld1d-conflict-keyed` | *(none)*; `SUMMARY items=35 resolved=35 … refused=0` | 0 | **red → killed** |
| `s3-equal-two` | `LEDGER-REFUSED id=P01 …` | 1 | pass |
| `s1-exact-width` | `LEDGER-REFUSED id=P01 …` (plus 31 more, and `ITEM P04 … status=UNRESOLVED`) | 1 | pass |

### LD3 — one-column row

| counter | marker line | exit | row verdict |
|---|---|---|---|
| pristine | `LEDGER-REFUSED id=ZY8 why=unknown or duplicate id` | 1 | pass |
| `ld1c-class-keyed` | `LEDGER-REFUSED id=ZY8 …` | 1 | pass |
| `ld1d-conflict-keyed` | `LEDGER-REFUSED id=ZY8 …` | 1 | pass |
| `s3-equal-two` | *(none)*; stderr `IndexError: list index out of range` | 1 | **red → killed** |
| `s1-exact-width` | `LEDGER-REFUSED id=ZY8 …` | 1 | pass |

### LD4 — resolve through the unchanged 4-column ledger

| counter | ITEM P04 line | exit | row verdict |
|---|---|---|---|
| pristine | `ITEM P04 SCORECARD.md:598 status=MOVED` | 0 | pass |
| `ld1c-class-keyed` | `ITEM P04 SCORECARD.md:598 status=MOVED` | 0 | pass |
| `ld1d-conflict-keyed` | `ITEM P04 SCORECARD.md:598 status=MOVED` | 0 | pass |
| `s3-equal-two` | `ITEM P04 SCORECARD.md:598 status=MOVED` | 0 | pass |
| `s1-exact-width` | `ITEM P04 SCORECARD.md:598 status=UNRESOLVED` + `LEDGER-REFUSED id=P04 …` | 1 | **red → killed** |

## 7. Row × mutant binding table (hand-drive result)

| row | pristine | ld1c | ld1d | s1 | s3 | nf6i2 | nf6j |
|---|---|---|---|---|---|---|---|
| LD1c | pass | **KILL** | **KILL** | pass | pass | — | — |
| LD3 | pass | pass | pass | pass | **KILL** | — | — |
| LD4 | pass | pass | pass | **KILL** | pass | — | — |
| NF6i2 | pass | — | — | — | — | **KILL** | pass |
| NF6j | pass | — | — | — | — | pass | **KILL** |

("—" = not driven because the row's mechanism does not touch that mutant's clause; every cell that matters was
driven. `KILL` = the counter's output no longer matches the row's expected got/marker, i.e. the harness would
count a mismatch and exit non-zero.)

**Redundancy:** none of the five rows is redundant w.r.t. the six new mutants. Each row has at least one unique
killer (LD1c → ld1c, ld1d; LD3 → s3; LD4 → s1; NF6i2 → nf6i2; NF6j → nf6j), and the earlier r88–r90 ledger rows
(LD1/LD1b/LD2/LD2b) do **not** kill ld1c/ld1d (class/target conflicts are refused by both keyed spellings — see
LD1c's ld1c/ld1d rows passing, while LD1/LD1b append class/target-conflicting duplicates), s1 (3-column rows are
accepted by `len(r)!=3`), or s3 (2-column rows are refused by `len(r)==2`). LD1c binds two mutants with one row,
which is exactly the prereg's Q162 minimal-killer claim, not redundancy.

**"Survive every population the lane has pinned before this round":** the row bodies are a strict prefix chain
(r83 36 ⊂ r84 44 ⊂ r85 47 ⊂ r86 49 ⊂ r87 51 ⊂ r88 53 ⊂ r89 57 ⊂ r90 58 ⊂ r91 63; verified row-by-row with
`diff <(grep -v '^#' prev) <(grep -v '^#' cur | head -n <prev_rows>)` — all OK; r87 differs only in its added
header comment line, so the whole-file `cmp` is not the right test there). Since a mutant's harness exit is a
function of the rows it mismatches, survival on the r90 superset implies survival on every earlier subset
[INFERENCE from the prefix chain + the r90 arm below]. The filed P2 control (written before F) records exactly
that, and my independent row drives agree:

```
census/round-91/controls/c1-control-r90.txt
MUTANT ld1c-class-keyed pop=r90 killed=no mismatches=0 errors=0 exit=0
MUTANT ld1d-conflict-keyed pop=r90 killed=no mismatches=0 errors=0 exit=0
MUTANT nf6i2-last-occurrence pop=r90 killed=no mismatches=0 errors=0 exit=0
MUTANT nf6j-pathch-narrow pop=r90 killed=no mismatches=0 errors=0 exit=0
MUTANT s1-exact-width pop=r90 killed=no mismatches=0 errors=0 exit=0
MUTANT s3-equal-two pop=r90 killed=no mismatches=0 errors=0 exit=0
SUMMARY mutants=22 sets=r90 pristine_r90=ok killed_r90=16 killed_total=16
```

## 7b. Harness-level sweep: the six new mutants on both populations

Independent of the row hand-drives, the same harness was run once per new mutant on each population
(receipts `receipts/sweep/<mutant>-<pop>.out`, summary `receipts/sweep/sweep-summary.txt`; 12 runs, ~8.5 min):

| mutant | r90 (58 rows) | r91 (63 rows) | the one red ROW on r91 |
|---|---|---|---|
| `ld1c-class-keyed` | EXIT=0 mismatches=0 | EXIT=1 mismatches=1 | `ROW LD1c … expect=LEDGER-REFUSED/1 got=- rc=0 match=no` |
| `ld1d-conflict-keyed` | EXIT=0 mismatches=0 | EXIT=1 mismatches=1 | `ROW LD1c … expect=LEDGER-REFUSED/1 got=- rc=0 match=no` |
| `nf6i2-last-occurrence` | EXIT=0 mismatches=0 | EXIT=1 mismatches=1 | `ROW NF6i2 … expect=QUARANTINED/- got=REFUSED rc=1 match=no` |
| `nf6j-pathch-narrow` | EXIT=0 mismatches=0 | EXIT=1 mismatches=1 | `ROW NF6j … expect=REFUSED/- got=QUARANTINED rc=1 match=no` |
| `s1-exact-width` | EXIT=0 mismatches=0 | EXIT=1 mismatches=1 | `ROW LD4 … expect=MOVED/- got=UNRESOLVED rc=1 match=no` |
| `s3-equal-two` | EXIT=0 mismatches=0 | EXIT=1 mismatches=1 | `ROW LD3 … expect=LEDGER-REFUSED/1 got=- rc=1 match=no` |

`grep 'match=no' *-r90.out` → none: every r90 arm is fully green, so all six survive the r90 population. On r91
each mutant turns exactly ONE row red, and the red row is the row the prereg assigns to it. This is the
harness-level confirmation of the row × mutant table above and of the kill rule (a row mismatch ⇒ non-zero exit).

## 8. Mismatches to the prereg

### FALSIFIES-WORDING (C1 stated limit iii) — HIGH (per the acceptance rule: any mismatch to the prereg is HIGH)

Exact sentence falsified (preregistration, C1 STATED LIMITS (iii)):

> "LD4 asserts an ITEM status and no exit code: the base run is not all-resolved (the r77 population is mostly
> false rows), so exit 1 is expected and not asserted."

Observed, with the frozen counter, the frozen r77 population and the frozen r77 ledger at BASE (the exact LD4
run), twice — once through the harness and once by hand:

```
$ python3 -B census/round-87/c1-pointer-counter.py --root <lane> --rev e65538e73c7f1a8f7570bc24a2215da8a90043f3 \
    --fleet-root /home/vgpnk/Projects/shokunin --population census/round-77/c2-population.tsv \
    --ledger census/round-77/c2-pointer-ledger.tsv
ITEM P04 SCORECARD.md:598 status=MOVED
SUMMARY items=35 resolved=35 unresolved=0 refused=0 mismatched=0 errors=0
EXIT=0
```

and the harness's own r91 receipt: `ROW LD4 where=ledger-resolve rev=BASE item=P04 class=- expect=MOVED/- got=MOVED rc=0 match=yes`.

So the base run **is** all-resolved (35/35) and exits **0**, not 1; the parenthetical ("the r77 population is
mostly false rows") is also wrong — the r77 population is the baseline MISSING-finding population, and its frozen
ledger resolves every row. Reproducer: `receipts/harness-r91.out` (ROW LD4, rc=0) and
`receipts/handdrive.out` (section `=== ledger drive LD4 ===`, pristine block).

The lane's own pre-freeze receipts already contradict the sentence, so this is not an artifact of my environment:

```
census/round-91/controls/c1-harness-smoke-r91.txt:65
ROW LD4 where=ledger-resolve rev=BASE item=P04 class=- expect=MOVED/- got=MOVED rc=0 match=yes
census/round-91/controls/NOTES.txt:6
  LD3=LEDGER-REFUSED/1, LD4=MOVED/0, NF6i2=QUARANTINED/1, NF6j=REFUSED/1.
```

Both filed before F. Impact: rationale only — LD4's row predicate asserts the ITEM status and `expect_rc='-'`, so
the predicate still holds and s1 is still killed (UNRESOLVED); but the prereg sentence must be narrowed by
amendment, not silently repaired (Amendment 59). No other C1 sentence was falsified by this seat's artifacts.

## 9. Risks / limits observed (not falsifications)

- The harness's fixture builder reads several lane working-tree byte sources (`census/round-32/waves/a2w1/…`,
  `census/round-84/records/c1-after.txt`, `.ufo/quarantine/`, `.ufo/waves/round-61/w1/…`) without pinning their
  shas; P04, P07 and I86S are pinned. Inherited from r90, not widened this round; a lane-side edit to an
  unpinned source would change fixture content silently.
- The leaf body text is `r80 fixture <leaf>` for the r91 leaves; cosmetic, no row depends on it.
- NF6i2/NF6j rows are fixture rows judged at R13; their `rc` is 1 on the pristine arm because the r78 population
  carries two refused items — the row asserts `got` only (`expect_rc='-'`), matching the harness's `ok` logic.
- The six new mutants turn exactly one row red each; the kill is therefore a clean row mismatch, not a harness
  error or a crash (except `s3-equal-two` on LD3, whose kill is the counter's IndexError — the kill rule counts
  it, and the harness records `got=-`).
- `census/round-91/records/c1-after.txt` (the L1's after receipt) was mid-write when sampled: 21 lines ending at
  `m7-round-blind` at 13:31, 37 lines ending at `m14-short-shape` at 13:36, no SUMMARY yet — the L1's artifact,
  not used as evidence here.
- This seat ran only the harness, the counter and hand-built ledgers/forges; the full-battery
  `killed_r91=22` predicate (44 harness runs) is the L1's run, not this seat's. My sweep independently covers
  the six new members on both populations (section 7b).

## 10. Receipt manifest (all under `.ufo/waves/round-91/w1/R91ExecC1Harness/receipts/`)

```
harness-r91.out            68 lines: 4 header + 63 ROW + SUMMARY; exit 0
harness-r91.err            empty
harness-r90.out            63 lines: 4 header + 58 ROW + SUMMARY; exit 0
handdrive.py               driver: recreates the six counter copies (count(old)==1 asserted), forges, ledgers
handdrive.out              208 lines: the six FORGE drives + three ledger drives × five counters
ledger-LD1c.tsv            frozen r77 ledger + P01/FLEET/- identical duplicate
ledger-LD3.tsv             frozen r77 ledger + ZY8 alone
forge-NF6i2.tsv, forge-NF6j.tsv
instrument-hashes.txt      the nine instrument sha256s + counter blob identity (worktree == base)
population-delta.txt       sizes, `cmp -n 14628` prefix proof, raw `diff -u` r90→r91
mutant-copies.sha256       full sha256 of the six counter copies built from c1-mutants.json
r13-fixture-check.txt      toplevel assertion, R13 commit, leaf listing/contents, ls-tree, git grep
sweep/sweep-summary.txt    12 RESULT lines (six mutants × r90/r91)
sweep/<mutant>-<pop>.out   12 full harness receipts; .err files empty
```

Counter-copy sha256 (built from the filed `c1-mutants.json`, not hand-edited):
`ld1c-class-keyed` ea5e4f445ede1a81…, `ld1d-conflict-keyed` 7acddc660cd940eb…,
`nf6i2-last-occurrence` 87942593f2ef15fd…, `nf6j-pathch-narrow` ab015cde230a78bc…,
`s1-exact-width` f1f59aaaec66d52b…, `s3-equal-two` f28049bc576d20da… (full hashes in
`receipts/mutant-copies.sha256`).

Tooling: no install or upgrade was needed or performed (operator rule 2026-10-19 recorded; pacman paused, no
uv/npx/official-binary use). Scratch `/fast/scratch/hyaku/souji-r91/R91ExecC1Harness/` deleted after copying
these receipts.
