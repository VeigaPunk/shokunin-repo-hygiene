# S90ExecC1 — C1 independent re-derivation (souji r90 w1)

Seat: S90ExecC1 (executor, leaf). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Lane HEAD at measurement start: `fd25bfc5430cf27c1af5e4c8b8f6d5899e91a20f` (F; `git show --stat` = 1 file, 150
insertions = the preregistration alone). While my runs were in flight the L1 committed `8eba0131` (wave evidence)
and `a711c357` (the after receipt); current HEAD at report write is `a711c357`. The five C1 instrument blobs are
invariant across `fd25bfc..a711c357` (`git diff --stat` empty) and the working tree equals HEAD for all five
(`git diff --stat HEAD` empty), so both measurements are on committed bytes under either HEAD.
Instrument commits: P1 `1952c1c7` (population, harness, battery, mutants), P2 `e2a11c73` (control receipts).
Frozen contract read first: `census/round-90/preregistration.txt` (150 lines) at HEAD.

## 0. Verdict

**C1 VERIFIES.** Both arms re-derive on committed bytes, independently, and match the prereg's stated
predicate verbatim; the pins match; the population is the r89 file byte-for-byte plus exactly one appended
line; LD2b is the sole killer of `m17c-no-malformed` and is itself killed by no other mutant.

- After (both populations): `SUMMARY mutants=16 sets=r89,r90 pristine_r89=ok pristine_r90=ok killed_r89=15 killed_r90=16 killed_total=31`, EXIT 0.
- Do-nothing control (`--only r89`): `SUMMARY mutants=16 sets=r89 pristine_r89=ok killed_r89=15 killed_total=15`, `m17c-no-malformed … killed=no … exit=0`, EXIT 0.
- No artifact produced by this seat falsifies any sentence of C1. No pin mismatch. No HIGH finding.

## 1. Commands and their exact SUMMARY lines

Both run from the lane root, committed instruments, fresh empty `--work` dirs under
`/fast/scratch/hyaku/souji-r90/S90ExecC1/`.

```
python3 -B census/round-90/c1-clause-battery.py \
  --counter census/round-87/c1-pointer-counter.py \
  --work /fast/scratch/hyaku/souji-r90/S90ExecC1/after --only r89,r90 --expect-killed 31
  -> ARM pristine pop=r89 rows=57 mismatches=0 errors=0 exit=0
  -> ARM pristine pop=r90 rows=58 mismatches=0 errors=0 exit=0
  -> MUTANT-PAIR m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0 | pop=r90 killed=yes mismatches=1 errors=0 exit=1
  -> SUMMARY mutants=16 sets=r89,r90 pristine_r89=ok pristine_r90=ok killed_r89=15 killed_r90=16 killed_total=31
  -> EXIT 0
```
(full receipt `receipts/c1-after-both.txt`, sha256 ac2253ee…; 6509 bytes of battery output + my `EXIT=0` line)

```
python3 -B census/round-90/c1-clause-battery.py \
  --counter census/round-87/c1-pointer-counter.py \
  --work /fast/scratch/hyaku/souji-r90/S90ExecC1/control --only r89 --expect-killed 15
  -> ARM pristine pop=r89 rows=57 mismatches=0 errors=0 exit=0
  -> MUTANT m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0
  -> MUTANT-PAIR m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0
  -> SUMMARY mutants=16 sets=r89 pristine_r89=ok killed_r89=15 killed_total=15
  -> EXIT 0
```
(full receipt `receipts/c1-control-r89.txt`, sha256 ea04e687…; 4466 bytes + my `EXIT=0` line)

Operational note (no data impact): my first launch of these two commands was terminated by my own
tool's 300 s deadline while host load average was ~77 from concurrent seats; the quoted receipts are
from complete reruns on fresh empty work dirs (sequential, 1022 s wall). No partial output is used.

Only `m17c-no-malformed` reads `killed=no` on r89 (sole survivor); on r90 every one of the sixteen reads
`killed=yes`, and every mutant line in both receipts shows `errors=0` (no kill is a harness error, all are
row mismatches, strictly greater than 0 except m17c/r89).

