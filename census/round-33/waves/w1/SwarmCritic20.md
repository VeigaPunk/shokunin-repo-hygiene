# SwarmCritic20 — round 33 w1, C1 item K22 (attack seat)

## Status
STATUS: PASS — K22 attacked as assigned (determinism, predicate faithfulness, out-of-set counts, frozen counter); verdict **NONDETERMINISTIC**, mechanism reproduced and named. Nothing in the lane modified; scratch removed.

## Evidence

Cell under test: `SCORECARD.md:422` at base `6017a482e7068d5afb7617640198fbb0fe743357`, read with

    git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 6017a482e7068d5afb7617640198fbb0fe743357:SCORECARD.md | sed -n 422p

Prose quote from that line: "40 of 41 cells now carry such a row and the one refusal is reported, not hidden" (17 words, no pipe). Stated outcome quote: "SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1" (no pipe). Frozen item: `census/round-33/c1-items.tsv:36` — line 422, exit `*`, predicate exactly that line, argv same three full40s as the cell, `--root <lane>` normalised to `--root .`.

### (1) Frozen argv, own scratch clone at 2d9bca55a9f042a2c9ed60a797a8069e74c41f46

Clone: `git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /fast/scratch/hyaku/souji-r33/AuditK22/c`, origin removed, `rev-parse --show-toplevel` = the clone, detached at `2d9bca55`. Env per run: `GIT_CONFIG_NOSYSTEM=1`, `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE` unset.

    python3 -B tools/souji-capability-cells.py --root . --rev 24f343c8ffc820c0f89b4252cbdc94ab9a673aab --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525

| reading | TMPDIR | rc | last line |
|---|---|---|---|
| run1 | fresh `/fast/.../AuditK22/tmp1` | 1 | `SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1 rev=24f343c8ffc8...` |
| run2 | fresh `/fast/.../AuditK22/tmp2` | 1 | same (byte-identical output, 42 lines: 41 `ITEM` + `SUMMARY`) |
| run3 | **TMPDIR unset** (`env -u TMPDIR`) | 1 | same (byte-identical to run1/run2) |

Further isolated runs of the same command in counter-style clones (`git clone --no-local --no-checkout`, `checkout -qf --detach 2d9bca55`): probea, probeb and loop4-9, 8 readings, all `bound_run=20 ... mismatches=1`, byte-identical to run1. Total direct readings: **11 AGREE / 0 MISMATCH**.

### (2) The frozen counter itself

    python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-33/c1-counter.py \
      --root /home/vgpnk/Projects/shokunin/souji-shokunin \
      --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
      --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
      --scratch /fast/scratch/hyaku/souji-r33/AuditK22/cnt --only K22

Three readings of this identical invocation:

    #1  ITEM K22 MISMATCH original rc=1 expect_exit=* predicate fails last=SUMMARY items=41 bound_run=19 bound_record=20 unbound=1 mismatches=2 rev=24f343c8ffc8...
        SUMMARY items=1 agree=0 mismatches=1 restated=0 partial=1 rev=2d9bca55a9f0...        rc=1
    #2  ITEM K22 AGREE    original rc=1 expect_exit=* predicate holds last=SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1 rev=24f343c8ffc8...
        SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f0...        rc=0
    #3  ITEM K22 MISMATCH original rc=1 expect_exit=* predicate fails last=SUMMARY items=41 bound_run=19 bound_record=20 unbound=1 mismatches=2 rev=24f343c8ffc8...
        SUMMARY items=1 agree=0 mismatches=1 restated=0 partial=1 rev=2d9bca55a9f0...        rc=1

The same counter logic, copied to scratch with a 3-line raw-output capture added (only delta, `diff` of the copy against the frozen counter: `171a172,174` writing `out`/`err`/`rc` for K22; verdict logic untouched), gave 12 sequential readings, all AGREE.

### (3) Flake reproduced and named

