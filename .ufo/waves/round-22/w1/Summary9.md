STATUS: PASS — r16-landing-gate success contract derived source-only; one positive vector, one load-bearing pass-count negative, and the summary-stderr impact (base false green, empty-stderr policy rejects) are below. Nothing was executed.

Scope: source/draft only. Read exactly: `census/round-21/run-acceptance.py`, `census/round-21/step-inventory.json`, `.ufo/waves/round-22/preregistration.txt`, `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`, `corpus/QUALITY.md`. `census/round-14/cache-demonstration.py` not needed (cache-only). The r16 fixture itself (`tests/fixtures/r16-landing-gate.py`) is NOT a named file and was not read; its real line format is therefore an unknown, and the vectors below are contract-synthetic. No grep/glob, no LSP (no LSP device available in this session; no semantic claims made), no tools installed.

## Literal success contract (observed in source)

Step row, `run-acceptance.py:301-303`, identical in frozen `step-inventory.json:127-140` (kind `summary`, no `baseline_mismatch_count`, no `record_checks`, no `auxiliary_lines`):

- `expected_summary` = `"SUMMARY\ttotal=15\tfailed=0"` (string form)
- `pass_pattern` = `r"^CASE\t[^\t]+\tPASS\t"`, `pass_count` = 15

`summarize_result` (`run-acceptance.py:347-419`) marks it matched iff all hold:

1. `returncode == 0` (`:367`).
2. `failure_lines(stdout + "\n" + stderr)` empty (`:353`, `:330-333`): no line starting `FAIL\t` / `CASE\tFAIL\t`, and none matching `^CASE\t[^\t]+\tFAIL(?:\t|$)`.
3. `summary_lines == ["SUMMARY\ttotal=15\tfailed=0"]` (`:373`), where summary_lines = every `stdout.splitlines()` line matching `^(?:SUMMARY|SELFTEST)(?:\t| ).*$` (`:118`, `:352`). Exactly one such line; any second SUMMARY/SELFTEST line fails.
4. No stdout line starting `INVENTORY\t` (`:374`, `:386-389`; expected auxiliary is `[]`).
5. `len(re.findall(pass_pattern, stdout, re.MULTILINE)) == 15` (`:400-404`) — exact equality, not ≥.
6. Not the carry probe, so no VIOLATION check (`:418`).

Stderr is never required empty on this branch (`:417`); it only matters via the FAIL-shaped vocabulary in (2). Counter and cache branches do require `not stderr` (`:445`, `:480`).

## Vectors (literal; decisions source-inferred, not executed)

```python
R16_STEP = {
    "name": "r16-landing-gate",
    "argv": ["<PYTHON>", "-B", "<ROOT>/tests/fixtures/r16-landing-gate.py",
             "--tool", "<ROOT>/tools/souji-landing-gate.py"],
    "expected_summary": "SUMMARY\ttotal=15\tfailed=0",
    "pass_pattern": r"^CASE\t[^\t]+\tPASS\t",
    "pass_count": 15,
}
_PASS = b"".join(b"CASE\tc%02d\tPASS\tok\n" % i for i in range(1, 16))

# P16: valid positive
R16_POSITIVE = (0, _PASS + b"SUMMARY\ttotal=15\tfailed=0\n", b"")

# W16: summary claims failed=0, but case 15 reports a status outside the
# failure vocabulary; only the pass-count guard can catch it
R16_ERROR_CASE = (
    0,
    b"".join(b"CASE\tc%02d\tPASS\tok\n" % i for i in range(1, 15))
    + b"CASE\tc15\tERROR\tgate crashed\n"
    + b"SUMMARY\ttotal=15\tfailed=0\n",
    b"",
)

# S16: positive stdout, rc 0, non-FAIL-shaped stderr
R16_STDERR = (
    0,
    _PASS + b"SUMMARY\ttotal=15\tfailed=0\n",
    b"Traceback (most recent call last):\nRuntimeError: landing gate could not complete\n",
)
```

| vector | base 41553ad decision | required changed decision | role |
|---|---|---|---|
| P16 | matched | matched | positive control |
| W16 | rejected (observed_pass_lines=14 ≠ 15) | rejected | retained negative; not a before→after discriminator |
| S16 | **matched (false green)** | rejected | stderr defect discriminator for this step |

Traces:
- P16: one SUMMARY line equal to expected; CASE lines don't match `SUMMARY_RE`; no INVENTORY; 15 findall hits (each needs the trailing `\t` after PASS); `CASE\tcNN\tPASS\t…` doesn't match the FAIL regex.
- W16: summary, auxiliary and failure checks all pass, since `ERROR` is neither `FAIL` nor `PASS`. 14 hits fail check 5. **Why W16 is the r16-specific negative:** this step's summary line has no `pass=` field (unlike `auditor-selftest`/`r20-audit-contract`), so stdout cannot cross-check itself. The exact `pass_count == 15` is the only line-level guard against a non-PASS/non-FAIL status, and any repair must keep it exact.
- S16: stderr lines don't start `FAIL\t` or `CASE\t`, so failure_lines is empty and `:417` marks it matched. Under an empty-stderr summary policy (`matched = matched and summary_match and pass_match and not stderr`, the same rule as `:445`/`:480`), it is rejected. Caveat for the oracle: S16's stderr must avoid FAIL-shaped lines, or base already rejects it and the vector stops discriminating.

## Stderr-policy impact on r16

- **Real positive control risk (unresolved):** a strict empty-stderr summary policy keeps the real r16 step green only if the real fixture writes zero stderr bytes on success. Per Q25, the fixture drives `souji-landing-gate.py` through cases where the gate must exit 1 with LG findings. [INFERENCE] If the fixture does not capture its child's stderr, gate diagnostics reach the fixture's stderr and the strict policy turns the real r16 control red. That would break the preregistered "retain all 18 real positive controls" requirement. Before adopting the policy, L1 MUST confirm from a real acceptance record that `commands[r16-landing-gate].stderr_sha256 == e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (the sha256 of empty input). Do not weaken the policy per-step to make it pass. A non-empty result is a real finding to report.
- Frozen inventory: `inventory_projection` (`:537-552`) copies only listed keys, so a branch-logic stderr change does not alter the projection or trip the `:600-602` refusal. A new step key would need adding to both the projection and the frozen JSON.
- Matrix: per AttackRunnerStepResults, `replay-matrix.sh` signatures omit stderr. A stderr-only regression still flips `matched`, which is in the signature, so parity stays meaningful after the repair.

## Bounded findings outside C1 (route only; not proposed for this claim)

- LOW, source-inferred from Python `re` semantics (a complemented set matches newline; `MULTILINE` affects only `^`/`$`): `[^\t]+` in the r16 pass pattern can span lines. `b"CASE\tc15\nnote\tPASS\tx\n"` counts as one PASS, so a truncated `CASE\tc15` line followed by any `…\tPASS\t…` line can fill the count. Unexecuted.
- LOW: PASS lines are counted, not identified. Fifteen copies of `CASE\tc01\tPASS\tok` satisfy check 5. This is the summary-step analog of the cache "counted not identified" defect. The preregistration scopes identity to cache checks only, so it needs its own future claim.

## Remaining unknowns

- The real r16 fixture's line format and success-time stderr (fixture not a named file; no run made).
- Whether the shared synthetic oracle fixture calls `summarize_result` directly or another seam. The vectors assume `(returncode, stdout_bytes, stderr_bytes)` inputs. For the summary branch, `revision` and `root` are unused (`:347-419` never reads them).

Report: .ufo/waves/round-22/w1/Summary9.md
