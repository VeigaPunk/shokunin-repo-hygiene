## Status

STATUS: PASS — all four requested tests ran against the frozen revision set; two cross-claim couplings and one instrument gap are reproduced with the frozen counters. Per-claim verdicts in Findings 6.

## Evidence

Scratch only: `/fast/scratch/hyaku/souji-r32/SwarmCritic37/` (clone `c`, `c2`, `c3`, all `--no-local`, `origin` removed; deleted at the end of this seat). Base `85b61a151923986e7e6b48f7084b9122561b5f3d`, prereg `3ec84fc81b3243429c834a051880b0bcde06291c`. No installs, no pacman, no lane writes.

E1 — frozen C1 counter at the prereg revision on the lane (base reading reproduced):

```
$ python3 -B .../census/round-32/c1-counter.py --root .../souji-shokunin --rev 3ec84fc... --base 85b61a1... --list-rev 3ec84fc...
SUMMARY items=44 bound_run=0 bound_record=0 bound_field=0 withdrawn=0 unbound=44 mismatches=44 rev=3ec84fc...   rc=1
```

E2 — surrogate-landing driver over all 27 `c2-items.tsv` commands: same argv, three revisions (base, base+44 SCORECARD binding rows, base+rows+surrogate C3 corpus/README/SOURCES/record/fixture), each in a clean clone checkout with TMPDIR under scratch; comparison is the counter's own normalization and last digit-bearing line.

```
MOVED=1/27
T18  base=rc0 SUMMARY total=52 pass=52 fail=0 blocked=0 inventory=exact baseline_mismatches=26
     simC1=rc0 ... baseline_mismatches=26
     simC3=rc0 ... baseline_mismatches=27   MOVED
T03  rc1 assertions=252 resolved=229 skipped=401 mismatches=23   (identical at base, simC1, simC3)
```

E3 — bisect of the single C3 file that moves T18 (each variant a commit on base, T18 argv unchanged):

```
BASE:                SUMMARY total=52 pass=52 fail=0 blocked=0 inventory=exact baseline_mismatches=26
V1 SOURCES append:   ... baseline_mismatches=26
V2 knowledge entry:  ... baseline_mismatches=27      <- only file added: corpus/knowledge/jj-abandoned-object-mtime-clock.md
V3 coverage row:     ... baseline_mismatches=26
V4 record+fixture:   ... baseline_mismatches=26
V5 wave report:      ... baseline_mismatches=26
```

E4 — frozen C2 counter at `W1` (base + a stand-in for the intended TMPDIR fix in `tests/fixtures/r20-input-binding.py` + the one knowledge entry), `--only T18`:

```
ITEM T18 FAIL base=rc1:W4235:SUMMARY ... baseline_mismatches=26  sbox=rc1:W4216:SUMMARY ... baseline_mismatches=27  regress
```

E5 — frozen C1 counter, `--only N35,N36`, three revisions differing only in `tools/souji-landing-gate.py`:

```
A rows only:                         MATCH         rc=0 observed=cases=10 pass=10 control=FALSE-GREEN-REJECTED
B rows + one REV precision rule off: RUN-MISMATCH  rc=1 observed=cases=10 pass=9 control=FALSE-GREEN-REJECTED   (mismatches=2, rc=1)
C rows + intended TMPDIR fix:        MATCH         rc=0 observed=cases=10 pass=10 control=FALSE-GREEN-REJECTED
```

E6 — Q59 instrument on the frozen prereg and on one mutant:

```
$ python3 -B tools/souji-axis-check.py --prereg census/round-32/records/preregistration.txt --scorecard SCORECARD.md
claims=3 flags=0
$ (mutant: CLAIM C2 axis calibration, surface-class instrument-repair unchanged)
claims=3 flags=0
$ (mutant: CLAIM C2 axis operability, surface-class knowledge-entry)
FLAG C2 R2 surface-class 'knowledge-entry' declared on 'operability'; allowed only on 'coverage'   flags=1
```

E7 — C1 run binding for N12 (cell integer 13, unit "fail") restated as a different quantity; accepted by v1 and by v2 (amendment A0):

```
ITEM N12 SCORECARD.md:161 literal=failed=0 binding=run MATCH bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools rc=0 observed=SUMMARY total=35 failed=0 skipped=2
```

E8 — the same item bound by the record the delivered row already cites, accepted (the replacement in A5):

```
ITEM N12 SCORECARD.md:161 literal=failed=13 binding=record MATCH census/round-17/jj-receipts-base5fa6017.txt:51
SUMMARY items=1 bound_run=0 bound_record=1 bound_field=0 withdrawn=0 unbound=0 mismatches=0
```

E9 — the line-423 pair bound by r31 records instead of the run, accepted (the replacement in A2):