Four such captures launched concurrently (`--only K22`, one scratch each): **3 MISMATCH / 1 AGREE**. The failing binding is always L32; three different failing cases inside the fixture:

    p1  ITEM L32 SCORECARD.md:173 literal=15/15 superseded binding=run RUN-MISMATCH
        python3 tests/fixtures/r23-record-agreement.py rc=1 observed=case=12 expect=rc!=0 K2 uncorrected>=1 (tally arm) got=rc=1 mismatches=2 keys=4 [K2/uncorrected]
    p2  ... rc=1 observed=case=1 expect=rc=0 mismatches=0 keys=4 json-bound got=rc=0 mismatches=0 keys=4
    p3  ... rc=1 observed=case=7 expect=rc!=0 K2 filed*>=1 got=rc=1 mismatches=4 keys=4 [K2/filed-occurrence-missing]

with `SUMMARY items=41 bound_run=19 bound_record=20 unbound=1 mismatches=2` in p1/p2/p3, and 20/1 in p4. A control with `--only K16,K22` (both items in one counter, `--jobs 6`) gave K22 AGREE twice (K16 MISMATCH both — the known base mismatch at `:173`: fixture prints `selftest=15/15`, row states `9/9`); in that schedule K16 finishes before K22 reaches L32.

Mechanism (source, opened this run): `tests/fixtures/r23-record-agreement.py:67` at `9f17a1ef` (bytes identical at `24f343c8`): `SCRATCH_ROOT = "/var/tmp/souji-r23-ExecFixtureAgreement"`; line 105 `shutil.rmtree(SCRATCH_ROOT, ignore_errors=True)`; line 584 re-creates it. Every concurrent execution of this fixture wipes and rebuilds the same global tree, so any two overlapping runs corrupt each other's cases and return rc=1. K22's run binding for L32 executes the **base blob** of that script (the tool overwrites the script from `--base`), so a tip-side repair can never reach this item's reading.

### (4) Predicate faithfulness and the stub control

The predicate is the cell's quoted line verbatim; exit `*` matches the cell (it states no exit; the tool exits 1 because its internal `mismatches=1` is the same L29 refusal the cell calls "the one refusal"). No fact beyond the quote is asserted, so nothing stricter. One laxity demonstrated: a scratch stub replacing `tools/souji-capability-cells.py` with a two-line script that only prints the quoted `SUMMARY` line and exits 1, committed in a throwaway scratch clone (`a590335144885d40f71f819b55cc08416eb241de`), scored **AGREE**:

    ITEM K22 AGREE original rc=1 expect_exit=* predicate holds last=SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1
    SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=a590335144885d40f71f819b55cc08416eb241de

So the predicate cannot distinguish the 41 real re-executions from a fabricated summary line — a class-wide property of output-line items, not K22-specific; the frozen predicate is faithful to the cell's *stated outcome*.

### (5) Out-of-set counts re-derived (records opened this run)

| cell statement | re-derivation | result |
|---|---|---|
| `40 of 41 cells` | `awk -F'\t' '/^ITEM/{print $3}' run1.out \| sort -u \| wc -l` = **23**; `census/round-31/c1-cells.tsv` col 2 distinct = 23; items = 41, bound literals = 40 (20 run + 20 record), unbound = 1 | noun is wrong: 41 **literals over 23 cells**, not 40 of 41 cells; "40 of 41 literals" is right |
| `census/round-31/records/c1-after-a4.txt` | record's 41 `ITEM` lines byte-identical to run1 (only the record's leading comment and trailing `rc=1` differ); its `SUMMARY` = the quoted line | not stale |
| `census/round-31/records/c1-before.txt` `unbound=22 mismatches=34` | record line 43: `SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34 rev=1d45496ae0e5...` | not stale (record-content check; not re-executed) |
| `census/round-31/c1-cells.tsv (41 items)` | `grep -vcE '^#\|^id'` = 41 | not stale |
| "the one refusal is reported" | run1 line 29: `ITEM L29 SCORECARD.md:170 literal=18/18 base-cell binding=- UNBOUND` | not stale |
| recorded at `24f343c8` / `9f17a1ef` | `c1-after-a4.txt` and `c1-cells.tsv` unchanged from `2d9bca55` to tip (`git log`, `git status --porcelain` empty) | not stale |

