# R91ReviewerC1 — C1 wording falsification review

Seat: R91ReviewerC1 (reviewer, v1 wave, souji round 91). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Lane tip at review: `a703bcb760ecdb22ec7df06af3059f219ebb95cf` (F, prereg alone). Instruments measured:
P1 `7fb865d8ce5cd76b9d087f890543b315efb58af3`, P2 `d287d3dec54ecc604799115c01ec405a61f46cf4`.
Interpreter: Python 3.14.8. Scratch: `/fast/scratch/hyaku/souji-r91/R91ReviewerC1` (deleted before yield; no `/tmp`
evidence). No lane writes, no git/jj mutation; every git call below is read-only plumbing or a fixture built by the
filed harness inside scratch.

Every number in this report comes from a run I executed on the committed bytes. The L1's own
`census/round-91/records/c1-after.txt` was still growing while I reviewed and is NOT my evidence.

---

## 1. Independent SUMMARYs (re-derived, not copied)

### 1.1 After predicate — verbatim command from the prereg, cwd = lane

```
python3 -B census/round-91/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
  --mutants census/round-91/c1-mutants.json --work /fast/scratch/hyaku/souji-r91/R91ReviewerC1/after \
  --only r90,r91 --expect-killed 38
```

Receipt: `receipts/after.txt`. Pristine arms: `ARM pristine pop=r90 rows=58 mismatches=0 errors=0 exit=0`,
`ARM pristine pop=r91 rows=63 mismatches=0 errors=0 exit=0`.
SUMMARY: `SUMMARY mutants=22 sets=r90,r91 pristine_r90=ok pristine_r91=ok killed_r90=16 killed_r91=22 killed_total=38`
Exit: 0.

### 1.2 Control — `--only r90 --expect-killed 16`

```
python3 -B census/round-91/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
  --mutants census/round-91/c1-mutants.json --work /fast/scratch/hyaku/souji-r91/R91ReviewerC1/control2 \
  --only r90 --expect-killed 16
```

Receipt: `receipts/control.txt` (59 lines). Pristine: `ARM pristine pop=r90 rows=58 mismatches=0 errors=0 exit=0`.
SUMMARY (verbatim): `SUMMARY mutants=22 sets=r90 pristine_r90=ok killed_r90=16 killed_total=16` — exit **0**.
The 16 `MUTANT-PAIR … killed=yes` lines are exactly the sixteen r90 members; the six `killed=no` members are exactly
`ld1c-class-keyed`, `ld1d-conflict-keyed`, `nf6i2-last-occurrence`, `nf6j-pathch-narrow`, `s1-exact-width`,
`s3-equal-two` (each `mismatches=0 errors=0 exit=0`).

### 1.3 "survive every population the lane has pinned before this round" (the word *every*)

The filed predicate scores only r90/r91; the prereg sentence says *every* pinned population. I measured the six new
members on all eight prior pinned populations (r83…r90), pristine included, through the frozen harness
(receipts `receipts/prior-run.txt`, `receipts/prior-table.json`; 56 runs):

```
SURVIVORS-DEAD-ON-A-PRIOR-POPULATION=0
PRISTINE-RED=0
```

Every one of the 48 mutant/population cells reads `mismatches=0 errors=0 exit=0`. This also agrees with the two
earlier receipts on the same counter bytes: `.ufo/waves/round-90/w1/S90MutCounter/q162.txt` (the four Q162 probes,
killed=no on r83…r90) and `.ufo/waves/round-90/w1/S90MutCounter/spellings.txt` (s1/s3, killed=no on r89/r90).
Row-level nesting r83 ⊂ r84 ⊂ … ⊂ r91 is byte-prefix true for all eight pairs (rows, not file headers), so the
"every" is additionally implied by survival on r90; I measured it rather than infer it.

---

## 2. Byte-level checks against the prereg's INSTRUMENTS/POPULATIONS paragraph

