# C1 delivery — E05 (SCORECARD.md:23, tests/fixtures/r28-wave-evidence-capture.sh)

Verdict: **MISMATCH at base → restatement by argv correction.** No value-drift cause exists (the frozen
predicate fails at the cause's parent too): the fixture writes its negative-case diagnostics to stderr
*after* the summary, and the counter reads `out+err`, so the last digit-bearing line was a stderr lane
path, then the usage banner (which carries the digit in `full40`).

## Counter ITEM line (verbatim, base)

```
ITEM	E05	MISMATCH	original	rc=0 expect_exit=0 predicate fails last=Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]] load=4.29
```

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

Exit 1 (`SUMMARY items=5 agree=3 mismatches=2`). Load `/proc/loadavg` before: `3.08 2.76 1.92`; after: `4.43 3.07 2.04`.
Counter bytes at `--list-rev`: sha256 `1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20`.
Lane HEAD at read time `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`; every measurement is at `--rev` /
the probe revision, never the lane worktree.

## Prior-correction / supersession grep (base `9c76c72:SCORECARD.md`)

```
grep -n -oE "SCORECARD\.md:23([^0-9]|$)" sc-base.md     → 295, 296, 297   (count=3)
```

All three are `R29-CORRECTION SCORECARD.md:23 …` prose lines. None restates or corrects the cell's
fixture literals: line 297 names the line ``fixture line `cases=6 pass=6 control=TAMPER-REJECTED` `` and
declares it out of its scope ("working-tree and tool-run claims and are not re-derived here from
committed bytes"). No correcting row binds the cell → **not AGREE under Q76**.
Related precedent, same artifact class: `R30-CORRECTION SCORECARD.md:314 R18 rc=0 observed=Usage: bash
tools/souji-wave-evidence-capture.sh …` followed by "the banner is refused as an observation" (base
lines 336 and 338).

## Cause (executed, parent vs cause)

Cause full40 **fec846dd1781a414ae3a7d71d2d8fa2fb17900eb** — *round-28: pin after measurements and source
recheck receipts*; `git blame -L 23,23 9c76c72 -- SCORECARD.md` names it, and it is the commit that wrote
the row's line: line-23 text present at the cause (1 occurrence) and absent at its parent (0).

Readings executed with the counter's own code path (private clone per run, scrubbed PATH/TMPDIR,
`GIT_CONFIG_NOSYSTEM=1`):

| rev | role | rc | predicate | last digit-bearing line (out+err) | load |
|---|---|---|---|---|---|
| `de478b483db66a8d8ff2d627cde1ccce6e21a014` | cause^1 | 0 | fails | `error: source directory not found: …/lane-2/.ufo/waves/round-26` | 21.61 |
| `fec846dd1781a414ae3a7d71d2d8fa2fb17900eb` | cause | 0 | fails | `error: source directory not found: …/lane-2/.ufo/waves/round-26` | 12.02 |
| `9c76c7222a8abff027af42e37f0d160d52526bba` | base/tip-of-scope, frozen argv | 0 | fails | `Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]]` | 4.29 |
| `9c76c7222a8abff027af42e37f0d160d52526bba` | base, corrected argv | 0 | — | `cases=15 pass=15 control=TAMPER-REJECTED` | 11.70 |

The predicate fails at the cause's **parent** as well, so no value-drift cause exists. The corrected argv
runs the row's own script and only drops the stderr diagnostics (`2>/dev/null`), so the run's last
digit-bearing line is the fixture's own summary: the r29 v2 layout prints `cases=15 pass=15` (the r28
six-case layout the row quotes is gone; the r33 row `| L38 | SCORECARD.md:314 | cases=15 pass=15 | run:
bash tests/fixtures/r28-wave-evidence-capture.sh |` already recorded the same run outcome).

## Proposed row (exact, for `### Round 34 registry restatements`)

```
| E05 | SCORECARD.md:23 | restated | 0 | `bash tests/fixtures/r28-wave-evidence-capture.sh 2>/dev/null` | `cases=15 pass=15 control=TAMPER-REJECTED` | fec846dd1781a414ae3a7d71d2d8fa2fb17900eb | the r28 fixture writes its negative-case diagnostics to stderr after the summary, so the counter's out+err last digit line was a lane-2 error path; stderr dropped, the same script's own summary binds (r29 v2 layout: 15 cases) |
```

## Simulation receipt (row verified end-to-end by the frozen counter)

Scratch clone `/fast/scratch/hyaku/souji-r34/RestateC1s6/sim/c` (origin removed, toplevel asserted),
`checkout -qf --detach 2b0171e…`, section + row appended, `SCORECARD.md` only, committed with the
throwaway identity `-c user.name=scratch -c user.email=scratch@invalid` → sim commit
`b54a50e95c0c3b5856290f038c209e6b186ac98c`.

```
ITEM	E05	AGREE	restated	rc=0 expect_exit=0 statement is the run's last digit-bearing line last=cases=15 pass=15 control=TAMPER-REJECTED load=18.44
SUMMARY items=5 agree=5 mismatches=0 restated=2 partial=1 rev=b54a50e95c0c3b5856290f038c209e6b186ac98c
```
