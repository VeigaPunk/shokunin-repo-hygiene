# C1 delivery — G05 (SKILL.md:219 as frozen, `census/round-17/gate-replays.py`)

Verdict: **MISMATCH at base and at the tip — NO honest restatement exists. ATTACK (item §1 + §2).**
The row's own claim is TRUE and executed (the tool prints the five pinned replay rows exactly), but the
frozen predicate spells its separators `\t` while the frozen counter collapses every output line to
single spaces *before* matching, so the frozen item can never agree at any revision. The only
correction route (corrected argv) is blocked by a second frozen defect: the item's `where` is one
line short (SKILL.md:219 is the r16-landing-gate row; the r17-gate-replays row is line 220), so the
frozen cause test can only bind an unrelated commit. A mechanically valid row is supplied at the end
for the L1 to rule on; it binds a foreign cause and should not be landed as an honest correction.

## Counter ITEM line (verbatim)

```
ITEM	G05	MISMATCH	original	rc=0 expect_exit=0 predicate fails last=gate-replays: wrote record to /fast/scratch/hyaku/souji-r34/RestateC1s2/cnt/c1.tuhcbt_r/G05.69ncemxk/s/g5.json load=2.84
```

At the tip `51acb5fb6fa38a6b593b3badb674cec559d7eb2c` (same predicate failure):

```
ITEM	G05	MISMATCH	original	rc=0 expect_exit=0 predicate fails last=gate-replays: wrote record to /fast/scratch/hyaku/souji-r34/RestateC1s2/cnt2/c1.pg8028fa/G05.iukh6qkg/s/g5.json load=12.96
```

## Command (executed)

```
export TMPDIR=/fast/scratch/hyaku/souji-r34/RestateC1s2/tmp
flock /fast/scratch/hyaku/souji-r34/RestateC1s2/ser.lock \
  python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
  --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
  --scratch /fast/scratch/hyaku/souji-r34/RestateC1s2/cnt --only G05,G07,G09,G11,G12
```

Exit 1; `SUMMARY items=5 agree=3 mismatches=2 restated=0 partial=1`. Load before `2.84 2.72 1.92`,
after `7.83 4.61 2.74` (`/proc/loadavg`). Counter bytes at `--list-rev`: sha256
`1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20`; items TSV sha256
`5de3678206dcc091d2a2f911f0fe085021c90431d1e40edeea9dd15765b06127`.

## Prior-correction / supersession grep (base `9c76c72:SCORECARD.md`, 525 lines, materialised to scratch)

```
grep -c -F 'G05' sc-base.md                              -> 0
grep -c -F 'SKILL.md:219' sc-base.md                     -> 0
grep -c -F 'gate-replays' sc-base.md                     -> 0
grep -c -F 'Round 34 registry restatements' sc-base.md    -> 0
```

No correcting, superseding or binding row exists for this cell; the item is not AGREE under Q76.

## Falsifier 1 — the row's claim is true, the predicate cannot see it (executed)

Frozen argv run at base in a scratch clone (`git clone -q --no-local`, `remote remove origin`,
`checkout -qf --detach 9c76c72`, cwd = clone root, `env -i PATH=/usr/bin:/bin TMPDIR=… GIT_CONFIG_NOSYSTEM=1`):

```
name	rev	round	exit	findings	match
r15-landing	b410186	15	1	5	True
r13-admitted	a31642d	13	0	0	True
r14-landing	cc21683	14	0	0	True
r16-landing	6ff91f5	16	0	0	True
r16-precarry	79bbe7a	16	1	29	True
gate	rev=WORKTREE	sha256=7489334c92acc2aa	expected_sha_match=False
gate-replays: wrote record to /fast/scratch/hyaku/souji-r34/RestateC1s2/g5s/g5.json
RC=0
```

Every frozen ANYLINE target is present verbatim in that output. Yet the counter's own `frozen_pred`
(instrument code imported read-only from the frozen counter) returns False on those very lines:

