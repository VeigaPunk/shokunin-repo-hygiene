# S86MutCounter — C1: are the two new rows load-bearing, and does a different single edit of the same clause survive?

Seat: mutation tester, r86 wave 1. Lane `souji-shokunin` at `2acbbfc8` (base, prereg F `d77b4258`, instruments `47602fa6`).
I did not commit, push, or mutate any git/jj state; every counter/harness run below reads the lane and writes only my
scratch and my seat dir. Frozen populations, items, ledger and `c1-mutants.json` are untouched (hashes re-checked after
the work, §9).

## Verdict in one paragraph

The frozen claim reproduces exactly on my invocation: both pristine arms green (47/0, 49/0), `killed_r85=6`,
`killed_r86=8`, so **NF-W and NF-Y are load-bearing: each is the only row that kills its clause** (c7 and m14 are
green on 47/47 without them, red on exactly one row with them). But **a different single edit of the c7 clause does
survive both populations** (`x3-c7-shape-only`), and it survives *provably*: on every path pair that can reach the
branch, the filed predicate `not _capture_ok(...)` is constant (the own-tree branch has already filtered the capture
side), so the clause NF-W binds is *"an own-tree wave-directory shape under a census token is refused"*, not the
"suffix" rule its message names. On the m14 side, the **got-half of the guard is dead code** (`x5` survives both and
no input in a 67 081-pair sweep tells it from the counter); NF-Y binds the guard's `len(want) < 2` half only. Nothing
in this report contradicts the frozen claim's wording; two narrowings are handed to the integrator in §8.

## 1. Instruments, hashes, invocation

    counter    census/round-86/c1-pointer-counter.py    8278ea4d41d0975b748419ba79de44d3eefc924d8f415071660def83f9fba1f3
    harness    census/round-86/c1-false-row-harness.py  2dac2e818c65bb9cd8a8361899b78cc33ddb91b9ba216d27e5b0f821804bc9d9
    battery    census/round-86/c1-clause-battery.py      d7e299c247066b3022fe19378af3ff16c076326ddbc86c289d9ca8a459cba9e5
    mutants    census/round-86/c1-mutants.json           6f055edea73e5b22d870cb1e85100251cf7ba47486519ed448582b1b9c6471a6  (8 members)
    items r85  census/round-85/c1-items.tsv            d9a2ad8cfa1853ed3620e0b57ac26f2af079d05be8e2a454316a7880808b5114  (3)
    items r86  census/round-86/c1-items.tsv            5abf3b01d8cfe50b9b64d465a4602bd5a9d8f6915ad257e02fb4ee5a9c9dade2  (4: +I86S)
    ledger     census/round-86/c1-ledger.tsv           7cbb28c9805c959925805b9e06dfdf5d9f8d01e57b1ad2645269e06cf782abce  (== r85 ledger, byte-equal, checked)
    pop r85    census/round-85/c1-false-rows.tsv       1468236cfc3c8f65e7fa9bb07884324ee8ae8b7f62d6d5ca984b9dfa04698d42  (47)
    pop r86    census/round-86/c1-false-rows.tsv       79db70f6740de41a326dc4193bf80c5394fe126d636cc98d4e26e4b5e140f561  (49)

My own bytes (this seat):

    .ufo/waves/round-86/w1/S86MutCounter/mutants-ext.json   b217daa59b7892a0f4a0f69c85e97339eb822737cd49204d86d7a76088264f46  (8 members)
    .ufo/waves/round-86/w1/S86MutCounter/run-ext.py         7c9b022a6d6a7b34091c954c86baee9dd24cef090b5823c3d42c7a63a98aecc5
    .ufo/waves/round-86/w1/S86MutCounter/reach.py           504bfea7df967bb8a5c9c3e3ddeaf3eab808cc44480368bd2214240f147b2762

Frozen counting command (preregistration), reproduced verbatim:

    python3 -B census/round-86/c1-clause-battery.py --counter census/round-86/c1-pointer-counter.py \
        --work /fast/scratch/hyaku/souji-r86/S86MutCounter/battery-work2 --only r85,r86 --expect-killed 14

