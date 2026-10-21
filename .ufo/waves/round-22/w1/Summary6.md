STATUS: PASS — r19-carry-wrap literal success contract derived from source; one positive stdout vector, one uniquely relevant wrong pass-count vector (plus summary alternates), and the stderr-policy impact are given below. Source-inferred only: nothing was run, built, or probed.

## Axes
- calibration: does each vector produce exactly the expected `matched` result, at base and after the change?
- operability: the vectors call `summarize_result` directly with no process, no /proc access and no fixture execution.
- coverage: the step-specific literals covered are the `changed/` prefix, `base_discriminating=2`, and the space separator.

## Observed contract (source)
- Step row: `census/round-21/run-acceptance.py` lines 294–296. It is identical to the frozen row in `census/round-21/step-inventory.json` lines 86–99:
  - `expected_summary`: `"SUMMARY total=4 failed=0 base_discriminating=2"` (the separator is a SPACE, not a tab)
  - `pass_pattern`: `^CASE\tpass\tchanged/`
  - `pass_count`: 4
  - `kind`: `summary`
  - argv: `<PYTHON> -B <ROOT>/tests/fixtures/r19-carry-wrap.py --tool <ROOT>/tools/souji-landing-gate.py`
- Summary-branch predicate (`summarize_result`, lines 347–419). `matched` is true only when all of the following hold:
  1. `returncode == 0`.
  2. `failure_lines(stdout + "\n" + stderr)` is empty. It recognizes only `FAIL\t`, `CASE\tFAIL\t` and `CASE\t<x>\tFAIL`, and the match is case-sensitive.
  3. The stdout lines matching `SUMMARY_RE` (`^(?:SUMMARY|SELFTEST)(?:\t| ).*$`) equal the exact one-element list `["SUMMARY total=4 failed=0 base_discriminating=2"]`.
  4. There are zero stdout lines starting with `INVENTORY\t` (the expected auxiliary list is `[]`).
  5. `len(re.findall(pass_pattern, stdout, re.MULTILINE)) == 4`. Only stdout is counted; pass lines on stderr do not count.
  6. There is no `baseline_mismatch_count` gate (the key is absent) and no `VIOLATION` gate (that gate applies only to `carry-invariant-probe`).
- stderr is never gated in the summary branch, except through the FAIL-marker scan. The counter branch (line 445) and the cache-demo branch (line 480) require `not stderr`.

## P1 — valid positive (expected matched=True at base and after the change)
```python
P1 = dict(step_name="r19-carry-wrap", returncode=0, stderr=b"",
          stdout=(b"CASE\tpass\tchanged/a\n"
                  b"CASE\tpass\tchanged/b\n"
                  b"CASE\tpass\tchanged/c\n"
                  b"CASE\tpass\tchanged/d\n"
                  b"SUMMARY total=4 failed=0 base_discriminating=2\n"),
          expected_matched=True)
# expected matched_counts: summary_lines=1, expected_pass_lines=4, observed_pass_lines=4,
# matched_pass_lines=4, expected/observed/matched_auxiliary_lines=0/0/0,
# baseline_mismatch_records=0, baseline_mismatches_reported=None, record_checks=0
```
The case suffixes `a`–`d` are synthetic. The real fixture's case names were not read because the file is outside the named-read contract. The predicate is suffix-agnostic past `changed/`.

## N1 — uniquely relevant wrong pass-count vector (expected matched=False at base and after the change)
```python
N1 = dict(P1, stdout=(b"CASE\tpass\tchanged/a\n"
                      b"CASE\tpass\tchanged/b\n"
                      b"CASE\tpass\tchanged/c\n"
                      b"CASE\tpass\tbase/d\n"
                      b"SUMMARY total=4 failed=0 base_discriminating=2\n"),
          expected_matched=False)  # observed_pass_lines=3 != 4; only pass_match fails
```
This isolates the step-specific `changed/` prefix anchor. Every other predicate holds, so a regression that loosened the pattern to `^CASE\tpass\t` would flip it to True.

Alternate negatives for the summary literal. Each fails only `summary_match`:
- `N1b`: `SUMMARY total=4 failed=0 base_discriminating=1` (wrong discriminating count; the value is step-unique, since seat-audit uses 12 and rev-pin uses 6).
- `N1c`: `SUMMARY\ttotal=4\tfailed=0\tbase_discriminating=2`. It still matches `SUMMARY_RE`, but the separator differs, so string equality fails. This step is space-separated, unlike r18/r16/r20.
- `N1d`: the SUMMARY line is missing. Then `[] != [expected]`.
- `N1e`: the SUMMARY line is duplicated. The list has length 2.

## Stderr-policy impact
- `S1`: the stdout of P1, `returncode=0`, and `stderr=b"Traceback (most recent call last):\n  ...\nRuntimeError: carry gate crashed\n"`.
  - At base: `matched=True` (a false green), because no FAIL marker appears and the summary branch never checks stderr.
  - After the change: it is REQUIRED to be False.
  - This is the r21 HIGH finding (`.ufo/waves/round-21/w2/AttackRunnerStepResults.md`), applied to this step.
- `S2` (control): P1 plus `stderr=b"CASE\tFAIL\tchanged/e\n"`. It is already False at base through `failure_lines`, which scans stderr. It must stay False.
- Minimal repair drafted at the shape used by the other branches. It is not applied, because the code belongs to L1:
```python
        matched = matched and summary_match and pass_match and not stderr
```
- Inventory interaction: `inventory_projection` (lines 537–552) copies only fixed keys. A code-level stderr gate therefore leaves the frozen `step-inventory.json` rows unchanged. A new per-step key, such as `"stderr": "empty"`, would not be frozen or projected.
- [INFERENCE] Positive-control risk: a uniform `not stderr` gate turns this real step red if `tests/fixtures/r19-carry-wrap.py` lets output from `souji-landing-gate.py` reach the fixture's stderr on success. I could not determine this: the fixture and historical acceptance records are outside the named reads. L1 SHOULD confirm before landing that the retained r19-carry-wrap `stderr_sha256` equals `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty) in the real 18-step positive-control run. The same check applies to all 12 summary-kind steps.

## Bounded residual (outside the three-defect claim; reported, not claimed)
- `failure_lines` is case-sensitive. Pass rows here are lowercase (`CASE\tpass\t`), so [INFERENCE] fail rows from this fixture would be `CASE\tfail\t…`, and those are not failure lines.
- `R1`: P1 plus an extra `CASE\tfail\tchanged/e` line, with the summary unchanged (`total=4`). It gives `matched=True` at base, and still True after the stderr repair.
  - Detection of a fixture-level failure rests entirely on the self-reported `SUMMARY failed=0` and on `pass_count==4`.
  - Unreported extra CASE rows are not counted.
- This is not one of the admitted r21 OPEN defects. Any action on it is L1's call; this report makes no claim about it.

## Verification / gaps
- Read:
  - `census/round-21/run-acceptance.py` (complete)
  - the r19-carry-wrap row of `census/round-21/step-inventory.json`
  - `.ufo/waves/round-22/preregistration.txt`
  - `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`
  - a targeted grep of `corpus/QUALITY.md` (Q25/Q36/Q48 rows)
- `census/round-14/cache-demonstration.py` was not needed for this step and was not opened.
- No LSP device is mounted in this session, so there are no semantic definition or reference results. The definitions above come from direct reads of a single file.
- All `matched` expectations are inferred from source, not executed. No tools were installed.

Report: .ufo/waves/round-22/w1/Summary6.md
