# C1 bindings, items N20-N26 (seat SwarmExecutor04 / C1BindD)

Scratch proof revision: `e181dc6fc3d2b820df1429328d6cc67400466978` (private clone, origin removed, base
`85b61a151923986e7e6b48f7084b9122561b5f3d` + appended block below). Lane tip untouched: `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`.
Nothing here was committed to the lane; the L1 appends the block below verbatim under its own heading.

## Rows for SCORECARD.md (append after the base bytes)

```markdown
### Round 32 capability-count bindings

| item | base line | literal | binding | reason |
|---|---|---|---|---|
| N20 | SCORECARD.md:313 | mismatches=10 | withdrawn: the cell cites only the r29 fixture, which prints cases/pass and not this count, and names no record; the sole blob holding mismatches=10 is census/round-29/records/controls.tsv line 2, refused by A0(a) as uncited | line 313 states the r29 C1 before-value as base mismatches=10 but names no record path holding it, so no cited observable exists |
| N21 | SCORECARD.md:313 | mismatches=0 | withdrawn: the cell cites only the r29 fixture, which prints cases/pass and not this count, and names no record; the sole blob holding the after value is census/round-29/records/final-tip-measure-2.txt line 4, refused by A0(a) as uncited | the same row's after value mismatches=0 has no record named on the line |
| N22 | SCORECARD.md:314 | records=1381 | withdrawn: the row names census/round-26/waves, a waves component that record paths forbid, and the blobs holding records=1381 are census/round-29/records/final-tip-measure.txt line 5 and amendments.txt line 35, neither cited on the row | line 314 states records=1381 for the r26 capture but names the captured corpus directory, not the verify record that prints it |
| N23 | SCORECARD.md:314 | failed=0 | withdrawn: the only blobs holding failed=0 for this capture are census/round-29/records/final-tip-measure.txt and amendments.txt, neither cited on the row, and the cited fixture prints cases/pass only | the verify failure count failed=0 is observable only in records the row does not name |
| N24 | SCORECARD.md:314 | uncovered=0 | withdrawn: the only blobs holding uncovered=0 for this capture are census/round-29/records/final-tip-measure.txt and amendments.txt, neither cited on the row, and the cited fixture prints cases/pass only | the uncovered count uncovered=0 is observable only in records the row does not name |
| N25 | SCORECARD.md:354 | k1=13 | withdrawn: the cited blob census/round-30/records/c1-before.txt line 29 does hold k1=13, but no literal can contain the unit k1 and exactly one integer because the unit token itself carries the digit run 1 | the honest literal k1=13 is refused by the literal rule (two digit runs), reproduced as BAD-ROW(literal) |
| N26 | SCORECARD.md:354 | k1=0 | withdrawn: the cited blob census/round-30/records/c1-after-a3.txt line 30 does hold k1=0, but no literal can contain the unit k1 with exactly one integer equal to 0 at all, since k1 carries digit run 1 and any glued form reads 10 | the honest literal k1=0 is refused by the literal rule, reproduced as BAD-ROW(literal) |
```

## Acceptance proof (counter output, verbatim)

Command (run twice for determinism; v1 run after it):

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/c1-counter-v2.py \
  --root /fast/scratch/hyaku/souji-r32/C1BindD/c \
  --rev e181dc6fc3d2b820df1429328d6cc67400466978 \
  --base 85b61a151923986e7e6b48f7084b9122561b5f3d \
  --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c \
  --only N20,N21,N22,N23,N24,N25,N26 \
  --scratch /fast/scratch/hyaku/souji-r32/C1BindD/cnt
