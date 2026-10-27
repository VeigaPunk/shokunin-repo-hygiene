# C1 delivery — E17a (SCORECARD.md:70, tools/souji-gate-check.py)

Verdict: **AGREE at base — no restatement row drafted.**

## Counter ITEM line (verbatim)

```
ITEM	E17a	AGREE	original	rc=0 expect_exit=0 predicate holds last=entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0 load=3.94
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
Serialization is the counter's own frozen Q77 lock at `<scratch>/c1.lock`; the invocation above is the one executed.
Counter bytes at `--list-rev`: sha256 `1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20`.
Lane HEAD at read time: `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`.

## Rendered row state at base

`git -C <lane> show 9c76c72:SCORECARD.md | sed -n '70p'` → the `### Round 24 measurements` row
`| assimilation (rides inside C1; no claim slot) | coverage 8 | ...`, whose after-cell reads
gate `entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0` (`census/round-24/records/gate-check-r24-entry.tsv`) and whose
counting command is the frozen item argv `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 …`.
The run's exit is 0 and its last digit-bearing line equals the frozen statement.

## Prior-correction / supersession sweep (Q76)

```
grep -n -F 'SCORECARD.md:70' <base SCORECARD.md>                       → no match
grep -n 'slice_verdicts=8 slice_total=8 fail=0' <base SCORECARD.md>    → 22, 70, 305 (70 = the row itself; 22/305 are other rows)
grep -n 'souji-gate-check' <base SCORECARD.md>                         → 32, 70, 103 (no correction row)
grep -n '^| E1[6789]' <base SCORECARD.md>                              → no match
```

No prior correction, supersession or binding row names this cell; the AGREE is a direct measurement, not a Q76 carry.

## Cause commit

Not applicable: the frozen (exit 0, predicate `entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0`) holds at `--rev`;
Q75's cause machinery is not engaged and no cause full40 is claimed.

## Proposed restatement row

None. Item agrees.
