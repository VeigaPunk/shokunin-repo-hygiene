STATUS: PASS — I derived the literal `auditor-selftest` success contract from the pinned runner source. This report gives one positive stdout vector, one pass-count negative vector, and the impact of the stderr policy on this step. It is source-inferred only: nothing was executed (no runner, selftest, test, build or probe), and no tools were installed.

## Success contract (observed in source)

Step row: `census/round-21/run-acceptance.py:276-277`, frozen identically in `census/round-21/step-inventory.json:8-19`.
- name `auditor-selftest`; argv `<PYTHON> -B <ROOT>/tools/souji-seat-audit.py --selftest`; kind defaults to `summary`.
- `expected_summary` = `"SELFTEST\tpass=118\tfail=0"` (a str); `pass_pattern` = `^PASS\t`; `pass_count` = 118. There are no `auxiliary_lines`, no `baseline_mismatch_count` and no `record_checks`.

`summarize_result` (`run-acceptance.py:347-419`) sets `matched` to True only if every condition below holds:
1. `returncode == 0` (line 367). An OSError invocation sets `returncode=None`, so the step fails (lines 617-619).
2. `failure_lines` is empty (lines 330-333, 353). It scans stdout, then `"\n"` if both streams are non-empty, then stderr. It looks for lines starting `FAIL\t` or `CASE\tFAIL\t`, or matching `^CASE\t[^\t]+\tFAIL(\t|$)`.
3. `summary_lines == ["SELFTEST\tpass=118\tfail=0"]` (line 373). `summary_lines` holds every stdout line (from `str.splitlines()`) that matches `^(?:SUMMARY|SELFTEST)(?:\t| ).*$` (lines 118, 352). So the step needs exactly one such line, and it must be byte-exact: a trailing space, a second `SUMMARY `/`SELFTEST ` line, or a missing line all fail.
4. There are zero stdout lines starting `INVENTORY\t`, because the expected auxiliary list is `[]` (lines 374, 386-390).
5. `len(re.findall(r"^PASS\t", stdout, re.MULTILINE)) == 118` exactly (lines 400-404). This counts stdout only. 117 or 119 fails, and so do lines in the `CASE\tpass\t` vocabulary.
6. **stderr is not a predicate.** Line 417 is `matched and summary_match and pass_match`. stderr only matters through the `FAIL`-marker scan in condition 2. The counter and cache branches do add `and not stderr` (lines 445, 480).

At run level, `all_matched` is `all(item["matched"])` (line 642), and the exit code is 0 only if it is true (line 655).

## Vectors (literal; expected decisions derived from source, not executed)

All three vectors use `returncode=0`.

**P1, valid positive (base True; changed True)**
```python
stdout = b"".join(b"PASS\tcase-%03d\n" % i for i in range(1, 119)) + b"SELFTEST\tpass=118\tfail=0\n"
stderr = b""
```
This gives 118 `^PASS\t` matches, one summary line equal to the expected string, no `INVENTORY\t` line and no FAIL marker, so it is matched. CRLF line endings would also match: `splitlines` strips `\r\n`, and `^` still anchors after `\n`.

**N1, pass-count negative (base False; changed False)**
```python
stdout = b"".join(b"PASS\tcase-%03d\n" % i for i in range(1, 118)) + b"SELFTEST\tpass=118\tfail=0\n"
stderr = b""
```
The summary text still claims 118, but only 117 `PASS\t` lines exist, so `pass_match` is False and nothing else changes. This is the vector specific to this step: it proves the count is taken independently of the self-reported summary. It is a no-regression control, not a before→after discriminator. An alternative with the same single-predicate isolation is P1 with the summary line removed: `summary_lines == []` fails condition 3.

**S1, stderr discriminator (base True, a false green; changed False)**
```python
stdout = P1.stdout
stderr = b"ERROR: self-test could not complete\n"
```
There is no `FAIL\t` marker, so on base `failure_lines` is empty and the step is matched. This is the summary-stderr defect named in the preregistration (`.ufo/waves/round-22/preregistration.txt:1`; also `.ufo/waves/round-21/w2/AttackRunnerStepResults.md:11-15`). A control that already rejects on base: stderr `b"FAIL\tx\n"` fails condition 2.

## Stderr policy impact

- **Draft change (summary branch only, line 417):**
```python
        matched = matched and summary_match and pass_match and not stderr
```
  `stderr` is the decoded str (line 351), and `b""` decodes to `""`, so this is byte-equivalent to `not stderr_bytes`. It makes summary steps consistent with lines 445 and 480. It also changes `matched` for S1, and the r21 matrix signature includes `matched`, so the matrix would now see the difference.
- **Risk to the 18 positive controls [INFERENCE, unresolved].** No named file shows whether the real `tools/souji-seat-audit.py --selftest`, or any of the other 11 summary steps, writes to stderr on success. If any does, for example a Python warning or diagnostics passed through from child processes, strict `not stderr` turns that real positive control red. That would break the preregistered "retain all 18 original real acceptance-step positive controls" requirement. Before adopting the strict policy, L1 must confirm that each summary step's retained `stderr_sha256` equals `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (the SHA-256 of empty input) in the actual acceptance output. If any step is non-empty, the fallback is an exact per-step expected stderr, not a relaxed policy.
- **Binding.** `inventory_projection` (lines 537-552) copies only the keys `name, expected_summary, pass_pattern, pass_count, record_checks, exact_json, baseline_mismatch_count`. So a stderr rule implemented in code, or as a non-projected step key, does not trip the frozen-inventory equality at line 601. It is bound only by the runner's own bytes. A projected key would require changing `step-inventory.json`.
- **Self-reference.** The runner hard-codes its own path in two places: the runtime-versus-committed check reads `census/round-21/run-acceptance.py` (line 223), and `INPUT_PATHS` lists that file (line 97). If L1 puts the change in a new round-22 runner file, both literals must move with it, or the new file refuses (or measures the wrong bytes).

## Bounded residuals (outside the claim; no axis claim)

- **Counted, not identified:** 118 identical lines `PASS\tsame\n` plus the correct summary are matched on both base and changed. This is the same class as the cache-check defect but is not in the preregistered C1 scope, so it is recorded only.
- **Line-splitting mismatch:** `summary_lines` and `failure_lines` use `splitlines()`, which also splits on `\r`, `\x0b`, `\x0c`, `\x1c`–`\x1e`, `\x85`, U+2028 and U+2029. `pass_count` uses `^` with `re.MULTILINE`, which anchors only after `\n`. From source reading, this causes undercounts or hidden marker splits, not a demonstrated false green. Not tested.

## Limits

I read only the named files. I did not read the source of `tools/souji-seat-audit.py`, so the real selftest's line format and stderr behavior are unknown; the vectors depend only on the runner's predicates. I did not read `census/round-14/cache-demonstration.py`, because it is not needed for this step. No LSP device was used and no grep fallback was used. No tools were installed, so I did not need to read `RULES.md`.

Report: .ufo/waves/round-22/w1/Summary1.md
Evidence: census/round-21/run-acceptance.py; census/round-21/step-inventory.json; .ufo/waves/round-22/preregistration.txt; .ufo/waves/round-21/w2/AttackRunnerStepResults.md
