# C1 delivery — G12 (SKILL.md:236 as frozen, `tests/fixtures/r21-read-root.py` + `tools/souji-seat-audit.py`)

Verdict: **AGREE at base and at the tip. No restatement row needed.**

## Counter ITEM lines (verbatim)

Base `9c76c7222a8abff027af42e37f0d160d52526bba`:

```
ITEM	G12	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=32 pass=32 fail=0 base_discriminating=14 load=7.83
```

Tip `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`:

```
ITEM	G12	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=32 pass=32 fail=0 base_discriminating=14 load=56.12
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
Loads recorded beside each ITEM line as printed above. The `{BLOB:6ff3413b…:tools/souji-seat-audit.py}`
substitution resolved (the item agreed, so `git show` extraction succeeded at the measured revision).

## Prior-correction / supersession grep (base `9c76c72:SCORECARD.md`)

```
grep -c -F 'G12' sc-base.md                                -> 0
grep -c -F 'SKILL.md:236' sc-base.md                       -> 0
grep -n -F 'read-root' sc-base.md                          -> 440, 441
```

Lines 440/441 are the r33 `N06`/`N07` rows for `SCORECARD.md:159`, citing
`census/round-21/oracle-acceptance.json` (produced by `count-read-root.py`). Neither restates nor
binds the r21-read-root fixture row; the `read-root` string match is the unrelated counter name.

`where` note for the record: frozen as `SKILL.md:236`, the r21-read-root row is on line 237.
