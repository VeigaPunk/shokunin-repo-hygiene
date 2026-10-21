STATUS: PASS — Vector traced from source. For `r19-revision-pin-fixture` with return code 0, NO stdout record (stdout empty) and the full expected record carried on stderr, the literal expected value is `"matched": false` on base 41553adb and `"matched": false` on the changed implementation. This is a non-base-discriminating negative control: it rejects any stderr "fix" that widens stdout-only parsing to stderr. Source-only; nothing executed.

## Scope and method

- Read only the named files: `census/round-21/run-acceptance.py` (all 659 lines), `census/round-21/step-inventory.json` (r19 row, lines 153–168), `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`, `.ufo/waves/round-22/preregistration.txt`, and `corpus/QUALITY.md` (a grep of that file only). `census/round-14/cache-demonstration.py` was not needed for this step.
- No LSP device was used. This is a single-file trace done by reading, not a semantic proof.
- No tools were installed or updated, and no tests, builds or probes were run.

## Step contract (observed)

The r19 row in `run-acceptance.py` (lines 307–309) and in `step-inventory.json` (lines 153–168) has these properties:

- `kind` is `summary` (the default).
- `expected_summary` is the string `"SUMMARY total=13 failed=0 base_discriminating=6"`.
- `pass_pattern` is `^CASE\tpass\t` and `pass_count` is 13.
- It has no `record_checks` key, so `matched_counts.record_checks` = 0. Only `agreement-pin-check` carries `record_checks: 1` and `expected_summary: ""`.
- It has no `auxiliary_lines` and no `baseline_mismatch_count`.

## Vector S11-A (primary): record on stderr, no stdout record

Inputs:
- `returncode` = 0
- `stdout_bytes` = `b""`
- `stderr_bytes` = the exact success record: `SUMMARY total=13 failed=0 base_discriminating=6\n` plus 13 lines of the form `CASE\tpass\t<id>\n`.

Base trace through `summarize_result` (lines 347–481):
1. Line 352: `summary_lines` is built from `stdout.splitlines()` only, so it is `[]`.
2. Line 353: the failure-scan text is `"" + "" + stderr`. The `"\n"` joiner is skipped because stdout is empty. None of the `CASE\tpass\t` lines match `failure_lines` (lines 330–333), so `failures` is `[]`.
3. Line 367: `matched = (0 == 0) and not []`, which is `True`.
4. Line 373: the expected summary is a non-empty string, so `summary_match = [] == [expected]`, which is `False`.
5. Lines 386–389: the auxiliary check is `[] == []`, which is `True`, but it cannot rescue `summary_match`.
6. Line 401: `re.findall` runs on stdout only, so `pass_count` = 0, which is not 13, so `pass_match` is `False`.
7. Line 417: `matched = True and False and False`, which is `False`. The step is not `carry-invariant-probe`, so the extra VIOLATION check does not apply.

Literal expected values:
- Base: `"matched": false`. This is a correct rejection, so there is no false green to repair here.
- Changed: `"matched": false`. Non-empty stderr is rejected in addition to the stdout summary and pass-count mismatches.
- `matched_counts` should be `summary_lines: 0`, `observed_pass_lines: 0`, `matched_pass_lines: 0`, `record_checks: 0`, `baseline_mismatch_records: 0`, `baseline_mismatches_reported: null`.

Companion rows on the same step, for the same oracle:

| id | returncode | stdout | stderr | base matched | changed matched |
|---|---|---|---|---|---|
| S11-A | 0 | empty | exact summary + 13 pass lines | false | false |
| S11-B | 0 | empty | empty | false | false |
| S11-C (positive control) | 0 | exact summary + 13 pass lines | empty | true | true |
| S11-D | 0 | exact summary + 13 pass lines | `warning: x\n` (no FAIL marker) | true (false green) | false |

- S11-B shows that this step does not have the empty-expected-summary shape that `agreement-pin-check` has.
- S11-D is the base-discriminating stderr case. It is included only as a cross-check and may overlap another seat's vector.

## Compatibility requirements for the changed implementation

1. **Keep parsing stdout-only.** `SUMMARY_RE`, `pass_pattern`, `INVENTORY\t` and `BASELINE_MISMATCH\t` must keep reading stdout only. If any of them read stderr (for example `stdout + stderr`), S11-A would flip to `true`, which is a new false green. S11-A exists to catch exactly that regression.
2. **Add the stderr check as an extra condition.** In the summary branch, the rejection should be `matched = matched and summary_match and pass_match and not stderr`. This matches the existing counter and cache-demo rules at lines 445 and 480. `not stderr` on the surrogateescape-decoded string is equivalent to `stderr_bytes == b""`, because empty bytes decode to `""` and any non-empty bytes decode to a non-empty string. `record_checks` must stay informational and must not start gating r19, which has 0.
3. **Leave the inventory unchanged.** `inventory_projection` (lines 537–552) does not project any stderr field. The stderr rule lives only in `summarize_result`, so `step-inventory.json` stays byte-unchanged and the frozen-inventory equality check at line 601 still holds. The changed `run-acceptance.py` must be the committed bytes, because `combined_snapshot` (lines 222–224) refuses a mismatch between the running and committed runner.
4. **The real positive control must have empty stderr.** All 18 positive controls must survive. That requires the real `tests/fixtures/r19-rev-pin.py --tool tools/souji-rev-pin.py --tool-dir <ROOT>` run at the integrated revision to exit 0, emit the exact summary and 13 pass lines, and write nothing to stderr. This is UNRESOLVED from source: that fixture is outside the named read set. That it may call git and could emit warnings is [INFERENCE] only. L1's acceptance run decides it.
5. **The synthetic oracle can call the summarizer directly.** The summary branch never reads `root`; only the cache-demo branch at line 454 does. Calling `summarize_result` directly with synthetic bytes therefore needs no filesystem, process, `/proc` or F5 access, which is consistent with the preregistration.

Draft oracle row (draft only, not added to any file):

```python
R19 = {"name": "r19-revision-pin-fixture", "argv": ["<PYTHON>"],
       "expected_summary": "SUMMARY total=13 failed=0 base_discriminating=6",
       "pass_pattern": r"^CASE\tpass\t", "pass_count": 13}
RECORD = ("SUMMARY total=13 failed=0 base_discriminating=6\n"
          + "".join("CASE\tpass\tc%02d\n" % i for i in range(13))).encode()
# id, returncode, stdout, stderr, expected matched (base, changed)
S11 = [
    ("S11-A", 0, b"", RECORD, False, False),
    ("S11-B", 0, b"", b"", False, False),
    ("S11-C", 0, RECORD, b"", True, True),
    ("S11-D", 0, RECORD, b"warning: x\n", True, False),
]
# result = summarize_result(R19, rc, out, err, "0" * 40, Path("/nonexistent"))
# assert result["matched"] is expected
```

## Remaining unknowns

- Whether the real r19 fixture's stderr is empty at the changed revision. This is not source-verified and is decided by L1's acceptance run.
- No LSP or semantic cross-check was done. The trace above is a manual reading of one file.