Per-mutant scoring (the same detector the battery calls, invoked directly so each mutant's red rows and its
`errors=` count are visible — the battery prints only the aggregate):

    python3 -B .ufo/waves/round-86/w1/S86MutCounter/run-ext.py \
        --work /fast/scratch/hyaku/souji-r86/S86MutCounter/ext-work \
        --receipts /fast/scratch/hyaku/souji-r86/S86MutCounter/receipts --jobs 14
    # 1 pristine + 16 mutants x 2 populations = 34 harness runs, every one `--population` pinned

Population additivity checked independently: the r86 population's first 47 rows are byte-identical, in order, to the
r85 population (script comparison, `prefix identical: True`), the two appended rows are NF-W and NF-Y at fixture rev
R9, and all 49 ids are unique.

## 2. Baseline (frozen battery, my invocation)

    ARM pristine pop=r85 rows=47 mismatches=0 errors=0 exit=0
    ARM pristine pop=r86 rows=49 mismatches=0 errors=0 exit=0
    SUMMARY mutants=8 sets=r85,r86 pristine_r85=ok pristine_r86=ok killed_r85=6 killed_r86=8 killed_total=14
    MUTANT-PAIR c7-census-in-tree pop=r85 killed=no mismatches=0 errors=0 exit=0 | pop=r86 killed=yes mismatches=1 errors=0 exit=1
    MUTANT-PAIR m14-short-shape pop=r85 killed=no mismatches=0 errors=0 exit=0 | pop=r86 killed=yes mismatches=1 errors=0 exit=1
    EXIT=0

Receipt: `receipts/frozen-battery.txt`. My independent per-mutant runs agree row for row (Table A).

## 3. Table A — the frozen eight, kills and rows

`killed` = harness exit != 0 (row mismatch or harness error). `red rows` = every `ROW ... match=no` line.
Columns "r85 / r86" carry the same red-row set unless stated: the two new rows change only c7 and m14.

| mutant | clauses edited | killed r85 | killed r86 | red rows (r85 == r86 unless split) | got vs expect |
|---|---|---|---|---|---|
| m6-digest-blind | digest test | **yes** (1/0/1) | **yes** (1/0/1) | NF-L | got=MOVED, expect=REFUSED |
| m7-round-blind | same-round test | **yes** (1/0/1) | **yes** (1/0/1) | NF-L2 | got=MOVED |
| m8-w-only-shapes | own-tree wave set | **yes** (2/0/1) | **yes** (2/0/1) | TF9, TF10 | got=REFUSED, expect=MOVED |
| m9-basename-only | own-tree suffix vs basename | **yes** (4/0/1) | **yes** (4/0/1) | TF8, TF9, TF10, NF-P | TF\* got=REFUSED; NF-P got=MOVED |
| m10-records-as-wave | non-wave dir is not a capture | **yes** (1/0/1) | **yes** (1/0/1) | NF-M | got=MOVED |
| m11-class-enum | class enum | **yes** (1/0/1) | **yes** (1/0/1) | NF-S | got=BOGUS |
| **c7-census-in-tree** | census-in-tree branch | **no** (0/0/0) | **yes** (1/0/1) | — / **NF-W** | — / got=MOVED, expect=REFUSED |
| **m14-short-shape** | own-tree short-shape guard | **no** (0/0/0) | **yes** (1/0/1) | — / **NF-Y** | — / got=MOVED, expect=REFUSED |

`(mismatches/errors/exit)`. Reproduces the frozen before/after receipt exactly: on the 47 rows c7 and m14 are
green (exit 0, 47/0), and each is killed on the 49 rows by exactly one row — NF-W for c7, NF-Y for m14 — with no
other row going red. **Both kills are status mismatches, not errors** (§7).

## 4. Table B — eight new single edits, scored on both pinned populations

All eight live in `mutants-ext.json`; every `old` occurs exactly once (asserted by the driver, and the diff receipt
`receipts/ext-diffs.txt` shows 16 single-hunk diffs). Three re-edit the c7 clause and three re-edit the m14 guard in
ways the frozen mutants do not; `x8` is a neighbour control.

