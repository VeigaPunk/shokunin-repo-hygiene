# R99Scribe — round-99 lesson draft (Gate + Mistakes)

Seat: R99Scribe (godspeed). Lane: souji @ `c94d678c8a76f3f87f73b49a11a9d4e2aff73e3b`.
Scratch: `/fast/scratch/hyaku/souji-r99/R99Scribe/` (deleted before yield).

**Deliverable:** the draft lesson blocks at
`.ufo/waves/round-99/w1/R99Scribe/lesson-draft.md` — a `## Gate` block (the two frozen predicates) and
three `## Mistakes` rows (M9, M10, M11), each in the form **class · evidence pointer · captured-by · fix**.

**This seat did not land the lesson.** The L1 (SoujiR99) freezes the predicates and commits the lesson
through the lane helper. This seat wrote only inside its own wave dir
(`.ufo/waves/round-99/w1/R99Scribe/` and `.ufo/waves/round-99/w1/R99Scribe.md`); it committed nothing,
pushed nothing, mutated no git/jj state, edited no `census/round-98/*` file, no `MANIFEST.json`, no
`.ufo/state/*`, no `.scratch/*`, and touched neither `considerthese` nor `shokuknow`.

**Tooling:** system `python3` only (3.14); nothing installed, nothing upgraded, no pacman transaction
(all pacman transactions are PAUSED host-wide), no sysctl mutated. No host-mutation need was found.

---

## Inputs read (committed evidence only)

| input | path | what was taken |
|---|---|---|
| plan (prereg + A0.1 frozen predicates) | `/home/vgpnk/Projects/shokunin/plans/round-99.md` | the two frozen predicates, the M6/Q173 relabel rule, the branch-(c) removal rule |
| r98 mistakes | `souji-shokunin/corpus/lessons/round-98.md` § Mistakes | M6 (do-nothing control over claimant-written labels), M7 (safety test bound to the wrong subject), M8 (survivor metric compares the wrong pair) |
| r98 spot-check routed defects 1–4 | `souji-shokunin/corpus/lessons/round-98-verifier-spotcheck.md` § "Routed defects" | 1 = M6/Q173 freeze-file gate; 2 = C2 branch-(c) wording; 3 = prefile ledger absent; 4 = `survivors` is not a C2 witness |

Reference instruments read but **not edited**: `census/round-98/c1-survivor-search.py`,
`census/round-98/declared-shapes.py`, `census/round-98/shapes/` (17 shapes), `census/round-98/c2-setup-arms.py`,
`census/round-98/c2-decoy-test.py`, `census/round-98/c2-cm8-mutant.py`, `census/round-98/c2-forgery-probe.py`,
`census/round-98/controls/`.

---

## Commands run, exit codes, observed summary lines

Every row below was executed by this seat in this round. Paths under `/home/vgpnk/Projects/shokunin/souji-shokunin`
are absolute; all `--work` dirs are under the seat's scratch (never `/tmp`).

### 1. C1 — the frozen-file shape table (r99 runner, r98 hook)

```
python3 -B census/round-99/declared-shapes.py --freeze census/round-99/shapes.tsv \
  --search census/round-99/c1-survivor-search.py --scripts census/round-98/shapes \
  --work /fast/scratch/hyaku/souji-r99/R99Scribe/w-frozen
```
exit **0**
```
FREEZE sha256=8bc642c44e0c1f6414fb4b07aaf922c01bf2d2ea8b91bda7bac81f60a05a8a14
SHAPES-SUMMARY shapes=17 mismatched=0
```
All 17 rows `ok` (per-shape lines in `R99Scribe/repro/out-population-movability.txt` and the frozen run's
own stdout; e.g. `SHAPE q1i-finally-then-catch.py kind=declared plain=0 hooked=0 ok`).

### 2. C1 — the two do-nothing controls on the SAME frozen file