## 2. Pin table — battery-printed and independently hashed vs prereg

| instrument | prereg pin | measured | rows | match |
|---|---|---|---|---|
| census/round-87/c1-pointer-counter.py | fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b | identical (sha256sum + battery header) | – | yes |
| census/round-90/c1-clause-battery.py | e7265335e4458e68d2277dd0ad4f36e68999a7ba70363d60dc2155bd9cfa2d39 | identical | – | yes |
| census/round-90/c1-false-row-harness.py | c3664747ffe712fde8f61c34562df2f0e92f2a0378b151bd0b4d74e91d629cbe | identical (battery header + sha256sum) | – | yes |
| census/round-90/c1-mutants.json | 392522489bc6f22a9747f64d311dbde7528dd0e8b481159db15d3eb038066dd5 | identical | 16 members | yes |
| census/round-90/c1-false-rows.tsv | d64d76954daea7da5d36e6f5eda96ae343bdd37db5071ea50bd55b30a1844b45 | identical | 58 | yes |
| census/round-89/c1-false-rows.tsv (control pop) | battery PINS/COPY pin 04570a64… | 04570a64855978bf697af71c161fe215945da5849f2f393fee15bb0d9f21e093 | 57 | yes |
| census/round-77/c2-pointer-ledger.tsv (frozen ledger) | "frozen r77 ledger" | 011faa0e96333b28af0418df8f56a5cbb169ed71aa0e9f688ee6d97d7aa39ba5 | 31 ids | used |

Independently confirmed the counter is UNCHANGED: its last modifying commit is r87 `77ccef7c`;
`git diff 77ccef7c:./census/round-87/c1-pointer-counter.py HEAD:./…` is empty and the r87 blob hashes to
fd0a8e24…. No `GIT_*` variables in the measuring shell; LANG=en_US.UTF-8 only.

Two precision notes, neither a numeric mismatch:
- The prereg's parenthetical "(…; the r89 sixteen byte-identical)" is true of the sixteen MEMBERS, not of
  the file. r89 file sha256 = bc7e6bb1983a19ab6781dba10b3b6c0be9085a7a1ed01d67d8eedec10aeb56ec vs r90
  39252248…; `cmp` differs at char 20 line 2 (the top-level `note` string). The member list is identical:
  same 16 ids in the same order and `json.dumps(members, sort_keys=True)` hashes equal for both files
  (1a93a7b66382145e1a7eaf2dfb506a08ee799af3cf4686252042b7f313c8bc25).
- Battery diff r89→r90 = docstring + PINS only (r89 path retargeted to census/round-89 at the same sha;
  one r90 entry added). Harness diff r89→r90 = docstring + POP_PINS entry + `elif rid in ("LD2", "LD2b")`
  (r89 had `rid == "LD2"`). No arm, judgement, summary or exit code changed — consistent with STATED
  LIMIT (i).

## 3. Population diff — r89 vs r90

- `cmp census/round-89/c1-false-rows.tsv census/round-90/c1-false-rows.tsv` → `EOF on …r89… after byte 14187`
  (exit 1: r89 is a strict prefix of r90).
- Prefix hash: first 14187 bytes of r90 sha256 = 04570a64855978bf697af71c161fe215945da5849f2f393fee15bb0d9f21e093
  = the r89 file's sha256. Byte-for-byte, same order.
- Sizes: r89 14187 B / 59 physical lines = 2 `#` comment lines + **57** data rows; r90 14628 B / 60 physical
  lines = **58** data rows. Appended bytes = 441 = exactly one line ending in `\n` (r89 already ended in `\n`:
  tail hexdump `…6f72 2e0a`).
- The appended line is `LD2b\tledger\tBASE\tr77\tZZ9\t-\t-\tLEDGER-REFUSED\t1\t<source>` — 10 columns. It is
  the only differing line; the earlier 57 are identical in content and order
  (`r90_rows[:57] == r89_rows` as parsed lists = True).