```
collapse('r15-landing\tb410186\t15\t1\t5\tTrue') -> 'r15-landing b410186 15 1 5 True'
frozen_pred(ANYLINE:\tb410186\t15\t1\t5\tTrue && … , lines, root, base) -> (False, 'predicate fails')
space-variant of the same conjunct against the collapsed line -> True
```

Cause: `frozen_pred` builds `flat_lines = [collapse(x) for x in lines]` and then runs `ANYLINE`
regexes against the collapsed strings, so a `\t` in the pattern can never match. This is
instrument-level, revision-independent: G05 cannot AGREE at base, at the C1 landing commit, or at the
tip. Blast radius inside the frozen 60-item set: the two tab-bearing predicates, G05 and G17b
(`COUNT:^SCENARIO\t…`, also matched against collapsed lines).

## Falsifier 2 — the `where` pointer is one line short, so the argv-correction cause test binds a foreign row

```
git show 2b0171e:SKILL.md | sed -n '219p'   -> | r16-landing-gate | gate | `python3 tests/fixtures/r16-landing-gate.py [--tool PATH]` | …
git show 2b0171e:SKILL.md | sed -n '220p'   -> | r17-gate-replays | gate | `python3 census/round-17/gate-replays.py [--gate-rev REV] --output <new.json>` | …
```

Sweep over all 23 SKILL.md items: the first named file's basename is absent from the frozen `where`
line for **20 of 23** (all five of my items: G05 219→220, G07 222→223, G09 230→231, G11 234→235,
G12 236→237). The counter's argv-correction check reads `SKILL.md` at `where` and demands the cause
have written *that* line, so for G05 it demands a cause that wrote the r16-landing-gate row. Executed
search for the exact-line writers: one, and only one —

```
4f9a4e8388fc09e7a02a140bf397fe6329005b6f  round-16: wave-2 honesty corrections
line 219 text absent in its parent a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae, present at the cause
git cat-file -e 4f9a4e83:census/round-17/gate-replays.py -> ABSENT (the script did not exist yet)
```

So the only mechanically admissible cause proves nothing about the row's claim: the frozen argv
"fails" there solely because the script did not exist. A row binding it passes the counter (below)
while asserting a cause for a different row — the exact gameability the contract asks to be reported.

## Mechanically valid row (validated in scratch, NOT recommended as an honest correction)

Applied in a scratch clone on top of the lane tip (`51acb5f`), committed with a throwaway identity,
then measured with the frozen counter at the scratch revision `d94df9ca5313457da695811b859802c900def1f9`:

```
| G05 | SKILL.md:219 | restated | 0 | `set -o pipefail; python3 census/round-17/gate-replays.py --output g5.json|sed -n '6p'` | `r16-precarry 79bbe7a 16 1 29 True` | 4f9a4e8388fc09e7a02a140bf397fe6329005b6f | Frozen ANYLINE predicate spells its separators backslash-t while the counter collapses output lines before matching, so the frozen argv cannot agree at any revision; SKILL.md:219 is one line short of the r17-gate-replays row at 220, so the frozen cause test binds only the r16-landing-gate row writer. |
```

```
ITEM	G05	AGREE	restated	rc=0 expect_exit=0 statement is the run's last digit-bearing line last=r16-precarry 79bbe7a 16 1 29 True load=57.37
SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=d94df9ca5313457da695811b859802c900def1f9
EXIT=0
```

Mechanics checked by that run: argv names the item's own script; exit 0; the quoted statement is the
run's collapsed LAST digit-bearing line (the tool's own fifth replay row — piping with `|sed` without
spaces keeps the row's cell delimiter ` | ` out of the argv cell); cause is an ancestor of
`--list-rev`. What it does *not* have is a true cause, per Falsifier 2.

**Ruling needed from the L1** (single integration owner): either land this row with the foreign-cause
anomaly disclosed (target reachable, cause attribution false by construction), or route G05 — and
G17b, same collapse defect — as instrument defects, in which case the frozen `agree=60` target is
unreachable this round. No amendment is available: the prereg admits amendments only before counter
data, and data exists (committed controls plus the feasibility run).
