# C1 slice 10/12 — E23a (SCORECARD.md:304, C2 committed-bytes receipts, v1 arm)

STATUS: MISMATCH — one appended restatement row, argv-corrected (revision-pinned). Row validated
through the frozen counter in a scratch clone (AGREE restated).

## Counter reading (base, flock)
```
$ flock .../run.lock python3 -B census/round-34/c1-counter.py --root <lane> \
    --rev 9c76c7222a8abff027af42e37f0d160d52526bba --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
    --scratch /fast/scratch/hyaku/souji-r34/RestateC1s10/cnt --only E23a
ITEM	E23a	MISMATCH	original	rc=1 expect_exit=0 predicate fails last=SUMMARY manifests=8 failed=0 uncovered=1 floor_violations=0 load=5.87
```
`/proc/loadavg` at the line's run: `5.87 4.33 2.63`; start of the serialized run `4.20 3.14 2.10`.
Item: exit 0, pred `SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0`,
files `census/round-29/c2-counter.py`, at `{REV}`.

## Prior-correction check (Q76)
```
$ git -C <lane> grep -n 'SCORECARD.md:304' 9c76c7222a8abff027af42e37f0d160d52526bba -- .
census/round-30/waves/w1/SwarmRevenger34.md:37:8. R18 `SCORECARD.md:314` ... only `SCORECARD.md:304`, `SCORECARD.md:314`, `SKILL.md:227`
census/round-30/waves/w1/deliver-cross-claim.md:46:  table (SCORECARD.md:304-307), the "Round 29 capability rows" (313-314), the
census/round-33/waves/w1/deliver-c1-enumeration-misses.md:36:| E23 | SCORECARD.md:304 (r29 measurements) | ...
$ git -C <lane> grep -nF '| C2 committed-bytes receipts |' 9c76c722 -- SCORECARD.md
SCORECARD.md:304:| C2 committed-bytes receipts | ...      (the row itself, once)
```
No correction/supersession/binding row for the cell exists at the base: the r30 hits are prose
about a *different* row (`SCORECARD.md:314`), and the r33 hit is the enumeration deliverable that
sourced the item. Q76 does not apply.

## Cause: de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b (argv correction; it wrote the row's line)
Route accepted by the frozen rule for this item: the row's line was written by a commit at which
the row's own argv already failed. Value drift is closed for E23a, because neither failing commit
touches `census/round-29/c2-counter.py` (that file has exactly one commit in its history:
`b8cb4b31`, its creation).

Executed readings (fresh clone per commit, origin removed, `PATH=/usr/bin:/bin`, fresh TMPDIR,
`GIT_CONFIG_NOSYSTEM=1`, cwd = clone root, under flock):

Parent `1dc678500c92164b0b2bea82b934dd03d1dfbf38` (original HOLDS):
```
$ python3 -B census/round-29/c2-counter.py --root . --rev 1dc678500c92164b0b2bea82b934dd03d1dfbf38
r26 records=1381 failed=0 uncovered=0 floor_violation=0
r27 records=124 failed=0 uncovered=0 floor_violation=0
r28 records=75 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0 rev=1dc678500c92164b0b2bea82b934dd03d1dfbf38
RC-a=0        load at run: 13.12 6.55 3.51
```
Cause `de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b` (original FAILS — predicate `manifests=3`):
```
$ python3 -B census/round-29/c2-counter.py --root . --rev de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b
r26 records=1381 failed=0 uncovered=0 floor_violation=0
...
r29 records=131 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=4 failed=0 uncovered=0 floor_violations=0 rev=de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b
RC 0        load at run: 6.94 4.33 2.63
```
Mechanism: `de874ee8` is the r29 landing commit; it added `census/round-29/waves/manifest.sha256`
in the same commit that authored line 304, so the row was born stale — `manifests` moves 3 -> 4
inside one commit. Row-line identity check against the frozen rule:
```
$ git show 2b0171e:SCORECARD.md | sed -n 304p > list.txt ; git show de874ee8:SCORECARD.md | sed -n 304p > cause.txt
$ cmp -s list.txt cause.txt && echo identical   -> line304-identical-YES
$ git show 1dc67850:SCORECARD.md | grep -cF "$(cat list.txt)"   -> 0
```
Tip (`9c76c722…`) additionally drifts to `manifests=8 … uncovered=1` because
`af7fd250c8a862130f88b8f77ad29debf343e54d` added `census/round-33/waves/w1-results.json` with no
manifest record — a second, later drift that the revision-pinned correction also quarantines.

## Proposed row (append at end of SCORECARD.md)
```
### Round 34 registry restatements

| E23a | SCORECARD.md:304 | restated | 0 | `python3 -B census/round-29/c2-counter.py --root . --rev b86200714069022954a3b498cf697d894119b45e` | `SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0 rev=b86200714069022954a3b498cf697d894119b45e` | de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b | the row was written by the commit that added r29's own waves manifest (manifests 3->4 in one step); its numbers hold at the revision the row itself names |
```

Verification of the corrected argv (pinned at the revision the row names, measured in a base clone):
```
$ python3 -B census/round-29/c2-counter.py --root . --rev b86200714069022954a3b498cf697d894119b45e
SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0 rev=b86200714069022954a3b498cf697d894119b45e
RC1=0
```
The corrected argv names the row's own script (`census/round-29/c2-counter.py`) and the statement is
that run's LAST digit-bearing line. `1dc678500c92164b0b2bea82b934dd03d1dfbf38` (the last commit at
which the claim held) is an equally valid pin — also measured rc 0 with the identical SUMMARY bar
the rev suffix.

## Frozen-counter probe of the row (scratch clone, throwaway identity)
Scratch clone of the lane at the list revision with only this section appended
(`511323e305f598ace7439b8845c3c11889a0f57f`):
```
$ python3 -B census/round-34/c1-counter.py --root <clone> --rev 511323e3… --list-rev 2b0171e2… \
    --scratch .../cnt2 --only E23a,E23b
ITEM	E23a	AGREE	restated	rc=0 expect_exit=0 statement is the run's last digit-bearing line last=SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0 rev=b86200714069022954a3b498cf697d894119b45e load=12.03
```

## Risk
None for the claim itself: the cell becomes a revision-scoped historical measurement, which is what
the row's "measured at" language already says. The restated cell no longer speaks about the tip —
stated plainly so the row is not read as a current-state claim.
