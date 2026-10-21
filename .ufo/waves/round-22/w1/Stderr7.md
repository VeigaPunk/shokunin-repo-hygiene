STATUS: PASS — the stderr/control combination for `landing-gate-selftest` is analyzed from source only. The case uses a correct stdout and return code 0, with one `PASS`-prefixed line on stderr. Base `41553adb` marks this step matched (`true`), which is a false green. After the repair, the literal expected value is `matched: false`. Nothing was executed. No tests, builds, or probes were run, and no tools were installed.

## Scope and evidence (source-inferred, not executed)

Files read: `census/round-21/run-acceptance.py` (the whole file), `census/round-21/step-inventory.json` (the `landing-gate-selftest` row only, found by a literal search of that one named file), `.ufo/waves/round-22/preregistration.txt`, and `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`. No LSP device was available in this toolset. The single search above was a row lookup, not a semantic caller trace. No caller trace was needed, because the step is evaluated only by `summarize_result`.

The inventory pins the step as `kind: summary`, with `expected_summary: "SELFTEST\tpass=65\tfail=0"`, `pass_pattern: "^CASE\\tpass\\t"` and `pass_count: 65` (`step-inventory.json` lines 101–111). This is the same row as `make_steps` in `run-acceptance.py` lines 297–298.

## How base 41553adb evaluates stderr with a PASS prefix

The evaluation is in `run-acceptance.py`, `summarize_result`:

1. **Summary line.** `summary_lines` is built from stdout only (line 352). The `SELFTEST` line on stderr is never consulted, and a `SELFTEST` line written only to stderr can never satisfy the summary.
2. **Failure markers.** `failures` scans stdout and stderr joined together (line 353). `failure_lines` (lines 330–333) flags only lines that start with `FAIL\t` or `CASE\tFAIL\t`, or that match `^CASE\t[^\t]+\tFAIL(\t|$)`. A line starting with `PASS\t` does none of these, so `failures == []`.
3. **Pass count.** `re.findall(pattern, stdout, re.MULTILINE)` counts stdout only (lines 400–402). A stderr line therefore cannot add to or subtract from the 65-line count.
4. **The summary branch never reads stderr.** The final decision is `matched = returncode == 0 and not failures` (line 367), followed by `and summary_match and pass_match` (line 417). The counter branch (line 445) and the cache-demo branch (line 480) both add `and not stderr`; the summary branch does not.

So base gives `matched = True`, `all_matched` stays true (line 642), and the runner exits 0 (line 655). This is the "summary stderr accepted despite success" defect named in the preregistration, triggered here by the most benign-looking stderr possible. A `PASS` prefix is also exactly what a defective fix would be tempted to allowlist.

## Literal vectors (one synthetic step, same inputs before and after)

| id | stdout | returncode | stderr bytes | base `matched` | repaired `matched` |
|---|---|---|---|---|---|
| S7-control | 65 × `CASE\tpass\tcNN\n` + `SELFTEST\tpass=65\tfail=0\n` | 0 | `b""` | `true` | `true` |
| S7-pass-prefix | same | 0 | `b"PASS\tlanding-gate selftest complete\n"` | `true` (false green) | **`false`** |
| S7-no-borrow (bound) | 64 CASE lines + the same SELFTEST line | 0 | `b"CASE\tpass\tc64\n"` | `false` | `false` |

- `S7-pass-prefix` is the discriminating vector: base gives `true`, the repair gives `false`.
- `S7-no-borrow` checks a different property. The repair must keep pass counting on stdout only, so a stderr line can never make up for a missing stdout pass line (pass count 64 ≠ 65 in both versions).
- Case names MUST NOT be `FAIL`. `CASE\tpass\tFAIL` matches the failure regex at line 333 and would invalidate the control.
- Compare with `result["matched"] is False` or `is True`, not `==`. The value is produced by `bool(...)` at line 481, and an identity check stays consistent with this round's bool/int scalar-strictness claim.

