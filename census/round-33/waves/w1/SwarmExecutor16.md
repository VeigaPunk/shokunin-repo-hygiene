# SwarmExecutor16 — r33 w1, C1 item K18

## Status

STATUS: PASS — K18 is an argv correction; one honest appended restatement row proved AGREE by the frozen counter at a scratch landing commit (`mismatches=0`), and the change is neither growth nor regression.

## Evidence

- Preregistration read first: `census/round-33/preregistration.txt` at lane base `6017a482e7068d5afb7617640198fbb0fe743357`; counter contract read at `census/round-33/c1-counter.py` (docstring + `judge`).
- Scratch: `/fast/scratch/hyaku/souji-r33/RestateK18/`; clone `git clone -q --no-local <lane> $D/c`, origin removed, `rev-parse --show-toplevel` = the clone path, detached at `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`; `TMPDIR=$D/tmp`, fresh subdir per run.
- Frozen argv `python3 tests/fixtures/r24-coverage-agreement.py`, three runs at 2d9bca55: each `rc=2`; no stdout digit line; stderr `usage: r24-coverage-agreement.py [-h] --tool TOOL` and `r24-coverage-agreement.py: error: the following arguments are required: --tool`.
- `python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py` -> `rc=0`, last line `cases=9 pass=9 control=FALSE-GREEN-REJECTED`.
- Cause: `git -C $D/c log -L175,175:SCORECARD.md` names `07f83e69979b1032f9de4fe876739a8dccc7242b` (round-26 C1 fix: append the two r24 capability rows), and no later commit changes that line. Line-175 text at 2d9bca55 is absent from SCORECARD.md at the cause's parent `d6fe8a1125a9723e7593df7b8b90ee6c05cdf9ff` and present at the cause (`False`/`True`).
- Bare argv at the cause (separate scratch clone at 07f83e69): `rc=2`, same missing-`--tool` error; `--tool` has been `required=True` since the fixture's first version `1efe406e7f39b8fe736be2a566053703a571ffc0` (line 331).
- Proof: appended `### Round 33 capability currency (C1, appended)` + table header + row to SCORECARD.md at 2d9bca55 in scratch, committed as `dfaf5de87623cd9c72f98602428d75fb7b974222`; counter with `--only K18` printed `ITEM K18 AGREE restated rc=0 expect_exit=0 statement is an output line last=cases=9 pass=9 control=FALSE-GREEN-REJECTED` and `SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=dfaf5de87623cd9c72f98602428d75fb7b974222`, exit 0.
- Scratch dir removed after receipts were copied; no lane file written outside `.ufo/waves/round-33/w1/`.

## Findings

1. K18 cause is the r26 row-writing commit `07f83e69979b1032f9de4fe876739a8dccc7242b`, not a value-drift commit: the fixture's `--tool` has been required since r24 (`1efe406`, `tests/fixtures/r24-coverage-agreement.py:331`), so the row's documented command never produced `9/9` — at `SCORECARD.md:175` (base `6017a482`).
2. No growth, no regression: the fixture has 9 cases at its first version and at base, all pass, and the always-zero control is rejected on all nine cases (`control=FALSE-GREEN-REJECTED`, also committed in `census/round-24/records/c2-fixture-after.tsv`). The row's stated count was right; only its argv was incomplete.
3. The L1 feasibility leg's cause for K18 is confirmed as the commit that wrote the current line-175 text, and its restated argv/statement reproduce at base within tolerance of the frozen rules (my row uses the same argv and statement).

## Attack log

n/a — K18 is a restatement item, no frozen predicate/target/counter/leg is challenged.

## Deliveries

- `.ufo/waves/round-33/w1/deliver-c1-K18.md` — row verbatim between ROW-BEGIN/ROW-END, full appended block, all receipts, growth/regression verdict.
- `.ufo/waves/round-33/w1/SwarmExecutor16.md` — this report.
