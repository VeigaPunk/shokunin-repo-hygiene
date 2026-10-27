# C1 delivery — G04a (SKILL.md:217, tools/souji-landing-gate.py)

Verdict: **AGREE at base — no restatement row drafted.**

## Counter ITEM line (verbatim)

```
ITEM	G04a	AGREE	original	rc=0 expect_exit=0 predicate holds last=SELFTEST pass=65 fail=0 load=4.36
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

The `souji-landing-gate` registry row is at base line 218; its self-test cell states
(65/0 at r19: 61 + four wrap cases) — the current reading. Run: rc 0, last digit-bearing line `SELFTEST pass=65 fail=0` — agrees.

## Prior-correction / supersession sweep (Q76)

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 2b0171e2:SCORECARD.md | grep -n 'SELFTEST pass=65'
→ 326:R30-CORRECTION SCORECARD.md:158 R05 rc=0 observed=SELFTEST pass=65 fail=0
→ 372:| L06 | SCORECARD.md:158 | pass=65 fail=0 | run: python3 tools/souji-landing-gate.py --selftest | ...
→ 503:| K05 | SCORECARD.md:158 | restated | 0 | same | `SELFTEST pass=65 fail=0` | ddb73474433977ff54b015ac3e77669ff2537353 | ...
git -C ... show 2b0171e2:SCORECARD.md | grep -nF 'SKILL.md:217'
→ (empty)
```

The prior rows (R30-CORRECTION/L06/K05) bind **SCORECARD.md:158** — a measurement row — not this registry cell.
No ledger row anywhere binds a `SKILL.md:<line>` cell (`grep -nE '^\| [A-Z][0-9]{2}[a-z]? \| SKILL\.md:'` → empty).
So no Q76 carry applies; the AGREE is a direct measurement of the item's own (argv, exit, predicate).

## Cause commit

Not applicable: original (exit 0, `SELFTEST pass=65 fail=0`) holds at the measured revision.

## Proposed restatement row

None. Item agrees.

## Defect found (reproduced) — frozen `where` cell is one row low

```
$ git -C <lane> show 9c76c72:SKILL.md | awk 'NR==217{print substr($0,1,90)}'
| r15-preservation-evidence | gate | `python3 tests/fixtures/r15-preservation-evidence.py`
$ ... | awk 'NR==218{print substr($0,1,90)}'
| souji-landing-gate | gate | `python3 tools/souji-landing-gate.py --root LANE --rev REV --round N [--f
```

`SKILL.md:217` is the `r15-preservation-evidence` row; this item's row is 218. Inert for AGREE; material for any
argv-correction restatement on this cell.
