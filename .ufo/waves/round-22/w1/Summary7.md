STATUS: PASS — landing-gate-selftest success contract derived from source; one positive vector, one pass-count/case negative vector, one stderr false-green vector drafted. Nothing executed.

Scope: source-inferred only. No tests, builds, probes, or the target tool were run. No tools installed. LSP device not used (Python source read directly by named file and line; no semantic-proof claims made). `tools/souji-landing-gate.py` itself is NOT in the named-file contract and was not opened, so its real emission format is inferred from the step definition only.

## Literal contract (observed)

Step row — `census/round-21/run-acceptance.py:297-298`, frozen identically in `census/round-21/step-inventory.json:100-112`:

- argv `[<PYTHON>, -B, <ROOT>/tools/souji-landing-gate.py, --selftest]`, kind `summary` (default), cwd `root`, env `CHILD_ENV` (`run-acceptance.py:107-117`, `:614-615`).
- `expected_summary = "SELFTEST\tpass=65\tfail=0"` (str), `pass_pattern = r"^CASE\tpass\t"`, `pass_count = 65`; no `baseline_mismatch_count`, no `auxiliary_lines`.

`summarize_result` (`run-acceptance.py:347-418`) marks it matched iff ALL of:

1. `returncode == 0` (`:366`).
2. `failure_lines(stdout + "\n" + stderr)` empty (`:353`, `:330-333`): no line starting `FAIL\t` or `CASE\tFAIL\t`, and none matching `^CASE\t[^\t]+\tFAIL(\t|$)`. Case-sensitive; lowercase `CASE\tfail\t…` is NOT a failure line.
3. `summary_lines == ["SELFTEST\tpass=65\tfail=0"]` (`:373`), where `summary_lines` = every `stdout.splitlines()` line matching `SUMMARY_RE = ^(?:SUMMARY|SELFTEST)(?:\t| ).*$` (`:118`, `:352`). Exactly one such line, byte-exact (tabs, not spaces).
4. Zero stdout lines starting `INVENTORY\t` (`:386-390`, expected auxiliary `[]`).
5. `len(re.findall(r"^CASE\tpass\t", stdout, re.MULTILINE)) == 65` exactly (`:400-404`). Not deduplicated, not tied to the summary's `pass=` number.
6. stderr: **no emptiness requirement in the summary branch** (`:417`); only counter (`:445`) and cache-demo (`:480`) require `not stderr`. stderr only matters via predicate 2.

The `carry-invariant-probe` VIOLATION check (`:418`) does not apply (name-gated).

## Positive vector (expected matched = True on base and changed)

```python
LANDING_GATE_SELFTEST_POSITIVE = {
    "returncode": 0,
    "stdout": b"".join(b"CASE\tpass\tcase-%02d\n" % i for i in range(1, 66))
              + b"SELFTEST\tpass=65\tfail=0\n",
    "stderr": b"",
    "expected_matched": True,
}
```

Derivation: 65 `^CASE\tpass\t` hits; exactly one `SUMMARY_RE` line, equal to the expected string; no `FAIL` marker; no `INVENTORY\t`; empty stderr (so it stays green after the stderr repair).

## Negative vector (uniquely relevant to this step: pass-pattern case)

```python
LANDING_GATE_SELFTEST_WRONG_CASE = {
    "returncode": 0,
    "stdout": b"".join(b"CASE\tPASS\tcase-%02d\n" % i for i in range(1, 66))
              + b"SELFTEST\tpass=65\tfail=0\n",
    "stderr": b"",
    "expected_matched": False,   # observed_pass_lines 0 != 65
}
```

Why this one: the summary line is correct and stderr is empty, so the ONLY failing predicate is pass-count (5). It discriminates landing-gate-selftest from its neighbours in the inventory: `r18-landing-pointers` counts `^CASE\tPASS\t` (`:300`), and `auditor-selftest` uses a `SELFTEST\t…` summary with `^PASS\t` (`:277`). An implementation that case-folds or reuses a neighbour's pattern would wrongly accept this vector. Base rejects it too, so it is a retained regression control, not a base false green.

