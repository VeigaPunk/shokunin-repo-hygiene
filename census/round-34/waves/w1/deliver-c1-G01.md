# C1 delivery — G01 (SKILL.md:201, tools/souji-census.sh)

Verdict: **AGREE at base — no restatement row drafted.**

## Counter ITEM line (verbatim)

```
ITEM	G01	AGREE	original	rc=0 expect_exit=0 predicate holds last=selftest: 69 checks, 0 failed load=4.43
```

## Command (executed, under flock, TMPDIR set by hand)

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
Lane HEAD at read time: `51acb5fb6fa38a6b593b3badb674cec559d7eb2c` (measurement is at `--rev`, the counter clones from `--rev`).

## Rendered row state at base

`git -C <lane> show 9c76c72:SKILL.md | awk 'NR==202'` → the `souji-census` registry row; its self-test cell reads
`TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` (69/0 at 4800fd7). No pipe in that quote.
The run's last digit-bearing line is `selftest: 69 checks, 0 failed` and exit is 0, matching the frozen item.

## Prior-correction / supersession sweep (Q76)

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 2b0171e2:SCORECARD.md | grep -n 'selftest: 69 checks'
→ NO MATCH
git -C ... show 2b0171e2:SCORECARD.md | grep -nE '^\| [A-Z][0-9]{2}[a-z]? \| SKILL\.md:'
→ (empty)   # no ledger row anywhere binds a SKILL.md:<line> cell
git -C ... show 2b0171e2:SCORECARD.md | grep -n 'souji-census.sh --selftest'
→ (empty)
git -C ... show 2b0171e2:SCORECARD.md | grep -n 'Round 34 registry restatements'
→ NO SECTION AT LIST-REV   (and NO SECTION AT BASE)
```

No prior correction, supersession or binding row exists for this cell; the AGREE is a direct measurement, not a Q76 carry.

## Cause commit

Not applicable: the item's original (exit 0, predicate `selftest: 69 checks, 0 failed`) holds at the measured revision,
so Q75's cause machinery is not engaged and no cause full40 is claimed.

## Proposed restatement row

None. Item agrees.

## Defect found (reproduced) — frozen `where` line cell is off by one row

At base, `SKILL.md:201` is **not** the row that carries this item's argv:

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 9c76c72:SKILL.md | awk 'NR==201{print substr($0,1,90)}'
| souji-vault-verify | probe | `bash tools/souji-vault-verify.sh --fallback <path>...` | 0
$ ... | awk 'NR==202{print substr($0,1,90)}'
| souji-census | probe | `bash tools/souji-census.sh --root DIR [--compare PREV.tsv] [--repo-t
```

The row storing the (argv, 69/0) pair is line 202; lines 195-220 of SKILL.md are byte-identical at base and at
`--list-rev` (both sha256 `a839f7f67223fb295589810ad2c7b9471e8141f2855a8627024b625cbfc749a4`), and SKILL.md is 428 lines at both.
Impact: inert for an AGREE item (the counter reads `where` only when a restatement row exists), but an argv-correction
row for this cell would make the counter fetch SKILL.md line 201 (the `souji-vault-verify` row) as "the row's line" in the
BAD-CAUSE check. Disclosed to the L1; no frozen predicate/target/item is proposed for change here.
