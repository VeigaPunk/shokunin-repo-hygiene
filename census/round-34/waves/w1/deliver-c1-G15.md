## Item G15 — AGREE at base; no restatement

Frozen item (census/round-34/c1-items.tsv @ 2b0171e2):
`G15	SKILL.md:239	0	SUMMARY total=8 pass=8 fail=0	census/round-21/run-acceptance.py	{REV}	python3 tests/fixtures/r21-replay-boundaries.py --tool census/round-21/run-acceptance.py --base-tool {BLOB:8513d6ac97076f34ff94a3fc1979c13e69c2d19a:census/round-21/run-acceptance.py}`

### Counter reading (base 9c76c7222a8abff027af42e37f0d160d52526bba)

```
ITEM	G15	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=8 pass=8 fail=0 base_discriminating=4 load=4.47
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=9c76c7222a8abff027af42e37f0d160d52526bba
```
Command: `flock <scratch>/tmp/c1s3.lock python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9c76c7222a8abff027af42e37f0d160d52526bba --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch /fast/scratch/hyaku/souji-r34/RestateC1s3/cnt --only G15`; exit 0; `cat /proc/loadavg` = 4.47 3.10 2.06.

### Counter reading (tip 51acb5fb6fa38a6b593b3badb674cec559d7eb2c)

```
ITEM	G15	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=8 pass=8 fail=0 base_discriminating=4 load=32.04
```
Same argv, `--rev 51acb5fb6fa38a6b593b3badb674cec559d7eb2c`; exit 0.

### Prior correction / supersession check (SCORECARD.md @ base)

```
grep -c 'G15' SCORECARD.md@base = 0
grep -c 'SKILL.md:239' SCORECARD.md@base = 0
grep -c 'r21-replay-boundaries' SCORECARD.md@base = 0
git show 9c76c722...:SCORECARD.md | grep -n '^###.*restate'  -> no match
```
No prior correction binds the cell; none is needed.

### Cause / proposed row

Not applicable: the frozen predicate is a bare regex matched against the run's LAST digit-bearing line; the observed last line `SUMMARY total=8 pass=8 fail=0 base_discriminating=4` matches it (re.search), exit 0 at base and at the tip. No cause walked, no row proposed.

Line-number note: the frozen `where` is one below the 1-based line (line 239 is the `r21-read-render-edges` row; `r21-replay-boundaries` is at 240).
