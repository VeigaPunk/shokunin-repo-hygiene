# C1 delivery — E19 (SCORECARD.md:101, tools/souji-record-agreement.py)

Verdict: **AGREE at base — no restatement row drafted.**

## Counter ITEM line (verbatim)

```
ITEM	E19	AGREE	original	rc=0 expect_exit=0 predicate holds last=keys=4 records=4 occurrences=17 mismatches=0 load=5.87
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

Exit 0. Load before/after: `3.94 3.11 2.10` / `5.87 3.52 2.24`. Serialization: counter's own Q77 flock at `<scratch>/c1.lock`.
Counter bytes at `--list-rev`: sha256 `1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20`.
Lane HEAD at read time: `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`.

## Rendered row state at base

`git -C <lane> show 9c76c72:SCORECARD.md | sed -n '101p'` → the `### Round 23 measurements` row
`| C1 record agreement | calibration 7 | ...`, whose after-cell reads
`mismatches=0` at the landing tip (`census/round-23/records/agreement-after.tsv`, `rev=eb1aa497…`) with `--no-worktree`, and
whose counting command is `python3 -B tools/souji-record-agreement.py --rev <full40> --no-worktree`
(written out at r21/r23 as the frozen item argv with `--rev eb1aa49783ae4a0d42e062aa5a61e49a91b0f76a`).
The run's exit is 0 and its last digit-bearing line is exactly the frozen statement.

Note on stability: the argv pins the measured revision (`--rev eb1aa497…`) and the tool reads committed bytes at that
revision, so the reading is insensitive to the checkout the clone is at; only the tool bytes at `--rev` could change it.

## Prior-correction / supersession sweep (Q76)

```
grep -n 'souji-record-agreement' <base SCORECARD.md>                     → 101 (the row itself), 173 (a capability row)
grep -n -F 'keys=4 records=4 occurrences=17 mismatches=0' <base SCORECARD.md> → no match (no correction row restates it)
grep -n -F 'SCORECARD.md:101' <base SCORECARD.md>                        → no match
grep -n '^| E1[6789]' <base SCORECARD.md>                                → no match
```

No prior correction, supersession or binding row names or restates this cell; the AGREE is a direct measurement.

## Cause commit

Not applicable: frozen (exit 0, predicate `keys=4 records=4 occurrences=17 mismatches=0`) holds at `--rev`; Q75's cause
machinery is not engaged and no cause full40 is claimed.

## Proposed restatement row

None. Item agrees.
