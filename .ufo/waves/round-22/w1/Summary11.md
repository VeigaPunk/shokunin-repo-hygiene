STATUS: PASS

Seat: SoujiR22.Summary11 (scout, leaf). Scope: literal success contract of acceptance step `r19-revision-pin-fixture`; one positive stdout vector, one uniquely relevant wrong/missing vector, stderr-policy impact. Nothing executed except a read-only base-identity check (below). No tools installed or updated.

## Evidence (observed)

- Base identity (executed, read-only): `git --no-optional-locks diff --stat 41553adb139d06511dc386bb3ce4326aebfba675 -- census/round-21/run-acceptance.py census/round-21/step-inventory.json` printed nothing (rc=0), so both working-tree files equal base. sha256: `run-acceptance.py` 1141839963d04e9e1b968d123fa8ffebeef5d33438537cdc636350c970eeaa2b; `step-inventory.json` 8b7b1cd8d19561d9f4e8f06e797038b03379350cb3f3932edf04bda7aa7d1310.
- Step row, `census/round-21/run-acceptance.py` lines 307–309, mirrored in `census/round-21/step-inventory.json` lines 154–168:
  - `expected_summary`: `"SUMMARY total=13 failed=0 base_discriminating=6"` (str; separators are single ASCII SPACE, not TAB)
  - `pass_pattern`: `r"^CASE\tpass\t"` (lowercase `pass`), `pass_count`: 13
  - kind defaults to `"summary"`; no `record_checks`, `baseline_mismatch_count`, or auxiliary lines.
  - argv: `<PYTHON> -B <ROOT>/tests/fixtures/r19-rev-pin.py --tool <ROOT>/tools/souji-rev-pin.py --tool-dir <ROOT>`
- Decision logic, `summarize_result` (lines 347–419):
  1. `matched = returncode == 0 and not failures` (line 367). `failures = failure_lines(stdout + "\n" + stderr)` (line 353). Lines 330–333 count a line as a failure only if it starts with `FAIL\t` or `CASE\tFAIL\t`, or matches `^CASE\t[^\t]+\tFAIL(?:\t|$)`.
  2. `summary_lines` = every stdout `splitlines()` line that matches `SUMMARY_RE = ^(?:SUMMARY|SELFTEST)(?:\t| ).*$` (line 118). Because `expected_summary` is a string, the step needs `summary_lines == ["SUMMARY total=13 failed=0 base_discriminating=6"]`: exactly one such line, byte-equal (line 373).
  3. `observed_auxiliary` (stdout lines that start with `INVENTORY\t`) must equal `[]` (lines 386–390).
  4. `len(re.findall(r"^CASE\tpass\t", stdout, re.MULTILINE)) == 13`. This is exact equality, so 12 fails and 14 fails (lines 400–404). `matched_pass_lines = min(...)` is only a report field; it does not gate the result.
  5. `matched = matched and summary_match and pass_match` (line 417). **stderr is never consulted in this branch except through `failure_lines`.** The counter branch (line 445) and the cache-demo branch (line 480) do add `and not stderr`.

## Positive vector (source-derived; matched=True on base and must stay True after repair)

returncode `0`, stderr `b""`, stdout (`\t` = TAB, `\n` = LF):

```text
CASE\tpass\tv01\n
CASE\tpass\tv02\n
CASE\tpass\tv03\n
CASE\tpass\tv04\n
CASE\tpass\tv05\n
CASE\tpass\tv06\n
CASE\tpass\tv07\n
CASE\tpass\tv08\n
CASE\tpass\tv09\n
CASE\tpass\tv10\n
CASE\tpass\tv11\n
CASE\tpass\tv12\n
CASE\tpass\tv13\n
SUMMARY total=13 failed=0 base_discriminating=6\n
```

As a Python literal for a fixture:

```python
POSITIVE_STDOUT = (
    "".join("CASE\tpass\tv%02d\n" % i for i in range(1, 14))
    + "SUMMARY total=13 failed=0 base_discriminating=6\n"
).encode()
POSITIVE = {"returncode": 0, "stdout": POSITIVE_STDOUT, "stderr": b"", "expected_matched": True}
```

Constraints the vector respects:
- Case names must not be `FAIL`. A line like `CASE\tpass\tFAIL\t…` matches `^CASE\t[^\t]+\tFAIL(?:\t|$)` and becomes a failure line.
- Only one stdout line may begin with `SUMMARY ` / `SUMMARY\t` / `SELFTEST ` / `SELFTEST\t`.
- No `INVENTORY\t` lines.

Trace through the checks: no failure lines; `summary_lines` has the one expected line; auxiliary `[]==[]`; pass count 13==13; so matched=True.

