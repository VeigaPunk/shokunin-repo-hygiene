STATUS: PASS — For `carry-invariant-probe`, a duplicated stdout summary line produces `matched == False` under the base runner whether stderr is empty or not. The stderr repair MUST keep that result False, so this combination is a non-discriminating negative control and not a false green. Everything below comes from reading source only: nothing was executed, no tools were installed, no LSP device was used, and grep was used only on the named file `corpus/QUALITY.md`.

## Scope and inputs

I read only these named files:

- `census/round-21/run-acceptance.py`: `SUMMARY_RE` at line 118, the `carry-invariant-probe` step at lines 304–306, `failure_lines` at lines 330–333, and the summary branch of `summarize_result` at lines 347–419 and 481.
- `census/round-21/step-inventory.json`: lines 141–152.
- `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`: the HIGH finding on summary stderr.
- `.ufo/waves/round-22/preregistration.txt`
- `corpus/QUALITY.md`: grep only.

I did not need `census/round-14/cache-demonstration.py`, because this question involves only the summary branch.

## Step facts

These were observed in the source.

- Expected summary: `S = "SUMMARY paragraphs=400 boundary_cuts=562 midline_cuts=842 violations=0"`. The value is a `str`, and it matches the frozen inventory at lines 141–152.
- `pass_pattern` is `None` and `pass_count` is `0`. As a result, the pass-line check is always `0 == 0`, which is True.
- The step has no `baseline_mismatch_count`. Its auxiliary expectation is `[]`.
- After the general summary checks, this step also rejects any stdout line that starts with `VIOLATION\t` (lines 418–419).
- `summary_lines` is built from stdout only, using `SUMMARY_RE = ^(?:SUMMARY|SELFTEST)(?:\t| ).*$`. Stderr is used only in the `failure_lines` scan (line 353).

## How the base runner decides the duplicate case

This trace is inferred from source. The input is return code 0, `stdout = S\nS\n`, and any stderr `E` that contains no `FAIL\t`, `CASE\tFAIL\t`, or `CASE\t*\tFAIL` lines.

1. Line 352: `summary_lines` is `[S, S]`.
2. Line 353: `failures` is `[]`. Line 367 sets `matched` to `True`.
3. Line 373: `summary_match` compares `[S, S] == [S]`, which is False.
4. Lines 386–390: both auxiliary lists are `[]`, so the auxiliary check passes and `summary_match` stays False.
5. Lines 400–404: the pass count is 0 and expected passes are 0, so `pass_match` is True.
6. Line 417: `matched` becomes `True and False and True`, which is False. The `VIOLATION` check at line 419 leaves it False.
7. Line 481: `result["matched"]` is `False`.

The result does not depend on `E`: the duplicate summary alone already sets `matched` to False, so stderr never changes the decision.

## Expected decisions

`base` is what the source predicts for base `41553adb`. `fixed` is the literal expected decision once the summary branch requires empty stderr.

| id | rc | stdout | stderr | base | fixed | discriminating |
|---|---|---|---|---|---|---|
| D1 | 0 | `S\nS\n` | `""` | False | **False** | no; duplicate-only control |
| D2 | 0 | `S\nS\n` | `"Traceback (most recent call last):\n"` | False | **False** | no; this is the stderr/duplicate combination |
| D3 | 0 | `S\n` | `S + "\n"` | True | **False** | yes; the copy on stderr is invisible to `SUMMARY_RE` |
| P0 | 0 | `S\n` | `""` | True | **True** | no; positive control |

- **D2 is the assigned row.** The expected value is literally `matched == False` both before and after the repair.
- D3 is the closest row that does discriminate. The duplicate summary is split across the two streams, so base gives a false green. It falls in the same class as the round-21 HIGH summary-stderr finding.

## Compatibility requirements for the stderr repair

1. **Stderr must be one more condition, not a replacement.** The repair MUST be an added conjunct, for example `matched = matched and summary_match and pass_match and not stderr`. It MUST leave the exact-list equality `summary_lines == [expected]` at line 373 unchanged. Deduplicating summary lines, testing `expected in summary_lines`, or checking `len(set(...)) == 1` would turn D1 into a false green. D1 and D2 are the regression guard against that.
2. **Summary extraction must keep reading stdout only.** `SUMMARY_RE` and the stdout-only extraction MUST stay as they are. D3 has to be rejected because stderr is not empty, not because stderr summaries start being counted.
3. **Empty means zero bytes.** "Empty stderr" means `stderr_bytes == b""`. It is equivalent to `not stderr` after `decode_exact`, because decoding with surrogateescape never produces an empty string from non-empty bytes. Stderr that is only whitespace (`"\n"`) MUST count as non-empty.
4. **The step inventory must not change.** The repair belongs in `summarize_result` logic, not in step data. The output of `inventory_projection(...)` must still equal the frozen `step-inventory.json` steps. Otherwise line 601 raises the Refusal "acceptance commands differ from the frozen r20 inventory".
5. **All 18 real positive controls must still match.** [INFERENCE, UNVERIFIED] Requiring empty stderr on every summary step assumes that all 11 real summary steps write nothing to stderr when they succeed. `CHILD_ENV` does not set `PYTHONWARNINGS`, so a warning on stderr could flip a real positive control to False. I could not read historical acceptance records, which are outside the named files. L1's acceptance run is the evidence that settles this.
6. **The production code under review stays untouched.** None of this affects the F5 parser/formatter or its 160-byte reason scope.

## Draft oracle rows

This is not written anywhere else. `summarize_result` takes `revision` and `root`, but the summary branch never uses them, so placeholder values are fine.

```python
S = b"SUMMARY paragraphs=400 boundary_cuts=562 midline_cuts=842 violations=0"
CARRY_STEP = {
    "name": "carry-invariant-probe", "argv": ["<PYTHON>", "-B", "<ROOT>/census/round-19/probe-carry-invariants.py"],
    "expected_summary": S.decode(), "pass_pattern": None, "pass_count": 0,
}
CARRY_DUP_VECTORS = (
    # (id, returncode, stdout, stderr, expected_matched_after_fix, base_matched)
    ("carry-dup-stdout-empty-stderr", 0, S + b"\n" + S + b"\n", b"", False, False),
    ("carry-dup-stdout-nonempty-stderr", 0, S + b"\n" + S + b"\n", b"Traceback (most recent call last):\n", False, False),
    ("carry-summary-duplicated-on-stderr", 0, S + b"\n", S + b"\n", False, True),
    ("carry-positive-control", 0, S + b"\n", b"", True, True),
)
# for vid, rc, out, err, want, _ in CARRY_DUP_VECTORS:
#     assert summarize_result(CARRY_STEP, rc, out, err, "0"*40, Path("/nonexistent"))["matched"] is want, vid
```

## Remaining unknowns

- Whether every real summary step writes nothing to stderr on success, as requirement 5 assumes. This needs L1's acceptance run.
- Whether a sibling seat already owns D3. The duplicate-on-stderr case belongs to the general summary-stderr class.

Report: .ufo/waves/round-22/w1/Stderr10.md
