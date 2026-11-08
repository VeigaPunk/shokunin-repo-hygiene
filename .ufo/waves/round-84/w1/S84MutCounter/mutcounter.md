# S84MutCounter — C1 extension: ten more single-edit mutants of the pointer counter

Seat S84MutCounter, souji round 84, wave w1. Read-only on the lane: this seat wrote only
`.ufo/waves/round-84/w1/S84MutCounter/` and its scratch (`/fast/scratch/hyaku/souji-r84/S84MutCounter/`,
removed before yield). No commit, no push, no git/jj mutation; `census/round-84/c1-mutants.json` was not edited.

## Verdict

- The five frozen mutants of `census/round-84/c1-mutants.json` were re-measured as the baseline: on the 44-row
  population all five are killed (`killed_r84=5`, mismatches 1/1/2/4/1 for m6/m7/m8/m9/m10, EXIT 0); on the 36-row
  population none is (`killed_r83=0`, 36/0, EXIT 0). The battery's pristine arms are 44/0 and 36/0.
- Ten more single-edit mutants were authored, applied exactly once each, and scored on both pinned populations:
  **4 of 10 are killed (x12, x14, x16, x18) and 6 survive (x11, x13, x15, x17, x19, x20).**
- Every killer row of the four killed mutants (`TF4`, `NF10`, `NF12b`, `NF4`, `NF6b`, `NF6c`, `NF6d`, `NF6e`, `NF3`)
  already exists in the r83 36-row population. **The ten-clause sweep adds no clause that the r84 rows newly bind**;
  the r84 delta remains exactly the five frozen mutants (m6–m10).
- Of the six survivors: two are bindable by one row the 44-row population lacks (x15 unknown class, x17
  LOCAL-POLICY disk check — both demonstrated below), two are a jointly-bindable redundant pair (x11 guard + x13
  basename: each single edit is shadowed, the joint edit is caught by a directory-token row), and two are
  unobservable through this harness on these populations (x19 token-on-line, x20 duplicate-ledger: they need a new
  item / a harness dimension, not another row).

## Pins and inputs (all observed)

| object | value |
|---|---|
| counter | `census/round-84/c1-pointer-counter.py` sha256 `052c4f3fdb3f902971b70f80653b4e84dc9a6b1c8deed355f067b3ff7d131d79` |
| harness | `census/round-84/c1-false-row-harness.py` sha256 `51b30dbd15c4c47173e9c29808f3b647f1ef932df7553dc8f5f3bd5b716b4e01` |
| population r83 | `census/round-83/c1-false-rows.tsv` sha256 `c9a6d58c1cf84a40a02a85a7342df2f2bd37301ba02e8f61ac91eded624e02eb`, 36 rows |
| population r84 | `census/round-84/c1-false-rows.tsv` sha256 `4795f009d6c873e733a2992bc86405d509dfb105b5f9950b3b9f82b2596e8f6f`, 44 rows |
| frozen mutants | `census/round-84/c1-mutants.json` sha256 `b71cf3d8d295448a016637c382dc2dd4fe5bf0d699abaeea81bf3a31f267abfa` (read only) |
| extension mutants | `.ufo/waves/round-84/w1/S84MutCounter/c1-mutants-ext.json` sha256 `a9426396190220b4a1b845a6e9be18e960a847aba7207a0ee58ced864b63fa93` |
| fixture revisions (stable in every log) | F0 `6436db6a…`, R1 `f28736a9…`, R2 `afc4beb7…`, R3 `bdea7114…`, R4 `0440ea31…`, R5 `d1ed98f4…`, R6 `fd1b8083…`, R7 `afc36569…` |

