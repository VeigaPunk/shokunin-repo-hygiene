# SwarmExecutor10 — round 34 w1, C1 slice 10/12 (items E20, E21, E22, E23a, E23b)

STATUS: PARTIAL — three items agree at the base as frozen; E23a is stale with one *validated*
restatement row (argv pin); E23b is stale and has **no** rule-conforming restatement (attack filed).

## Evidence

All readings executed under `flock /fast/scratch/hyaku/souji-r34/RestateC1s10/run.lock`, lane run
with `python3 -B`, everything else in scratch; `/proc/loadavg` recorded beside every reading.
Round-34 freeze read first: `census/round-34/preregistration.txt` (2b0171e2…), then the counter
docstrings and `census/round-34/c1-items.tsv`.

Frozen counter, all five items at the base revision:
```
$ flock .../run.lock python3 -B census/round-34/c1-counter.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
    --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
    --scratch /fast/scratch/hyaku/souji-r34/RestateC1s10/cnt --only E20,E21,E22,E23a,E23b
ITEM	E20	AGREE	original	rc=0 expect_exit=0 predicate holds last=5 load=3.94
ITEM	E21	AGREE	original	rc=0 expect_exit=0 predicate holds last=entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0 load=3.94
ITEM	E22	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY k1=0 k2=0 mismatches=0 rev=1dc678500c92164b0b2bea82b934dd03d1dfbf38 load=5.87
ITEM	E23a	MISMATCH	original	rc=1 expect_exit=0 predicate fails last=SUMMARY manifests=8 failed=0 uncovered=1 floor_violations=0 load=5.87
ITEM	E23b	MISMATCH	original	rc=1 expect_exit=0 predicate holds last=SUMMARY manifests=8 failed=0 uncovered=1 lost=0 fidelity=0 floor_violations=0 tool_unchanged=0 load=5.96
SUMMARY items=5 agree=3 mismatches=2 restated=0 partial=1 rev=9c76c7222a8abff027af42e37f0d160d52526bba
```
Load at dispatch of the serialized run: `4.20 3.14 2.10 6/4401 3888188`; load when this report was
written: `29.36 15.59 7.61 22/7680 1622593` (Q77 note: the E23a/E23b cause readings ran at 6.94–13.12).

Cause executions (one fresh clone per commit, `--no-local`, origin removed, detached, toplevel
asserted = the clone, `PATH=/usr/bin:/bin`, fresh TMPDIR, `GIT_CONFIG_NOSYSTEM=1`, cwd = clone root,
`cat /proc/loadavg` beside each):

```
parent 1dc678500c92164b0b2bea82b934dd03d1dfbf38   (v1 and v2 both HOLD, rc 0)
  SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0 rev=1dc67850…            RC-a=0
  SUMMARY manifests=3 failed=0 uncovered=0 lost=0 fidelity=0 floor_violations=0 tool_unchanged=0 rev=1dc67850…  RC-b=0
cause  de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b   (line-304 writer)
  v1: SUMMARY manifests=4 failed=0 uncovered=0 floor_violations=0 rev=de874ee8…       RC 0    (predicate manifests=3 FAILS)
  v2: SUMMARY manifests=4 failed=0 uncovered=0 lost=0 fidelity=0 floor_violations=0 tool_unchanged=0 rev=de874ee8…  RC 0  (HOLDS)
8aaacf518d0dc9292d5258abf7d74bdaea1b76e7          (v2 instrument creation)
  v1: manifests=3 failed=152 uncovered=14 … RC1=1    v2: … fidelity=11 … tool_unchanged=1 RC=1
d65a5c4328896742d2ec951f7156c6a70aa9325a          (r33 capture)
  v2: SUMMARY manifests=8 failed=0 uncovered=0 … RC=0
af7fd250c8a862130f88b8f77ad29debf343e54d          (r33 salvage; adds only census/round-33/waves/w1-results.json)
  v2: SUMMARY manifests=8 failed=0 uncovered=1 … RC=1   v1: same uncovered=1, RC1=1
(also executed at b8620071: v1 rc 0 `SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0 rev=b8620071…`;
 v2 rc 0 `SUMMARY manifests=3 … lost=0 fidelity=0 floor_violations=0 tool_unchanged=0 rev=b8620071…`)
```

Row-line provenance of `SCORECARD.md:304`: line text at 2b0171e == line text at de874ee8 (`cmp`
identical), zero occurrences in de874ee8's parent tree — `de874ee8` is the row's author.