| Prereg statement | Re-derived | Verdict |
|---|---|---|
| counter `census/round-87/c1-pointer-counter.py` sha256 `fd0a8e24…`, BYTE-UNCHANGED | `fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b`; same hash at lane base `681f6c72` (`git show 681f6c72:… \| sha256sum`); `git diff 681f6c72..HEAD -- census/round-87/c1-pointer-counter.py` empty | holds |
| r90 population 58 rows sha256 `d64d7695…` (do-nothing control) | hash matches; unchanged vs `681f6c72` | holds |
| r91 population 63 rows sha256 `fdc3d238…` = "the r90 58 rows byte-for-byte in order plus LD1c, LD3, LD4, NF6i2 and NF6j" | hash matches; `r91.startswith(r90)` on full bytes is True; non-comment rows 58 → 63 and `rows91[:58] == rows90`; appended ids in order `LD1c, LD3, LD4, NF6i2, NF6j` | holds |
| harness `census/round-91/c1-false-row-harness.py` sha256 `5c6a1cf9…` ("the r90 harness plus the R13 fixture block and leaves, the `ledger-resolve` row type, the LD1c/LD3 append shapes and the r91 pin") | hash matches; `diff` vs the r90 harness shows exactly: docstring, r91 `POP_PINS` entry, R13 block + two leaves, `R13` in the rev-label tuple, `ledger-resolve` in the where-tuple/root selection, LD1c/LD3 append shapes, and the ledger-resolve branch. No judgement code for lane/fixture/ledger rows changed | holds |
| battery `census/round-91/c1-clause-battery.py` sha256 `5f717a1b…` ("the r90 battery plus the r91 pin, the r90 pin path fix and its own sha256 print") | hash matches; `diff` vs the r90 battery shows exactly those three changes | holds |
| mutants `census/round-91/c1-mutants.json` sha256 `3c26051e…`, 22 members ("the r90 sixteen byte-for-byte plus the four Q162 probes and the two spelling edits") | hash matches; 22 unique ids; the sixteen member texts are byte-identical to `census/round-90/c1-mutants.json` (r91's member array body equals r90's for its full length); the four Q162 members are byte-identical to `.ufo/waves/round-90/w1/S90MutCounter/q162-probes.json`, and `s1-exact-width`/`s3-equal-two` to `spellings.json`; each `old` occurs exactly once in the counter and each `new` occurs zero times | holds |
| `s2` (`len(r) <= 2`) is logically equivalent to the frozen guard | `len(r) < 3` ≡ `len(r) <= 2` over integer lengths | holds |

Kill rule, decoded from the filed battery: `k = rc != 0 or mism > 0 or errs > 0`; harness exit 2 before its SUMMARY
raises `BATTERY-FATAL` (battery exit 2, INVALID), so no scored kill can come from a usage error; a red pristine arm
prints `score=invalid` and exits 2. The prereg's kill-rule sentence and "no work reaches 38" control are consistent
with the code.

Guards re-tested (cheap, no scoring side effects): non-empty `--work` → `BATTERY-FATAL: … is not empty`, rc 2;
`--work /tmp/r91x` → `BATTERY-FATAL: --work under /tmp`, rc 2; `--only r99` → `BATTERY-FATAL: --only 'r99' is not a
subset …`, rc 2. (Note: the bad-`--only` path creates `<work>/mut` before validating the set — cosmetic.)

---

## 3. Sentence table

Legend: **holds** = an artifact of mine confirms the sentence; **neutral** = true but not measured by my artifacts
(or measured only by others); **falsifies-wording** = an artifact of mine refutes the sentence as written.

