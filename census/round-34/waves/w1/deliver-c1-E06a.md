# C1 delivery — E06a (SCORECARD.md:22, corpus/SOURCES.md at ed270c4)

Verdict: **AGREE at base — no restatement row drafted.**

## Counter ITEM line (verbatim, base)

```
ITEM	E06a	AGREE	original	rc=0 expect_exit=0 predicate holds last=139 load=4.29
```

Measured argv: `bash -c "grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md"`
run at `ed270c42161cd62829783a5e5d2ef4e27089331c`; the run's last digit-bearing line `139` matches the
frozen predicate `^139$` and the stated exit 0.

## Command (executed)

```
export TMPDIR=/fast/scratch/hyaku/souji-r34/RestateC1s6/tmp
flock -w 1800 /fast/scratch/hyaku/souji-r34/RestateC1s6/run.lock \
 python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
  --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
  --scratch /fast/scratch/hyaku/souji-r34/RestateC1s6/cnt --only E05,E06a,E06b,E07,E08a
```

Exit 1 for the slice (`mismatches=2`, both outside this item). Load before: `3.08 2.76 1.92`; after:
`4.43 3.07 2.04`. Counter bytes at `--list-rev`: sha256 `1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20`.

## Prior-correction / supersession grep (base `9c76c72:SCORECARD.md`)

```
grep -n -oE "SCORECARD\.md:22([^0-9]|$)" sc-base.md     → count=0
```

No correcting row binds the cell; none is needed — the item agrees on the base reading.

## Cause

Not applicable (AGREE original). No cause walk, no parent/tip executions, no corrected argv.

## Proposed row

None.
