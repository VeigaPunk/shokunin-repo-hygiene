STATUS: PASS (source-inferred only; nothing executed)

# Summary5 — r19-seat-audit-shapes literal success contract

Scope: read only `census/round-21/run-acceptance.py`, `census/round-21/step-inventory.json`,
`.ufo/waves/round-22/preregistration.txt`, `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`.
The fixture `tests/fixtures/r19-seat-audit-shapes.py` is NOT in the named-file contract and was not
opened; every claim about its real output is marked [INFERENCE]. No tests, builds, or probes were run.
No tools installed. No LSP device is mounted in this session; the evidence is literal source reading of
one function, so no claim relies on semantic references.

## Observed contract (source facts)

The step definition (`run-acceptance.py` lines 291–293, mirrored at `step-inventory.json` lines 73–85):

- `kind` absent, so it defaults to `"summary"` (line 368).
- `expected_summary` = the string `"SUMMARY total=17 failed=0 base_discriminating=12"`. It is separated by
  ASCII spaces, not tabs, unlike the r20 steps.
- `pass_pattern` = `^CASE\tpass\tchanged/`, `pass_count` = 17.
- No `baseline_mismatch_count`, `record_checks`, or auxiliary lines.

`summarize_result` (lines 347–482) marks this step `matched` iff all of the following hold:

1. `returncode == 0` (line 367).
2. `failure_lines(stdout + sep + stderr)` is empty (lines 330–333, 353). It only recognizes lines starting
   `FAIL\t` or `CASE\tFAIL\t`, or matching `^CASE\t[^\t]+\tFAIL(\t|$)`. It is uppercase only.
3. `summary_lines == ["SUMMARY total=17 failed=0 base_discriminating=12"]` (line 373). `summary_lines` is every
   stdout line, from `str.splitlines()`, that matches `^(?:SUMMARY|SELFTEST)(?:\t| ).*$` (line 118). The list must
   have exactly one element and match byte for byte. Any second `SUMMARY `/`SUMMARY\t`/`SELFTEST `/`SELFTEST\t`
   line fails the step.
4. `observed_auxiliary == []`, meaning no stdout line starts with `INVENTORY\t` (lines 386–390, where
   `expected_auxiliary = []` for a string expectation).
5. `len(re.findall(r"^CASE\tpass\tchanged/", stdout, re.MULTILINE)) == 17` (lines 400–404, 417).
6. **stderr is not consulted**, apart from the failure-marker scan in item 2. The counter branch (line 445) and the
   cache-demo branch (line 480) both require `not stderr`. The summary branch does not.

## Valid positive stdout vector

```python
R19_SHAPES_POSITIVE = {
    "step": "r19-seat-audit-shapes",
    "returncode": 0,
    "stdout": "".join(f"CASE\tpass\tchanged/shape-{i:02d}\n" for i in range(1, 18))
              + "SUMMARY total=17 failed=0 base_discriminating=12\n",
    "stderr": "",
    "expected_matched": {"base": True, "changed": True},
}
```

This gives 17 pattern hits, one exact summary line, no `INVENTORY\t` line, no failure marker, rc 0, and empty
stderr, so it passes on both base and changed. Case suffixes after `changed/` are free-form for the runner.
The real fixture's case names are unknown [INFERENCE], and the oracle must not depend on them.

## Uniquely relevant wrong-summary vector (negative control)

```python
R19_SHAPES_LOST_BASE_DISCRIMINATION = {
    "step": "r19-seat-audit-shapes",
    "returncode": 0,
    "stdout": "".join(f"CASE\tpass\tchanged/shape-{i:02d}\n" for i in range(1, 18))
              + "SUMMARY total=17 failed=0 base_discriminating=11\n",
    "stderr": "",
    "expected_matched": {"base": False, "changed": False},
}
```

Why this vector is uniquely relevant: `base_discriminating=12` is the only step-specific quantity that neither
the pass count nor rc/failure markers can see. All 17 changed cases still pass and nothing says FAIL. Only the
literal summary equality (item 3) rejects a fixture that has lost discrimination against the baseline auditor.
Both base and changed must reject it. It is a retained negative control, not a before→after discriminator.

An alternate pass-count vector, if L1 prefers it: keep the exact positive summary but change one pass line to
`CASE\tpass\tbase/shape-17`. That gives 16 hits for `^CASE\tpass\tchanged/`, so the step must fail on both base and
changed. This shows the `changed/` qualifier is load-bearing.

## stderr policy impact

The before→after discriminator for this step, which is the round-22 stderr defect:

```python
R19_SHAPES_STDERR_FALSE_GREEN = {
    "step": "r19-seat-audit-shapes",
    "returncode": 0,
    "stdout": R19_SHAPES_POSITIVE["stdout"],
    "stderr": "Traceback (most recent call last):\nRuntimeError: shape case aborted\n",
    "expected_matched": {"base": True, "changed": False},   # base = observed false green
}
```

- **Base (source-inferred):** `matched=True`. The stderr has no `FAIL\t`/`CASE\tFAIL…` marker, and the summary branch
  never checks emptiness. This confirms the AttackRunnerStepResults HIGH finding for this step specifically.
- **Changed (required):** `matched=False` once the summary branch requires `not stderr`, in parity with lines 445
  and 480.
- **Positive-control risk [INFERENCE, unverified]:** an empty-stderr rule turns this real step red if
  `r19-seat-audit-shapes.py` lets child auditor diagnostics reach its own stderr on success. That could happen
  if it runs `--tool` subprocesses without capturing stderr while the negative-shape cases make the auditor print
  refusals. I could not check this because the fixture is outside the named read set. Before enforcing the rule, L1
  should confirm from the fixture source, or from the retained acceptance record's
  `stderr_sha256 == e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (SHA-256 of empty), that this
  step's real stderr is empty. If it is not, the "retain all 18 positive controls" preregistration clause and the
  stderr repair conflict, and L1 must decide which wins.

## Bounded additional observations (no claim, outside the three admitted defects)

- This fixture's pass vocabulary is lowercase (`CASE\tpass\t`). `failure_lines` matches only uppercase `FAIL`.
  A line `CASE\tfail\tchanged/x` is therefore not a failure marker. For this step, failure detection rests entirely
  on items 3 and 5. For example, 17 pass lines, one extra `CASE\tfail\tchanged/18`, and an exact summary still give
  `matched=True`, because the runner never checks `total=` against the number of case lines. This is source-inferred.
  The real fixture's failure-line form is unknown.
- `summary_lines` uses `str.splitlines()`, which also splits on `\r`, `\x0b`, `\x0c`, `\x1c–\x1e`, `\x85`, `\u2028`
  and `\u2029`. The pass count uses `re.MULTILINE`, where `^` follows only `\n`. The two can disagree on line
  boundaries for adversarial output. I am noting this only; I make no repair claim.

## Remaining unknowns

- The real stdout and stderr of `tests/fixtures/r19-seat-audit-shapes.py`, including case names, failure vocabulary,
  and whether stderr is empty on success. The source is outside the named file set.

Report: .ufo/waves/round-22/w1/Summary5.md
