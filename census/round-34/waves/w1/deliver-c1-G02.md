# C1 delivery — G02 (SKILL.md:215, tools/souji-preservation-evidence.py)

Verdict: **AGREE at base — no restatement row drafted.**

## Counter ITEM line (verbatim)

```
ITEM	G02	AGREE	original	rc=0 expect_exit=0 predicate holds last=selftest: 47/47 passed load=4.47
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

The `souji-preservation-evidence` registry row is at base line 216; its self-test cell states
(47/47 at r16; 24/47 as landed r15) — 47/47 is the current reading, matching the run. No pipe in that quote.
Run: rc 0, last digit-bearing line `selftest: 47/47 passed`.

## Prior-correction / supersession sweep (Q76)

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 2b0171e2:SCORECARD.md | grep -n '47/47'
→ NO MATCH
git -C ... show 2b0171e2:SCORECARD.md | grep -n 'souji-preservation-evidence.py --selftest'
→ (empty)
git -C ... show 2b0171e2:SCORECARD.md | grep -nE '^\| [A-Z][0-9]{2}[a-z]? \| SKILL\.md:'
→ (empty)   # no ledger row binds any SKILL.md cell
git -C ... show 2b0171e2:SCORECARD.md | grep -n 'Round 34 registry restatements'
→ NO SECTION AT LIST-REV
```

No prior correction binds this cell; AGREE is a direct measurement.

## Cause commit

Not applicable: original (exit 0, `selftest: 47/47 passed`) holds at the measured revision.

## Proposed restatement row

None. Item agrees.

## Defect found (reproduced) — frozen `where` cell is one row low

```
$ git -C <lane> show 9c76c72:SKILL.md | awk 'NR==215{print substr($0,1,90)}'
| r17-jj-receipts | gate | `bash tests/fixtures/r17-jj-receipts.sh --tool-dir DIR` | 0 cle
$ ... | awk 'NR==216{print substr($0,1,90)}'
| souji-preservation-evidence | gate | `python3 tools/souji-preservation-evidence.py --roo
```

`SKILL.md:215` is the `r17-jj-receipts` row; the item's own row is 216. Frozen `where` says 215. Inert for AGREE;
material for any argv-correction restatement (the counter would fetch line 215 as "the row's line").
SKILL.md lines 195-220 are identical at base and `--list-rev` (sha256 `a839f7f67223fb295589810ad2c7b9471e8141f2855a8627024b625cbfc749a4`).
