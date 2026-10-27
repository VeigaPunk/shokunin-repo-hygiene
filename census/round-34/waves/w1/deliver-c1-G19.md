# deliver-c1-G19 (SKILL.md:243, r22-mutation-adequacy mutants=59 killed=52 survived=7)

Seat: SwarmExecutor04 (C1 slice 4/12). Base 9c76c7222a8abff027af42e37f0d160d52526bba; --list-rev
2b0171e2071fdc9c16a69bed12b0d040e574d8c8.

## Status

STATUS: PASS (AGREE at base; no restatement needed, no row drafted).

## Counter ITEM line

    python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
      --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
      --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
      --scratch /fast/scratch/hyaku/souji-r34/RestateC1s4/cnt --only G19

    ITEM	G19	AGREE	original	rc=0 expect_exit=0 predicate holds last="survived": 7 load=4.22

(load beside the reading: `4.20 3.14 2.10` after the batch SUMMARY.)

## Prior-correction grep (informational for an AGREE item)

`git show 9c76c72:SCORECARD.md` -> no match for `mutation-adequacy` or `59-mutant`; `mutants` matches only
line 414 (round-31 C3 row prose, "L13's two remover-subtraction mutants"), which is not a binding of this
SKILL cell.

## Cause / proposed row

None: the frozen (exit 0, `ANYLINE:"mutants": 59 && ANYLINE:"killed": 52 && ANYLINE:"survived": 7`) holds at
the measured revision.

## Deliveries

This file only.
