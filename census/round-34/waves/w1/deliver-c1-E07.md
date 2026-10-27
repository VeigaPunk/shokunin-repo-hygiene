# C1 delivery — E07 (SCORECARD.md:31, tools/souji-landing-gate.py)

Verdict: **MISMATCH at base → restatement by argv correction.** The freeze's stated exit (2) matches, but
the predicate never holds: the gate reads seat reports from the `--rev` tree, and the row's revision
`6cb22dc…` predates the committed round-27 report capture (`census/round-27/waves/`, added at `765fe8b`).
No value-drift cause exists — the frozen predicate fails at the row-writing commit **and at its parent**.

## Counter ITEM line (verbatim, base)

```
ITEM	E07	MISMATCH	original	rc=2 expect_exit=2 predicate fails last=COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-27/ or census/round-27/waves/ at 6cb22dc20c9fdb3c7a49eaa1accabca339054c17 load=4.43
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

Exit 1 (`SUMMARY items=5 agree=3 mismatches=2`). Load before: `3.08 2.76 1.92`; after: `4.43 3.07 2.04`.
Counter bytes at `--list-rev`: sha256 `1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20`.

## Prior-correction / supersession grep (base `9c76c72:SCORECARD.md`)

```
grep -n -oE "SCORECARD\.md:31([^0-9]|$)" sc-base.md     → count=0
```

No correction, supersession or binding row names this cell. The only rows citing `findings=2` are the
three round-27 measurement rows themselves (base lines 31-33). → **not AGREE under Q76.**

## Cause (executed, parent vs cause)

Cause full40 **c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0** — *round-27: record measured claims and honest
stop*; `git blame -L 31,31 9c76c72 -- SCORECARD.md` names it. Line-31 text present at the cause (1) and
absent at its parent (0). The cause's parent is the measured revision itself (`6cb22dc…`).

Readings executed with the counter's own code path (private clone per run, scrubbed PATH/TMPDIR,
`GIT_CONFIG_NOSYSTEM=1`):

| rev | role | rc | predicate | last digit-bearing line (out+err) | load |
|---|---|---|---|---|---|
| `6cb22dc20c9fdb3c7a49eaa1accabca339054c17` | cause^1 | 2 | fails | `COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-27/ at 6cb22dc…` | 21.61 |
| `c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0` | cause | 2 | fails | `COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-27/ at 6cb22dc…` | 8.33 |
| `68447afef62e4761249af55a2467657f04046537` | r30 gate (drift probe) | 2 | fails | `… under .ufo/waves/round-27/ or census/round-27/waves/ at 6cb22dc…` | 13.13 |
| `8024b540b04d677d47cf51a0d1132ec8705ef14a` | r31 gate (drift probe) | 2 | fails | `… under .ufo/waves/round-27/ or census/round-27/waves/ at 6cb22dc…` | 13.13 |
| `9c76c7222a8abff027af42e37f0d160d52526bba` | base/tip-of-scope, frozen argv | 2 | fails | same COULD-NOT-EVALUATE line | 4.43 |
| `9c76c7222a8abff027af42e37f0d160d52526bba` | base, corrected argv | 0 | — | `SUMMARY findings=0 checked_reg=76 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=29 status_lines=79 carry_heading=1 checked_reports=94` | 12.19 |

The predicate fails at the cause's parent too, and no gate-era commit makes it hold, so value drift is
ruled out by execution: the row's `findings=2 rc 2` was a live-worktree reading of the gitignored
`.ufo/waves/round-27/` reports (its receipt `census/round-27/records/c1-after.tsv` pins gate sha256
`02b58f81…`, findings 2, rc 2), not a committed-bytes reading. The corrected argv keeps the row's own
script and question (landing gate, round 27) and moves the measured revision to the r34 base, the tip the
whole round measures; there the committed capture (`checked_reports=94`) verifies with `findings=0` rc 0.
The alternative capture revision `765fe8b` was executed and rejected as the restatement: it yields
`findings=29`, all `LG-SEAT-UNCARRIED` against the r28-era lesson, a carry claim the row does not make.

## Proposed row (exact, for `### Round 34 registry restatements`)

```
| E07 | SCORECARD.md:31 | restated | 0 | `python3 -B tools/souji-landing-gate.py --root . --rev 9c76c7222a8abff027af42e37f0d160d52526bba --round 27 --fleet-root /home/vgpnk/Projects/shokunin` | `SUMMARY findings=0 checked_reg=76 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=29 status_lines=79 carry_heading=1 checked_reports=94` | c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0 | 6cb22dc predates the committed round-27 report capture (added 765fe8b), so the gate has no reports to read at the row revision; measured at the r34 base it reports findings=0 rc 0 |
```

## Simulation receipt (row verified end-to-end by the frozen counter)

Same scratch clone/commit as the slice (`b54a50e95c0c3b5856290f038c209e6b186ac98c`, `SCORECARD.md` only):

```
ITEM	E07	AGREE	restated	rc=0 expect_exit=0 statement is the run's last digit-bearing line last=SUMMARY findings=0 checked_reg=76 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=29 status_lines=79 carry_heading=1 checked_reports=94 load=19.60
SUMMARY items=5 agree=5 mismatches=0 restated=2 partial=1 rev=b54a50e95c0c3b5856290f038c209e6b186ac98c
```
