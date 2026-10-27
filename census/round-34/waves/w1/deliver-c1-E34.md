# C1 item E34 — SCORECARD.md:369 — AGREE (no restatement)

Seat SwarmExecutor12, round 34 w1. Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`,
base `9c76c7222a8abff027af42e37f0d160d52526bba`, list-rev `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`.

## Counter ITEM line (executed, frozen counter)

```
$ flock /fast/scratch/hyaku/souji-r34/RestateC1s12/c1.lock -c "python3 -B census/round-34/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9c76c7222a8abff027af42e37f0d160d52526bba --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch /fast/scratch/hyaku/souji-r34/RestateC1s12/cnt --only E29,E31,E32,E33,E34"
ITEM	E34	AGREE	original	rc=0 expect_exit=0 predicate holds last=fixture: 5/5 checks passed load=13.60
```

Item: `SCORECARD.md:369`, exit=0, predicate `fixture: 5/5 checks passed`,
files `tests/fixtures/r13-cert-evidence.py`,
argv `python3 tests/fixtures/r13-cert-evidence.py`.

## Prior correction / supersession / binding row (Q76) — none binding this cell

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 2b0171e2:SCORECARD.md | grep -n "SCORECARD.md:369"
(no output)
$ grep -n "external fixture 5/5\|r13-cert-evidence" SCORECARD.md   # at 9c76c72
153:| declared-evidence integrity | reject inconsistent declared artifact/evidence digests, ...
369:| L03 | SCORECARD.md:153 | 5/5 | record: census/round-13/verification.json | Written at 23014d4, whose `ev
```

Line 369 is itself the r31 supersession (L03) of the SCORECARD.md:153 cell; the only other
line naming the fixture is the original capability cell at 153. No r34 restatement row is
needed or proposed.

## Verdict

AGREE at the base revision: exit 0 as stated and the fixture's last digit-bearing line is the
stated one. Nothing was edited.
