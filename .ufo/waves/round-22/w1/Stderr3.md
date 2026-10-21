STATUS: PASS — For `r20-audit-contract`, the UTF-8 stderr diagnostic case is a false green in the base code (it is marked `matched: true`). The repaired code MUST mark it `matched: false`, and the paired positive control with empty stderr MUST stay `matched: true`. This is a source-only analysis: I executed nothing and installed no tools.

## Axes
- Calibration: the case should fail, and the base code passes it. This is a false green.
- Operability: the case must not crash, and it must be recorded byte-exactly.
- Coverage: the 18 real positive controls must stay green.

## Vector (literal, synthetic)
The step dict is the frozen inventory row (`census/round-21/step-inventory.json` lines 34–48 and `run-acceptance.py` lines 280–282). Fields used: kind `summary` (the default); `expected_summary` = `"SUMMARY\ttotal=78\tpass=78\tfail=0\tbase_discriminating=11"`; `pass_pattern` = `r"^CASE\tPASS\t"`; `pass_count` = 78.

| Case | returncode | stdout bytes | stderr bytes | base `matched` | repaired `matched` |
|---|---|---|---|---|---|
| D: UTF-8 diagnostic | `0` | `STDOUT` (below) | `"erreur : vérification incomplète — 基準\n".encode("utf-8")` | `True` (FALSE GREEN) | **`False`** |
| C: positive control | `0` | `STDOUT` | `b""` | `True` | **`True`** |

`STDOUT = b"".join(b"CASE\tPASS\tt%02d\n" % i for i in range(1, 79)) + b"SUMMARY\ttotal=78\tpass=78\tfail=0\tbase_discriminating=11\n"`

The case IDs `t01`..`t78` are chosen so that no ID starts with `FAIL`. An ID that did would make the line `CASE\tPASS\tFAIL…` match `failure_lines` (`^CASE\t[^\t]+\tFAIL`, line 333) and confound the vector.

## Source trace of base `summarize_result` for case D (observed in source)
- Decoding happens at lines 350–351. `decode_exact` is `utf-8` with `surrogateescape` (line 198). Valid UTF-8 decodes losslessly, and `stderr` becomes a non-empty `str`.
- `summary_lines` (line 352, via `SUMMARY_RE` at line 118) equals `[expected]`, so `summary_match` is True (line 373).
- `failure_lines` runs over `stdout + "\n" + stderr` (line 353). No line starts with `FAIL\t` or `CASE\tFAIL\t`, and no line matches `CASE\t…\tFAIL`, so the result is `[]`.
- There are no `INVENTORY\t` lines, matching the expected `[]` (lines 386–389). `baseline_mismatch_count` is absent (line 394).
- `re.findall(r"^CASE\tPASS\t", stdout, re.MULTILINE)` finds 78 matches, so `pass_match` is True (lines 400–404).
- `matched = returncode == 0 and not failures and summary_match and pass_match` (lines 367 and 417) evaluates to **True**. The summary branch has no stderr term. The counter branch (line 445) and the cache-demo branch (line 480) both have `and not stderr`.
- `all_matched` is True (line 642), and `main` returns 0 (line 655). This is the HIGH finding in `.ufo/waves/round-21/w2/AttackRunnerStepResults.md` lines 11–15, here instantiated for `r20-audit-contract` with a non-ASCII diagnostic.

## Repair draft (summary branch only, mirrors lines 445/480 idiom)
```python
        matched = matched and summary_match and pass_match and not stderr
```
This replaces line 417. Because `decode_exact` uses `surrogateescape`, `stderr` is empty exactly when `stderr_bytes` is empty: every input byte becomes at least one code point. So `not stderr` also rejects:
- invalid UTF-8 (each bad byte becomes a lone surrogate);
- a bare BOM `b"\xef\xbb\xbf"`, which decodes to `"\ufeff"` because the codec is `utf-8`, not `utf-8-sig`;
- whitespace-only stderr.

