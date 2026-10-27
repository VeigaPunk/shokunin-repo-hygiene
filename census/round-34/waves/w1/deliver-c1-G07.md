# C1 delivery — G07 (SKILL.md:222 as frozen, `tests/fixtures/r18-census-bounded.py` + `tools/souji-census.sh`)

Verdict: **AGREE at base and at the tip. No restatement row needed.**

## Counter ITEM lines (verbatim)

Base `9c76c7222a8abff027af42e37f0d160d52526bba`:

```
ITEM	G07	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=12 failed=0 load=6.94
```

Tip `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`:

```
ITEM	G07	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=12 failed=0 load=55.00
```

## Command (executed)

```
export TMPDIR=/fast/scratch/hyaku/souji-r34/RestateC1s2/tmp
flock /fast/scratch/hyaku/souji-r34/RestateC1s2/ser.lock \
  python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
  --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
  --scratch /fast/scratch/hyaku/souji-r34/RestateC1s2/cnt --only G05,G07,G09,G11,G12
```

and the same with `--rev 51acb5fb6fa38a6b593b3badb674cec559d7eb2c --scratch …/cnt4 --only G07,G09,G12`.
Loads recorded beside each ITEM line as printed above (`/proc/loadavg` before the base run
`2.84 2.72 1.92`; before the tip run `32.11 18.50 9.05`).

## Prior-correction / supersession grep (base `9c76c72:SCORECARD.md`)

```
grep -c -F 'G07' sc-base.md                                -> 0
grep -c -F 'SKILL.md:222' sc-base.md                       -> 0
grep -c -F 'census-bounded' sc-base.md                     -> 0
grep -c -F 'Round 34 registry restatements' sc-base.md     -> 0
```

No prior correction binds the cell; not needed, the item agrees on its original (exit, predicate).

`where` note for the record: frozen as `SKILL.md:222`, the r18-census-bounded row is on line 223
(`SKILL.md:222` is the r17-transcript-manifest row). Irrelevant to an agreeing item — the mounted
argv is the frozen one and the counter reads `where` only for restatement rows.