| # | Sentence (prereg, C1) | Verdict | Evidence |
|---|---|---|---|
| 1 | "Six mutant edits survive every population the lane has pinned before this round" (the six named) | **holds** | §1.2 (r90) + §1.3 (r83…r90, 48/48 green) |
| 2 | "are bound by five new population rows (LD1c, LD3, LD4, NF6i2, NF6j)" | **holds** | §4: each of the six is killed by exactly one of the five rows on r91 (mismatch, `errors=0`); deleting any row lets its mutant(s) survive on a pristine-green 62-row population; LD1c carries two mutants |
| 3 | "LD1c appends an IDENTICAL duplicate to the frozen r77 ledger (`P01<TAB>FLEET<TAB>-`), which both duplicate-keyed spellings accept" | **holds** | r77 ledger `P01 FLEET - …` (4 cols); harness LD1c append is `P01\tFLEET\t-\t…`; both mutants accept it (`falsifies-wording` no) |
| 4 | "LD3 appends a ONE-COLUMN ledger row (`ZY8` alone), which `len(r) == 2` stores and crashes on" | **holds** | direct probe: pristine prints `LEDGER-REFUSED id=ZY8 why=unknown or duplicate id` rc 1, items 35/35 resolved; `s3-equal-two` raises `IndexError: list index out of range` at the store, prints 0 ITEM lines and no ZY8 marker, rc 1 |
| 5 | "LD4 (`where=ledger-resolve`) requires item P04 to resolve MOVED through its UNCHANGED 4-column base ledger entry, which the width-exact reader (`len(r) != 3`) refuses" | **holds** | base ledger P04 row is 4 columns (`MOVED\tcensus/round-32/waves/a2w1/SwarmExecutor08.md\t…`); pristine prints `ITEM P04 SCORECARD.md:598 status=MOVED`; `s1-exact-width` prints `status=UNRESOLVED` + `LEDGER-REFUSED id=P04`; harness passes the base ledger path, unmodified, and no `--forge` |
| 6 | "NF6i2 and NF6j are fixture-revision R13 rows (the token WHOLE first and as a suffix later; the token after each of `. _ @ + ~ -`)" | **holds** | R13 block text in the harness; `_whole` is left-to-right (`line.find` loop) and PATHCH contains `._@+~-`; only `_declared` uses both, so the two edits can only touch declaration matching |
| 7 | POPULATIONS / INSTRUMENTS hashes and immutability (table above) | **holds** | §2 |
| 8 | PREDICATE (after) prints the exact SUMMARY and exits 0 | **holds** | §1.1 |
| 9 | "Control: … `--only r90 --expect-killed 16` reads `killed_r90=16` with ALL SIX new members `killed=no`, EXIT 0" | **holds** | §1.2 |
| 10 | "A mutant is killed … iff the harness exits non-zero … an edit whose `old` does not occur exactly once … INVALID (battery exit 2). A kill of the unmutated counter … INVALID" | **holds** (code + pristine arms) | §2 kill-rule decoding; both pristine arms green in §1.1/§1.2 |
| 11 | STATED LIMIT (iii): "LD4 asserts an ITEM status and no exit code: the base run is not all-resolved (the r77 population is mostly false rows), so exit 1 is expected and not asserted." | **FALSIFIES-WORDING** | §5.3: the base run IS all-resolved (`SUMMARY items=35 resolved=35 …`, rc 0; pre-freeze `ROW LD4 … rc=0`); LD4's row population is the c2 item file, not the mostly-false c1 row population |
| 12 | STATED LIMIT (ii) Q162 minimality ("a same-class-different-target row would kill only `ld1c`"; identical duplicate is the minimal killer) | **neutral/holds** | mutant edits: ld1c refuses only class conflicts, ld1d refuses class-or-target; LD1c's append is class- AND target-equal, so it kills both — confirmed in §4 |
| 13 | STATED LIMITS (i),(iv),(v) | neutral | (i)/(iv) are declared res non-measured surfaces; (v) matches the battery code |

---

## 4. Is each of the five new rows load-bearing?

Method: for each of the five new rows, delete exactly that row from a copy of the r91 population (63 → 62), then score
the six new mutants plus the pristine counter on the reduced population with a harness copy whose ONLY change is the
population-pin branch (my copy `derived-harness.py`, sha256 `8cd871504d2c3f718d1a1cb2db9af4e85535a8958b77adad86ac8b8bd83339a3`;
a pinned population still goes through `POP_PINS` unchanged, so the r90/r91 runs are the frozen semantics). Plus, on
the FULL r91 population, the red-row set of each new mutant, so the killing row is named rather than inferred.
Driver: `derive-driver.py`. Receipts: `receipts/derive-table.json`, `receipts/derive/<population>--<arm>.txt`,
`receipts/derive-run.txt`. The five reduced populations are kept at `receipts/derived-populations/minus-<id>.tsv`
(62 rows each; sha256 prefix LD1c `c4126d90…`, LD3 `f8294f29…`, LD4 `4ae4b704…`, NF6i2 `cafa77f7…`,
NF6j `82624e02…`); each is the frozen 63-row file with the single row whose first field equals that id removed and
nothing else changed.

### 4.1 Killing-row set on the full r91 population (red rows per arm)

| arm | exit | red rows | SUMMARY |
|---|---|---|---|
| pristine | 0 | — | `rows=63 mismatches=0 accepted=0 refused_true=0 errors=0` |
| `ld1c-class-keyed` | 1 | **LD1c** | `rows=63 mismatches=1 … errors=0` |
| `ld1d-conflict-keyed` | 1 | **LD1c** | `rows=63 mismatches=1 … errors=0` |
| `nf6i2-last-occurrence` | 1 | **NF6i2** | `rows=63 mismatches=1 … refused_true=1 errors=0` |
| `nf6j-pathch-narrow` | 1 | **NF6j** | `rows=63 mismatches=1 accepted=1 … errors=0` |
| `s1-exact-width` | 1 | **LD4** | `rows=63 mismatches=1 … errors=0` |
| `s3-equal-two` | 1 | **LD3** | `rows=63 mismatches=1 … errors=0` |

