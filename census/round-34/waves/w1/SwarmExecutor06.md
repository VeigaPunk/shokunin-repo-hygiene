# SwarmExecutor06 — r34 w1, C1 slice 6/12 (E05, E06a, E06b, E07, E08a)

## Status

STATUS: PASS — all five frozen items resolved at base `9c76c7222a8abff027af42e37f0d160d52526bba`
(`--list-rev 2b0171e2…`): E06a, E06b, E08a AGREE original; E05 and E07 MISMATCH and are restated by
argv correction, each row verified end-to-end by the frozen counter in a scratch clone
(`items=5 agree=5 mismatches=0 restated=2`, exit 0). No frozen predicate, target, counter, item or leg
changed; nothing committed.

## Evidence

Counter (frozen, sha256 `1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20` at
`--list-rev`), under the counter's Q77 flock plus my own, `TMPDIR` set by hand, rev = base:

```
ITEM	E05	MISMATCH	original	rc=0 expect_exit=0 predicate fails last=Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]] load=4.29
ITEM	E06a	AGREE	original	rc=0 expect_exit=0 predicate holds last=139 load=4.29
ITEM	E06b	AGREE	original	rc=0 expect_exit=0 predicate holds last=6 load=4.43
ITEM	E07	MISMATCH	original	rc=2 expect_exit=2 predicate fails last=COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-27/ or census/round-27/waves/ at 6cb22dc20c9fdb3c7a49eaa1accabca339054c17 load=4.43
ITEM	E08a	AGREE	original	rc=0 expect_exit=0 predicate holds last=135 load=4.43
SUMMARY items=5 agree=3 mismatches=2 restated=0 partial=1 rev=9c76c7222a8abff027af42e37f0d160d52526bba
```

Load `/proc/loadavg` `3.08 2.76 1.92` before, `4.43 3.07 2.04` after. Lane HEAD read at
`51acb5fb6fa38a6b593b3badb674cec559d7eb2c`; all measurement is at `--rev`, never the lane worktree.

Cause executions (counter's own `run_item`/`frozen_pred` path, one private clone per revision, scrubbed
PATH/TMPDIR, `GIT_CONFIG_NOSYSTEM=1`; load beside each):

```
E05 de478b483db66a8d8ff2d627cde1ccce6e21a014 (cause^1) rc=0 pred_holds=False last=error: source directory not found: …/lane-2/.ufo/waves/round-26 load=21.61
E05 fec846dd1781a414ae3a7d71d2d8fa2fb17900eb (cause)   rc=0 pred_holds=False last=<same stderr line> load=12.02
E05 9c76c72… (base, corrected argv)                    rc=0 last=cases=15 pass=15 control=TAMPER-REJECTED load=11.70
E07 6cb22dc20c9fdb3c7a49eaa1accabca339054c17 (cause^1) rc=2 pred_holds=False last=COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-27/ at 6cb22dc… load=21.61
E07 c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0 (cause)   rc=2 pred_holds=False last=<same> load=8.33
E07 68447afef62e4761249af55a2467657f04046537 (r30 gate) rc=2 pred_holds=False last=… or census/round-27/waves/ … load=13.13
E07 8024b540b04d677d47cf51a0d1132ec8705ef14a (r31 gate) rc=2 pred_holds=False last=<same> load=13.13
E07 9c76c72… (base, corrected argv)                    rc=0 last=SUMMARY findings=0 checked_reg=76 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=29 status_lines=79 carry_heading=1 checked_reports=94 load=12.19
```

Row-writing proof: line 23 text present at `fec846d` (1) / absent at `fec846d^1` (0); line 31 text
present at `c973d1a` (1) / absent at `c973d1a^1` (0). `git blame -L 23,23` → `fec846d`; `-L 31,31` →
`c973d1a`.

Simulation (scratch clone of the lane, origin removed, toplevel asserted, `checkout -qf --detach
2b0171e…`, section + two rows appended, `SCORECARD.md` only, throwaway identity) → sim commit
`b54a50e95c0c3b5856290f038c209e6b186ac98c`:

```
ITEM	E05	AGREE	restated	rc=0 expect_exit=0 statement is the run's last digit-bearing line last=cases=15 pass=15 control=TAMPER-REJECTED load=18.44
ITEM	E06a	AGREE	original	rc=0 expect_exit=0 predicate holds last=139 load=18.44
ITEM	E06b	AGREE	original	rc=0 expect_exit=0 predicate holds last=6 load=18.44
ITEM	E07	AGREE	restated	rc=0 expect_exit=0 statement is the run's last digit-bearing line last=SUMMARY findings=0 … checked_reports=94 load=19.60
ITEM	E08a	AGREE	original	rc=0 expect_exit=0 predicate holds last=135 load=19.60
SUMMARY items=5 agree=5 mismatches=0 restated=2 partial=1 rev=b54a50e95c0c3b5856290f038c209e6b186ac98c
```

## Findings

1. **E05 cell stale + counter stream artefact** (`SCORECARD.md:23`, `tests/fixtures/r28-wave-evidence-capture.sh`).
   The row quotes `cases=6 pass=6 control=TAMPER-REJECTED`; the fixture at base is the r29 v2 layout and
   prints `cases=15 pass=15 control=TAMPER-REJECTED`. The frozen predicate nevertheless fails for a
   second reason: the fixture writes its negative-case diagnostics to stderr *after* stdout, and the
   counter's last-digit rule reads `out.splitlines() + err.splitlines()` (`c1-counter.py`, `judge`), so
   the last digit-bearing line is a lane-2 error path, then the usage banner (it carries the digits of
   `full40`). Same artefact class already adjudicated at base lines 336/338: `R30-CORRECTION
   SCORECARD.md:314 R18 rc=0 observed=Usage: …` — "the banner is refused as an observation".
   Restated by argv correction (cause `fec846d`, last writer of the row).

2. **E07 cell not reproducible from committed bytes** (`SCORECARD.md:31`, `tools/souji-landing-gate.py:511-541`).
   `_report_paths` reads seat reports from the `--rev` tree; `6cb22dc…` carries neither
   `.ufo/waves/round-27/` nor `census/round-27/waves/` (that capture is added by `765fe8b`, round 28), so
   the row's own command exits 2 with `COULD-NOT-EVALUATE` at the row-writing commit **and its parent**.
   The recorded `findings=2 rc 2` (`census/round-27/records/c1-after.tsv`, gate sha256 `02b58f81…`) was a
   live-worktree reading of the gitignored wave dir. Restated by argv correction (cause `c973d1a`) to the
   base-revision reading, `findings=0` rc 0 over `checked_reports=94`. The capture revision `765fe8b` was
   also executed and rejected for the statement: it yields `findings=29`, all `LG-SEAT-UNCARRIED` against
   the r28-era lesson — a carry claim the row does not make.

3. **E06a/E06b/E08a agree** (`SCORECARD.md:22`, `SCORECARD.md:32`): `139` and `6` at `ed270c4`, `135` at
   `6cb22dc`, exits 0. No prior row names either cell (`grep -oE "SCORECARD\.md:(22|32)([^0-9]|$)"` → 0).

4. **Q76 sweep** (base `9c76c72:SCORECARD.md`): E05's cell is referenced by three `R29-CORRECTION
   SCORECARD.md:23` prose lines (295-297); none restates or corrects the fixture literals — line 297
   declares the line out of its committed-bytes scope ("not re-derived here"). E07/E06a/E06b/E08a cells:
   zero references. No item is AGREE-by-prior-correction.

## Deliveries

- `.ufo/waves/round-34/w1/deliver-c1-E05.md` — ITEM line, greps, cause `fec846d` with parent/cause/base
  readings, exact restatement row (argv correction: `… 2>/dev/null`).
- `.ufo/waves/round-34/w1/deliver-c1-E06a.md` — AGREE original, no row.
- `.ufo/waves/round-34/w1/deliver-c1-E06b.md` — AGREE original, no row.
- `.ufo/waves/round-34/w1/deliver-c1-E07.md` — ITEM line, greps, cause `c973d1a` with parent/cause/
  drift-probe/base readings, exact restatement row (measured revision moved to the r34 base).
- `.ufo/waves/round-34/w1/deliver-c1-E08a.md` — AGREE original, no row.

Notes for the L1: append both rows verbatim under `### Round 34 registry restatements` (they were
validated by the frozen counter against a simulated landing commit); no other file needs to move. No tool
installed or upgraded. Scratch `/fast/scratch/hyaku/souji-r34/RestateC1s6/` removed after the receipts
above were copied.