| id | edited line(s) of the r86 counter | killed r85 | killed r86 | red rows (r85 / r86) | verdict |
|---|---|---|---|---|---|
| x1-c7-not-only | 418 — the `not` of the census-in-tree condition (branch at 417) | **yes** (1/0/1) | **yes** (2/0/1) | TF11 / TF11, **NF-W** | killed in the opposite direction by r85 already (TF11) |
| x2-c7-capture-to-owntree | 418 — c7's capture test replaced by the own-tree test | no (0/0/0) | **yes** (1/0/1) | — / **NF-W** | **NF-W is the only killer** |
| **x3-c7-shape-only** | 418 — branch kept, suffix test replaced by the capture-prefix shape | no (0/0/0) | **no** (0/0/0) | — / — | **SURVIVES — dead clause half (§5.1)** |
| x4-m14-guard-lt-1 | 366 — `< 2` relaxed to `< 1` on both sides | no (0/0/0) | **yes** (1/0/1) | — / **NF-Y** | **NF-Y is the only killer** |
| **x5-m14-guard-want-only** | 366 — got-half of the disjunction dropped | no (0/0/0) | **no** (0/0/0) | — / — | **SURVIVES — dead clause half (§5.2)** |
| x6-m14-guard-lt-3 | 366 — `< 2` tightened to `< 3` | **yes** (4/0/1) | **yes** (4/0/1) | TF4, TF6, TF7, TF11 | r85 already binds the threshold upward |
| x7-m14-guard-and | 366 — `or` turned into `and` | no (0/0/0) | **yes** (1/0/1) | — / **NF-Y** | **NF-Y is the only killer** |
| x8-owntree-no-assimilation | 351 — `assimilation/` dropped from the wave set | **yes** (1/0/1) | **yes** (1/0/1) | TF10 | neighbour control: r85 binds it, the new rows do not |

Reading the two rows' discriminating power: across the six r85 mutants + eight c7/m14-class mutants scored here, NF-W
is red only for c7-class edits (frozen c7, x1, x2) and NF-Y only for m14-class edits (frozen m14, x4, x7). Neither
row is red for any of the six r85 mutants, and neither is red for `x8`. The six r85 mutants' red-row sets are
identical on both populations, so the two new rows contribute **zero** kill outside their own clause, and the kill
delta 6 -> 8 is entirely theirs.

## 5. Survivors: dead, not merely unexercised

`reach.py` (`receipts/ext-reach.txt`) diffs each mutant against the pristine counter in-process:

- **(a) judge level.** A scratch fixture repo (`git init` under my scratch, toplevel asserted twice) holds 30 target
  shapes with one body whose sha256 is the item's `frozen` digest; probe items are fabricated, so the token is absent
  at the revision and the digest/basename/round tests pass and execution reaches the branch. Pairs whose pristine
  status short-circuits (CAPTURED/MISMATCH) are dropped and never counted as differences; a difference is split into
  STATUS (what the harness compares) and WHY-only (message text, invisible to the harness).
- **(b) `_owntree_ok` sweep.** 67 081 component path pairs, depth <= 3 over `{X, w1, w2, waves, records, a2w1}`.
- **(c) c7 predicate equivalence** (x3 only): on the 504 census path pairs that the own-tree branch ACCEPTS — exactly
  the set on which the c7 branch can fire, because both branches carry the same `target[:round] == token[:round]`
  prefix test — does the mutant's predicate agree with the filed one?

| survivor | judge status diffs / probes | `_owntree_ok` diffs / pairs | classification |
|---|---|---|---|
| x3-c7-shape-only | **0 / 30** | 0 / 67 081 | **DEAD** (c7 predicate equivalence: 504 reachable pairs, 0 disagreements) |
| x5-m14-guard-want-only | **0 / 30** | 0 / 67 081 | **DEAD** |

(For reference, the probes do fire on the live clauses — e.g. c7's status diffs are B2; m14/x4/x7's are A1, B5, C1,
U6; x2's are B2 and C8 (assimilation is the same shape class as NF-W's `w1/`). So "0" above is a measured zero on a
matrix that demonstrably distinguishes the clauses the row is meant to bind.)

### 5.1 x3 — the c7 suffix test is dead on every input that reaches the branch

