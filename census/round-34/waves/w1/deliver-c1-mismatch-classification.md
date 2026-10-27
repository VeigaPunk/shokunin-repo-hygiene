# C1 mismatch classification — all 23 SKILL.md registry items (L1 follow-up)

Scope: every frozen C1 item whose `where` is a `SKILL.md` registry row (23 items). Measured at
`9c76c7222a8abff027af42e37f0d160d52526bba` with the frozen counter and `--list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8`.
No frozen item, predicate, counter or leg is proposed for change; every row below is a finding.

## 1. Base reading, all 23 items

```
flock <scratch>/run.lock python3 -B <lane>/census/round-34/c1-counter.py --root <lane> \
  --rev 9c76c7222a8abff027af42e37f0d160d52526bba --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
  --scratch <scratch>/cnt --only <chunk>
```

| item | base | item | base | item | base |
|---|---|---|---|---|---|
| G01 | AGREE | G07 | AGREE | G16 | AGREE |
| G02 | AGREE | G09 | AGREE | G17a | **MISMATCH** (rc 1) |
| G03 | AGREE | G11 | **MISMATCH** (rc 0) | G17b | **MISMATCH** (rc 1) |
| G04a | AGREE | G12 | AGREE | G18 | AGREE |
| G04b | AGREE | G13 | AGREE | G19 | AGREE |
| G05 | **MISMATCH** (rc 0) | G14 | AGREE | G20 | AGREE |
| — | — | G15 | AGREE | G21 | **MISMATCH** (rc 1) |
| — | — | — | — | G23 | **MISMATCH** (rc 1) |
| — | — | — | — | G24 | **MISMATCH** (rc 2) |
| — | — | — | — | G26 | AGREE |

16 AGREE, 7 MISMATCH. Verbatim ITEM lines for G05/G11/G17a/G17b/G21/G23/G24 (abridged to the fields
that classify; the report holds the full lines):

```
ITEM G05  MISMATCH original rc=0 expect_exit=0 predicate fails last=gate-replays: wrote record to <scratch>/g5.json
ITEM G11  MISMATCH original rc=0 expect_exit=0 predicate fails last=SUMMARY total=45 pass=45 fail=0 blocked=0 inventory=exact baseline_mismatches=not-requested
ITEM G17a MISMATCH original rc=1 expect_exit=0 predicate fails last=SUMMARY total=1 pass=0 fail=1
ITEM G17b MISMATCH original rc=1 expect_exit=0 predicate fails last=Note: switching to '9c76c7222a8abff027af42e37f0d160d52526bba'.
ITEM G21  MISMATCH original rc=1 expect_exit=0 predicate fails last=FAIL rev-not-40-hex: rc=2 summary=None lines=[] stderr=... can't open file '/var/tmp/souji-r29-c1-fixture/tools/souji-registry-agreement.py'
ITEM G23  MISMATCH original rc=1 expect_exit=0 predicate fails last=SUMMARY manifests=8 failed=0 uncovered=1 floor_violations=0 rev=9c76c72...
ITEM G24  MISMATCH original rc=2 expect_exit=0 predicate fails last=python3: can't open file '<clone>/tools/souji-capability-agreement.py'
```

All seven mismatches have a `where` cell affected by the one-line-low binding (G24 is the one cell that is
exact — and it is broken for a different reason, §3.7).

## 2. Correction type per mismatch (same-value vs argv correction vs neither)