Every kill is a ROW MISMATCH (`errors=0`), not a harness error, so the claim is not resting on stated limit (v).
Each mutant has exactly ONE killing row, and it is the row the claim attributes to it.

### 4.2 Leave-one-out: delete the row, show the loss (62-row populations, pristine green in all five)

| deleted row | survives | everything else |
|---|---|---|
| LD1c | `ld1c-class-keyed` (exit 0), `ld1d-conflict-keyed` (exit 0) | other four still red on their own rows |
| LD3 | `s3-equal-two` (exit 0) | other five still killed |
| LD4 | `s1-exact-width` (exit 0) | other five still killed |
| NF6i2 | `nf6i2-last-occurrence` (exit 0) | other five still killed |
| NF6j | `nf6j-pathch-narrow` (exit 0) | other five still killed |

All five `minus-* pristine` arms: `rows=62 mismatches=0 …` exit 0 — the reduced population is a *valid* control, so
the losses above are the row's binding power and nothing else. **Each of the five new rows is individually
load-bearing, and the sentence "bound by five new population rows" holds at full strength**: deleting any one row
takes `killed_r91` from 22 to 21 (LD1c: 20, since it kills two mutants), so the filed `killed_r91=22` cannot be
reached with a four-row population.

### 4.3 Cross-check that my harness copy did not shift the semantics

The `full` arm's fixture line reproduces the pre-freeze receipt's rev ids (see the `# fixture …` line in
`receipts/derive/full--pristine.txt`, `R13=8a61ecf4e4f494cac85cfd80d8170c3666818766`, identical to
`census/round-91/controls/c1-harness-smoke-r91.txt`), and `full pristine` reports `rows=63 mismatches=0`, exactly what
my independent battery run's `ARM pristine pop=r91` reports. My copy differs only in the pin branch, which is
unreached for pinned populations.


---

## 5. LD4 strength probe

### 5.1 Question

LD4 asserts an ITEM status (`MOVED`) and no exit code. Can a counter that refuses the WHOLE ledger still print
`ITEM P04 … status=MOVED` by another route?

### 5.2 Answer: **no** — `judge()` has exactly one MOVED route, and it needs a ledger entry

`census/round-87/c1-pointer-counter.py`:

- `judge()` returns `CAPTURED`/`MISMATCH` first if `rev_digest(root, rev, token)` is not None; P04's token
  `.ufo/waves/round-32/a2w1/SwarmExecutor08.md` is absent at BASE (`git cat-file -e BASE:…` rc 128, "exists on
  disk, but not in <BASE>"), so this branch cannot fire. Its ledger target is present at BASE with the frozen digest
  `d0693448…` (= `P04_PIN`), so the MOVED branch would pass if an entry existed.
- `if entry is None: return "UNRESOLVED", ""` — a refused ledger means no entry.
- The only `MOVED` return is `return cls, ""` inside `elif cls == "MOVED":` where `cls` came from the entry.
- `main()` prints `ITEM … status=<judge st>` at one site (line 546); the forge path (line 570) prints `FORGE …`, and
  the harness's `ledger-resolve` branch passes no `--forge`, so the forged-entry bypass that makes TF3/TF6… insensitive
  to the ledger cannot produce an ITEM line. The ledger-resolve branch also passes the base ledger path itself
  (`--ledger os.path.join(lane, lfile)`), never a copy.

### 5.3 Reproducers (lane tip `a703bcb7`, BASE `e65538e7`; receipts under `receipts/probe/`)

Whole ledger refused (empty ledger file, r77 item population), `pristine-empty-ledger.out`:

```
ITEM P04 SCORECARD.md:598 status=UNRESOLVED
SUMMARY items=35 resolved=4 unresolved=31 refused=0 mismatched=0 errors=0      rc=1
```

Width-exact spelling (`s1-exact-width`, copies in `derived/s1-exact-width.py`; real 4-column base ledger),
`s1-base.out`:

```
ITEM P04 SCORECARD.md:598 status=UNRESOLVED
SUMMARY items=35 resolved=4 unresolved=31 refused=31 mismatched=0 errors=0     rc=1
(plus LEDGER-REFUSED id=P01, P04, P05, … why=unknown or duplicate id)
```

Pristine (same population, same ledger), `pristine-base.out`:

```
ITEM P04 SCORECARD.md:598 status=MOVED
SUMMARY items=35 resolved=35 unresolved=0 refused=0 mismatched=0 errors=0      rc=0
```

The last line is the FALSIFIES-WORDING evidence for STATED LIMIT (iii): the base run IS all-resolved (35/35) and
exits 0, so "the base run is not all-resolved … exit 1 is expected" is refuted — the ledger-resolve population is the
c2 *item* file (all resolvable at BASE), not the c1 row population ("mostly false rows"). Consequence: asserting
`rc=0` on LD4 was available and would have been a strictly stronger grip (a counter that refuses the ledger exits 1
and prints 31 unresolved), and the stated reason for omitting it is wrong. The claim sentence itself (#5) is
unaffected: the STATUS assertion already kills the width-exact spelling, and the exit-1 consequence is independent
evidence of the same failure.

---

## 6. Falsification summary

Exactly one sentence of the frozen C1 text is refuted by my artifacts: STATED LIMITS (iii)'s premise that the
ledger-resolve base run is not all-resolved and exits 1 (recorded in full in §7). No CLAIM, POPULATIONS,
INSTRUMENTS, KILL RULE or PREDICATE sentence is falsified: every hash, the r90-prefix shape, the counter's
immutability, both predicate SUMMARYs, the control, the six survivors on all eight prior populations, and the
five-row binding all re-derive.

---

## 7. `FALSIFIES-WORDING` rows

### FALSIFIES-WORDING 1 — STATED LIMITS (iii), the parenthetical premise

**Exact sentence** (`census/round-91/preregistration.txt`, C1 STATED LIMITS (iii)):
> "LD4 asserts an ITEM status and no exit code: the base run is not all-resolved (the r77 population is mostly false
> rows), so exit 1 is expected and not asserted."

**Refuted clause**: "the base run is not all-resolved … so exit 1 is expected".

**Reproducer** (committed bytes, lane tip `a703bcb7`, BASE `e65538e7`):

```
python3 -B census/round-87/c1-pointer-counter.py --root . --rev e65538e73c7f1a8f7570bc24a2215da8a90043f3 \
  --fleet-root /home/vgpnk/Projects/shokunin --population census/round-77/c2-population.tsv \
  --ledger census/round-77/c2-pointer-ledger.tsv
→ SUMMARY items=35 resolved=35 unresolved=0 refused=0 mismatched=0 errors=0     rc=0
```

Also visible in the filed pre-freeze receipt `census/round-91/controls/c1-harness-smoke-r91.txt`:
`ROW LD4 where=ledger-resolve rev=BASE item=P04 class=- expect=MOVED/- got=MOVED rc=0 match=yes`.

**Narrowing** (for the L1's amendment): the base run IS all-resolved and exits 0; LD4's missing exit-code assertion
was a choice, not an impossibility; the row as filed still binds the width-exact spelling through the ITEM status.
No claim sentence in the CLAIM/PREDICATE paragraphs is refuted by this row.

(additional FALSIFIES rows, if any, are appended below from §4)

---

## 8. Residual risk and verification gaps

1. **Exit-code granularity of the battery.** `--expect-killed 38` gates on the SUM `killed_r90 + killed_r91`; a run
   with 17/21 would also exit 0. The predicate requires the exact printed SUMMARY, so the split is asserted by the
   receipt line, not by the exit code — a receipt consumer that reads only `rc` can be misled. My §1.1 shows the exact
   line, so the filed claim is met; this is a grip remark, not a defect in the wording.
2. **`s1-exact-width` has exactly one killer (LD4).** If a later round deletes LD4 or relaxes it, s1 survives again;
   the coverage is a single row, and that row asserts only a status (see §5).
3. **Mutant `new` strings are never asserted absent from the counter** by the battery (only `old`-count == 1). I
   checked all 22 `new` strings occur 0 times in the frozen counter; a battery check would make the INVALID rule
   cover a `new` string that already exists.
4. **Fixture determinism** is only as good as the pinned dates/env in the harness; my runs reproduce the frozen
   fixture's rev ids where compared (see `receipts/derive/full--pristine.txt` `# fixture … R13=` vs the smoke receipt
   `R13=8a61ecf4e4f494cac85cfd80d8170c3666818766`).
5. **No independent static verifier for the population's 10-column shape** beyond the harness's own check; I read the
   population and re-counted rows/columns, not a second parser.
6. **`census/round-91/records/` was untracked and growing** while I reviewed (L1 filing after-data). My numbers come
   only from my own runs; a reader should reproduce from §1/§5 commands, not from that directory.