```
python3 -B census/round-99/declared-shapes.py --freeze census/round-99/shapes.tsv \
  --search census/round-98/controls/c1-r95-search.py --scripts census/round-98/shapes --work <scratch>
```
exit **1**
```
FREEZE sha256=8bc642c44e0c1f6414fb4b07aaf922c01bf2d2ea8b91bda7bac81f60a05a8a14
SHAPES-SUMMARY shapes=17 mismatched=3
MISMATCH t1-catch-module-falloff.py
MISMATCH t4-reraise-at-module.py
MISMATCH q1i-finally-then-catch.py
```
```
python3 -B census/round-99/declared-shapes.py --freeze census/round-99/shapes.tsv \
  --search census/round-98/controls/c1-r97-search.py --scripts census/round-98/shapes --work <scratch>
```
exit **1**
```
SHAPES-SUMMARY shapes=17 mismatched=3
MISMATCH q1o-save-then-bare-raise.py
MISMATCH q1q-caught-then-direct.py
MISMATCH q1i-finally-then-catch.py
```
Both controls exceed `mismatched=0` on the frozen file. **Note for the L1:** the plan's A0.1 says the r95
control must print `mismatched>=4`; the measured value on the frozen file is **3** (rows `t1`, `t4`, `q1i`),
and the r98 receipt `census/round-98/records/shapes-r95.txt` also reads `mismatched=3`. The plan's `>=4`
threshold is not met by the frozen file. Flagged as a predicate observation, not edited.

### 3. C1 — the relabel attack (routed defect 1 / Q173)

```
python3 -B census/round-99/declared-shapes.py \
  --freeze .ufo/waves/round-99/w1/R99Critic/reproducers/shapes-relabel.tsv \
  --search census/round-99/c1-survivor-search.py --scripts census/round-98/shapes --work <scratch>
```
exit **1**
```
FREEZE sha256=004356d76d94c54158232f250077c6995b5103b16f34ef4111e4933bc6cc330a
SHAPES-SUMMARY shapes=17 mismatched=3
MISMATCH q1o-save-then-bare-raise.py
MISMATCH q1q-caught-then-direct.py
MISMATCH q1i-finally-then-catch.py
```
The count moves 0 → 3 under relabelling with the hook untouched, and the printed freeze hash changes.
**routed defect 1 (M6/Q173) is satisfied in mechanism.**

### 4. M9 — population and hash binding of the frozen file (my reproducer)

```
SCRATCH=/fast/scratch/hyaku/souji-r99/R99Scribe/pm \
  bash .ufo/waves/round-99/w1/R99Scribe/repro/population-movability.sh
```
exit **0**; output saved verbatim at `R99Scribe/repro/out-population-movability.txt`:
```
frozen                 exit=0  SHAPES-SUMMARY shapes=17 mismatched=0
drop-q1q               exit=0  SHAPES-SUMMARY shapes=16 mismatched=0
dup-q1q                exit=0  SHAPES-SUMMARY shapes=18 mismatched=0
brokenhook-frozen      exit=1  SHAPES-SUMMARY shapes=17 mismatched=3
brokenhook-flipped     exit=0  SHAPES-SUMMARY shapes=17 mismatched=0
--- freeze hashes (the runner prints these; nothing compares them to the pinned value) ---
8bc642c44e0c1f6414fb4b07aaf922c01bf2d2ea8b91bda7bac81f60a05a8a14  .../census/round-99/shapes.tsv
132ef7f9d411663798126bfd61f533484201b85910e9b7c7b45578e090e3182c  .../shapes-drop-q1q.tsv
bd54a53266ab74aee9aa0dbafa0c1bd3cf21f9f34199750e423c5bef5372a4b4  .../shapes-dup-q1q.tsv
59dc65efb1ad57b59b22e8eca769b718221789fed6b1667c6e6d270c77e751eb  .../shapes-flip-t1t4q1i.tsv
```
The last row is the decisive pair: the **same** broken hook (the `_souji_stamp(exc, "EH")` leg replaced
with `pass`) reads `mismatched=3` against the frozen file (exit 1) and `mismatched=0` against a copy with
three rows flipped (exit 0). Two independent defects cancel and the summary line is green.

