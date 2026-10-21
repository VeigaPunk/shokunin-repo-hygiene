STATUS: PASS — `r16-landing-gate` with a successful stdout and a single surrogateescaped stderr byte is a summary-branch false green on base (`matched: true`); the repaired summarizer MUST yield literal JSON `false` (Python `False`, `type(...) is bool`). Source-only: nothing was executed, no tools installed.

## Vector (distinct stderr/control combination: lone non-UTF-8 byte)

Step: `r16-landing-gate` (`kind` defaults to `summary`), frozen in `census/round-21/step-inventory.json` lines 127–140 and `census/round-21/run-acceptance.py` lines 301–303:
`expected_summary = "SUMMARY\ttotal=15\tfailed=0"`, `pass_pattern = r"^CASE\t[^\t]+\tPASS\t"`, `pass_count = 15`.

Producer result fed to `summarize_result(step, returncode, stdout_bytes, stderr_bytes, revision, root)`:

```python
returncode   = 0
stdout_bytes = b"".join(b"CASE\tc%02d\tPASS\tok\n" % i for i in range(15)) + b"SUMMARY\ttotal=15\tfailed=0\n"
stderr_bytes = b"\x85"          # lone continuation byte: invalid UTF-8
```

Chosen byte `0x85`: under `surrogateescape` it becomes `"\udc85"`; under a Latin-1/cp1252-style or `b"\xc2\x85"` interpretation it would be U+0085 NEL, which Python treats as whitespace (`str.isspace`, `str.strip`, `str.splitlines` separator). This makes the vector discriminate against repairs that normalize or strip stderr, not only against "no stderr check at all".

| Implementation | `result["matched"]` (literal) | Reason |
|---|---|---|
| base `41553adb…` round-21 runner | `true` | Summary branch (lines 369–419) never consults stderr; `failure_lines` sees `"\udc85"` as a non-failure line. |
| repaired summarizer | `false` | Non-empty stderr bytes on a summary step MUST fail the step. |

Downstream (source-inferred): `all_matched` becomes `false`, `matched_command_count` drops by one, `main` returns `1`.

## Trace on base (source-inferred)

1. `decode_exact` (line 197–198) decodes with `"utf-8", "surrogateescape"` → `stderr == "\udc85"`; no `UnicodeDecodeError`, so no crash path.
2. Line 353: `failure_lines(stdout + "\n" + stderr)`. `"\udc85"` is not one of the `str.splitlines` separators (U+0085 is; U+DC85 is not), so it stays its own line after the `"\n"` join and matches none of `FAIL\t`, `CASE\tFAIL\t`, `^CASE\t[^\t]+\tFAIL(?:\t|$)` → `failures == []`.
3. Line 367: `matched = returncode == 0 and not failures` → `True`.
4. Summary branch: `summary_lines == ["SUMMARY\ttotal=15\tfailed=0"]` (line 373), no `INVENTORY\t` lines vs `[]` expected (line 389), 15 pass-pattern hits (line 401) → `matched = True` at line 417. Lines 418–419 apply only to `carry-invariant-probe`.
5. Line 481: `result["matched"] = bool(True)` → false green. Counter (line 445) and cache-demo (line 480) branches already AND `not stderr`; summary is the only gap, matching `.ufo/waves/round-21/w2/AttackRunnerStepResults.md` HIGH finding 2.

## Compatibility requirements for the repair

1. **Test emptiness on the bytes, or on the exact surrogateescape decode.** `not stderr_bytes` and `not decode_exact(stderr_bytes)` are equivalent, because the surrogateescape decode is injective and produces an empty string only for empty input. Any of these would reopen the false green for this vector or its NEL relative: `stderr.strip()`, `stderr.isspace()`, `str.splitlines()`-based "any non-blank line", `bytes.decode(..., "ignore")`, or filtering to printable characters. `decode("ignore")` turns `b"\x85"` into `""`; the Latin-1 or `b"\xc2\x85"` readings turn it into NEL, which `strip` removes.
2. **Preserve exact retention.** `stderr_sha256 = sha256_bytes(stderr_bytes)` (line 362) must stay computed over the raw bytes, and `result["stderr"]` must stay the surrogateescape string, so `"\udc85".encode("utf-8", "surrogateescape") == b"\x85"` recovers the exact byte.
3. **Keep the record writer surrogate-safe.** `write_exclusive` (lines 485–491) uses `json.dump(..., ensure_ascii=True)`, so a lone surrogate is written as the escape `"\udc85"` and never reaches the UTF-8 text stream (CPython documented `ensure_ascii` behavior, source-inferred). Switching to `ensure_ascii=False` while keeping `encoding="utf-8"` (strict) would raise `UnicodeEncodeError` at write time. The `except` at line 652 does not list `UnicodeError` explicitly, but `UnicodeEncodeError` is a `ValueError` subclass, so the run would be refused with no record rather than producing a failed-step record. That violates "reject malformed producer data without a crash" in spirit, because it loses the result.
4. **Emit a real boolean.** The existing `bool(matched)` gives JSON `false`. Oracle comparisons MUST use `is False` (or `type(v) is bool and not v`), never `== 0` or a falsy check. Otherwise the oracle repeats the bool/int confusion this round is repairing (preregistration C1).
5. **Keep inventory and historical compatibility.** `inventory_projection` (lines 538–552) copies only `name`, `expected_summary`, `pass_pattern`, `pass_count`, `record_checks`, `exact_json` and `baseline_mismatch_count`. A stderr gate placed in branch logic does not change the projection, so `step-inventory.json` and the Refusal at lines 600–602 stay byte-compatible. A new per-step key added to that copy list would require an inventory change.
6. **Do not regress the positive control.** The real `r16-landing-gate` positive control stays green only if `tests/fixtures/r16-landing-gate.py` writes zero stderr bytes on success. That file is outside my read scope; see the unresolved gap below.

Draft (for L1 integration; placement is equivalent at line 367 or line 417):

```python
        matched = matched and summary_match and pass_match and not stderr_bytes
```

Oracle row (draft):

```python
{"name": "summary-stderr-surrogateescaped-byte", "step": "r16-landing-gate",
 "returncode": 0,
 "stdout": b"".join(b"CASE\tc%02d\tPASS\tok\n" % i for i in range(15)) + b"SUMMARY\ttotal=15\tfailed=0\n",
 "stderr": b"\x85",
 "expect_base_matched": True, "expect_changed_matched": False,
 "expect_stderr_roundtrip": True}  # result["stderr"].encode("utf-8", "surrogateescape") == b"\x85"
```

## Observed vs inferred

- Observed (read): lines 197–198, 301–303, 330–333, 350–367, 369–419, 445, 480–481, 485–491, 538–552, 600–602 and 652–655 of `census/round-21/run-acceptance.py`; inventory rows 127–140; the round-21 attack review; the round-22 preregistration; QUALITY.md Q48.
- Inferred, not executed: Python `surrogateescape` mapping, `str.splitlines` and `str.isspace` treatment of U+0085 versus U+DC85, `json` `ensure_ascii` escaping of lone surrogates, and `UnicodeEncodeError` being a `ValueError` subclass.

## Unresolved

- Real `r16-landing-gate` stderr on success is unknown: the fixture was not read and nothing was run. L1's post-integration acceptance must confirm that the step still reports `matched: true`.
- No LSP device was available for this source; no semantic definition or reference proof is claimed, and only the named-file grep was used.

Report: .ufo/waves/round-22/w1/Stderr9.md