### (6) Scratch behaviour of the item's command

The frozen argv passes no `--scratch`; the tool's default (source at `24f343c8`, `tools/souji-capability-cells.py:151`): `--scratch", default=os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku") + "/souji-r31/c1-counter"` — so the item ignores the caller's TMPDIR for its own work tree and writes under a fixed shared path; a live `c1.92hqrs_h` work dir was observed there during a run (removed by the tool), and `/var/tmp/souji-r23-ExecFixtureAgreement` was created/removed by the fixture (absent after).

## Findings

1. **K22 is nondeterministic at the same revision.** Two readings of the unmodified frozen counter on `2d9bca55` disagree (`bound_run=19 mismatches=2` vs `20/1`); 17 sequential counter-logic readings split 15 AGREE / 2 MISMATCH (the two `--only K16,K22` controls included), and 4-way concurrency gives 1 AGREE / 3 MISMATCH. Location: `census/round-33/c1-counter.py` + `tools/souji-capability-cells.py` at `24f343c8`, L32 (`SCORECARD.md:173`).
2. **Cause: global fixed scratch inside a run binding.** `tests/fixtures/r23-record-agreement.py:67` hard-codes `/var/tmp/souji-r23-ExecFixtureAgreement` and wipes it at line 105; overlapping executions corrupt each other. Because the tool runs the script's **base blob**, K22's reading can never be stabilised by a tip-side fixture fix.
3. **The predicate itself is faithful to the quoted line**, but it is a summary-only string check: a stub that prints the line scores AGREE, and it does not test the cell's prose (execution from the base blob, per-cell binding). Not stricter than the quote; the prose "40 of 41 cells" is numerically wrong at cell granularity (23 cells / 41 literals) and sits outside the predicate.
4. **Impact on the claim:** C1's frozen target is `mismatches=0` read once at landing and once at tip. K22 can flip that reading to 1 whenever another execution of the same fixture overlaps it (any peer running the lane suite or the counter; the wave has many). A restatement cannot repair K22: its cause execution would hit the same flake, and the original outcome holds in most isolated runs, so no commit exists where it deterministically stopped being true. No item/predicate/target change is proposed — this is reported as the attack.

## Attack log

| hypothesis | test | result |
|---|---|---|
| H1 deterministic | frozen argv ×3 (2 fresh TMPDIR, 1 unset) + 8 more isolated runs; frozen counter ×3; concurrent ×4 | **falsified** — 5 MISMATCH readings (2 sequential counter, 3 concurrent), always `bound_run=19 mismatches=2`, always L32 |
| H2 lax predicate | summary-only stub committed in scratch, scored by the frozen counter | **partially**: AGREE for a fabricated summary (class-wide; the quote is the stated outcome) |
| H3 strict predicate | compare predicate fields to the cell quote and prose | no fact beyond the quote; the 20/20 split is finer than the prose "40 of 41" but is in the quote |
| H4 stale out-of-set counts | records, `c1-cells.tsv`, distinct cells, L29 line | one residual: "40 of 41 **cells**" (23 cells); records/tsv/refusal all current |

**Verdict: NONDETERMINISTIC** — reproduced with the counter's own logic, named binding L32, named mechanism (hard-coded `/var/tmp` scratch in `tests/fixtures/r23-record-agreement.py`), and an isolated 11/11 AGREE control showing the flip is concurrency, not revision drift.

## Deliveries
- `.ufo/waves/round-33/w1/SwarmCritic20.md` (this report).
- Scratch `/fast/scratch/hyaku/souji-r33/AuditK22` removed; no lane file, git/jj state or outside path touched. No tools installed.
