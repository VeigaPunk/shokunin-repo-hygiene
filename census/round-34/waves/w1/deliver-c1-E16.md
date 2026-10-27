# C1 delivery — E16 (SCORECARD.md:69, tests/fixtures/r24-receipt-verify.py + tools/souji-receipt-run.py)

Verdict: **AGREE at base — no restatement row drafted.**

## Counter ITEM line (verbatim)

```
ITEM	E16	AGREE	original	rc=0 expect_exit=0 predicate holds last=cases=8 pass=8 refusals=2/2 regress=5/5 load=3.94
```

## Command (executed)

```
export TMPDIR=/fast/scratch/hyaku/souji-r34/RestateC1s9/tmp
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
  --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
  --scratch /fast/scratch/hyaku/souji-r34/RestateC1s9/cnt --only E16,E17a,E17b,E18,E19
```

Exit 0. Load `/proc/loadavg` before/after: `3.94 3.11 2.10` / `5.87 3.52 2.24`.
Serialization is the counter's own frozen Q77 lock at `<scratch>/c1.lock` (fcntl.LOCK_EX, taken before any item runs);
the invocation above is the exact one executed, with `TMPDIR` set by hand as required.
Counter bytes at `--list-rev`: sha256 `1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20`.
Lane HEAD at read time: `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`; the measurement is at `--rev` (the counter clones from `--rev`).

## Rendered row state at base

`git -C <lane> show 9c76c72:SCORECARD.md | sed -n '69p'` → the `### Round 24 measurements` row
`| C3 receipt verify/run symmetry | operability 8 | ...`, whose after-cell reads
`cases=8 pass=8 control=FALSE-GREEN-REJECTED`, rc 0 (`census/round-24/records/c3-after.tsv`, `rev=778747eb…`), and whose
counting command is `python3 -B tests/fixtures/r24-receipt-verify.py --tool tools/souji-receipt-run.py --lane-roo…`.
The run's exit is 0 and its last digit-bearing line is `cases=8 pass=8 refusals=2/2 regress=5/5`, matching the frozen item.

## Prior-correction / supersession sweep (Q76)

```
grep -n -F 'SCORECARD.md:69' <base SCORECARD.md>            → no match
grep -n 'refusals=2/2 regress=5/5' <base SCORECARD.md>      → 69 (the row itself only)
grep -n 'r24-receipt-verify' <base SCORECARD.md>            → 69 (the row itself only)
grep -n '^| E1[6789]' <base SCORECARD.md>                   → no match (no r34 ledger row exists at base or list-rev)
```

No prior correction, supersession or binding row names this cell; the AGREE is a direct measurement, not a Q76 carry.

## Cause commit

Not applicable: the item's frozen (exit 0, predicate `cases=8 pass=8 refusals=2/2 regress=5/5`) holds at `--rev`, so
Q75's cause machinery is not engaged and no cause full40 is claimed.

## Proposed restatement row

None. Item agrees.