Kill rule (the battery's, frozen): a cell is KILLED iff `census/round-84/c1-false-row-harness.py` exits non-zero on
that population. The killer rows below are the ROW ids whose `match=` flips from `yes` (pristine) to `no` (mutant);
every run reported `errors=0`, so no cell is a harness error.

## Method

`c1-mutants-ext.json` holds ten members in the frozen shape `{id, clause, old, new}`. The driver asserts each `old`
occurs **exactly once** in the counter text (all ten: `occurrences=1`), writes `mutants/<id>.py`, and runs the
pinned harness once per cell (`--population <pin>`) in a fresh scratch work dir; the fixture is deleted after each
run and the full harness stdout is kept in `receipts/logs/<id>-<pop>.log`. The harness itself rebuilds its fixture
per run from the lane and re-checks the population pin. Two pristine runs (one per population) gate the driver.

Ten cells × two populations = 20 mutant runs + 2 pristine runs, all present under `receipts/logs/`.
Driver summary (`receipts/driver.out`):

```
PRISTINE pop=r83 exit=0 summary={'rows': 36, 'mismatches': 0, 'errors': 0}
PRISTINE pop=r84 exit=0 summary={'rows': 44, 'mismatches': 0, 'errors': 0}
SUMMARY mutants=10 r83_killed=4 r84_killed=4
```

## Baseline five (frozen mutants, re-measured)

`receipts/battery-r84.out`: `ARM pristine pop=r84 rows=44 mismatches=0 errors=0 exit=0`; each of m6…m10
`killed=yes` (mismatches 1, 1, 2, 4, 1); `SUMMARY mutants=5 sets=r84 pristine_r84=ok killed_r84=5 killed_total=5`,
EXIT 0. `receipts/battery-r83.out`: `ARM pristine pop=r83 rows=36 mismatches=0 errors=0 exit=0`; all five
`killed=no`; `SUMMARY mutants=5 sets=r83 pristine_r83=ok killed_r83=0 killed_total=0`, EXIT 0. The delta is real and
the controls stand.

Killer rows, observed with the same driver (`receipts/frozen-five-results.json`, logs in `receipts/logs-frozen5/`;
this is attribution only — the battery above is the canonical scorer): m6 digest-blind → `NF-L`; m7 round-blind →
`NF-L2`; m8 w-only shapes → `TF9`, `TF10`; m9 basename-only → `TF8`, `TF9`, `TF10`, `NF-P`; m10 records-as-wave →
`NF-M`. `killed_r83=0` for all five, so every one of these rows is an r84 row. (m9 refuses `TF9`/`TF10` as well
because a basename-only rule requires `len(got)==2` and those suffixes have three components.)

## Table — ten mutants, both populations (observed)

| mutant | clause it removes or widens | killed r83 | killed r84 | row(s) that kill it (r83 = r84) |
|---|---|---|---|---|
| `x11-owntree-short-guard` | `_owntree_ok`'s `len(want) < 2 or len(got) < 2` guard | no | no | — (survives both) |
| `x12-owntree-no-capture-fallback` | the `_capture_ok` fallback call before the wave-dir branch | yes | yes | `TF4` (got `REFUSED`, expect `MOVED`) |
| `x13-basename-blind` | the MOVED last-component (basename) test | no | no | — (survives both) |
| `x14-location-unbound` | `target[:tr.start(0)] not in (token_prefix, "census")` | yes | yes | `NF10`, `NF12b` (got `MOVED`, expect `REFUSED`) |
| `x15-unknown-class-free` | the unknown-class refusal (`cls not in CLASSES`) | no | no | — (survives both) |
| `x16-quarantine-undeclared` | the QUARANTINED `_declared` check | yes | yes | `NF4`, `NF6b`, `NF6c`, `NF6d`, `NF6e` (got `QUARANTINED`) |
| `x17-localpolicy-disk-blind` | the LOCAL-POLICY `on_disk != frozen` check | no | no | — (survives both) |
| `x18-no-round-free` | the `not kr` refusal | yes | yes | `NF3` (got `MOVED`, expect `REFUSED`) |
| `x19-token-on-line-free` | the R0 token-on-line check | no | no | — (survives both) |
| `x20-duplicate-ledger-free` | the duplicate-ledger-id refusal in `_ledger` | no | no | — (survives both) |

Cell evidence (mismatches/errors/exit; all from `results.json` and the logs):

- x12: r83 1/0/1, r84 1/0/1 — x14: 2/0/1 both — x16: 5/0/1 both — x18: 1/0/1 both.
- x11, x13, x15, x19, x20: 0/0/0 both; the full ROW lines are byte-identical to pristine (diff of
  `grep '^ROW '` is empty) in both populations.
- x17: 0/0/0 both, but the counter's own exit status changes on 10 fixture rows in each population (10 of 40 on r84, 10 of 32 on r83; see below).

Mutant file hashes (each = filed counter with one edit; also in `results.json`):

```
9594a031a95edcb41f208a28522c3c945f7298b5de97d58724bb1003e379469a  x11-owntree-short-guard.py
cda9156a662660a3690fd4b30e1caa880d24d6325161a1fcd03894350d25e0d1  x12-owntree-no-capture-fallback.py
08ff83e63972e2385a1c16ac06223b3f950cd0edfbfc13eeb8db718777eb78c1  x13-basename-blind.py
822bcacc70bb081aac4d89f33e72746be339ec2a08ac256f2caa8915c72eb1f4  x14-location-unbound.py
af3962e5662d12bbdc8013dbdce42b02f5c04eedd8b7a62baa6911296541db12  x15-unknown-class-free.py
532ae3865a7c1236305493e89a34bef7777da9b72949ab640b3d12b1af92fad8  x16-quarantine-undeclared.py
b72ea9540da5434ca59b19489dcbb9ca013dfb1e1f58ba7407e7c2324597f3b7  x17-localpolicy-disk-blind.py
cf46b82dbc591838ebeb520dc89e7d0959d47e845ef6c8f93a5cf547615babbb  x18-no-round-free.py
55fe5dbd7a0d6313fbbe35f9726c7e895e8c51385a09374cb40cb0c69ba88998  x19-token-on-line-free.py
efedd43a8478fdb250e525b8780ea10c40026b1e50437caa0bde47212372962b  x20-duplicate-ledger-free.py
```

## Bound by both populations (x12, x14, x16, x18)

Each of these four clauses is killed by a row that predates r84, so the r83 population kills them too:

- **x12** (`_capture_ok` fallback): `TF4` (`.ufo/waves/round-32/waves/a2w1/SwarmExecutor08.md`, R5) is a TRUE row
  the fallback keeps and nothing else does — `got=REFUSED` vs `expect=MOVED`. The r83 knowledge should state this
  clause as population-bound (r83's own rows already do it), not as an r84 gain.
- **x14** (location binding): `NF10` (`corpus/round-32/decoy/…`, R1) and `NF12b`
  (`census-archive/round-32/decoy/…`, R5) flip to `MOVED`. `DM07` (`corpus/round-321/…`) does not move: the
  round-equality clause refuses it first — a useful reminder that rows are not unique to one clause.
- **x16** (quarantine declaration): five QUARANTINED rows flip to `QUARANTINED` (`NF4` NOT-THE-STUB, `NF6b`
  substring-only declaration, `NF6c` no declaration, `NF6d` declaration outside AUTHORITY, `NF6e` declaration only
  at a later rev). The clause is exercised five ways already.
- **x18** (`not kr`): `NF3` (item L02, token `census/operator-sweep-20261019` names no `round-<N>`) flips to
  `MOVED`.

## Survivors — findings routed to r85

### 1. x15 unknown-class refusal — population gap, one row suffices

Row shape (proposed): `where=lane rev=BASE popl=r77 item=P02 class=RENAMED target=- expect=REFUSED expect_rc=-`.
Item P02 (`corpus/knowledge/absentdir`, frozen `-`) is absent at BASE and on the lane disk, so with the refusal
removed no later branch refuses an unknown class. Direct reproducer (`receipts/row-shape-reproducers.txt`): pristine
`FORGE R-X15 … got=REFUSED`, x15 `got=RENAMED` (a resolving class) — the harness would score `match=no`. Note the
class column of a population row is free text (nothing validates it against `CLASSES`), and a row whose token has
frozen bytes or disk bytes still refuses through the later `frozen`/`on_disk` branches, so the item must be one
absent at rev and on disk.

### 2. x17 LOCAL-POLICY disk check — population gap with no LOCAL-POLICY row at all

Row shape (proposed): `where=fixture rev=R7 popl=r77 item=P16 class=LOCAL-POLICY target=- expect=REFUSED
expect_rc=-`. The fixture's `.ufo/quarantine` is non-empty (the harness's own quarantine copies), so its listing
digest differs from P16's frozen `d:e3b0…`; pristine refuses the row and x17 accepts it as `LOCAL-POLICY`. Direct
reproducer: pristine `ITEM P16 … status=REFUSED class=LOCAL-POLICY why=lane disk bytes absent or changed`,
x17 `ITEM P16 … status=LOCAL-POLICY`, `FORGE R-X17 … got=LOCAL-POLICY` (pristine `got=REFUSED`).

Secondary observation, measured: removing this check also changes the counter's **own exit status** from 1 to 0 on
10 fixture rows in each population (10 of 40 on r84, 10 of 32 on r83; the fixture disk refuses P16/P28 in the
r77 population and L02/L03 in the r78 population, and the mutant resolves them). Those rows all pin `exp_rc='-'`, so the harness reports
`match=yes` and exits 0 — the exit-status change is invisible (`receipts/x17-exit-status-probe.txt`: pristine
`counter_rc=1`, x17 `counter_rc=0` at F0 with the r77 population and at R1 with the r78 population; ROW logs:
`rc-changed=10` in both populations). Cheaper alternative for r85: pin `expect_rc=1` on one F0 fixture row
(e.g. `NF2`) in the amended population — that catches this exit-status change without a new class row.

### 3. x11 guard + x13 basename — a jointly bindable redundant pair (not two clauses)

Neither single edit can be distinguished by any row:

- x13 (basename): on every acceptance path the last component is already implied — `_owntree_ok`'s wave branch
  compares `got[1:] == want[1:]` (last component included), `_capture_ok` compares the token's whole suffix, and a
  token with no `round-<N>` is refused by the `not kr` clause. The joint probe line
  (`receipts/probe-survivors.out`, first line) shows the strongest candidate row (directory token `.ufo/waves/round-32/a2w1` frozen `d:<listing>`, target
  `.ufo/waves/round-32/w2` with an equal listing) is still `REFUSED` under x13 alone.
- x11 (guard): for the guard to matter, `got[1:] == want[1:]` must hold with a short side. Unequal component
  counts cannot be equal as lists; equal counts of one force the target's single component to equal the token's
  single component below the same round, i.e. `target == token`, which is `CAPTURED` (or a digest `MISMATCH`), never
  a MOVED row. The basename clause also refuses the only differing-directory candidate first, so x11 alone is
  unreachable as a decider.
- The joint edit (both clauses removed) **is** caught: the joint probe line gives `joint_x11_x13=MOVED` (pristine `REFUSED`).
  So r85 can bind the pair with one row: an item whose token is a **directory one component below its round**
  (frozen `d:<listing>`), target one component below the same round in a real `w2/` with an equal listing, expect
  `REFUSED`. This needs a new **counter-population item** (no r77/r78 item has a single-component directory token;
  P11/P18 tokens are `w1/<name>`, two components), i.e. a pinned-population revision, not just a row.

### 4. x19 token-on-line check — unobservable through the harness on these populations

The harness takes the judged line/token from the counter's pinned r77/r78 populations; all 57 items carry their
token on the recorded line at their own bases (`d4f51563…`, `a8558d41…`, checked item by item), and a row cannot
alter an item's line. The x19 probe line (`receipts/probe-survivors.out`, fourth line) shows a mismatched
`(line, token)` pair as `ERROR`
under the pristine counter and `ABSENT` under x19 — so the effect is real and a row with `expect=ERROR` would kill
it, but no row of the two pinned populations can carry such an item. r85 would need a third pinned population (or
an item-defining row / harness feature).

### 5. x20 duplicate-ledger refusal — unobservable through the harness on these populations

The harness passes the lane's fixed ledger per population label (`POPS` in `census/round-84/c1-false-row-harness.py`)
and compares only the `FORGE` line and (where `exp_rc` is pinned) the counter's exit code. The `PROBE-LEXER` line
(`receipts/probe-survivors.out`): the same duplicate-id ledger gives `_ledger` `bad=['P01']` on the pristine counter
and `bad=[]` on x20; the duplicate only changes `SUMMARY refused`/rc, which no row observes. Neither r77 nor r78
ledger has a duplicate or an unknown id (31/31 and 19/19 unique ids). r85 would need a harness dimension (a
per-row ledger, or comparing the counter's SUMMARY) — not a population row.

## What this means for the r84 claim's wording

- Do not state that the ten-clause sweep extends the population's discrimination. It does not: the four kills are
  already carried by r83 rows, and the six survivors are unchanged by r84's five new rows (None of x11, x13, x15,
  x17, x19, x20 is affected by TF8–TF10/NF-P/NF-L/NF-L2/NF-M/NF-Q).
- The r84 delta stays the five frozen mutants, each killed by an r84 row measured above (m6→NF-L, m7→NF-L2,
  m8→TF9+TF10, m9→TF8+TF9+TF10+NF-P, m10→NF-M), 44/0, EXIT 0. Note m8's and m10's edits target the same regex line
  with different replacements; the battery applies each to the pristine text independently.
- r85 has two cheap additions (one row for x15, one row for x17 — the latter also fixable by pinning `expect_rc` on
  an F0 row), one population revision for the x11/x13 pair, and two harness extensions (x19, x20) that a row alone
  cannot cover.

## Reproduction

```
# baseline (both ends; both must be green, 44/0 and 36/0, killed 5 and 0)
python3 -B census/round-84/c1-clause-battery.py --counter census/round-84/c1-pointer-counter.py \
    --work <empty dir outside /tmp> --only r84 --expect-killed 5
python3 -B census/round-84/c1-clause-battery.py --counter census/round-84/c1-pointer-counter.py \
    --work <empty dir outside /tmp> --only r83

# the ten mutants (writes mutants/, results.json, receipts/logs/)
python3 -B .ufo/waves/round-84/w1/S84MutCounter/mutcounter-driver.py \
    --harness census/round-84/c1-false-row-harness.py --counter census/round-84/c1-pointer-counter.py \
    --lane /home/vgpnk/Projects/shokunin/souji-shokunin --fleet-root /home/vgpnk/Projects/shokunin \
    --work <scratch>/drive --out .ufo/waves/round-84/w1/S84MutCounter \
    --mutants .ufo/waves/round-84/w1/S84MutCounter/c1-mutants-ext.json --jobs 4

# survivor probes (throwaway two-file git repo in scratch; never the lane)
python3 -B .ufo/waves/round-84/w1/S84MutCounter/probe-survivors.py <scratch>
```

## Stated limits

- A kill is `harness EXIT != 0` (the frozen rule); the harness does not compare the counter's own exit status except
  where a population row pins `exp_rc`, which is why x17 survives despite changing that status on 10 rows per population.
- The ten mutants are hand-written single edits, not a generated battery; each `old` is asserted to occur exactly
  once, but no claim is made that the ten clauses are exhaustive.
- The x11/x13/x15/x17/x19/x20 row-shape demonstrations are `judge`/`_ledger`-level probes on a throwaway
  two-file git repo (all six) plus direct counter `--forge` runs for the x15 and x17 shapes; they are not scored
  through the pinned harness,
  whose population file cannot be extended without changing its sha256 pin. The x17 exit-status observation is
  measured on the harness's own r84 fixture (reused read-only from `battery-r84`).
- The fixture rev ids were identical in the pristine and all mutant logs of both populations, so the cells compare
  the same bytes.
- The r77/r78 population rows were checked for R0 (token on the recorded line) at their own bases; that check is a
  property of the pinned counter populations, not of the harness.

## Deliverables (this seat dir)

```
c1-mutants-ext.json                 ten mutants, {id, clause, old, new}, counter sha256 pinned in the note
mutants/x11-…-x20-….py              the ten applied counter texts (sha256 above)
mutcounter-driver.py                applies once, scores both populations, attributes killer rows
probe-survivors.py                  judge/_ledger probes for the survivor row shapes
results.json                        per-cell exit/summary/killers/sha256
mutcounter-table.md                 the table alone
receipts/battery-r83.out|err        baseline five on 36 rows (killed_r83=0, EXIT 0)
receipts/battery-r84.out|err        baseline five on 44 rows (killed_r84=5, EXIT 0)
receipts/driver.out|err             pristine 36/0 and 44/0 (exit 0) + 20 mutant runs
receipts/logs/*.log                 22 full harness stdout logs (pristine + 10 mutants × 2 populations)
receipts/frozen-five-driver.out      killer-row attribution run for m6–m10 (10 runs, both populations)
receipts/frozen-five-results.json    per-cell exit/summary/killers for m6–m10
receipts/frozen-five-input.json      the five frozen members as fed to the driver
receipts/logs-frozen5/*.log          those 10 harness stdout logs
receipts/probe-survivors.out        PROBE lines (x11+x13 joint, x15, x17, x19) and PROBE-LEXER
receipts/row-shape-reproducers.txt  direct counter runs for the x15 and x17 row shapes
receipts/x17-exit-status-probe.txt  counter_rc 1→0 under x17 at F0 (r77) and R1 (r78)
receipts/sha256sums.txt             sha256 of every file above + the scripts and JSON
```

Host tooling: none installed or upgraded (no `uv tool`, `npx`, binary, or package manager transaction). Scratch
`/fast/scratch/hyaku/souji-r84/S84MutCounter/` was removed after the receipts above were copied here.