Whether that strictness is wanted for whitespace-only stderr is a judgement for sibling seats and L1; the literal D/C vectors don't depend on it.

## Compatibility requirements
1. **Positive control (REQUIRED):** case C must give `matched: True`, with `failure_lines == []` and `matched_counts.observed_pass_lines == 78`.
2. **Real step (REQUIRED, UNRESOLVED from named sources):** the real `r20-audit-contract` run must write zero stderr bytes on success.
   - L1 should confirm this when it runs acceptance on base `41553adb139d06511dc386bb3ce4326aebfba675`: the record's `stderr_sha256` must equal `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, the SHA-256 of empty input.
   - The same holds for all 12 summary-kind steps (lines 276–311).
   - If any of them writes benign stderr on success (for example a forwarded child-tool diagnostic or a Python warning), the repair turns a real positive control red. That would harm coverage, so the move would not be no-harm.
   - `tests/fixtures/r20-audit-contract.py` is outside my read contract, so I can't check this from source.
3. **Record fidelity (observed in source):** the record must keep byte-exact stderr.
   - `stderr_sha256` is computed from the raw bytes (line 362), and `stderr` is the `surrogateescape` text (line 360). The repair must not change either.
   - `write_exclusive` uses `json.dump(..., ensure_ascii=True)` (line 490). Non-ASCII characters are written as `\uXXXX` escapes and lone surrogates as `\udcXX`, so the output stays ASCII and nothing crashes. [INFERENCE] This rests on how `ensure_ascii` behaves; I did not open the documentation this round.
4. **No change to `failure_lines` vocabulary, F5 code, or the 160-byte synthetic-only scope.** The repair touches line 417 only.
5. **Child encoding:** `CHILD_ENV` sets `LC_ALL=C` and `PYTHONUTF8=1` (lines 107–111). A child Python process would therefore write UTF-8 stderr. [INFERENCE] This rests on the Python UTF-8 Mode documentation, which I did not open this round; the vector does not depend on it, because it injects bytes directly.

## Bounded side finding (not part of the D/C claim)
Line handling is inconsistent between checks. `summary_lines` and `failure_lines` use `str.splitlines()`, which also splits on U+0085, U+2028, U+001C–U+001E and other separators. `pass_count` uses `re.MULTILINE` `^`, which splits only on `\n`.

- For stderr, this only adds failure detection. For example, `"note\u2028FAIL\tx"` counts as a failure line in the base code, so it is not a false green.
- For stdout, a summary line hidden behind U+2028 inside a `CASE` line would be counted by `summary_lines` but not as a new `^` line.
- I have not shown this to be a false green, and it is not in the round22 claim. I'm only flagging it.

## Draft synthetic-oracle cases (for L1 integration; no file created)
```python
R20_STEP = {
    "name": "r20-audit-contract", "argv": ["<PYTHON>"],
    "expected_summary": "SUMMARY\ttotal=78\tpass=78\tfail=0\tbase_discriminating=11",
    "pass_pattern": r"^CASE\tPASS\t", "pass_count": 78,
}
R20_STDOUT = (b"".join(b"CASE\tPASS\tt%02d\n" % i for i in range(1, 79))
              + b"SUMMARY\ttotal=78\tpass=78\tfail=0\tbase_discriminating=11\n")
CASES = (
    ("r20-summary-utf8-stderr", 0, R20_STDOUT,
     "erreur : vérification incomplète — 基準\n".encode("utf-8"), False),
    ("r20-summary-empty-stderr-control", 0, R20_STDOUT, b"", True),
)
# expected base outcomes (calibration before→after): utf8-stderr True→False; control True→True
```

## Confidence and remaining unknowns
- High: the base outcome for D is True, the repaired outcome is False, and C is True in both. This follows from a line-by-line reading of the named runner.
- Unresolved: whether the real summary steps write empty stderr on success (compatibility requirement 2). This needs L1's acceptance execution.
- The `lsp` device is not available in this session, so all definition and caller tracing was done by reading the named file directly. No grep result is presented as semantic proof.
- Tools installed: none.