Reaching the c7 branch means the own-tree branch (line 405) returned False, which for these pairs is
`_owntree_ok(...) == True`. There are exactly two ways that can happen:

1. `_capture_ok` is True. Then the filed predicate `not _capture_ok` is False (no refusal) and x3's predicate
   `not CAPTURE.match(target below the round)` is also False, because `_capture_ok` cannot be True unless
   `CAPTURE` matched. Identical.
2. `_owntree_ok`'s second disjunct held: the target below the round starts `w[0-9]+/`, `a2w1/` or `assimilation/`
   and the remaining components equal the token's from index 1. `CAPTURE` requires `waves/`, `wave/` or
   `records/wave-*/`, so it cannot match those prefixes: both predicates are True. Identical.

So on the reachable set `not _capture_ok(...)` is the constant `True`, and c7's effective rule is *"a census-rooted
token's target under the same census round must not be an own-tree wave-directory shape"*. The measured 504/504
agreement is the corroboration; the case analysis is the proof. Concretely (receipt): a census token moved to
`census/round-84/waves/sub/<name>` — a capture prefix whose remainder is NOT a suffix of the token's tail — is
refused by the **own-tree** branch (`why=own-round-tree target is neither...`), so the c7 branch is never consulted
for it; that shape is the only one on which the suffix test could have mattered.

**Consequence for the claim, stated narrowly:** NF-W binds the *presence* of the c7 branch (that is what makes the
frozen c7 mutant red), and it is the only row that does. It does not bind the branch's suffix test, and no single edit
of that suffix test can be killed by this population — `x3` is a counterexample in exactly the sense r85 recorded for
`m15-empty-want`. The row's own source note ("the census-in-tree clause is the ONLY refusal for a census-rooted token
landing in a wave directory under its own round") is correct as written: a *wave directory*, i.e. `w<N>/`, not a
capture.

### 5.2 x5 — the guard's got-half is dead

`if len(want) < 2 or len(got) < 2:` — dropping the got-half survives both populations and 67 081/67 081 path pairs
agree. It is dead by construction: `got` has fewer than 2 components only when the target below the round has <= 1
component, and then neither `_capture_ok` (needs a `waves/`-style prefix plus content) nor `OWNTREE_WAVE` (needs a
wave directory plus a following `/`) can match, so both fall-through disjuncts are False and the function returns
False with or without the got-half. The guard's *load-bearing* half is `len(want) < 2`, and that is exactly the half
NF-Y exercises (m14, x4 and x7 are red under NF-Y; x5 is not). The `len(got) < 2` half is in the same class as r85's
`m15-empty-want`: reachable code, no discriminating input.

### 5.3 What the survivors say about the m14 kill

m14's judge diffs are A1 (`.ufo/waves/round-32/X -> .../waves/X`), B5 (the NF-Y shape), C1 (the same shape with a
different name) and U6 — all four are the same class: token one component below its round, target a capture under
that round. The guard's want-half is what refuses them. So NF-Y's kill is the right mechanism, not an incidental one
— and it is the *only* row that exercises that class, which is why m14 is green on 47/47.

## 6. Does NF-W / NF-Y kill exactly one clause each?

Measured, within a 16-mutant battery (8 frozen + 8 authored):

| row | red under | not red under |
|---|---|---|
| NF-W | c7-census-in-tree, x1, x2 (all three edit the c7 branch) | the six r85 mutants, m14, x4, x5, x6, x7, x8 |
| NF-Y | m14-short-shape, x4, x7 (all three edit the guard) | the six r85 mutants, c7, x1, x2, x3, x5, x8 |

Both new rows are also never red "for the wrong reason": on both populations every mutant's `errors=` is 0, no
`ROW ... match=error` line exists in any of the 34 receipts, no harness run exited 2, and no run printed a traceback.

The honest scope of that sentence: a row can only bind a clause some mutant drops. "One clause each" is a measured
fact about this battery, not a proof about the counter's rule; and §5 shows NF-W binds the branch while leaving the
clause's suffix test unbound.

## 7. Errors vs mismatches