### 5. M10 — the narrowed reap cannot reach the T1 escapee it exists to reap

```
python3 -B .ufo/waves/round-99/w1/R99Scribe/repro/repro_escapee_underkill.py \
  --counter .ufo/waves/round-99/w1/R99Scribe/repro/c2-setup-arms-pinned.py --work <scratch>
```
exit **1** (the script exits 1 when the escapee is still alive after the reap); output saved verbatim at
`R99Scribe/repro/out-escapee-underkill.txt`:
```
COUNTER sha256=03e8a99e2e447e4c5e7067dea191450c7d5ec10102cb33e2a246b5b3d1c02b57
SUBSREAPER prctl(PR_SET_CHILD_SUBREAPER,1) rc=0 counter_pid=690172
PROBE spawn_pid=690297 spawn_starttime=7397208
ESCAPEE pid=690314 ppid=690172 state=S starttime=7397208
ESCAPEE argv_carries_token=True
ESCAPEE is_descendant_of_spawn_pid=False is_descendant_of_counter=True
SURVIVORS (committed r99 predicate) = 0
REAP _reap_owned killed=0 escapee_alive_after_reap=True state_after=S
VERDICT escapee_reaped=False survivors_reported=0
```
The pinned counter copy (`R99Scribe/repro/c2-setup-arms-pinned.py`) is byte-identical to the committed
`census/round-99/c2-setup-arms.py` (both sha256 `03e8a99e2e447e4c5e7067dea191450c7d5ec10102cb33e2a246b5b3d1c02b57`).

The same conclusion is visible in the executor seat's committed receipts
(`.ufo/waves/round-99/w1/R99ExecC2/counter-r99.out`): `ARM T1 exit=2 want=2 line=yes conform=yes survivors=0`
with the T1 arm's `--survivors 0 planted-killed 0` — **`planted-killed 0`**: nothing was killed, yet the
count reads 0 and the arm conforms.

### 6. C2 — the cross-arm probe (r99 counter), and the probe repair

