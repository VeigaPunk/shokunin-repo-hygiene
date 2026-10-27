# SwarmScribe34 — round 34 w1, Mistakes-row draft

## Status

STATUS: PASS — three `## Mistakes` rows drafted in the lesson table shape at `.ufo/waves/round-34/w1/deliver-mistakes.md`, each carrying a committed location, a named captured-by criterion (or `none`) and a named red-before state; no counter was run and no lane artifact other than these two wave-dir files was written.

## Evidence

Revisions: base `9c76c7222a8abff027af42e37f0d160d52526bba`; content freeze `2b591924f607940febbb99f922cc9bb090508eb6`; re-pinned `--list-rev` `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`; lane master / HEAD at read time `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`.

1. Ref sweep for attempt-1's instrument bytes (every ref, including `refs/jj/keep/*`):

```
$ git -C <lane> log --all --format='%H %ad %s' --date=short -- census/round-34/c1-counter.py
2b591924f607940febbb99f922cc9bb090508eb6 2026-10-26 round-34: freeze — preregistration (attempt 2, amendments A1-A4), C1/C2 counters, ...
3cc0733db4a661aae48a352dc9e26867f5df7d6d 2026-10-26
bf49f569f7e3b482ca45c44aefdad55093020332 2026-10-26
```
`c2-counter.py` adds `2b0171e`, `4492934`, `73f029e`, `b0f9500` — all attempt-2 lineage.

2. Those two earlier commits carry the attempt-2 bytes, not attempt-1's:

```
$ git -C <lane> diff --name-status bf49f56 2b59192
A	census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc
```
Only a deleted pyc differs; every `census/round-34/` and `tests/fixtures/` path is byte-identical to the freeze. No reachable commit carries a pre-amendment counter.

3. The committed record of both defects is the amendment log, `sed -n '133,175p' census/round-34/preregistration.txt`: A1 at `:138-147`, A2 at `:148-154`, A3 at `:155-156` ("attempt 1 died before writing it").

4. Repaired code pins (working tree = HEAD): `census/round-34/c1-counter.py:194,235,301` (argv override threaded through `run_item`/`holds`), `:268` (`BAD-ROW(argv correction names no row file)`), `:311-313` (statement must equal the collapsed last digit-bearing line); `census/round-34/c2-counter.py:56-63` (`validate_legs` refusals), `:237-255` (selftest: good set accepted, both bad sets refused, fail branches at `:245` and `:252`).

5. Committed receipts, all at `51acb5f` — `census/round-34/records/junk-c1.txt` (`cases=3 pass=3 control=STUB-REJECTED`; `BAD-ROW(argv correction names no row file)`; `statement is not the run's last digit-bearing line`); `feasibility-final.txt` (leg G3 PASS printing `SELFTEST pass witness-required rejected junk-only rejected`, rev `60def78d16017be528ba6b439e350918587cb80b`, `SUMMARY legs=13 pass=9 fail=4 harm=0`); `controls.txt` (C1 do-nothing `agree=35 mismatches=25`).

6. r33 lesson (`sed -n '71p;76p' corpus/lessons/round-33.md`): `:76` records 37 attack items built and not dispatched and 48 seats against the 64-seat floor; `:71` carries the 37 items to r34. Its `## Mistakes` rows sit at `:41-45` and contain none of these.

7. Criteria read at HEAD: `corpus/QUALITY.md` Q70 ("must reach the item-level target under every frozen counter version"), Q78 ("every item's full call tree runs once under the frozen measurement conditions"), Q71-Q77 for context.

8. Pointer durability: `git cat-file -e HEAD:.ufo/waves/round-33/make-spec-w2.py` → rc 128; `git check-ignore -v .ufo/waves/round-33/make-spec-w2.py` → `.gitignore:1:.ufo/waves/`.

9. Wave snapshot at read time: `ls -a .ufo/waves/round-34/` → `make-spec-w1.py w1 w1-dispatch.json w1-render.out w1-run.err w1-spec.json w1.ready w1.ready.dispatched` (no `w2.ready`).

No scratch directory was created and no tool was installed: the draft needs no clone and no fixture run, so nothing was removed at the end.

## Findings

1. **The red-before of both attempt-1 fixes is amendment-log-only.** Attempt-1's counters are not reachable from any ref (Evidence 1-2), so no command can reproduce `SELFTEST fail` or an ignored argv override; the rows cite `census/round-34/preregistration.txt:138-154` and say so instead of implying a runnable witness. A reproducible red arm would be a *receipt for the landed fix*, not a predicate change: a stub counter whose `validate_legs` accepts a junk-only set must then print `SELFTEST fail (junk-only accepted)` (`census/round-34/c2-counter.py:252`, a branch the landed selftest already has).
2. **Captured-by split inside candidate (a).** M1 is Q70(a) (the frozen counter version could not reach `agree=60` by honest work — a reachability defect), M2 is Q78 (G3's call tree is the counter's own `--selftest`, never dry-run before the freeze). If the L1 wants one criterion across both, Q70(a) covers both; the draft names the sharper one per row so the lesson records the mechanism, not a blanket.
3. **M3 is a mining, not a duplicate.** The r33 conformance defect is reported in `## Wave` and `## Residuals` (`corpus/lessons/round-33.md:71,76`) and never as a `## Mistakes` row (`:41-45`), and no Q70-Q78 clause binds a round's dispatch count or its planned wave to execution — hence captured-by `none`, which is the criterion gap the row records.
4. **Do not point M3 at the r33 wave-2 spec file.** `corpus/lessons/round-33.md:71` names `.ufo/waves/round-33/make-spec-w2.py`, which is gitignored (`.gitignore:1`) and absent at HEAD (`git cat-file -e` rc 128); the draft cites the lesson lines only, so the r34 row adds no unresolvable pointer (Q31, Q65).
5. **M3's r34 side is prospective.** At read time `.ufo/waves/round-34/` holds `w1.ready`/`w1.ready.dispatched` and no `w2.ready`; the two-wave fix can only be claimed conforming after w2 is built and dispatched. Observed state, not a defect, and recorded as such in the row.
6. **Class mapping for integration.** Candidate (a) yields M1 `vacuous` + M2 `landing` (the composite label the seat spec gives); candidate (b) yields M3 `conformance`. A one-row merge of M1+M2 is possible but would put two mechanisms and two red-befores in one cell pair.

## Deliveries

- `.ufo/waves/round-34/w1/deliver-mistakes.md` — the three rows in the `corpus/lessons/round-33.md:39` table shape, plus the class mapping, the limits that shaped the wording and one-line justifications per row.
- `.ufo/waves/round-34/w1/SwarmScribe34.md` — this report.
