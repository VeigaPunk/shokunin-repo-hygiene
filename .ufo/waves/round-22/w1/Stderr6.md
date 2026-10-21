STATUS: PASS — source-only. For the `r19-carry-wrap` summary step, a successful process (exit 0) that prints the exact expected stdout plus warning text on stderr is a false green in the current summarizer. Source reading predicts `matched == True` on base. The literal expected decision after the repair is `matched == False`. The paired empty-stderr control MUST stay `True`. Nothing was executed: no runner, fixture, test, build, git command, or probe.

## Axes

- calibration: the warning-text row turns a predicted false green into an expected red.
- operability: the change is one predicate line, with no new step key and no change to the environment.
- coverage: the row adds one distinct stderr shape, warning text that is not a failure marker. The paired positive control is retained.

No trade-off between axes is proposed.

## Observed facts (source, `census/round-21/run-acceptance.py`, working-tree bytes)

1. `make_steps` defines `r19-carry-wrap` (lines 294–296) with:
   - kind `summary` (the default)
   - `expected_summary` = `"SUMMARY total=4 failed=0 base_discriminating=2"`
   - `pass_pattern` = `r"^CASE\tpass\tchanged/"`
   - `pass_count` = 4

   The frozen row in `census/round-21/step-inventory.json` (lines 86–99) has the same values.
2. `failure_lines` (lines 330–333) flags only lines that start with `FAIL\t` or `CASE\tFAIL\t`, or that match `^CASE\t[^\t]+\tFAIL(\t|$)`. It scans stdout and stderr together (line 353).
3. The summary branch decides with `matched = returncode == 0 and not failures` (line 367), then `matched and summary_match and pass_match` (line 417). It never consults `stderr`.
4. The counter branch (line 445) and the cache-demo branch (line 480) both end with `and not stderr`. This is an exact-empty test on the decoded `str`.
5. `pass_count` counts stdout only (line 401). `SUMMARY_RE` also matches stdout only (line 352).
6. `inventory_projection` (lines 537–552) projects only the keys `name`, `expected_summary`, `pass_pattern`, `pass_count`, `record_checks`, `exact_json`, `baseline_mismatch_count`, and `kind`, plus the normalized `argv`. `main` refuses to run if that projection differs from the frozen inventory (lines 600–602).
7. `CHILD_ENV` (lines 107–117) does not set `PYTHONWARNINGS`. With CPython's default filters, a `DeprecationWarning` triggered in `__main__` is shown on stderr. [INFERENCE from Python's documented defaults; the documentation was not opened this round.]
8. `all_matched` is `all(item["matched"] …)` (line 642), and the exit code depends on it (line 655).

## Vector: r19-carry-wrap / stderr warning text

Inputs, passed directly to `summarize_result(step, returncode, stdout_bytes, stderr_bytes, revision, root)`:

- `step`: the `r19-carry-wrap` row exactly as `make_steps` builds it (or the frozen inventory row with placeholder argv). For the summary kind, `revision` and `root` are unused.
- `returncode`: `0`
- `stdout`: four lines matching `^CASE\tpass\tchanged/` (real tab characters; synthetic case names) plus exactly one line `SUMMARY total=4 failed=0 base_discriminating=2`. There are no `INVENTORY\t`, `FAIL`, or `VIOLATION\t` lines.
- `stderr`: `b"tests/fixtures/r19-carry-wrap.py:1: DeprecationWarning: synthetic warning text\n"`. It contains no line starting with `FAIL\t` or `CASE\t`.

Base evaluation, traced through the source:

- `failures` is `[]`.
- `summary_lines` equals `[expected]`.
- Observed auxiliary lines `[]` equal the expected `[]`.
- There is no `baseline_mismatch_count` key.
- The pass count of 4 equals the expected 4.
- The step is not `carry-invariant-probe`.

The result is `matched = True`, which is the false green.

| row | returncode | stdout | stderr | base `matched` (source-inferred) | literal expected `matched` after repair |
|---|---|---|---|---|---|
| r19-carry-wrap/stderr-warning-text | 0 | exact (4 CASE pass + SUMMARY) | warning text (above) | `True` | **`False`** |
| r19-carry-wrap/stderr-empty-control | 0 | identical | `b""` | `True` | **`True`** |

Two sub-variants should get the same expected value, `False`, if L1 wants extra rows:

- stderr `b"WARNING: synthetic\n"`.
- stderr `b"warning: may FAIL\tlater\n"`. Here `FAIL` is not at the start of the line, so `failure_lines` still misses it.

Neither sub-variant is needed for the claim.

## Draft repair (one line, summary branch, line 417)

```python
        matched = matched and summary_match and pass_match and not stderr
```

## Compatibility requirements

- **C1, consistent predicate.** Use `not stderr` on the decoded string, the same test the counter and cache-demo branches use. Do not use `.strip()`, a `warning`/`DeprecationWarning` allow-list, or any prefix filter, because each of these reopens the false green for this row.
- **C2, no environment suppression.** Do not add `PYTHONWARNINGS`, `-W ignore`, or any other `CHILD_ENV` or argv change to silence warnings. That would hide the signal, and argv changes would also break the frozen-inventory equality check.
- **C3, frozen inventory unchanged.** Do not add a new projected step key. A branch-level rule keeps `inventory_projection(...) == frozen["steps"]` byte-equal. A new key outside the projection list would be ignored by the check but is still unnecessary.
- **C4, real positive controls.** All 18 real acceptance steps must still match. For `r19-carry-wrap` and the other 13 summary-kind steps, the repair is compatible only if each real successful run writes zero stderr bytes. This was not observed. The fixture `tests/fixtures/r19-carry-wrap.py` is not a named file, so whether it captures or inherits stderr from the base and changed landing-gate child processes is unknown. L1 check: in the existing r21 acceptance record and in the post-repair run, every summary step's `stderr_sha256` must equal `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, the SHA-256 of empty input. If any r21 summary step had non-empty stderr while `matched=True`, its historical outcome projection changes. That must be disclosed as a changed projection, not suppressed.
- **C5, F5 untouched.** The repair touches only `summarize_result`. F5 code and the 160-byte reason scope stay byte-identical to base.

## Unknowns and limits

- I read working-tree bytes of `census/round-21/run-acceptance.py`. Byte identity with base `41553adb139d06511dc386bb3ce4326aebfba675` was not verified, because git was not run.
- The `r19-carry-wrap` fixture's real stderr behavior is unobserved; see C4.
- `census/round-14/cache-demonstration.py` was not needed for this stderr row and was not read.
- No LSP device is available in this toolset. `summarize_result` was traced by reading the single named file. No grep was used, and no semantic-caller proof is claimed.
- No tools were installed.

Report: .ufo/waves/round-22/w1/Stderr6.md