**First committed probe** (sha256 `0910e243e4fefdeb00f0649524b74d9f60ee103d3d1fce6093c9e1fb31eb981f`),
run by this seat:
```
python3 -B census/round-99/c2-cross-arm-probe.py --counter census/round-99/c2-setup-arms.py \
  --probe census/round-98/c2-forgery-probe.py --tool tools/souji-record-agreement.py \
  --before census/round-92/controls/c2-before-tool.py --work <scratch> --arm-timeout 200 --label r99
```
exit **2**
```
ARM T1 exit=-15 want=2 line=no conform=no survivors=0
ARMS-SUMMARY arms=20 conform=16
T1-REAP survivors 0 planted-killed 0
CROSS-ARM-PLANTED n=0 dead=0 alive=0 counter_exit=1 token=.../arms/fixture-pipe-holder.py
CROSS-ARM-SUMMARY verdict=inconclusive (no carrier pids recorded)
```
Two probe defects, both measured by this seat (see M11): the probe looked for `carrier.pid` one directory
too shallow (`arms/<arm>/carrier.pid` vs the fixture's actual `arms/<arm>/positive/carrier.pid`), and the
carrier inherited the fixture's stdout pipe, so every arm died with
`C2-FORGERY-FATAL: the fixture run for the positive control exceeded --timeout 120s`.

**Repaired committed probe** (sha256 `22eda14170decb34549e6e1a7787ea72f283a1771398ae1a187b9b3f3e7cb154`),
run by this seat against the r99 counter:
```
python3 -B census/round-99/c2-cross-arm-probe.py --counter census/round-99/c2-setup-arms.py \
  --probe census/round-98/c2-forgery-probe.py --tool tools/souji-record-agreement.py \
  --before census/round-92/controls/c2-before-tool.py --work <scratch> --arm-timeout 200 --label r99
```
exit **0**
```
ARM T1 exit=2 want=2 line=yes conform=yes survivors=0
ARMS-SUMMARY arms=20 conform=17
T1-REAP survivors 0 planted-killed 0
CROSS-ARM-RESULT carrier pid=1933178 ppid=1525 argv_token=yes state=S      (30 such lines, all state=S)
CROSS-ARM-PLANTED n=30 dead=0 alive=30 counter_exit=1 token=.../arms/fixture-pipe-holder.py
CROSS-ARM-SUMMARY verdict=spared
```
Full receipt at `R99Scribe/repro/out-crossarm-r99.txt` (30 `CROSS-ARM-RESULT` lines, every one
`argv_token=yes state=S` — none killed).

**r98 control leg** (the same probe against `census/round-98/c2-setup-arms.py`, which still carries branch
(c)): see §"C2 cross-arm probe — r98 control leg" below.

Note for the L1: `conform=17`, not `20`, on a probe leg — the probe swaps the counter's fixtures, and under
the swapped fixture the forgery probe rejects nothing, so three arms (P1, P2, S1) lose their expected exit
code. `conform=20` is therefore **not** a binding byte on a cross-arm probe leg.

### 7. Read-only git checks

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD            -> c94d678c8a76f3f87f73b49a11a9d4e2aff73e3b
git -C ... status --porcelain                                                -> ?? census/round-99/
git -C ... ls-files .ufo/waves/round-98/ | wc -l                              -> 0   (.ufo/waves/ is gitignored)
git -C ... check-ignore -v .ufo/waves/round-99/w1/R99Reviewer1.md            -> .gitignore:1:.ufo/waves/
```
All read-only. No `add`/`commit`/`stash`/`checkout`/`reset`/`pull`/`push`; no mutating `jj` command.

---

## C2 cross-arm probe — r98 control leg

Same repaired committed probe (sha256 `22eda141…`), same fixtures, same `--arm-timeout 200`, only
`--counter` swapped to the r98 counter (which still carries branch (c)):

```
python3 -B census/round-99/c2-cross-arm-probe.py --counter census/round-98/c2-setup-arms.py \
  --probe census/round-98/c2-forgery-probe.py --tool tools/souji-record-agreement.py \
  --before census/round-92/controls/c2-before-tool.py --work <scratch> --arm-timeout 200 --label r98
```
exit **1**
```
ARM T1 exit=2 want=2 line=yes conform=yes survivors=0
ARMS-SUMMARY arms=20 conform=17
T1-REAP survivors 0 planted-killed 32
CROSS-ARM-PLANTED n=30 dead=30 alive=0 counter_exit=1 token=.../arms/fixture-pipe-holder.py
CROSS-ARM-SUMMARY verdict=killed
```
Full receipt at `R99Scribe/repro/out-crossarm-r98.txt` (30 `CROSS-ARM-RESULT` lines, all dead).

**The probe discriminates in both directions — the C2 cross-arm leg is measured:**

| counter | branch (c) | `T1-REAP` | carriers | verdict | exit |
|---|---|---|---|---|---|
| r99 (`census/round-99/c2-setup-arms.py`) | removed | `survivors 0 planted-killed 0` | `n=30 dead=0 alive=30` | **spared** | 0 |
| r98 (`census/round-98/c2-setup-arms.py`) | present | `survivors 0 planted-killed 32` | `n=30 dead=30 alive=0` | **killed** | 1 |

Both runs report `ARM T1 … survivors=0 conform=yes` — the `survivors` byte is identical on both sides of
the discriminator, which is precisely why it cannot be the witness (M10). The discriminator is
`planted-killed` / the carriers' own pids.

**The C2 claim's cross-arm leg holds as written**: "a counter-descendant carrier outside the spawn chain
is not signalled (branch (c) removed)" — measured, 30/30 spared under r99, 30/30 killed under r98, same
probe, same fixtures, one `--counter` apart.

---

## Findings

Every finding carries a reproducer under this seat's wave dir.

### F1 (calibration, HIGH) — the frozen label file does not bind the shape table's population, and the runner only prints the hash

- **Reproducer:** `.ufo/waves/round-99/w1/R99Scribe/repro/population-movability.sh`
  (output: `.ufo/waves/round-99/w1/R99Scribe/repro/out-population-movability.txt`).
- **Measured:** frozen file → exit 0 `shapes=17 mismatched=0`; q1q row deleted → exit 0
  `shapes=16 mismatched=0`; q1q row duplicated → exit 0 `shapes=18 mismatched=0`; broken hook against the
  frozen file → exit 1 `shapes=17 mismatched=3`; **broken hook against a three-row-flipped copy → exit 0
  `shapes=17 mismatched=0`**. The runner prints `FREEZE sha256=…` but nothing in the run compares it to
  the pinned `8bc642c44e0c1f6414fb4b07aaf922c01bf2d2ea8b91bda7bac81f60a05a8a14`.
- **Captured-by:** reviewer seat (`R99Reviewer1.md` F1, F2, F3) and mutation seat (`R99MutC1.md` F2) also
  report the population and detector-blindness halves; this seat adds the explicit broken-hook cancellation
  pair with its own reproducer.
- **Lesson row:** M9.

### F2 (operability, HIGH) — the narrowed reap does not reach the T1 escapee, and `survivors=0` cannot see it

- **Reproducer:** `.ufo/waves/round-99/w1/R99Scribe/repro/repro_escapee_underkill.py`
  (output: `.ufo/waves/round-99/w1/R99Scribe/repro/out-escapee-underkill.txt`).
- **Measured:** `ESCAPEE is_descendant_of_spawn_pid=False is_descendant_of_counter=True`,
  `SURVIVORS (committed r99 predicate) = 0`, `REAP _reap_owned killed=0 escapee_alive_after_reap=True`,
  `VERDICT escapee_reaped=False survivors_reported=0`. The committed executor receipt
  (`R99ExecC2/counter-r99.out`) shows the same: `ARM T1 … conform=yes survivors=0` with
  `--survivors 0 planted-killed 0`.
- **The `survivors` byte is byte-identical on both sides of the discriminator** (measured by this seat,
  §"C2 cross-arm probe — r98 control leg"): r99 `survivors 0 planted-killed 0` → `verdict=spared`; r98
  `survivors 0 planted-killed 32` → `verdict=killed`; both print `ARM T1 … conform=yes survivors=0`.
  `survivors=0` therefore cannot witness the reap.
- **Captured-by:** reviewer seat (`R99Reviewer2.md` F2), critic seat
  (`R99Critic/reproducers/analyze_t1.py`), executor seat (`R99ExecC2.md` F1 — it names the escapee pid
  `3624139`, still alive after the run), connector seat
  (`R99Connector/reap-rule.out`: `REAP-RULE-SUMMARY control_killed=False escapee_killed=False
  spawned_escapee_leaked=True`), and this seat with a live reproducer.
- **Lesson row:** M10.

### F3 (operability, MEDIUM) — the first committed cross-arm probe could not fail and reported `inconclusive`

- **Reproducer:** the committed probe's own receipts, reproduced by this seat and saved at
  `.ufo/waves/round-99/w1/R99Scribe/repro/out-crossarm-r99.txt` (post-repair) and quoted in §6 above
  (pre-repair).
- **Measured (pre-repair):** `CROSS-ARM-PLANTED n=0 dead=0 alive=0` and
  `CROSS-ARM-SUMMARY verdict=inconclusive (no carrier pids recorded)`, exit 2, while the carriers were
  alive; and `ARMS-SUMMARY arms=20 conform=16` with every arm's
  `C2-FORGERY-FATAL: … exceeded --timeout 120s`.
- **Captured-by:** this seat. (The executor seat repaired the probe in-round to sha256 `22eda141…`; this
  seat did not edit it and re-measured the repaired file.)
- **Lesson row:** M11.

### F4 (calibration, LOW) — the plan's r95 control threshold is not met by the frozen file

- **Measured:** r95 hook against the frozen file → exit 1 `shapes=17 mismatched=3` (rows `t1`, `t4`,
  `q1i`). The r98 receipt `census/round-98/records/shapes-r95.txt` reads `mismatched=3` as well.
  `plans/round-99.md` A0.1 states the r95 control must print `mismatched>=4`.
- **Not a defect in the runner** — a predicate observation for the L1 (predicates are L1-frozen; this
  seat did not edit the plan or any predicate).
- **Lesson row:** none (see the note in the draft).

### F5 (conformance, INFO) — routed defect 3 (prefile falsification ledger) is still open

- `souji-shokunin/.ufo/waves/round-99/` contains `claims.json` but **no** `claim-falsification.tsv`
  (`.ufo/waves/round-98/` contains both). `scripts/hyaku/prefile-falsification.py` therefore cannot pass
  for r99 as it stood when this seat looked.
- Status-neutral conformance item; it belongs to the L1's file-writing step, not to the lesson blocks.

---

## Out of scope for this seat

- Landing or editing `corpus/lessons/round-99.md` — the L1's job (this seat delivered a draft only).
- Editing any predicate (the plan's A0.1, the runner, the counter, the probe) — L1-frozen.
- The no-harm 278-mutant population measurement (executor/census seat) — not re-run here.
- The 83-decoy scale run — the executor seat's committed receipt
  (`R99ExecC2.md`: r99 `dead=0 alive=86 verdict=spared`, r97 `dead=60 alive=25 verdict=killed`) was read,
  not re-run.

## Known limits of this seat's own work

- The r98 control leg of the cross-arm probe is reported in the section above; if it did not finish within
  its budget, that is stated there explicitly rather than papered over.
- The `## Mistakes` rows are **drafts**; the L1 decides which are admitted as r99 lessons and what wording
  ships. No predicate was edited in place by this seat.
- The broken-hook reproducer mutates only a **scratch copy** of the search file
  (`R99Scribe/repro/broken-search.py`); the lane's `census/round-99/c1-survivor-search.py` was never
  modified (sha256 `e8ba780a5b8d807ff199c33a679d7d8dd7259fb93e934d123b009e9f9f2649e1`, identical to the
  r98 hook).

## Artifact paths

| path | contents |
|---|---|
| `.ufo/waves/round-99/w1/R99Scribe.md` | this report |
| `.ufo/waves/round-99/w1/R99Scribe/lesson-draft.md` | the draft `## Gate` + `## Mistakes` blocks (the deliverable) |
| `.ufo/waves/round-99/w1/R99Scribe/cross-arm-probe-scribe.py` | this seat's /proc-scanning cross-arm probe (independent of the committed one) |
| `.ufo/waves/round-99/w1/R99Scribe/repro/population-movability.sh` | M9 reproducer |
| `.ufo/waves/round-99/w1/R99Scribe/repro/out-population-movability.txt` | M9 measured output |
| `.ufo/waves/round-99/w1/R99Scribe/repro/repro_escapee_underkill.py` | M10 reproducer |
| `.ufo/waves/round-99/w1/R99Scribe/repro/out-escapee-underkill.txt` | M10 measured output |
| `.ufo/waves/round-99/w1/R99Scribe/repro/c2-setup-arms-pinned.py` | byte-pinned copy of the committed r99 counter |
| `.ufo/waves/round-99/w1/R99Scribe/repro/out-crossarm-r99.txt` | C2 cross-arm probe receipt (r99 counter, `verdict=spared`) |
| `.ufo/waves/round-99/w1/R99Scribe/repro/out-crossarm-r98.txt` | C2 cross-arm probe receipt (r98 counter control) |
| `.ufo/waves/round-99/w1/R99Scribe/repro/out-brokenhook-{frozen,flipped}.txt` | the M9 cancellation pair's raw runner output |
| `.ufo/waves/round-99/w1/R99Scribe/repro/out-{drop-q1q,dup-q1q}.txt` | the M9 population rows' raw runner output |
