STATUS: PASS — literal success contract for `revision-helper-selftest` derived from source; one positive vector, one uniquely relevant wrong-summary vector (plus a pass-count vector), and the summary-stderr impact identified. Source-inferred only: nothing was executed.

# Scope and method

- Read only the named files: `census/round-21/run-acceptance.py`, `census/round-21/step-inventory.json`, `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`, `.ufo/waves/round-22/preregistration.txt`, `corpus/QUALITY.md` (only to check for related rows). `census/round-14/cache-demonstration.py` is not relevant to this step, so I did not open it.
- No LSP device was exposed in this session. Literal grep over the named files was the fallback, and nothing here is presented as semantic proof. The contract is fully local to `summarize_result`, so caller tracing does not change the answer.
- Nothing was run: no tests, builds, probes, or the step itself. No tools were installed or updated.

# Observed contract (source facts)

Step definition, `census/round-21/run-acceptance.py:278-279`:
- `argv = [sys.executable, "-B", <ROOT>/tools/souji-rev-pin.py, "--selftest"]`
- `expected_summary = "SUMMARY total=11 failed=0"` (single **spaces**, str form)
- `pass_pattern = r"^CASE\tpass\t"` (lowercase `pass`, trailing tab required), `pass_count = 11`
- No `kind` key, so it defaults to `"summary"` (line 368). No `record_checks`, no `baseline_mismatch_count`, no auxiliary lines.

`census/round-21/step-inventory.json:20-32` matches byte-for-byte in meaning: same summary, `"^CASE\\tpass\\t"` (the JSON escape for the same regex), 11, `"kind": "summary"`, and the same argv template.

`matched` for this step is true exactly when ALL of these hold (lines 352-417):
1. `returncode == 0` (line 367).
2. `failure_lines(stdout + "\n" + stderr)` is empty (lines 330-333, 353). Only `FAIL\t`, `CASE\tFAIL\t`, and `^CASE\t[^\t]+\tFAIL(\t|$)` count. All are **uppercase**.
3. `summary_lines == ["SUMMARY total=11 failed=0"]` (line 373). `summary_lines` is every **stdout** `splitlines()` line matching `SUMMARY_RE = ^(?:SUMMARY|SELFTEST)(?:\t| ).*$` (line 118). So there must be exactly one such line, byte-exact, with no trailing whitespace, and no extra `SUMMARY`/`SELFTEST` lines.
4. No stdout line starts with `INVENTORY\t`, because `expected_auxiliary = []` (lines 374, 386-390).
5. `len(re.findall(r"^CASE\tpass\t", stdout, re.MULTILINE)) == 11`, counted from stdout only, with exact equality (lines 400-404).
6. **stderr is not consulted**, except through condition 2. `BASELINE_MISMATCH\t` and `VIOLATION\t` lines are counted or ignored but do not gate this step (lines 391-398, 418-419).

# Vectors (draft fixture rows, for L1 integration)

```python
# (name, returncode, stdout_bytes, stderr_bytes, expected_base, expected_changed)
REVISION_HELPER_VECTORS = [
    # P1 positive control: literal success contract.
    ("rev-helper/positive", 0,
     b"".join(b"CASE\tpass\tcase-%02d\n" % i for i in range(1, 12))
     + b"SUMMARY total=11 failed=0\n",
     b"", True, True),
    # N1 uniquely relevant wrong summary: r18-landing-pointers' tab-separated literal
    # ("SUMMARY\ttotal=11\tfailed=0", run-acceptance.py:300) with identical counts.
    ("rev-helper/tab-summary", 0,
     b"".join(b"CASE\tpass\tcase-%02d\n" % i for i in range(1, 12))
     + b"SUMMARY\ttotal=11\tfailed=0\n",
     b"", False, False),
    # N2 pass-count shortfall: correct summary, 10 pass lines.
    ("rev-helper/ten-passes", 0,
     b"".join(b"CASE\tpass\tcase-%02d\n" % i for i in range(1, 11))
     + b"SUMMARY total=11 failed=0\n",
     b"", False, False),
    # S1 summary-stderr false green: P1 stdout, rc 0, stderr free of FAIL markers.
    ("rev-helper/stderr-on-success", 0,
     b"".join(b"CASE\tpass\tcase-%02d\n" % i for i in range(1, 12))
     + b"SUMMARY total=11 failed=0\n",
     b"ERROR: self-test could not complete\n", True, False),
]
```

Expected `matched_counts` for P1 (lines 405-416): `summary_lines=1, expected_pass_lines=11, observed_pass_lines=11, matched_pass_lines=11, expected_auxiliary_lines=0, observed_auxiliary_lines=0, matched_auxiliary_lines=0, baseline_mismatch_records=0, baseline_mismatches_reported=None, record_checks=0`. `stderr_sha256 = e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

Why N1 is uniquely relevant: this is the only step whose summary has the same counts (`total=11 failed=0`) and the same `pass_count` (11) as another step (`r18-landing-pointers`, line 300). The two differ only by separator (space here, tab there) and pass-token case (`pass` here, `PASS` there). N1 keeps this step's own `CASE\tpass\t` lines and changes only the separator. That isolates the byte-exact summary-equality gate (condition 3) and catches any "normalize whitespace" or cross-step lookup regression. On base it is a regression guard, not a false green: it already fails at line 373. N2 is the pass-count counterpart and also fails at line 404 on base.

# stderr policy impact

- **Defect on base (source-inferred):** S1 gives `matched=True` on base. The summary branch (line 417) never requires empty stderr, while the counter branch (line 445) and the cache-demo branch (line 480) do. This is the same defect `AttackRunnerStepResults.md:11-15` reports for `auditor-selftest`, and it applies identically here. S1's stderr must avoid uppercase `FAIL\t` and `CASE\t…\tFAIL` markers; otherwise condition 2 already rejects it on base and the vector no longer separates base from the changed implementation.
- **Minimal repair (draft, not applied):** line 417 becomes `matched = matched and summary_match and pass_match and not stderr`. Under the changed implementation, P1, N1, and N2 keep their decisions and S1 flips to False.
- **Positive-control risk (unresolved):** the repair keeps the real 18-step positive control green only if the real `souji-rev-pin.py --selftest` writes **zero** stderr bytes on success. `tools/souji-rev-pin.py` was not a named file, so I did not read it. For example, it may launch git subprocesses whose stderr is inherited rather than captured. L1 MUST confirm the retained real acceptance record for this step has `stderr == ""` / `stderr_sha256 == e3b0c442…b855` before landing the repair. Otherwise the new gate turns a true positive red. The same check applies to every other `kind == "summary"` step.
- **Adjacent gap, reported but not claimed as a defect of this step:** `failure_lines` is uppercase-only, while this step's pass token is lowercase. A stdout line `CASE\tfail\tx` is not recognized as a failure. With 11 pass lines and the literal summary present, it would still match. Whether `souji-rev-pin.py` emits lowercase `CASE\tfail\t` is [INFERENCE] from the `pass` casing alone; it was not observed. This is outside the three preregistered defects, so it is listed only and no fix is proposed.

# Remaining unknowns

- The real stderr bytes of `souji-rev-pin.py --selftest` on success: not readable within this contract, and not executed.
- The real failure-line vocabulary of `souji-rev-pin.py`: not read.