## Uniquely relevant wrong/missing vector (source-derived; matched=False on base and after repair)

This is the same as the positive vector, except the SUMMARY line drops the step-specific `base_discriminating` field:

```python
MISSING_FIELD_STDOUT = (
    "".join("CASE\tpass\tv%02d\n" % i for i in range(1, 14))
    + "SUMMARY total=13 failed=0\n"
).encode()
MISSING_FIELD = {"returncode": 0, "stdout": MISSING_FIELD_STDOUT, "stderr": b"", "expected_matched": False}
```

Why this is the relevant negative for this step:
- `base_discriminating=6` is the only part of the expected summary that separates this step's literal from its sibling `revision-helper-selftest`. That sibling also uses SPACE separators, the same `^CASE\tpass\t` pattern, and the expected summary `SUMMARY total=11 failed=0` (line 279).
- A prefix or field-subset matcher would wrongly accept this vector. The current exact list equality rejects it: `["SUMMARY total=13 failed=0"] != [expected]`, so summary_match=False. Pass count is still 13, so the rejection is attributable to the summary alone.

Two alternates in the same family (also False on base), if L1 wants extra coverage:
- Separator confusion with the TAB-style siblings: `SUMMARY\ttotal=13\tfailed=0\tbase_discriminating=6`. It matches `SUMMARY_RE`, so it is collected as a summary line, but it is not byte-equal, so it is rejected.
- Pass-count vocabulary confusion: 12 `CASE\tpass\t` lines plus 1 `CASE\tPASS\tv13` line (the uppercase vocabulary of r16/r18/r20-audit-contract) with the correct SUMMARY. The count is 12≠13, so it is rejected. The uppercase line is not a failure line.

## Stderr policy impact (the claim defect, as it applies to this step)

The false-green vector is the positive vector with non-empty stderr:

```python
STDERR_NOISE = {"returncode": 0, "stdout": POSITIVE_STDOUT,
                "stderr": b"Traceback (most recent call last):\nRuntimeError: rev-pin case aborted\n",
                "expected_matched": False}
```

- Base (source-inferred from lines 367–417): no failure-marker line, the summary matches, the count is 13, and stderr is not gated, so **matched=True. This is a false green.**
- Repair: add the same `and not stderr` gate that lines 445 and 480 already use to the summary branch's final conjunction (line 417). Sketch, not applied:

```python
        matched = matched and summary_match and pass_match and not stderr
```

  After the repair: STDERR_NOISE gives False, POSITIVE stays True, MISSING_FIELD stays False.
- Stderr that contains a recognized marker, e.g. `b"CASE\tFAIL\tv13\n"`, is already False on base because `failure_lines` scans stderr. It is not discriminating between base and repair. Use non-marker text, as above.
- Stderr consisting only of `b"\n"` is a non-empty string, so the repaired gate rejects it. That is the intended strict policy, the same as counter and cache-demo.

## Bounded findings / unresolved gaps

1. **UNRESOLVED (positive-control risk):** the repaired gate keeps this real step green only if the real `tests/fixtures/r19-rev-pin.py` run writes **zero bytes** to stderr. The fixture source and historical results are outside the named-file contract, so I did not read them. If the fixture or the `souji-rev-pin.py` child forwards any stderr, adding the gate turns this real positive control red. L1 must confirm from the acceptance run that `stderr_sha256 == e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (sha256 of empty bytes) for this step, before and after the repair.
2. **OBSERVED, not in C1 scope:** `failure_lines` recognizes only uppercase `FAIL`. This step's vocabulary is lowercase (`CASE\tpass\t`). [INFERENCE] I infer the fixture's failure lines would be lowercase `CASE\tfail\t…`, but I did not read the fixture to confirm it. Any lowercase fail line is invisible to `failure_lines`, so for this step failure detection rests entirely on the exact summary literal plus the exact pass count. Extra non-`pass` CASE lines, such as a 14th `CASE\tfail\tx` alongside 13 passes and `total=13`, are not counted and would be accepted. Recorded only; this is not a C1 axis claim, and the preregistration excludes malicious-producer attestation.
3. **OBSERVED, minor:** `summary_lines` uses `str.splitlines()`, which also breaks on `\x0b \x0c \x1c-\x1e \x85 \u2028 \u2029`. `re.findall(..., re.MULTILINE)` anchors `^` only after `\n`. The two can disagree on exotic separators. No vector above depends on this, and all vectors use LF only.

## Observed vs inferred

- Observed: step literals, file identity with base, and the branch logic line references.
- Source-inferred (not run): every `matched` outcome stated for every vector, on base and after the repair.
- Not observed: real fixture stdout/stderr; fixture failure vocabulary.