## Compatibility requirements

1. **Positive control is preserved (REQUIRED).** The real `landing-gate-selftest` run must still be `matched: true`. That holds only if `tools/souji-landing-gate.py --selftest` writes nothing to stderr under `CHILD_ENV`. I could not check this from source, because that tool is not a named file. **Unresolved gap:** L1 MUST confirm that the step's `stderr_sha256` in the integrated acceptance run equals `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (the SHA-256 of empty input). The same applies to all 12 summary-kind steps among the 18 (the others are 1 cache-demo step and 5 counter steps). If any real step emits benign stderr, an empty-stderr rule turns a historical positive into a failure. That would have to be reported, not hidden by an allowlist.
2. **No stderr allowlist (REQUIRED).** Any non-empty stderr, including `PASS…`, `CASE\tpass…`, `SELFTEST…`, or whitespace such as `b"\n"`, must make the step fail. This matches the existing rule in the counter and cache-demo branches, so one policy covers all three kinds.
3. **Stdout-only counting is unchanged (REQUIRED).** `summary_lines` and `pass_count` must stay stdout-only, as `S7-no-borrow` checks. Merging stderr into the count would open a new false green.
4. **The record shape is unchanged.** `stderr` and `stderr_sha256` are already kept (lines 360–362), so no new fields are needed. The matrix signature (name, returncode, summary, counts, matched flag, per AttackRunnerStepResults) will now pick up a stderr change through the matched flag. It still does not compare stderr content directly.
5. **No change to F5, the process scanner, `/proc`, or TSVs.** The repair touches only `summarize_result`.

## Draft repair (for L1 to integrate; not applied)

The cleanest change is to move the stderr check into the shared base condition and drop the two duplicated per-branch checks:

```python
    matched = returncode == 0 and not failures and not stderr_bytes
```

with these edits to the existing lines:

```python
        matched = matched and json_match            # counter branch (was: ... and not stderr)
        matched = matched and demo_match            # cache-demo branch (was: ... and not stderr)
```

Checking `not stderr_bytes` is equivalent to `not stderr`, because surrogateescape decoding maps empty to empty and non-empty to non-empty. Using the bytes avoids depending on how the text was decoded. When `returncode is None` (line 617), stderr is non-empty and returncode is already disqualifying, so the result is unchanged.

Synthetic vector draft (calls `summarize_result` directly; `root` is unused by the summary kind):

```python
STEP = {"name": "landing-gate-selftest", "argv": ["<PYTHON>"],
        "expected_summary": "SELFTEST\tpass=65\tfail=0",
        "pass_pattern": r"^CASE\tpass\t", "pass_count": 65}
OK = ("".join("CASE\tpass\tc%02d\n" % i for i in range(65))
      + "SELFTEST\tpass=65\tfail=0\n").encode()
SHORT = ("".join("CASE\tpass\tc%02d\n" % i for i in range(64))
         + "SELFTEST\tpass=65\tfail=0\n").encode()
VECTORS = (
    ("S7-control",     OK,    b"",                                       True),
    ("S7-pass-prefix", OK,    b"PASS\tlanding-gate selftest complete\n", False),
    ("S7-no-borrow",   SHORT, b"CASE\tpass\tc64\n",                      False),
)
for name, out, err, expected in VECTORS:
    got = summarize_result(STEP, 0, out, err, "0" * 40, Path("/nonexistent"))["matched"]
    assert got is expected, (name, got, expected)
```

The base expectation for `S7-pass-prefix` is `True`. That is the before-side discrimination, and the fixture should record it as the base outcome.

## Remaining unknowns

- Whether real `souji-landing-gate.py --selftest` writes anything to stderr. See compatibility requirement 1; this must be confirmed during L1's acceptance run.
- Whether other seats prefer the per-branch fix to the hoisted one. Both produce the same `matched` value for every vector above.

## Tooling

No installs or updates. RULES.md was not read because no install was needed.
