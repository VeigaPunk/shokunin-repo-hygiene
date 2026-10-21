# SoujiR22.Attack01 — vector `stderr/auditor-selftest/error` (want=False)

Seat: SoujiR22.Attack01, leaf, source-only. Target code `4f83fd222ffbd8825340221a8c426550ef891191`, baseline `41553adb139d06511dc386bb3ce4326aebfba675`.

## STATUS

**PASS (source-only).** From reading the source, the expected decision `want=False` is correct. The fixture feeds exactly the stored delta (one stderr replacement and nothing else). In the changed summarizer, the only conjunct that rejects this input is the new `and not stderr` (run-acceptance.py:463). The baseline accepts the same input, so this vector does discriminate base from changed, which is the R22-M2 defect. The paired positive `positive/auditor-selftest` still accepts under the changed code. The no-harm check passed: all 18 original public records have `"stderr": ""`, so none of them is newly rejected. I found no concrete mismatch.

Limits: nothing was executed. Every observed value below is derived by reading source. L1's run of all 214 decisions plus the actual 18-step acceptance is the only runtime evidence. I did not hash any files myself. Input integrity rests on the oracle's own SHA-256 gate (r22-result-oracle.py:33-35) and on the receipt's own record of the inventory digest (see Evidence point 2). I did not assess F5 byte identity because the F5 path is not a named path for this seat. It stays HELD. I installed no tools.

## Evidence

### 1. Stored delta (oracle JSON lines 23-29)

```
{"id": "stderr/auditor-selftest/error", "want": false, "group": "stderr",
 "step_name": "auditor-selftest", "stderr": "ERROR: synthetic producer incomplete\n"}
```

The vector has no `stdout`, `returncode`, `json_set` or `stdout_nested_array_depth` key, so the only delta is stderr. The id occurs exactly once in the fixture, so `--case` selects exactly one vector.

### 2. Reconstruction from pinned public inputs, done before looking at the predicate

- **Original record** (final-out-S1.json lines 29-218, `name: auditor-selftest`):
  - `returncode: 0` (213) and `stderr: ""` (214), with the empty-input SHA-256 at line 215.
  - `stdout` has 118 `PASS\t…` lines plus `SELFTEST\tpass=118\tfail=0\n` (216).
  - `observed_summary: ["SELFTEST\tpass=118\tfail=0"]` (210-212), `observed_pass_lines: 118` (204) and `matched: true` (195).
  - At the receipt level: `all_matched: true` (3), `matched_command_count: 18` (4724) and `measured_commit ff425ab835614f38205426330b9cdb93fd267045` (4725). That commit equals the oracle's `revision` (oracle JSON line 7).
- **Frozen inventory** (step-inventory.json lines 7-19): `expected_summary "SELFTEST\tpass=118\tfail=0"`, `pass_pattern "^PASS\\t"`, `pass_count 118`, `kind "summary"`. This matches `make_steps` at run-acceptance.py:301-302. The receipt records the inventory digest as `8b7b1cd8…1310` (final-out-S1.json:145), equal to the oracle's `frozen_inventory_sha256` (oracle JSON line 6).
- **How the fixture feeds it** (r22-result-oracle.py):
  1. `record = records['auditor-selftest']` (67).
  2. stdout is taken from the record, because the case has no `stdout` key (68).
  3. The step is the frozen inventory row after `<REV>`/`<REVISION>` substitution (59-60, 83). It is not cache-demo, so lines 84-85 do not apply.
  4. `returncode` is taken from the record, i.e. 0 (88).
  5. `stderr = "ERROR: synthetic producer incomplete\n"` is encoded with `surrogateescape` (90).
  6. The runner's `decode_exact` (run-acceptance.py:223-224) round-trips it to the identical non-empty `str`.

  **The fixture actually feeds the intended input.**
- **Is the expected decision correct?** The preregistration says: "summary stderr accepted despite success" is the defect. The lesson file (round-22.md:7) says: "Summary stderr must be zero bytes, including whitespace and invalid UTF8". `auditor-selftest` is a summary step and this stderr is 37 non-empty bytes, so **`want=False` is correct** under the preregistered contract. The expectation is literal and is not derived from the implementation.

### 3. Baseline predicate on this input (git show 41553adb:census/round-21/run-acceptance.py)

- `failures = failure_lines(stdout + "\n" + stderr)`. The combined text adds an empty line and `ERROR: synthetic producer incomplete`. Neither starts with `FAIL\t` or `CASE\tFAIL\t`, nor matches `^CASE\t[^\t]+\tFAIL`, so `failures == []`.
- `matched = (0 == 0) and not []`, which is True.
- `summary_lines` is computed from stdout only, so it equals `[expected]`. Auxiliary lines are `[] == []`, `baseline_mismatch_count` is absent, and `pass_count` is 118 == 118. All of these are True.
- The baseline ends with `matched = matched and summary_match and pass_match`, with no stderr term.