Row probe through the frozen counter (scratch clone of the lane at the list revision, throwaway
identity, `511323e305f598ace7439b8845c3c11889a0f57f`):
```
ITEM	E23a	AGREE	restated	rc=0 expect_exit=0 statement is the run's last digit-bearing line last=SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0 rev=b86200714069022954a3b498cf697d894119b45e load=12.03
ITEM	E23b	MISMATCH	restated	BAD-CAUSE(the row's own argv held at the cause)
```

## Findings

1. **E20 agrees** — `SCORECARD.md:102`, `grep -c` of tool-bound receipts in `census/` = 5, rc 0,
   at `eb1aa49783ae4a0d42e062aa5a61e49a91b0f76a`. No row.
2. **E21 agrees** — `SCORECARD.md:103`, `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0`, rc 0
   at the base; `tools/souji-gate-check.py` unchanged. No row.
3. **E22 agrees** — `SCORECARD.md:303`, `SUMMARY k1=0 k2=0 mismatches=0`, rc 0; already
   revision-pinned (`--rev 1dc67850… --list-rev b8cb4b31…`), hence stable. No row.
4. **E23a is stale at birth** — `SCORECARD.md:304` (v1 arm). Its author commit
   `de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b` added `census/round-29/waves/manifest.sha256` in the
   same commit, pushing `manifests` 3→4, so the row's own argv already failed in the commit that
   wrote it. Value drift is closed (the script's only commit is its creation, `b8cb4b31`), so the
   honest route is the argv correction: pin `--rev b8620071…` (the revision the row itself names,
   also the last green commit family). Row validated by the frozen counter → `AGREE restated`.
5. **E23b is stale by data drift, not by its script** — `SCORECARD.md:304` (v2 arm). Its predicate
   still holds verbatim at the base; only the frozen exit 0 is stale, because
   `af7fd250c8a862130f88b8f77ad29debf343e54d` committed `census/round-33/waves/w1-results.json`
   without a manifest record → `uncovered=1` and the counter's exit rule flips to 1. The honest
   correction (pin `--rev b8620071…`, rc 0, exact SUMMARY above) is the same shape as E23a's and
   true, but no cause can satisfy the frozen rule (attack log below).
6. **Q76 contributes nothing to this slice** — no correction/supersession/binding row exists at the
   base for `SCORECARD.md:102`, `:103`, `:303` or `:304`
   (`git grep -n 'SCORECARD.md:10[23]'`/`':30[34]'` at 9c76c722…): the only hits are the r33
   enumeration deliverable that sourced the items and r30 prose about the *different* row
   `SCORECARD.md:314`.

## Attack log

**A-10.1 — E23b (SCORECARD.md:304, v2 arm) is unrestatable under the frozen cause rule.**
Reproduced state, three executed routes:
- cause = `af7fd25` (true drift onset; parent `d65a5c43` holds, cause fails; cause changes exactly
  one path, `census/round-33/waves/w1-results.json`) → `BAD-ROW(cause touches none of the item files)`,
  because the frozen `files` cell names only `census/round-29/c2-counter-v2.py`.
- cause = `8aaacf51` (the only commit touching that file) → `BAD-CAUSE(original at parent=False at
  cause=False; need True/False)` — the script does not exist at the parent and was red at its own
  creation (`failed=152 uncovered=14 fidelity=11 tool_unchanged=1`).
- argv correction with cause = `de874ee8` (the only commit that wrote the row's line) →
  `BAD-CAUSE(the row's own argv held at the cause)` — v2 was green there; only v1 flipped.
Consequences for the L1, stated without proposing a frozen change: the item cannot reach AGREE by
any rule-conforming row, so `SUMMARY items=60 agree=60 mismatches=0` is unreachable for E23b as
frozen. Any repair would have to loosen the cause-file binding (forbidden by the stricter-only
constraint), or the item must be recorded as a named miss with this reproduction. Reproducer command
and outputs are in `.ufo/waves/round-34/w1/deliver-c1-E23b.md`.

**A-10.2 — the same rule makes the v1/v2 halves of one row asymmetric.** E23a and E23b share
`SCORECARD.md:304` and the same author commit; the v1 arm is correctable because the author commit
itself flipped it, the v2 arm is not because the author commit did not. That asymmetry is a property
of the frozen cause rule, not of the row: a row whose two arms drift at different commits can only
be half-corrected.

## Deliveries

- `.ufo/waves/round-34/w1/deliver-c1-E20.md` (AGREE, no row)
- `.ufo/waves/round-34/w1/deliver-c1-E21.md` (AGREE, no row)
- `.ufo/waves/round-34/w1/deliver-c1-E22.md` (AGREE, no row)
- `.ufo/waves/round-34/w1/deliver-c1-E23a.md` (validated restatement row, argv-pinned)
- `.ufo/waves/round-34/w1/deliver-c1-E23b.md` (blocked + three-route reproducer)
