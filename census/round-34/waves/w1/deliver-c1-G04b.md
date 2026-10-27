# C1 delivery — G04b (SKILL.md:217, tests/fixtures/r18-landing-pointers.py + tools/souji-landing-gate.py)

Verdict: **AGREE at base — no restatement row drafted.**

## Counter ITEM line (verbatim)

```
ITEM	G04b	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=11 failed=0 load=4.25
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

Same registry row as G04a (base line 218). Its self-test cell names the external fixture
`python3 tests/fixtures/r18-landing-pointers.py --tool tools/souji-landing-gate.py` (11/0). No pipe in that fragment.
Run: rc 0, last digit-bearing line `SUMMARY total=11 failed=0` — agrees.

## Prior-correction / supersession sweep (Q76)

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 2b0171e2:SCORECARD.md | grep -n 'total=11 failed=0'
→ 331:R30-CORRECTION SCORECARD.md:167 R10 rc=0 observed=SUMMARY total=11 failed=0
→ 388:| L22 | SCORECARD.md:167 | total=11 failed=0 | run: python3 tools/souji-rev-pin.py --selftest | ...
git -C ... show 2b0171e2:SCORECARD.md | grep -n 'r18-landing-pointers.py'
→ (empty)
git -C ... show 2b0171e2:SCORECARD.md | grep -nF 'SKILL.md:217'
→ (empty)
```

The prior rows (R30-CORRECTION/L22) bind **SCORECARD.md:167** with a different argv (`tools/souji-rev-pin.py --selftest`);
they do not bind this cell. No ledger row binds any `SKILL.md:<line>` cell. No Q76 carry; direct measurement.

## Cause commit

Not applicable: original (exit 0, `SUMMARY total=11 failed=0`) holds at the measured revision.

## Proposed restatement row

None. Item agrees.

## Defect found (reproduced) — frozen `where` cell is one row low

```
$ git -C <lane> show 9c76c72:SKILL.md | awk 'NR==217{print substr($0,1,90)}'
| r15-preservation-evidence | gate | `python3 tests/fixtures/r15-preservation-evidence.py`
$ ... | awk 'NR==218{print substr($0,1,90)}'
| souji-landing-gate | gate | `python3 tools/souji-landing-gate.py --root LANE --rev REV --round N [--f
```

The row carrying the r18-landing-pointers fixture is line 218 (`grep -nF 'r18-landing-pointers.py' SKILL.base.md` → 218);
the frozen cell says 217. Inert for AGREE; material for any argv-correction restatement on this cell.
