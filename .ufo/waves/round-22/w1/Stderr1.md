STATUS: PASS — The ordinary-ERROR-on-stderr vector for `auditor-selftest` gives base `matched=True`, which is a false green. The repaired summarizer must give `matched=False`, and the paired empty-stderr control must give `True` on both base and changed code. All results are inferred from source; nothing was executed.

Scope: source-only reading of the named files: `census/round-21/run-acceptance.py`, `census/round-21/step-inventory.json`, `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`, `.ufo/waves/round-22/preregistration.txt`, `corpus/QUALITY.md`, plus one grep over the named `census/round-14/cache-demonstration.py`. No tests, builds, probes, or `/proc` were used. No tools were installed. No LSP device is mounted in this session, so the symbol trace below comes from a direct read of a single file, not a semantic proof.

## Vector (literal)

Step: `auditor-selftest`, taken as-is from the inventory (`step-inventory.json` lines 7–19; `run-acceptance.py` lines 276–277). The step has no `kind` key, so it defaults to `"summary"` (line 368). Its `expected_summary` is the string `"SELFTEST\tpass=118\tfail=0"`, its `pass_pattern` is `^PASS\t`, and its `pass_count` is 118.

| id | returncode | stdout | stderr bytes | base `matched` | changed `matched` | discriminating |
|---|---|---|---|---|---|---|
| S1-ERR | 0 | 118 × `PASS\tc<i>\n` then `SELFTEST\tpass=118\tfail=0\n` | `b"ERROR: self-test could not complete\n"` | **True** (false green) | **False** | yes |
| S1-CTL | 0 | identical | `b""` | **True** | **True** | no (positive control) |

Base trace for S1-ERR in `summarize_result` (lines 347–482):
- `summary_lines`: `SUMMARY_RE` (line 118) matches only `SELFTEST\t…`, and only stdout is scanned (line 352). The result is `[expected]`, so `summary_match=True` (line 373).
- `failures`: lines 353 and 330–333 join stdout and stderr. `ERROR: …` does not start with `FAIL\t` or `CASE\tFAIL\t`, and it does not match `^CASE\t[^\t]+\tFAIL`. The result is `[]`.
- Line 367 gives `matched = True` (rc 0, no failures).
- The `INVENTORY\t` auxiliary lines are `[] == []` (lines 385–390), and `baseline_mismatch_count` is not set for this step.
- `re.findall(r"^PASS\t", stdout, re.M)` finds 118 lines, equal to `pass_count`, so `pass_match=True` (lines 400–404).
- Line 417 gives `matched = True and True and True`. No stderr check exists in this branch, so `result["matched"] = True`. The counter branch (line 445) and the cache-demo branch (line 480) both have `and not stderr`.

This is a concrete instance of the r21 finding "Summary steps can pass with arbitrary error text on stderr" (AttackRunnerStepResults.md lines 13–17), using the same message text.

## Compatibility requirements

1. **The predicate is byte-emptiness, not a marker spelling.** The fix is `matched = matched and summary_match and pass_match and not stderr` in the summary branch, the same idiom as lines 445 and 480.
   - `stderr` comes from `decode("utf-8", "surrogateescape")` (line 198), which is lossless, so `not stderr` holds exactly when `stderr_bytes == b""`.
   - Adding `ERROR` to `failure_lines` is NOT compatible with Q11 ("checkers test behaviour, not marker spellings"). Under that approach, `error:`, `Traceback …`, or any other text would still pass.
   - A whitespace-only stderr such as `b"\n"` is non-empty and must also give `False`. [INFERENCE: this follows the same predicate; it is not a separate vector here.]
2. **Unchanged surfaces.**
   - The changed branch keeps `failure_lines` (S1-ERR still records `[]`), `observed_summary`, `matched_counts`, and the retained `stderr`/`stderr_sha256` fields.
   - Only `matched` flips.
   - `inventory_projection` (lines 538–552) projects step definitions, not results, so the frozen `step-inventory.json` comparison (lines 600–602) is unaffected.
   - The r21 matrix signature includes `matched` (AttackRunnerStepResults.md line 30), so the flip propagates there.
3. **The 18 real positive controls must stay matched. This is unverified from the named files and is the main compatibility risk.**
   - The new predicate applies to all 12 summary-kind real steps, not only `auditor-selftest`.
   - Every one of them must emit exactly `b""` on stderr under `CHILD_ENV` (lines 107–117) at the changed revision.
   - I could not read these files under my scope: the auditor, the fixtures, `verify-agreement-pin.py`, and the probe. Benign stderr from them, such as a Python warning or child `git` chatter, would flip a real positive control to `False`.
   - L1's acceptance run must observe `stderr == ""` on all 12 summary records.
   - If any real step does emit benign stderr, that is a finding to report. It must not be absorbed through an allowlist or by relaxing the oracle (Q41: never relax the oracle merely to get green).
4. **The oracle stays hermetic.**
   - The summary branch never uses `root` or `revision`; `root` is read only in the cache-demo branch (line 454).
   - The synthetic fixture can therefore call the base and changed `summarize_result` directly. It needs a step dict carrying `name`, `argv`, `expected_summary`, `pass_pattern`, and `pass_count`, plus literal bytes.
   - This requires no process execution and no `/proc`, and it does not touch F5, as the preregistration requires.
   - Base loading would use `importlib` on the hyphenated file. That only sets `sys.dont_write_bytecode` at import (line 22) and has no other side effects.

Draft oracle rows (synthetic, literal expectations reviewed independently of implementation output):

```python
AUDITOR_STEP = {
    "name": "auditor-selftest", "argv": ["<PYTHON>", "-B", "<ROOT>/tools/souji-seat-audit.py", "--selftest"],
    "expected_summary": "SELFTEST\tpass=118\tfail=0", "pass_pattern": r"^PASS\t", "pass_count": 118,
}
AUDITOR_STDOUT = b"".join(b"PASS\tc%d\n" % i for i in range(118)) + b"SELFTEST\tpass=118\tfail=0\n"
CASES = (
    # (id, step, returncode, stdout, stderr, base_expected, changed_expected)
    ("S1-ERR", AUDITOR_STEP, 0, AUDITOR_STDOUT, b"ERROR: self-test could not complete\n", True, False),
    ("S1-CTL", AUDITOR_STEP, 0, AUDITOR_STDOUT, b"", True, True),
)
```

## Gaps (not resolved here)

- No real summary step's actual stderr bytes were observed. Requirement 3 depends on L1's acceptance run.
- The changed runner's path and name are L1's integration choice, so they are not named here.
- Interaction with the cache-check and JSON scalar-type repairs is outside this vector. Those repairs touch other branches; S1 depends only on the summary branch.