**Baseline result: `observed=True`, which disagrees with `want=False`.** The vector is base-discriminating. The `ERROR:` spelling deliberately sits outside the FAIL-marker list, so a marker-list expansion would not repair it. That makes it the right witness for R22-M2.

### 4. Changed predicate on this input (4f83fd2; the working tree has an empty diff against it for all named paths)

- Lines 393-410 are unchanged, so `failures == []` and `matched` starts True.
- Summary branch, lines 412-462: same result as baseline, all True. The `int()` try/except at lines 427-431 is not reached because `baseline_mismatch_group` is absent for this step.
- Line 463: `matched = matched and summary_match and pass_match and not stderr`. `not "ERROR: …\n"` is False, so **`matched` becomes False**.
- Lines 464-465 apply only to `carry-invariant-probe`, so they are not reached.
- Line 538 sets `result["matched"] = bool(False)`. The oracle check at r22-result-oracle.py:97 is `type(False) is bool and False is False`, so the vector passes.
- **Single cause:** every other conjunct is True, so the rejection is attributable only to line 463. Diagnostics are retained, not suppressed: `result["stderr"] = stderr` (403) and `stderr_sha256` (406).

### 5. Paired positive `positive/auditor-selftest` (oracle JSON lines 10-15, want=True)

The inputs are the same record with stderr `""`. Line 463 evaluates `not ""`, which is True, and every other conjunct is as in point 4. **The changed code returns `observed=True`, which equals `want`, so the positive still passes.** The baseline also returns True.

## Attacks on the changed predicate

| Attack | Source reading | Outcome |
|---|---|---|
| Whitespace-only stderr (`"\n"`) | `not "\n"` is False | rejected; the sibling vector `stderr/auditor-selftest/blank` covers this |
| A `PASS\t` line in stderr inflating the pass count | `pass_count` uses `re.findall(pattern, stdout, …)` on stdout only (447); stderr is rejected anyway | rejected; sibling `/pass` covers this |
| A `SELFTEST\t…` summary line in stderr | `summary_lines` is computed from stdout only (395) | it cannot satisfy the summary; any stderr rejects |
| Invalid UTF-8 stderr | `surrogateescape` gives a non-empty `str` such as `"\udc85"` | rejected; covered only for `r16-landing-gate` (oracle JSON 4079-4081), and the predicate is step-independent |
| Exception escape on this path | the summary branch has no JSON decode; the only new `int()` is guarded (427-431) | no crash surface for this vector |
| Mutation `not stderr` → `not stderr.strip()` (drafted, not executed) | the `/error` vector still dies, but the `/blank` vectors (12 summary steps) would wrongly pass | `/error` alone does not kill this mutation; the `/blank` siblings do |
| Mutation: delete `and not stderr` at line 463 (drafted, not executed) | the summary stderr vectors return True | **killed vector: `stderr/auditor-selftest/error`**, together with the other summary-step `stderr/*` vectors; `positive/auditor-selftest` is unaffected |

## No-harm connection

- **The 18 frozen original outputs are preserved.** Every per-command `"stderr"` in final-out-S1.json is `""`. That is the 12 summary records (214, 404, 597, 798, 989, 1180, 1370, 1561, 1752, 1941, 2134, 2325) plus the cache-demo and the 5 counter records (3381, 3618, 3855, 4100, 4345, 4560), 18 in total. The new line 463 therefore cannot newly reject any original positive. Counter and cache-demo already required `not stderr` at baseline.
- **Variable cache paths/times and subset extra fields:** line 463 is inside the `kind == "summary"` branch only, so it does not interact with the cache-demo comparison (lines 493-536) or with the non-exact counter subset check (476-478).
- **F5 byte hold:** not touched by `run-acceptance.py`. I did not verify byte identity because the path is not named for this seat, so it stays HELD.
- **Operability risk, [INFERENCE], not observed:** under the strict contract, the actual 18-step run now fails closed on any interpreter-emitted stderr. Examples are a `SyntaxWarning` or `DeprecationWarning` from a producer under the L1 run's `/usr/bin/python3`, which `-B` would not cache away. The baseline would have accepted that. This is the intended contract ("diagnostics retained, not suppressed"), not a defect. However, the public r21 receipt shows only that these producers emitted zero stderr under the interpreter used then. It does not show that they do so under the interpreter of the current run. Only L1's actual run can settle this.
- **Minor operability gap:** `matched_counts` (451-462) has no field naming the stderr rejection. The cause can only be inferred from `matched: false` alongside a non-empty `stderr`/`stderr_sha256`. That is not harm, but if a reason field were ever added it would also be the natural place to report this cause.

## Verification for L1

Run `python3 tests/fixtures/r22-result-oracle.py --runner <baseline run-acceptance.py> --case stderr/auditor-selftest/error`. Expect `observed: true, pass: false`. Then run `--runner census/round-21/run-acceptance.py` at 4f83fd2. Expect `observed: false, pass: true`. Do the same for `--case positive/auditor-selftest` and expect `observed: true` on both runners. Then run the full 214-vector oracle and the actual 18-step acceptance.
