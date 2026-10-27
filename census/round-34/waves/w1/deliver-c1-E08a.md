# C1 delivery — E08a (SCORECARD.md:32, corpus/SOURCES.md at 6cb22dc)

Verdict: **AGREE at base — no restatement row drafted.**

## Counter ITEM line (verbatim, base)

```
ITEM	E08a	AGREE	original	rc=0 expect_exit=0 predicate holds last=135 load=4.43
```

Measured argv: `bash -c "grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md"`
run at `6cb22dc20c9fdb3c7a49eaa1accabca339054c17`; the run's last digit-bearing line `135` matches the
frozen predicate `^135$` and the stated exit 0. (Distinct cell from E06a: pinned at the round-27 close,
`135` rows, versus `139` at the round-28 close.)

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
grep -n -oE "SCORECARD\.md:32([^0-9]|$)" sc-base.md     → count=0
```

No correcting row binds the cell; none is needed — the item agrees on the base reading.

## Cause

Not applicable (AGREE original). No cause walk, no parent/tip executions, no corrected argv.

## Proposed row

None.
