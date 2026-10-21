STATUS: PASS — I derived the literal success contract for `r18-landing-pointers` from the source of `census/round-21/run-acceptance.py` and `census/round-21/step-inventory.json`. The report gives one positive vector, one uniquely relevant wrong-summary vector (plus a pass-count alternate), and the stderr-policy impact. Everything here comes from reading source. Nothing was executed, and no tools were installed.

## Contract (observed in source)

The step definition is at `census/round-21/run-acceptance.py:299-300`, and the frozen copy at `census/round-21/step-inventory.json:113-126` is byte-equivalent:

- `argv`: `<PYTHON> -B <ROOT>/tests/fixtures/r18-landing-pointers.py --tool <ROOT>/tools/souji-landing-gate.py`
- `kind`: `summary`, because no `kind` key means the default at line 368.
- `expected_summary`: the **string** `"SUMMARY\ttotal=11\tfailed=0"`. It uses tabs and has no `pass=` or `base_discriminating=` field.
- `pass_pattern`: `r"^CASE\tPASS\t"`. It is case-sensitive and uppercase, unlike the lowercase `pass` pattern in the r19 and rev-pin rows.
- `pass_count`: 11. The row has no `record_checks` and no `baseline_mismatch_count`, and it is not the `carry-invariant-probe` row.

`summarize_result` (lines 347-419) sets `matched` to true only when **all** of the following conditions hold:

1. `returncode == 0` (line 367).
2. `failure_lines(stdout + sep + stderr)` is empty (lines 330-333 and 353). A failure line is any line, in stdout or stderr, that starts with `FAIL\t` or `CASE\tFAIL\t`, or that matches `^CASE\t[^\t]+\tFAIL(\t|$)`.
3. `summary_lines == ["SUMMARY\ttotal=11\tfailed=0"]` (line 373). Here `summary_lines` is every stdout line, split with `splitlines()`, that matches `^(?:SUMMARY|SELFTEST)(?:\t| ).*$` (line 118). The comparison is exact list equality, so a duplicate or extra `SUMMARY`/`SELFTEST` line fails.
4. `observed_auxiliary == []` (lines 386-389): stdout contains no line starting with `INVENTORY\t`.
5. `len(re.findall(r"^CASE\tPASS\t", stdout, re.M)) == 11` (lines 401-404). This is an exact count, not a minimum, and it scans stdout only.
6. Stderr is not checked at all beyond condition 2. Compare the counter branch (line 445) and the cache-demo branch (line 480), which both require `not stderr`.

## Positive vector (derived; synthetic case IDs)

The real case names live in `tests/fixtures/r18-landing-pointers.py`, which is not in my named read set. So the IDs below are placeholders, and the contract does not constrain them.

```text
returncode = 0
stderr     = b""
stdout     =
CASE\tPASS\tp01
CASE\tPASS\tp02
CASE\tPASS\tp03
CASE\tPASS\tp04
CASE\tPASS\tp05
CASE\tPASS\tp06
CASE\tPASS\tp07
CASE\tPASS\tp08
CASE\tPASS\tp09
CASE\tPASS\tp10
CASE\tPASS\tp11
SUMMARY\ttotal=11\tfailed=0
```

(`\t` means one TAB byte, and each line ends with `\n`.) The expected decision is `matched=True` on both the base and the repaired implementation. The resulting `matched_counts` are `summary_lines=1`, `expected_pass_lines=11`, `observed_pass_lines=11`, `matched_pass_lines=11`, `expected_auxiliary_lines=0`, and `observed_auxiliary_lines=0`.

## Uniquely relevant wrong vector

**Primary (wrong summary, separator only).** Use the positive vector above, but replace the last line with `SUMMARY total=11 failed=0`, using spaces instead of tabs. Return code stays 0 and stderr stays empty.

- This line is byte-identical to the expected summary of the `revision-helper-selftest` row (line 279) apart from the separators. It still matches `SUMMARY_RE`, which accepts a tab or a space, so it is collected as a summary line, and the pass count is still 11.
- The expected decision is `matched=False`, because `["SUMMARY total=11 failed=0"] != ["SUMMARY\ttotal=11\tfailed=0"]`.
- Why this vector matters: it is the one mutation that a whitespace-normalizing or shared-literal "repair" of the summary comparison would silently turn green. It pins exact per-step literal comparison while the summarizer is being edited.

**Alternate (wrong pass count, case vocabulary).** Use the positive vector, but write all 11 case lines as `CASE\tpass\tpNN`, lowercase as in the r19 rows, with the correct summary, return code 0 and empty stderr.

- The observed pass lines drop to 0 against 11 expected, so the expected decision is `matched=False`.
- No failure line is emitted, so only the pass-count gate catches this vector.
- A related trap: a lowercase `CASE\tfail\tx` line is **not** a recognized failure line. In that case, too, the pass-count equality (10 against 11) is the only rejecting gate.

## Stderr policy impact

- **Base (source-inferred):** take the positive stdout with `stderr = b"Traceback (most recent call last):\n...\nRuntimeError: x\n"`. The base implementation returns `matched=True`, which is a false green. That is the r21 HIGH summary-stderr defect, and it applies to this row. If stderr instead contains `FAIL\tx` or `CASE\tFAIL\tx`, the base already returns `matched=False` through `failure_lines`.
- **Repair:** add `and not stderr` to the summary branch, mirroring lines 445 and 480. With that change, the Traceback vector becomes `matched=False`, and the positive vector (empty stderr) stays `matched=True`.
- **Risk to the retained real positive control (UNRESOLVED, inference):** a strict empty-stderr policy turns the real `r18-landing-pointers` control green only if the real fixture writes **zero** stderr bytes on success. The fixture drives `tools/souji-landing-gate.py`. If it lets the gate child inherit stderr instead of capturing it, refusal diagnostics from negative cases would reach the fixture's stderr, and the real control would turn red under the repair. I could not verify this because the fixture source is outside the named read set and execution is forbidden. L1's post-integration acceptance run is the deciding evidence: the r18 record must show `stderr == ""`, i.e. `stderr_sha256 == e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. If it does not, the stderr policy needs a reviewed per-step exception rather than a blanket rule.
- **Matrix note:** the r21 matrix signature omits stderr (`AttackRunnerStepResults.md`, "Matrix / residual risk"). Stderr-only differences on this row are therefore invisible to selected-summary parity unless the repair gates `matched` on stderr.

## Remaining unknowns

- The real r18 case IDs, the real stdout shape, and whether the real fixture emits stderr on success. All three depend on the fixture source or an executed run, which are not available to this leaf.
- The historical r21 recorded r18 `stderr`. Historical outputs are not in the named read set.