Equivalent single-predicate alternatives the L1 can pick from if a different isolation is preferred (all expected False on base and changed):
- Missing summary: the 65 positive CASE lines, no `SELFTEST` line → `summary_lines == []` ≠ expected.
- Short count: 64 `CASE\tpass\t` lines plus the correct summary → 64 ≠ 65 (summary still claims 65).
- Space-separated summary: `SELFTEST pass=65 fail=0` still matches `SUMMARY_RE` (the `(?:\t| )` branch), so it is collected but ≠ the tab literal → False.

## Stderr policy impact (the r21 HIGH defect, `AttackRunnerStepResults.md:11-15`)

False-green vector — expected matched False after repair, observed-by-source True on base:

```python
LANDING_GATE_SELFTEST_STDERR = {
    "returncode": 0,
    "stdout": LANDING_GATE_SELFTEST_POSITIVE["stdout"],
    "stderr": b"Traceback (most recent call last):\nRuntimeError: selftest aborted\n",
    "expected_matched": False,   # base: True (summary branch ignores stderr)
}
```

On base, every predicate 1–5 holds and the stderr text contains no `FAIL\t`/`CASE\t…FAIL` marker, so `matched` is True; that is the false green. A repair adding `and not stderr` to the summary branch at `:417` flips it to False, matching counter/cache-demo.

Impact on the real positive control (inference, unresolved): after the repair, the real `souji-landing-gate.py --selftest` run must produce byte-empty stderr, or the retained 18-step positive set loses this step. Nothing in the named files shows what this tool writes to stderr. `CHILD_ENV` sets no `PYTHONWARNINGS`, so the default Python warning filters apply; and if selftest subcases spawn children whose stderr is inherited rather than captured, that output lands in the step's stderr. **L1 MUST confirm, before landing the repair, that the r21 recorded result for `landing-gate-selftest` has `stderr == ""` (`stderr_sha256 == e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`).** If it does not, the stderr repair turns this real positive red, and the step needs an explicit, reviewed stderr allowance instead of a silent exemption.

## Bounded findings beyond the assigned question (no fix claimed or drafted)

- F-a (pass-count/summary blind spot, source-inferred): extra lowercase `CASE\tfail\t…` lines are not failure lines, and the pass count is an exact equality over `CASE\tpass\t` only. So the 65 positive lines + `CASE\tfail\tx` + `SELFTEST\tpass=65\tfail=0` → matched True on base. Whether the real tool spells failures `CASE\tfail\t` is [INFERENCE] from its lowercase `pass` convention (tool source not opened). This is not one of the three preregistered defects; reported for L1 triage only, no scope added.
- F-b (line-splitting divergence): summary collection uses `str.splitlines()` (which also splits on `\r`, `\x0b`, `\x0c`, `\x1c`–`\x1e`, `\x85`, `\u2028`, `\u2029`), while pass counting uses `re.MULTILINE` `^`, which anchors only after `\n`. A `\r`-joined stdout can therefore make the two predicates see different line sets. Edge case, not preregistered; noted only.
- Duplicate CASE lines are counted: 65 identical `CASE\tpass\tx` lines satisfy predicate 5. This is consistent with the "counted rather than identified" theme, but the preregistration scopes identity only to cache checks.

## Remaining unknowns

- Real stderr bytes of `tools/souji-landing-gate.py --selftest` at base 41553adb (not in named files; L1 checks the recorded r21 result).
- Real failure-line spelling of the landing-gate selftest (affects F-a only).

Report: .ufo/waves/round-22/w1/Summary7.md
Sources read: census/round-21/run-acceptance.py; census/round-21/step-inventory.json; .ufo/waves/round-21/w2/AttackRunnerStepResults.md; .ufo/waves/round-22/preregistration.txt; corpus/QUALITY.md (grep only). census/round-14/cache-demonstration.py not needed for this step.
Installs: none.