- Parsed r90: 58 rows, 58 unique ids, every row exactly 10 columns, `where ∈ {lane, ledger, fixture}`.
- `ZZ9` is ABSENT from the frozen r77 ledger (`grep -c '^ZZ9' census/round-77/c2-pointer-ledger.tsv` → 0,
  exit 1), so the harness's appended 2-column row lands on an id the ledger has never seen.

## 4. LD2b by hand — counter level

Replicated exactly the harness's `where=ledger` branch: `dup = r77 ledger bytes (+'\n' if absent) + "ZZ9\tABSENT\n"`,
then
`counter --root <lane> --rev e65538e73c7f1a8f7570bc24a2215da8a90043f3 --fleet-root /home/vgpnk/Projects/shokunin
--population census/round-77/c2-population.tsv --ledger dup`, cwd=lane. Mutant texts written in scratch from
c1-mutants.json with `src.count(old) == 1` asserted (all 16 members apply exactly once; for every id
`count=1`, so the battery's INVALID/exit-2 condition cannot trigger).

| counter | rc | stdout marker | stderr | row verdict |
|---|---|---|---|---|
| pristine | 1 | `LEDGER-REFUSED id=ZZ9 why=unknown or duplicate id`; `SUMMARY items=35 resolved=35 unresolved=0 refused=1 mismatched=0 errors=0` | empty | green (expect LEDGER-REFUSED/1) |
| m17-duplicate-id | 1 | same marker; `refused=1` | empty | green |
| m17b-target-keyed | 1 | same marker; `refused=1` | empty | green |
| m17c-no-malformed | 1 | **no stdout at all** (crash inside `_ledger`, before the header prints) | `line 494, in _ledger / ledger[r[0]] = (r[1], r[2]) / IndexError: list index out of range` | RED (`got=-` vs expect `LEDGER-REFUSED`) |

Contrast proving the shape is load-bearing (r89 LD2 row, id `P02` which IS in the frozen ledger): driven under
m17c it is still refused — `LEDGER-REFUSED id=P02`, rc=1, row green. m17c's duplicate leg fires first, so LD2
cannot reach the dropped length guard. ZZ9's absence is what removes the duplicate leg and exposes `len(r) < 3`.
(`receipts/ld2-contrast.txt`, `receipts/ld2b-handdrive-counter.out.txt`.)

Nuance worth recording: m17c's crash exits 1, which equals the row's expected rc; the row goes red only because
the marker is missing. That is exactly the prereg MECHANISM sentence ("raises IndexError with no marker: the
harness scores the row red"), and it means the kill is carried by the marker check, not by rc.

## 5. LD2b by hand — harness level (census/round-90/c1-false-row-harness.py)

Four full harness runs on `--population census/round-90/c1-false-rows.tsv`, fresh empty work dirs, plus one run of
m17c on the r89 population.

| counter | ROW LD1 | ROW LD1b | ROW LD2 | ROW LD2b | harness SUMMARY | exit |
|---|---|---|---|---|---|---|
| pristine | yes | yes | yes | yes | rows=58 mismatches=0 accepted=0 refused_true=0 errors=0 | 0 |
| m17-duplicate-id | NO | NO | yes | yes | rows=58 mismatches=2 accepted=0 refused_true=0 errors=0 | 1 |
| m17b-target-keyed | yes | NO | yes | yes | rows=58 mismatches=1 … errors=0 | 1 |
| m17c-no-malformed | yes | yes | yes | **NO** | rows=58 mismatches=1 … errors=0 | 1 |
| m17c on r89 pop | yes | yes | yes | (row absent) | rows=57 mismatches=0 … errors=0 | 0 |

The m17c r90 line is exactly `ROW LD2b where=ledger rev=BASE item=ZZ9 class=- expect=LEDGER-REFUSED/1 got=- rc=1 match=no`
— one mismatch, and it is LD2b. Therefore **LD2b is the sole killer of m17c**, and the delta between r89 and r90
for the same mutant text is that single row (green on 57 rows, red on 58).

## 6. Attribution table (mutant → rc, marker/IndexError, row verdict)

| mutant | change | rc on LD2b drive | marker | crash | LD2b row | killed on r89 / r90 (battery) |
|---|---|---|---|---|---|---|
| pristine | – | 1 | `LEDGER-REFUSED id=ZZ9` | no | green | – / – |
| m17-duplicate-id | drops `r[0] in ledger` | 1 | `LEDGER-REFUSED id=ZZ9` | no | green | yes (LD1/LD1b) / yes (LD1/LD1b) |
| m17b-target-keyed | duplicate only when target repeats | 1 | `LEDGER-REFUSED id=ZZ9` | no | green | yes (LD1b) / yes (LD1b) |
| m17c-no-malformed | drops `len(r) < 3` | 1 | none (no stdout) | IndexError at `ledger[r[0]] = (r[1], r[2])`, counter line 494 | **red** | no / yes (LD2b) |

So of the four `_ledger` mutants, only m17c is killed by LD2b, and m17c is killed by nothing else on r90
(one mismatch only) and by nothing at all on r89 (mismatches=0, exit=0).

## 7. Corroboration (read only after my own measurements were fixed)

- My control receipt is byte-identical to both committed pre-freeze receipts: first 4466 bytes =
  d0e06880e58a5e6a691b2f8f3b49b74286864a83ef6f6ce2a75ff3773cad2127 =
  `census/round-90/controls/c1-before-r89-population.txt` = `census/round-90/records/prefreeze-c1-control.txt`.
- My after receipt's first 6509 bytes = d584dabb42326c352867595dfa11696f16a6133c0e96d9152dd1369a65915ce9, which
  equals the L1's then-untracked `census/round-90/records/c1-after.txt` (now committed at `a711c357`; `git show
  HEAD:census/round-90/records/c1-after.txt | sha256sum` = d584dabb…) and `records/prefreeze-c1-both.txt`.
  Independent run, byte-identical tool output.

## 8. What I could NOT check

- C2 (different seat/precondition); I did not exercise it.
- I attributed row-level kills only for `m17`, `m17b`, `m17c` (the claim's mechanism); the other thirteen
  mutants' r90 kills are taken from the battery's per-mutant counts (`errors=0`, mismatches>0) and were not
  individually row-attributed by me.
- I did not re-derive the r77 ledger's internal authority beyond its sha, its id list, and `ZZ9` absence, nor
  whether the same 35-item r77 population is otherwise unchanged across rounds.
- I did not inspect the counter's 578 lines outside the `_ledger` path, the population/ledger pinning, and the
  `LEDGER-REFUSED` printer.
- No check of any state outside the lane; no git/jj mutation was performed anywhere.

## 9. Scratch

Scratch `/fast/scratch/hyaku/souji-r90/S90ExecC1` (battery work dirs ~2.9 GB each while running) was deleted
before yield; all receipts were copied into `./receipts/` first. No scratch left behind.

Receipt inventory (sha256; committed at `8eba0131`):
```
ac2253ee3423eeaaf6fb7d8e7df3bac8368d1ec67e2bfa278e2674f266c134d1  c1-after-both.txt
ea04e6871d10da3372bc22d33c34cad5162ce5d5252d3bc9b4a11f1be5cb36ad  c1-control-r89.txt
9dd4ed9372827fc1c805c54820fd5212ef29083843c18f83be4ffba595195b85  ld2-contrast.txt
6fe9ed19119515c2626f28c08e93cd7946b45e0de8f7d336e873860a65c39b0b  ld2b-handdrive-counter.out.txt
438b1608cb0c1a508336c3c08b77a961247335f8f671325a81e534fb31d7e774  m17.txt
0298b6de3e0672a88f22c970bde07660437c8f9623d7b5c6b8e1fb6c04574a1d  m17b.txt
561c74c44a149e983b5a424b14f16844b7d701b5c33b372047108af5ecae48c8  m17c-on-r89.txt
7412f9418f42738aa8dd245aab9d0db6d71934ac9d4b208e1ddade0807583979  m17c.txt
9ad2083f9cae1f4442a48530a896c5f09c325b81448954064c73c313b23367b9  pristine.txt
```
