# C1 slice 10/12 — E22 (SCORECARD.md:303, C1 registry/record agreement, r29)

STATUS: AGREE — no restatement row.

## Counter reading (base, flock)
```
$ flock /fast/scratch/hyaku/souji-r34/RestateC1s10/run.lock python3 -B census/round-34/c1-counter.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
    --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
    --scratch /fast/scratch/hyaku/souji-r34/RestateC1s10/cnt --only E22
ITEM	E22	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY k1=0 k2=0 mismatches=0 rev=1dc678500c92164b0b2bea82b934dd03d1dfbf38 load=5.87
```
`/proc/loadavg`: `4.20 3.14 2.10 6/4401 3888188` (start), `5.87` load at the E22 line.
Item: exit 0, pred `SUMMARY k1=0 k2=0 mismatches=0`, files `tools/souji-registry-agreement.py`,
at `{REV}`, argv `python3 -B tools/souji-registry-agreement.py --root . --rev
1dc678500c92164b0b2bea82b934dd03d1dfbf38 --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804`.
The argv is already revision-pinned, so the reading is stable at any measured revision.

## Prior-correction check (Q76)
```
$ git -C <lane> grep -n 'SCORECARD.md:303' 9c76c7222a8abff027af42e37f0d160d52526bba -- .
census/round-33/waves/w1/deliver-c1-enumeration-misses.md:35:| E22 | SCORECARD.md:303 (r29 measurements) | ...
```
Only the r33 enumeration deliverable; no correction/restatement row binds the cell.

## Cause
None needed (AGREE at the base revision).

## Proposed row
None.