```
ITEM N35 SCORECARD.md:423 literal=cases=10 binding=record MATCH census/round-31/records/c2-after-v1.txt:22
ITEM N36 SCORECARD.md:423 literal=pass=10 binding=record MATCH census/round-31/records/c2-after-v2.txt:22
SUMMARY items=2 bound_run=0 bound_record=2 bound_field=0 withdrawn=0 unbound=0 mismatches=0
```

## Findings

1. **C3's mandated knowledge entry moves C2's T18; C2's target is unreachable at the tip.** `census/round-32/c2-items.tsv` row T18 runs `tests/fixtures/r20-input-binding.py --baseline 12516f7d...`; `tests/fixtures/r20-input-binding.py:1136-1160` (`compare_baseline`) counts every closure path whose bytes differ from the frozen baseline tree, so a *new* `corpus/knowledge/*.md` adds exactly one mismatch (E3 V2: 26 to 27). C3 must add `corpus/knowledge/jj-abandoned-object-mtime-clock.md` (`census/round-32/records/preregistration.txt`, C3 line). C2's predicate requires SBOX to print BASE's line (`census/round-32/c2-counter.py`, "SBOX exits with BASE's exit code and prints BASE's S"), so after C3 lands no C2 fix can pass T18 (E4). This is a second, independent reason T18 cannot pass: the T18 owner seat reports four sandbox aborts from baseline-pinned entrypoint bytes (`.ufo/waves/round-32/w1/SwarmExecutor14.md`, its ATTACK); mine survives that repair, because it moves the line rather than the exit path. Fixture docstring, `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r20-input-binding.py:6-7`: "changes one owned input at a time with an inert comment/whitespace mutation (or one valid added knowledge record)".

2. **C1's run bindings are not isolated from C2.** The counter materializes only the entry script from the base blob into the REV clone (`census/round-32/c1-counter.py`, `run()`); every callee the script reaches by path is REV bytes. C1 docstring: "The script is taken from the --base blob and run (no shell) in a private git clone --no-local at REV". Line 423 names `tests/fixtures/r31-landing-gate-precision.py --tool tools/souji-landing-gate.py` (`SCORECARD.md:423`), and that fixture subprocesses the tool path (`tests/fixtures/r31-landing-gate-precision.py:190-203`); C2 owns `tools/souji-landing-gate.py` in three items' `files` column (T02, T29, T30). One rule edit at REV flips N35/N36 to RUN-MISMATCH (E5 B). The prereg's sentence "C2's tool edits cannot move C1" is false as a mechanism; the same channel exists at line 168 (`r20-audit-contract.py` imports the REV auditor, `tests/fixtures/r20-audit-contract.py:406-407`, a T10 file) and line 161 (`r17-jj-receipts.sh` calls `$LANE/tools/souji-verify.sh`, `tests/fixtures/r17-jj-receipts.sh:125-130`, a T15 file; that one measured neutral: `SUMMARY total=35 failed=0 skipped=2` before and after the TMPDIR change). Delivered wave-1 rows already take these bindings: `.ufo/waves/round-32/w1/deliver-c1-bind-N35-N43-L29.md:13-15` (N35, N36, N37 by the line-423 run), `.ufo/waves/round-32/w1/deliver-c1-bind-N12-N19.md:20` (N16 by `r19-seat-audit-shapes.py`, measured neutral), and `:23` (N19 by `run: python3 -B tools/souji-coverage-agreement.py --root . --rev 778747e...`, a tool C2 lists for T21/T22).

3. **C3's legs L2 and L3 execute REV tools that C2 edits.** `census/round-32/c3-counter.py` L2 runs `tools/souji-coverage-agreement.py` at REV (file listed for T21/T22) and L3 runs `tools/souji-gate-check.py` at REV (file listed for T05, whose scratch root is the literal at `tools/souji-gate-check.py:231`). No live movement for the listed fix site: with `--snapshot-dir census/round-31/sources` the entries line stays `entries=1 ok=0 slice_verdicts=0 slice_total=0 fail=1` before and after the TMPDIR change. Coupling is contingent, not structural.

4. **Q59's instrument cannot see C2's surface-class.** `tools/souji-axis-check.py`, R2: "Other surface-classes (receipt-binding, measurement) are neutral." C2 declares `surface-class: instrument-repair` (`census/round-32/records/preregistration.txt`, MACHINE BLOCK, CLAIM C2), which is in neither `SURFACE_AXIS` nor `NEUTRAL_SURFACES`, and the R2 branch only flags a class that is in `SURFACE_AXIS`. E6: an axis-swapped mutant still prints `flags=0`, so the prereg's Q59 claim of an instrument rather than a hand review is unmet for that claim.

