STATUS: PASS — scoped source inspection completed; vectors below are source-inferred, not executed.

## Axes
Calibration: literal, independently specified expected decisions. Operability: preserve the existing zero-pass-line positive case. Coverage: isolate exact-summary rejection and nonempty-stderr rejection without changing production scope. No axis trade proposed.

## Observed contract and trace
- `census/round-21/run-acceptance.py:304-306`, `make_steps`: `carry-invariant-probe` runs the round-19 probe with expected summary `SUMMARY paragraphs=400 boundary_cuts=562 midline_cuts=842 violations=0`, `pass_pattern=None`, `pass_count=0`.
- `census/round-21/step-inventory.json:141-152` independently records the same literal and `kind="summary"`.
- `run-acceptance.py:118`: `SUMMARY_RE` recognizes lines beginning `SUMMARY` or `SELFTEST` followed by tab or space. `summarize_result` collects matching stdout lines (`:350-352`); the string contract requires the entire collected list to equal the singleton expected line (`:372-374`). Missing, changed, or duplicated recognized summaries therefore reject.
- `summarize_result:386-390` also requires no `INVENTORY\t` lines for this step; `:400-404` yields observed pass count zero unconditionally because the pattern is absent. This is not a probe with missing required PASS records: zero is the intended count, regardless of PASS-looking text.
- Common gates require return code zero and no recognized failure lines (`:353,367`). `failure_lines:330-333` recognizes `FAIL\t`, `CASE\tFAIL\t`, and `CASE\t<field>\tFAIL` forms. The carry-specific additional gate rejects stdout lines starting `VIOLATION\t` (`:418-419`), even if the summary claims zero violations.
- Caller trace: the acceptance loop captures stdout/stderr and return code separately (`:614-619`), passes them to `summarize_result` (`:623`), and appends that result (`:626`). These are literal source traces, not language-server semantic proof: `xd://lsp` is unavailable (device discovery returned `No such tool`), so no server answered this file and text fallback was used.

## Two literal oracle vectors
These are standalone synthetic inputs to the actual step returned by `make_steps`, with its existing metadata unchanged. Byte strings use Python escape notation; they are drafts only.

Positive:
```python
returncode = 0
stdout_bytes = b"SUMMARY paragraphs=400 boundary_cuts=562 midline_cuts=842 violations=0\n"
stderr_bytes = b""
expected_matched = True
```
Source-inferred counts: one summary, zero expected and observed pass lines, zero auxiliary lines, no failure/violation records. The single trailing newline is consumed by `splitlines()`.

Uniquely relevant wrong-summary negative (only `paragraphs` changes, avoiding failure-line, nonzero-exit, stderr, and carry-violation confounders):
```python
returncode = 0
stdout_bytes = b"SUMMARY paragraphs=401 boundary_cuts=562 midline_cuts=842 violations=0\n"
stderr_bytes = b""
expected_matched = False
```
Source-inferred cause: singleton summary equality fails; pass count still correctly equals zero. This tests the carry-specific literal numerical summary, not generic missing PASS counting. Both existing and repaired implementations should retain these decisions.

## Stderr policy impact
Observed current defect: the summary branch finishes at `:417-419` without requiring empty stderr, whereas counter and cache-demo branches explicitly require it (`:445,480`). Stderr is scanned for recognized failures and retained/hashed, but ordinary nonempty stderr does not independently reject.

Discriminating derivative of the positive vector:
```python
stderr_bytes = b"warning: synthetic carry diagnostic\n"
# Keep positive returncode and stdout unchanged.
expected_current_matched = True
expected_repaired_matched = False
```
The repaired expectation follows `.ufo/waves/round-22/preregistration.txt:1`, which explicitly admits summary stderr accepted despite success as an OPEN defect. Any nonempty stderr, including whitespace, should lose acceptance under an empty-stderr policy; the valid positive remains green. A `VIOLATION\t...` line on stderr also evades the current carry-specific stdout-only check and generic failure patterns; the empty-stderr policy closes that route without moving the violation parser. Recognized `FAIL\t...` stderr already rejects, so it is not an independently discriminating repair vector.

## Confidence and bounds
High confidence in the literal summarizer contract and derived decisions; no tests, probes, builds, subprocesses, or production edits were run. Probe producer source was outside the named readable files and was not opened: the positive is a valid acceptance input, not a claim about complete real producer output. Historical/base byte identity and final integration behavior were not assessed. No tools were installed or updated.

Report: .ufo/waves/round-22/w1/Summary10.md