Every kill above is a **status mismatch with a named `got`**: `got=MOVED` (a false row that resolved), `got=REFUSED`
(a true row that was refused), or `got=BOGUS` (NF-S). Aggregate over all 34 harness runs: `mismatches>0` on exactly
the killed arms, `errors=0` everywhere, `accepted=0` and `refused_true=0` on the pristine arms, no run with
exit 2, no fixture failure, no traceback. In particular the two *new* rows are not error-kills: c7 -> NF-W
`got=MOVED rc=1`, m14 -> NF-Y `got=MOVED rc=1`, so the delta is a discrimination delta, not a crash delta.

## 8. Hand-off to the integrator (no lane edit made; populations and mutants are frozen and untouched)

1. **The claim's wording holds** as written; I found nothing that falsifies a sentence of it. `killed_r85=6`,
   `killed_r86=8`, both pristine arms green, and each new row is the sole killer of its clause.
2. **Narrow candidate sentence for the wave's artefacts (not this file):** C1's stated wording describes the c7
   clause as "a wave capture keeping the token's full path suffix". Measured, the suffix test cannot discriminate on
   any input that reaches the branch (`x3` is dead, 504/504 predicate agreement), so the row binds the branch's
   existence, and the branch's enforced rule is "an own-tree wave-directory shape under a census token is refused".
   Likewise the m14 row binds `len(want) < 2` only; `len(got) < 2` is dead code of the same class as r85 `m15`.
3. **Still unrowed after r86** (unchanged by this seat): the c7 suffix test (dead, so a row cannot bind it — a code
   decision, not a row), the guard's got-half (dead), and the other r85-measured guards (m12, m16, m17).
4. Nothing here authorises a population edit, a mutant-file edit, quarantine, or a signal to any process.

## 9. Non-mutation / restoration evidence

- No mutating git/jj command was run in the lane; the harness's `git clone --shared` (read-only) and my probe
  fixture's `git init` live under my scratch, and every `git -C` call asserts the fixture toplevel first (the probe
  asserts it twice).
- Lane instrument hashes after the work, identical to §1: counter `8278ea4d…`, harness `2dac2e81…`,
  battery `d7e299c2…`, `c1-mutants.json` `6f055ede…`, populations `1468236c…` / `79db70f6…`, items `5abf3b01…`,
  ledger `7cbb28c9…`.
- Every python invocation used `-B`; no `__pycache__` remains in my seat dir or the lane census dirs I read.
- All 16 mutant copies, the 34 harness work dirs and the probe fixture lived under
  `/fast/scratch/hyaku/souji-r86/S86MutCounter/`; receipts were copied into
  `.ufo/waves/round-86/w1/S86MutCounter/receipts/` and the scratch dir was deleted before this report was finished.

## 10. Files (this seat's write scope only) and tooling

    .ufo/waves/round-86/w1/S86MutCounter.md                       this report
    .ufo/waves/round-86/w1/S86MutCounter/mutants-ext.json         the eight authored mutants (old/new, clause)
    .ufo/waves/round-86/w1/S86MutCounter/run-ext.py               scoring driver (hashes, exactly-once, 2 x 17 arms)
    .ufo/waves/round-86/w1/S86MutCounter/reach.py                 dead-vs-unexercised differential (judge + function)
    .ufo/waves/round-86/w1/S86MutCounter/receipts/frozen-battery.txt
    .ufo/waves/round-86/w1/S86MutCounter/receipts/ext-console.txt       (driver console + full table)
    .ufo/waves/round-86/w1/S86MutCounter/receipts/ext-summary.txt       (per-arm mismatches/errors, red rows)
    .ufo/waves/round-86/w1/S86MutCounter/receipts/ext-<id>__<pop>.txt   (34 harness receipts; the pristine pair is
                                                                         c1-pointer-counter__<pop>.txt)
    .ufo/waves/round-86/w1/S86MutCounter/receipts/ext-diffs.txt         (16 single-hunk diffs)
    .ufo/waves/round-86/w1/S86MutCounter/receipts/ext-reach.txt         (probe matrix + verdicts)

Tooling: no installs or upgrades were needed or attempted; no pacman transaction; python3 (system) only, stdlib.