5. **A C1 run literal may restate a different quantity, leaving the cell stale.** The literal check is `len(ints(lit)) != len(iints)` (count only) for all kinds, and value equality is enforced only in the `record` and `field` branches (`census/round-32/c1-counter.py`); a run binding whose literal is `failed=0` scores MATCH for an item whose cell integer is 13 (E7), under v1 and v2. The prereg allows restating ("A run literal may restate the integer (a corrected count)"), so `mismatches=0` does not imply the cells are right. The delivered row `.ufo/waves/round-32/w1/deliver-c1-bind-N12-N19.md:16` is exactly this exploit: literal `failed=0` for a cell whose integer is 13. A record binding on the same delivery's own citation, `census/round-17/jj-receipts-base5fa6017.txt:51`, literal `failed=13`, MATCHes (E8).

6. **Claim verdicts.** C1 calibration: axis is right (self-assessment file, the class the R2 table maps to calibration) and its SCORECARD append moves nothing in C2's 27 commands or in C3's legs (E2: 26 of 27 identical; T03 unaffected because `tools/souji-declared-evidence.py` reads at `--rev`); defects are Findings 2 and 5. C2 operability: axis is right by `AXES.md` (runnable artifacts), but the claim is killed by C3 through T18 (Finding 1) and its attribution is unverified by the Q59 instrument (Finding 4). C3 coverage: axis is right (knowledge-entry plus registry rows), but its verification is not independent of C2's patches (Finding 3).

## Attack log

A1 — C3 defeats C2 by adding its own mandated file. Reproduced: E3 V2 and E4 (base line 26, REV line 27 for T18; every other item unchanged). Impacted axes: operability (C2 target), coverage (C3 becomes the cause of a sibling's miss). Smallest safe correction: before any landing, the L1 issues a stricter-only enumeration amendment removing T18 from `census/round-32/c2-items.tsv`, or replaces it with a command from the same file that prints no baseline diff; the target `fail=0` stays over the reduced set. Keeping T18 and C3 cannot both succeed.

A2 — C2 can move C1 through a run callee. Reproduced: E5 (MATCH at A, RUN-MISMATCH at B, MATCH under the intended TMPDIR fix at C). Impacted axes: calibration (C1's target depends on bytes C1 does not own). Smallest safe correction, verified at scratch rev `ec3f2f2d2699`: rebind N35 and N36 as `record: census/round-31/records/c2-after-v1.txt:22` and `c2-after-v2.txt:22` (E9), and N37 on `c2-after-v3.txt:22` (same line shape, distinct occurrence), instead of the three run rows at `.ufo/waves/round-32/w1/deliver-c1-bind-N35-N43-L29.md:13-15`; do the same for N19 if C2 ever edits `tools/souji-coverage-agreement.py`. If a run binding is kept, the L1 must re-run the C1 counter after C2 lands and, if it moved, replace the binding or take a `withdrawn:` row inside the eight-row cap. Adopted by the binding seat this run: all three run rows replaced by the record rows above at its rev `fb969674de64`, reporting `bound_run=0 bound_record=6 bound_field=1 withdrawn=3 unbound=0 mismatches=0` (its message, not re-run here).

A3 — C2 can move C3's L2/L3. Reproduced structurally; the listed fix site is output-neutral in one measured case (Finding 3). Impacted axes: coverage. Smallest safe correction: none needed for the enumerated sites; the L1 should re-run the C3 counter after C2 lands and treat a moved leg as a C2 defect, not a C3 one.

A4 — Q59 R2 is bypassable by a novel surface-class string. Reproduced: E6. Impacted axes: calibration (the axis-honesty instrument). Smallest safe correction: make R2 flag any class outside `SURFACE_AXIS` keys and `NEUTRAL_SURFACES` (exit 1, FLAG R2 unknown surface-class), and rename C2's class to the listed `instrument-acquisition`, which R2 already permits on operability.

A5 — C1 run literals can confirm a different quantity. Reproduced: E7 under v1 and v2, and delivered as `.ufo/waves/round-32/w1/deliver-c1-bind-N12-N19.md:16`. Impacted axes: calibration. Smallest safe correction, verified at scratch rev `f6cf4bf88e5b`: bind N12 as `record: census/round-17/jj-receipts-base5fa6017.txt:51` with literal `failed=13` (E8), and in general require a run literal's integers to equal the item's integers (value equality, as `record` and `field` already do); a corrected count then lands as a record, a field, or a withdrawal, and the stale cell stays visible.

Negative results, with the sweep that produced them: C1's append moved 0 of 27 C2 commands and no C3 leg (E2); a committed wave report under `.ufo/waves/round-32/w1/` moved 0 (E3 V5); C3's SOURCES row, coverage row, record and fixture each moved 0 on their own (E3 V1, V3, V4).

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/SwarmCritic37.md` (this report).