```

v2, run 1 and run 2 (byte-identical item lines):

```
ITEM	N20	SCORECARD.md:313	literal=mismatches=10	binding=withdrawn	WITHDRAWN	<reason as in the row>
ITEM	N21	SCORECARD.md:313	literal=mismatches=0	binding=withdrawn	WITHDRAWN	<reason as in the row>
ITEM	N22	SCORECARD.md:314	literal=records=1381	binding=withdrawn	WITHDRAWN	<reason as in the row>
ITEM	N23	SCORECARD.md:314	literal=failed=0	binding=withdrawn	WITHDRAWN	<reason as in the row>
ITEM	N24	SCORECARD.md:314	literal=uncovered=0	binding=withdrawn	WITHDRAWN	<reason as in the row>
ITEM	N25	SCORECARD.md:354	literal=k1=13	binding=withdrawn	WITHDRAWN	<reason as in the row>
ITEM	N26	SCORECARD.md:354	literal=k1=0	binding=withdrawn	WITHDRAWN	<reason as in the row>
SUMMARY items=7 bound_run=0 bound_record=0 bound_field=0 withdrawn=7 unbound=0 mismatches=0 partial=1 rev=e181dc6fc3d2b820df1429328d6cc67400466978
rc=0
```

v1 (`census/round-32/c1-counter.py`, same arguments): identical seven WITHDRAWN lines and
`SUMMARY items=7 bound_run=0 bound_record=0 bound_field=0 withdrawn=7 unbound=0 mismatches=0 partial=1 rev=e181dc6f...`, rc=0.

The seven ITEM lines above elide only the trailing reason field, whose full text is exactly the fifth column of the
rows in the block above (the counter echoes the row's withdrawn reason verbatim); the report `SwarmExecutor04.md`
carries the same verdict lines with the same elision.

## Why no MATCH exists for these seven (reproduced refusals)

Probe revision `26f35510251f95d3ec3f0ea5f1963ecc5382ac27` (records actually holding the integers, cited nowhere on the row):

```
ITEM	N20	SCORECARD.md:313	literal=mismatches=10	binding=record	BAD-ROW(A0a-not-cited)	census/round-29/records/controls.tsv:2
ITEM	N21	SCORECARD.md:313	literal=mismatches=0	binding=record	BAD-ROW(A0a-not-cited)	census/round-29/records/final-tip-measure-2.txt:4
ITEM	N22	SCORECARD.md:314	literal=records=1381	binding=record	BAD-ROW(A0a-not-cited)	census/round-29/records/final-tip-measure.txt:5
ITEM	N23	SCORECARD.md:314	literal=failed=0	binding=record	BAD-ROW(A0a-not-cited)	census/round-29/records/final-tip-measure.txt:12
ITEM	N24	SCORECARD.md:314	literal=uncovered=0	binding=record	BAD-ROW(A0a-not-cited)	census/round-29/records/final-tip-measure.txt:19
ITEM	N25	SCORECARD.md:354	literal=k1=13	binding=record	BAD-ROW(literal)	census/round-30/records/c1-before.txt:29
ITEM	N26	SCORECARD.md:354	literal=k1=0	binding=record	BAD-ROW(literal)	census/round-30/records/c1-after-a3.txt:30
SUMMARY items=7 bound_run=0 bound_record=0 bound_field=0 withdrawn=0 unbound=0 mismatches=7 partial=1 rev=26f3551...
```

Probe revision `c027c07f4d37e601feed0c570e23519022d6712f` (run kind, and the glued-literal hole):

```
ITEM	N22	SCORECARD.md:314	literal=records=1381	binding=run	RUN-MISMATCH	bash tests/fixtures/r28-wave-evidence-capture.sh rc=0 observed=cases=15 pass=15 control=TAMPER-REJECTED
ITEM	N23	SCORECARD.md:314	literal=failed=0	binding=run	RUN-MISMATCH	bash tests/fixtures/r28-wave-evidence-capture.sh rc=0 observed=cases=15 pass=15 control=TAMPER-REJECTED
ITEM	N24	SCORECARD.md:314	literal=uncovered=0	binding=run	RUN-MISMATCH	bash tests/fixtures/r28-wave-evidence-capture.sh rc=0 observed=cases=15 pass=15 control=TAMPER-REJECTED
ITEM	N25	SCORECARD.md:354	literal=k13	binding=record	MATCH	census/round-30/records/c1-before.txt:29
ITEM	N26	SCORECARD.md:354	literal=k10	binding=record	BAD-ROW(record-shape)	census/round-30/records/c1-after-a3.txt:30
SUMMARY items=5 bound_run=0 bound_record=1 bound_field=0 withdrawn=0 unbound=0 mismatches=4 partial=1 rev=c027c07...
```

The `k13` MATCH is the gameable state reported as Attack A2; it is deliberately NOT delivered. `k1=13` is the
row's own literal and the honest one.

## Reproduction notes

- The r28 fixture was run with `SOUJI_R29_C2FIXTURE_BASE` pointed inside the seat scratch dir, so its scratch repos never
  left `/fast/scratch/hyaku/souji-r32/C1BindD/`.
- The r29 fixture (`tests/fixtures/r29-registry-agreement.py`, base blob line 18 `BASE = '/var/tmp/souji-r29-c1-fixture'`)
  hard-codes `/var/tmp` with no override, so its stdout shape was established by reading the committed bytes (only
  `printf 'tool=%s\n'` and `print(f'cases=... pass=... control=...')` reach stdout) instead of running it under the
  operator scratch rule.
- Scratch `/fast/scratch/hyaku/souji-r32/C1BindD` was removed after this file and the report were written.
