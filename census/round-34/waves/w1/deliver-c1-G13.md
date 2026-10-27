## Item G13 — AGREE at base; no restatement

Frozen item (census/round-34/c1-items.tsv @ 2b0171e2):
`G13	SKILL.md:237	0	SUMMARY total=27 pass=27 fail=0 leaks=0 base_leaks=19 max_reason_bytes=160	tests/fixtures/r21-reason-canary.sh,tools/souji-proc-census.sh	{REV}	bash tests/fixtures/r21-reason-canary.sh --tool tools/souji-proc-census.sh --base {BLOB:6ff3413bba9c8430c3b0bc4d2052e21d0407183f:tools/souji-proc-census.sh}`

### Counter reading (base 9c76c7222a8abff027af42e37f0d160d52526bba)

```
ITEM	G13	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=27 pass=27 fail=0 leaks=0 base_leaks=19 max_reason_bytes=160 load=4.29
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=9c76c7222a8abff027af42e37f0d160d52526bba
```
Command: `flock <scratch>/tmp/c1s3.lock python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9c76c7222a8abff027af42e37f0d160d52526bba --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch /fast/scratch/hyaku/souji-r34/RestateC1s3/cnt --only G13`; exit 0; `cat /proc/loadavg` = 4.29 3.02 2.02.

### Counter reading (tip 51acb5fb6fa38a6b593b3badb674cec559d7eb2c)

```
ITEM	G13	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=27 pass=27 fail=0 leaks=0 base_leaks=19 max_reason_bytes=160 load=32.04
```
Same argv, `--rev 51acb5fb6fa38a6b593b3badb674cec559d7eb2c`; exit 0.

### Prior correction / supersession check (SCORECARD.md @ base, counter's restatement section)

```
grep -c 'G13' SCORECARD.md@base = 0
grep -c 'SKILL.md:237' SCORECARD.md@base = 0
grep -c 'r21-reason-canary' SCORECARD.md@base = 1   # line 13, coverage capability row, not a correction row
git show 9c76c722...:SCORECARD.md | grep -n '^###.*restate'  -> no match (no restatement section exists at base)
```
No prior correction binds the cell; none is needed.

### Cause / proposed row

Not applicable: the frozen (exit 0, `SUMMARY total=27 pass=27 fail=0 leaks=0 base_leaks=19 max_reason_bytes=160`) holds at base and at the tip. No cause walked, no row proposed.

### Line-number note (affects every G-item in this slice)

The frozen `where` column is one below the 1-based line: line 237 of SKILL.md @ base is the `r21-read-root` row; `r21-reason-canary` is at line 238. I did not touch the frozen table; recorded here so a restatement row (if one is ever needed) is placed on the right row.