| item | failure mechanism (executed) | correction that would be honest | does an honest cause exist? | frozen-counter verdict |
|---|---|---|---|---|
| G05 | predicate unattainable: counter collapses whitespace, predicate's five `ANYLINE:\t…` conjuncts need tabs; the tool's real rows are tab-separated and match the row's stated 1/5, 0/0, 0/0, 0/0, 1/29 | none (predicate encoding, not a repo value) | **no** — original never holds at any revision | unreachable |
| G11 | value drift 36→45 **but** the frozen predicate (`total=36 pass=36 fail=0`) was never true: at the drift parent 1988860 the run prints `SUMMARY total=36 pass=32 fail=4`; the row's text claims only "36 literal cases", the `pass=36 fail=0` is enumeration overreach | same-value | **no** — executed BAD-CAUSE(original at parent=False at cause=False) | unreachable |
| G17a | deterministic drift to `matched=16` (of 18): passes at 7a6667cd (2/2 runs), fails at 98e5203 (2/2 runs); 98e5203 touches `tools/souji-evidence-cache.py` and other tools, **not** either item file; non-monotonic (9e8982b7 also fails, later commits pass) | same-value needs a cause touching `tests/fixtures/r21-source-refs.py` or `census/round-21/run-acceptance.py` | **no** | unreachable |
| G17b | same runner drift (S1/S2/S3 `exit=1 matched=16/18`) **plus** an unattainable predicate: `COUNT:^SCENARIO\t…` is matched against whitespace-collapsed lines (proved: regex matches the raw line, not the collapsed one) | argv correction only | only via the off-by-one neighbour cause | unreachable honestly |
| G21 | the row's own command passes a **relative** `--tool` which the fixture resolves with `cwd=/var/tmp/souji-r29-c1-fixture` → `BASE/tools/…` never exists; with an absolute tool the fixture prints the row's stated `cases=20 pass=20 control=FALSE-GREEN-REJECTED` (rc 0) | **argv correction** (`--tool {CLONE}/tools/souji-registry-agreement.py`; runs the row's own script) | honest cause 1dc6785 (wrote the row) **rejected**; neighbour cause 6cb22dc **accepted** | blocked honestly, gameable §3.6 |
| G23 | row's `uncovered=0` now false: base prints `manifests=8 … uncovered=1`; the counter file has a single commit (b8cb4b3), so no post-freeze commit touches an item file; at b8cb4b3 the run prints `manifests=3 failed=152 uncovered=14` (the row never held) | same-value | **no** | unreachable |
| G24 | item `at` = `9420341d…` predates `tools/souji-capability-agreement.py` (added at d4928ec) → the checked-out clone cannot contain the row's script: `git cat-file -e 9420341d:tools/souji-capability-agreement.py` → path does not exist | neither (item/counter repair) | n/a | unreachable |

Net: **0 of the 7 mismatches has an honest restatement the frozen counter would accept.** The C1 target
`agree=60 mismatches=0` is therefore unreachable on the frozen item set (already ≥6 items can never agree),
independently of the other 37 E-items.

## 3. Executed evidence

### 3.1 G05 predicate unattainability (counter's own function)

```
python3 -B - <<'EOF'  (imports census/round-34/c1-counter.py, ARGS-free calls frozen_pred)
G05 pred on the tool's real tab rows  -> (False, 'predicate fails')
G05 pred on space rows               -> (False, 'predicate fails')
G05 collapsed flat line sample       -> 'r15-landing b410186 15 1 5 True'
G17b COUNT test on tab line          -> False
G17b COUNT test on raw line          -> True
EOF
```

The manual run of G05 at base shows the table the row claims is really printed:
`r15-landing b410186 15 1 5 True`, `r13-admitted a31642d 13 0 0 True`, `r14-landing cc21683 14 0 0 True`,
`r16-landing 6ff91f5 16 0 0 True`, `r16-precarry 79bbe7a 16 1 29 True` (tabs in the original) — so the row is
honest and only the item's predicate encoding fails.

### 3.2 G11 drift point and the parent reading

```
clone@1988860: python3 tests/fixtures/r20-input-binding.py  →  SUMMARY total=36 pass=32 fail=4 blocked=0 inventory=exact baseline_mismatches=not-requested  (rc 1)
clone@4f30f23: same argv                                    →  SUMMARY total=45 pass=45 fail=0 blocked=0 inventory=exact baseline_mismatches=not-requested  (rc 0)
```

`4f30f23` touches `tests/fixtures/r20-input-binding.py` (item file) ✓, but the frozen original (exit 0,
`pass=36 fail=0`) does not hold at its parent, so the counter rejects the row:
`BAD-CAUSE(original at parent=False at cause=False; need True/False)`.

### 3.3 G17a/G17b attribution

```
base 2/2 runs:        CASE FAIL refs/remotes/synthetic/main runner_exit=1 matched=16  | SUMMARY total=1 pass=0 fail=1
7a6667cd 2/2 runs:    CASE pass refs/remotes/synthetic/main runner_exit=0 matched=18  | SUMMARY total=1 pass=1 fail=0
98e5203 1 run:        CASE FAIL ... matched=16   (98e5203 --name-only contains tools/souji-evidence-cache.py et al., no r21 file)
bisect 4f83fd2..a416d0b: pass at 07f83e6/76c94eb/76bb697/85b61a1/7a6667c, fail at 9e8982b/98e5203 (non-monotonic)
```

G17b's own run prints `SCENARIO S1 exit=1 matched=16/18` ×3 and `MATRIX scenarios=3 replayed=0 summaries_equal=True`.

### 3.4 G21 the row's own command, and the corrected one

```
row 246 self-test cell: python3 -B tests/fixtures/r29-registry-agreement.py --tool tools/souji-registry-agreement.py
as stated  → cases=20 pass=0 control=FALSE-GREEN-REJECTED  (every case: can't open file '/var/tmp/souji-r29-c1-fixture/tools/souji-registry-agreement.py')
absolute   → cases=20 pass=20 control=FALSE-GREEN-REJECTED  (rc 0)
```

Cause of the row's text: `git log -S 'tests/fixtures/r29-registry-agreement.py --tool tools/souji-registry-agreement.py' -- SKILL.md`
→ `1dc678500c92164b0b2bea82b934dd03d1dfbf38` (round-29 C3 commit).

### 3.5 G23 at its author commit

```
clone@b8cb4b3: python3 -B census/round-29/c2-counter.py --root . --rev b8cb4b3…  →  SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0  (rc 1)
census/round-29/c2-counter.py history: b8cb4b3 only (single commit)
```

### 3.6 Executed counter verdicts in a throwaway clone (the off-by-one in action)

Scratch clone of the lane at base, `SCORECARD.md` appended (append-only preserved), throwaway identity:

```
honest row:   | G21 | SKILL.md:245 | restated | 0 | `python3 -B tests/fixtures/r29-registry-agreement.py --tool {CLONE}/tools/souji-registry-agreement.py` | `cases=20 pass=20 control=FALSE-GREEN-REJECTED` | 1dc678500c92164b0b2bea82b934dd03d1dfbf38 | … |
             → ITEM G21 MISMATCH restated BAD-CAUSE(cause did not write the row's line)
neighbour row: same row with cause 6cb22dc20c9fdb3c7a49eaa1accabca339054c17
             → ITEM G21 AGREE restated rc=0 expect_exit=0 statement is the run's last digit-bearing line
```

`6cb22dc` is the round-27 commit that wrote SKILL.md line 245 (the `souji-pre-report-gate` row) — a row with no
relation to this item. The frozen `where` cell (`SKILL.md:245`) makes the counter test that neighbour row's text
instead of the item's own row (246), so the honest cause is refused and a foreign cause is accepted.

### 3.7 G24 construction defect

```
git cat-file -e 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b:tools/souji-capability-agreement.py
fatal: path 'tools/souji-capability-agreement.py' exists on disk, but not in '9420341d9a814cb6089c25fb03a4cc9b23dc0d1b'
git log --diff-filter=A -- tools/souji-capability-agreement.py → d4928ec86b667e3d1ed0adb07fb088e500cf1631 (round-30)
```

The item's `at` pin came from the argv's `--rev 9420341d` (the do-nothing measured rev), not from the checkout the
script exists at. The counter checks the clone out at `at`, so no argv — corrected or not — can run the row's own
script for this item.

## 4. Consequence for the frozen C1 target

- `SUMMARY items=60 agree=60 mismatches=0` cannot be reached on the frozen item set: six SKILL items (G05, G11,
  G17a, G23, G24, and G17b honestly) have no accepted restatement, and the seventh (G21) only "agrees" through a
  cause the item's own row has nothing to do with.
- The one accepted path is the off-by-one false-accept, which is a Q75 cause-requirement bypass. It must not be
  used: it would land a restatement ledger whose cause column names commits unrelated to the cells.
- The honest repair options are the L1's alone (and none is a predicate loosening): correct the frozen `where`
  cells to the row the argv belongs to; correct G24's `at` to `{REV}`; widen the `files` set for G17a/G17b/G23 to
  the data the commands actually read; and re-derive G05/G17b predicates that do not encode `\t` into
  whitespace-collapsed matching. Because counter data already exists (the do-nothing control), any of these is a
  post-data change and has to be recorded as such — my report states the state, not a proposal to loosen anything.
