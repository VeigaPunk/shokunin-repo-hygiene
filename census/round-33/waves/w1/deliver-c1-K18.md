# C1 K18 — SCORECARD.md:175 restatement (argv correction)

Item: K18, SCORECARD.md:175 at base 6017a482e7068d5afb7617640198fbb0fe743357; frozen exit `0`;
frozen predicate `\b9/9\b || \bcases=9 pass=9\b`; files tests/fixtures/r24-coverage-agreement.py,tools/souji-coverage-agreement.py;
frozen argv `python3 tests/fixtures/r24-coverage-agreement.py`.

Kind: ARGV CORRECTION (the row names the fixture without its required `--tool`). NOT value drift.

## Row (append under `### Round 33 capability currency`)

ROW-BEGIN
| K18 | SCORECARD.md:175 | restated | 0 | `python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py` | `cases=9 pass=9 control=FALSE-GREEN-REJECTED` | 07f83e69979b1032f9de4fe876739a8dccc7242b | the r26 row wrote the fixture without its required --tool argument; with the tool the fixture prints its 9/9 summary |
ROW-END

Full appended block as proved in scratch (header + table header + row):

```
### Round 33 capability currency (C1, appended)

| id | row | status | exit | run | statement | cause | reason |
|---|---|---|---|---|---|---|---|
| K18 | SCORECARD.md:175 | restated | 0 | `python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py` | `cases=9 pass=9 control=FALSE-GREEN-REJECTED` | 07f83e69979b1032f9de4fe876739a8dccc7242b | the r26 row wrote the fixture without its required --tool argument; with the tool the fixture prints its 9/9 summary |
```

## Receipts

Scratch: `/fast/scratch/hyaku/souji-r33/RestateK18/` (`TMPDIR=$D/tmp`, fresh subdir per run).
Clone: `git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin $D/c`, origin removed at once,
`git -C $D/c rev-parse --show-toplevel` -> `/fast/scratch/hyaku/souji-r33/RestateK18/c`,
detached at `2d9bca55a9f042a2c9ed60a797a8069e74c41f46` (preregistration commit).

### 1. Frozen argv, 3 runs, fresh TMPDIR each (cwd = clone root, GIT_CONFIG_NOSYSTEM=1)

`python3 tests/fixtures/r24-coverage-agreement.py`

run 1: `rc=2`; stdout digit lines: (none); stderr digit lines:
```
usage: r24-coverage-agreement.py [-h] --tool TOOL
r24-coverage-agreement.py: error: the following arguments are required: --tool
```
run 2: `rc=2`; identical stderr lines; stdout digit lines: (none).
run 3: `rc=2`; identical stderr lines; stdout digit lines: (none).

So the row's own command produces NO statement carrying the claim and exits 2, not 0.

### 2. The argv that carries the claim

`python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py` -> `rc=0`.
Complete stdout lines carrying digits (the last is the summary chosen as the statement):
```
case=1 name=clean-map expect: grounded=2 mapped=* dangling=0 mismatches=0 rows=[none] exit=0 ; got: grounded=2 mapped=2 dangling=0 mismatches=0 rows=[none] exit=0 -> pass
...
case=9 name=rev-not-full40 expect: exit=2 for --rev in ['d42791e10f4d', 'HEAD', 'd42791e10f4dd237d13b1b4717dc5e260daf731z'] ; got: exits=[2, 2, 2] -> pass
control case=1 got: ... -> FAIL
...
control case=9 got: exits=[0, 0, 0] -> FAIL
cases=9 pass=9 control=FALSE-GREEN-REJECTED
```

### 3. Cause: which commit wrote the CURRENT line-175 text

```
git -C $D/c log -L175,175:SCORECARD.md --format='COMMIT %H %ad %s' --date=short
COMMIT 07f83e69979b1032f9de4fe876739a8dccc7242b 2026-10-25 round-26 C1 fix: append the two r24 capability rows (debris census, coverage-map agreement) after record-agreement row — wave ExecC1Surgery found omission; spans re-verified byte-equal
+| coverage-map agreement (r24) | at a full 40-hex revision, ... (one commit touches the line; no later commit changes it)
```
Byte checks against the line text at --list-rev (2d9bca55), line 175:
`IN_PARENT(d6fe8a1125a9723e7593df7b8b90ee6c05cdf9ff)=False`, `IN_CAUSE(07f83e69...)=True`.
The cause's parent is `d6fe8a1125a9723e7593df7b8b90ee6c05cdf9ff`.

Line 175 (base) evidence cell, verbatim tail: `tests/fixtures/r24-coverage-agreement.py` 9/9 (`c2-fixture-after.tsv`) —
the row names the fixture with no argument.

### 4. Bare argv fails at the cause (clone at 07f83e69, origin removed)

`python3 tests/fixtures/r24-coverage-agreement.py` -> `rc=2`;
`usage: r24-coverage-agreement.py [-h] --tool TOOL` / `r24-coverage-agreement.py: error: the following arguments are required: --tool`.
`python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py` -> `rc=0`,
last line `cases=9 pass=9 control=FALSE-GREEN-REJECTED`.

`--tool` has been `required=True` since the fixture's first version, 1efe406e7f39b8fe736be2a566053703a571ffc0
(line 331: `ap.add_argument("--tool", required=True)`): the row's command never produced its stated outcome.

### 5. Scratch landing + counter (the proof)

Appended the block above to SCORECARD.md at 2d9bca55 in the scratch clone; committed with throwaway identity:
scratch landing commit `dfaf5de87623cd9c72f98602428d75fb7b974222`.

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-33/c1-counter.py \
  --root /fast/scratch/hyaku/souji-r33/RestateK18/c \
  --rev dfaf5de87623cd9c72f98602428d75fb7b974222 \
  --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
  --scratch /fast/scratch/hyaku/souji-r33/RestateK18/cnt --only K18
ITEM	K18	AGREE	restated	rc=0 expect_exit=0 statement is an output line last=cases=9 pass=9 control=FALSE-GREEN-REJECTED
SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=dfaf5de87623cd9c72f98602428d75fb7b974222
counter rc=0
```

## Growth or regression?

Neither: NO change in case count and NO capability lost. The fixture shipped with 9 cases at its first version
(1efe406; cases 1-9 in `make_cases`) and prints `cases=9 pass=9` at the cause and at base; the fitted control
still rejects the always-zero emitter on all nine control cases (`control=FALSE-GREEN-REJECTED`). The only defect is
that the r26-added row documented a command the fixture refuses (missing required `--tool`). Not reported as a
regression.

## Scratch cleanup

`/fast/scratch/hyaku/souji-r33/RestateK18` removed after these receipts were copied (the counter's own `--scratch`
work dir was already self-removed).
