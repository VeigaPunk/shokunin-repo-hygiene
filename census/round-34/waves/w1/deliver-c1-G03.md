# C1 delivery — G03 (SKILL.md:216, tests/fixtures/r15-preservation-evidence.py)

Verdict: **AGREE at base — no restatement row drafted.**

## Counter ITEM line (verbatim)

```
ITEM	G03	AGREE	original	rc=0 expect_exit=0 predicate holds last=fixture: 8/8 checks passed load=4.36
```

## Command (executed, under flock)

```
export TMPDIR=/fast/scratch/hyaku/souji-r34/RestateC1s1/tmp
flock /fast/scratch/hyaku/souji-r34/RestateC1s1/run.lock \
  python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
  --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
  --scratch /fast/scratch/hyaku/souji-r34/RestateC1s1/cnt --only G01,G02,G03,G04a,G04b
```

Exit 0. Load before/after: `3.09 2.74 1.90` / `4.25 3.10 2.07`.
Counter bytes at --list-rev: sha256 `1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20`.

## Rendered row state at base

The `r15-preservation-evidence` registry row is at base line 217; its self-test cell states (8/8 at r16).
Run: rc 0, last digit-bearing line `fixture: 8/8 checks passed` — agrees.

## Prior-correction / supersession sweep (Q76)

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 2b0171e2:SCORECARD.md | grep -n '8/8 checks passed'
→ NO MATCH
git -C ... show 2b0171e2:SCORECARD.md | grep -n 'tests/fixtures/r15-preservation-evidence.py'
→ (empty)
git -C ... show 2b0171e2:SCORECARD.md | grep -nE '^\| [A-Z][0-9]{2}[a-z]? \| SKILL\.md:'
→ (empty)
git -C ... show 2b0171e2:SCORECARD.md | grep -n 'Round 34 registry restatements'
→ NO SECTION AT LIST-REV
```

No prior correction binds this cell; AGREE is a direct measurement.

## Cause commit

Not applicable: original (exit 0, `fixture: 8/8 checks passed`) holds at the measured revision.

## Proposed restatement row

None. Item agrees.

## Defect found (reproduced) — frozen `where` cell is one row low

```
$ git -C <lane> show 9c76c72:SKILL.md | awk 'NR==216{print substr($0,1,90)}'
| souji-preservation-evidence | gate | `python3 tools/souji-preservation-evidence.py --roo
$ ... | awk 'NR==217{print substr($0,1,90)}'
| r15-preservation-evidence | gate | `python3 tests/fixtures/r15-preservation-evidence.py`
```

`SKILL.md:216` is the `souji-preservation-evidence` row; this item's row is 217. Off-by-one is systematic across the
frozen SKILL.md registry items (see the report's sweep). Inert for AGREE; material for argv-correction restatements.
