STATUS: PASS — For `r19-seat-audit-shapes`, the input "valid stdout, exit 0, stderr has a FAIL marker with no tab" is a false green at base 41553adb: `matched` is `True`. After the repair, the literal expected `matched` is `False`. Source only. No code was run.

Axes: calibration (this vector), operability (no change to the record shape), coverage (one stderr/control combination). No trade-offs between axes.

## Vector (source-inferred, not executed)

Step row: `r19-seat-audit-shapes` (`census/round-21/step-inventory.json` lines 72–84; `run-acceptance.py` lines 291–293). This is a summary step with these expectations:
- expected summary `SUMMARY total=17 failed=0 base_discriminating=12`
- pass pattern `^CASE\tpass\tchanged/`
- pass count 17

| id | returncode | stdout | stderr (bytes) | base matched | repaired matched | base-discriminating |
|---|---|---|---|---|---|---|
| S5-fail-notab | 0 | 17 × `CASE\tpass\tchanged/<n>\n` + `SUMMARY total=17 failed=0 base_discriminating=12\n` | `b"FAIL r19 shape mismatch\n"` (space, no tab) | `True` | `False` | yes |
| S5-fail-bare | 0 | same | `b"FAIL\n"` | `True` | `False` | yes |
| S5-control-clean (positive control) | 0 | same | `b""` | `True` | `True` | no |
| S5-control-tab (existing-detector control) | 0 | same | `b"FAIL\tr19 shape mismatch\n"` | `False` | `False` | no |

## Why base gives True (observed in source)

- `failure_lines` (`run-acceptance.py` lines 330–333) recognizes only three line shapes: lines starting with `FAIL\t`, lines starting with `CASE\tFAIL\t`, and lines matching `^CASE\t[^\t]+\tFAIL(?:\t|$)`.
  - `FAIL r19 …` and a bare `FAIL` match none of these, so `failures == []` (line 353).
  - The scan runs over stdout and stderr joined together.
- Line 367 sets `matched = returncode == 0 and not failures`, which is `True`.
- In the summary branch (lines 369–419):
  - `summary_lines` comes from stdout only and equals `[expected]`.
  - There are no `INVENTORY\t` lines, which equals the expected `[]`, so `auxiliary_match` is true.
  - `pass_count` is 17 out of 17.
  - Line 417 therefore leaves `matched` as `True`.
- Nothing in the summary branch checks `stderr`. Only the counter branch (line 445) and the cache-demo branch (line 480) do `and not stderr`.
- `all_matched` (line 642) can therefore be `True` while stderr contains a failure word.

## Expected after the repair (literal)

- `matched` is `False` for S5-fail-notab and S5-fail-bare.
- `matched` is `True` for S5-control-clean.
- `matched` is `False` for S5-control-tab.
- `failure_lines` is `[]` for both no-tab vectors, both before and after the repair. That field must not start reporting them.

## Compatibility requirements

1. **Where to fix.** Add the stderr gate to the summary-branch `matched` predicate, for example by changing line 417 to `matched = matched and summary_match and pass_match and not stderr`. This matches the existing counter and cache-demo branches.
   - Do NOT widen `failure_lines` to cover bare or space-separated `FAIL`.
   - Widening it would change the retained `failure_lines` record field and its projection.
   - It would also not catch other stderr text, such as `ERROR: …` from the AttackRunnerStepResults example, because the vocabulary would still be narrow.
2. **Empty means zero bytes.** Whitespace-only stderr (`b"\n"`) must also fail. Under `not stderr` on the decoded string this already holds. State it explicitly so nobody adds `.strip()` and creates a new false green.
3. **Real positive controls.** All 18 real acceptance steps, including the real `r19-seat-audit-shapes` run, must emit zero stderr bytes, or the gate turns them red.
   - `[INFERENCE]` I could not check this, because `tests/fixtures/r19-seat-audit-shapes.py` is not a named readable file.
   - Unresolved: whether any real summary step writes warnings or diagnostics to stderr under `CHILD_ENV`. L1's acceptance run must confirm all 18 still match.
4. **Record shape.** The retained fields `stderr`, `stderr_sha256`, `failure_lines` and `matched_counts` must stay unchanged; only `matched` changes. The frozen `step-inventory.json` projection (lines 537–552) must stay byte-identical. The gate is code, not an inventory key, so `inventory_projection` does not change.
5. **Same scenario before and after.** Feed the same synthetic tuple `(step, returncode, stdout_bytes, stderr_bytes)` into `summarize_result` at base and at the changed implementation.
   - The step comes from `make_steps`, or is a literal copy of the inventory row.
   - Process scanner, `/proc`, F5 and historical TSVs must not be touched.
   - `root` is used only by the cache-demo branch, so a placeholder `Path` is fine for summary vectors.

Draft oracle rows (for L1 integration; no file created):

```python
R19 = {"name": "r19-seat-audit-shapes", "argv": ["<PYTHON>"],
       "expected_summary": "SUMMARY total=17 failed=0 base_discriminating=12",
       "pass_pattern": r"^CASE\tpass\tchanged/", "pass_count": 17}
OK_STDOUT = b"".join(b"CASE\tpass\tchanged/%d\n" % i for i in range(17)) \
    + b"SUMMARY total=17 failed=0 base_discriminating=12\n"
STDERR5 = (
    # (id, stderr, base_matched, repaired_matched)
    ("S5-fail-notab", b"FAIL r19 shape mismatch\n", True, False),
    ("S5-fail-bare", b"FAIL\n", True, False),
    ("S5-control-clean", b"", True, True),
    ("S5-control-tab", b"FAIL\tr19 shape mismatch\n", False, False),
)
# assert summarize_result(R19, 0, OK_STDOUT, err, REV, ROOT)["matched"] is expected
# assert summarize_result(...)["failure_lines"] == ([] if b"\t" not in err else [err.decode().rstrip("\n")])
```

## Remaining unknowns / limits

- The real r19 fixture's stderr behaviour has not been verified (file not in the named read set). It must be confirmed by L1's acceptance run.
- A stdout `FAIL` line without a tab is also undetected, and a stderr-only gate does not catch it. That is a separate combination outside this seat's scope and is not claimed here.
- The `xd://lsp` device is unavailable in this session. The only text search was one grep of the named `corpus/QUALITY.md`, and it is not used as semantic proof.
- No tools were installed. Nothing was executed.

Report: .ufo/waves/round-22/w1/Stderr5.md
