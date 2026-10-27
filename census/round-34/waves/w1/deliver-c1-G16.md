## Item G16 — AGREE at base; no restatement

Frozen item (census/round-34/c1-items.tsv @ 2b0171e2):
`G16	SKILL.md:240	0	SUMMARY total=3 pass=3 fail=0	census/round-21/run-acceptance.py	{REV}	python3 tests/fixtures/r21-source-head.py --tool census/round-21/run-acceptance.py --base-tool {BLOB:522dcd768ca90afe166532d37d306d3df70aeea5:census/round-21/run-acceptance.py}`

### Counter reading (base 9c76c7222a8abff027af42e37f0d160d52526bba)

```
ITEM	G16	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=3 pass=3 fail=0 base_discriminating=1 load=4.36
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=9c76c7222a8abff027af42e37f0d160d52526bba
```
Command: `flock <scratch>/tmp/c1s3.lock python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9c76c7222a8abff027af42e37f0d160d52526bba --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch /fast/scratch/hyaku/souji-r34/RestateC1s3/cnt --only G16`; exit 0; `cat /proc/loadavg` = 4.36 3.10 2.07.

### Counter reading (tip 51acb5fb6fa38a6b593b3badb674cec559d7eb2c)

```
ITEM	G16	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=3 pass=3 fail=0 base_discriminating=1 load=33.64
```
Same argv, `--rev 51acb5fb6fa38a6b593b3badb674cec559d7eb2c`; exit 0.

### Prior correction / supersession check (SCORECARD.md @ base)

```
grep -c 'G16' SCORECARD.md@base = 0
grep -c 'SKILL.md:240' SCORECARD.md@base = 0
grep -c 'r21-source-head' SCORECARD.md@base = 0
git show 9c76c722...:SCORECARD.md | grep -n '^###.*restate'  -> no match
```
No prior correction binds the cell; none is needed.

### Cause / proposed row

Not applicable: the frozen predicate is a regex matched against the run's LAST digit-bearing line; the observed last line `SUMMARY total=3 pass=3 fail=0 base_discriminating=1` matches it (re.search), exit 0 at base and at the tip. No cause walked, no row proposed.

Line-number note: the frozen `where` is one below the 1-based line (line 240 is the `r21-replay-boundaries` row; `r21-source-head` is at 241).
