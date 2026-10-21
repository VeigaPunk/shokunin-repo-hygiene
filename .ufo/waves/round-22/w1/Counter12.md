STATUS: PASS — Source-only analysis of counter-predicate nonfinite JSON numeric semantics on base 41553adb139d06511dc386bb3ce4326aebfba675 (`git show` reads per L1 instruction) and the currently integrated working-tree draft of the named runner. No execution; all findings source-inferred from pinned bytes plus Python stdlib `json` documentation (named public source). Axes exercised: calibration (verdict correctness), operability (record/artifact strictness, crash-free malformed handling), coverage (boundary vector selection). No lane/fleet/census-root directory reads; no tools installed.

## Actual counter expectations/values located

Base `COUNTER_EXPECTATIONS` (`census/round-21/run-acceptance.py:120-180`, byte-identical in working tree): four exact counters (`exact_json=True`) and one subset counter (`exact_json=False`). Boundary-critical expected values: `r13-counter-31984f4` expects `F2_entry: 0` and `evidence_gate: 0` (lines 126-131; frozen inventory `census/round-21/step-inventory.json:208-234`); `r14-counter-a31642d` expects `cache_gate: 0`, `cache_fixture: 0`, `boundary_fixture: 0` (lines 148-156); subset counter `r13-counter-b576341` expects `admitted_entries: 6` (lines 171-179; inventory lines 322-338). The zero-valued integer expectations are exactly where nonfinite-adjacent decode semantics bite (underflow → `0.0 == 0`).

## Findings (by severity)

### F1 — MEDIUM: nonfinite literals accepted by decoder and re-emitted into the acceptance record (base AND current draft)

Python `json.loads` accepts the non-standard literals `NaN`, `Infinity`, `-Infinity` by default (`parse_constant` hook; stdlib docs, https://docs.python.org/3/library/json.html) and decodes out-of-range valid literals (`1e400`) to `inf` via `float`. The counter branch (base:422; draft:468) and cache-demo branch (base:448; draft:494) pass no `parse_constant`/`parse_float` hooks, so decoded `observed`/`payload` may contain `nan`/`inf`. `result["observed_json"]` (draft:481/525) flows verbatim into `record["commands"]` (draft:705) and `write_exclusive`'s `json.dump(..., ensure_ascii=True)` (draft:546; base:490) without `allow_nan=False`, re-emitting `NaN`/`Infinity` as bare tokens.

Verdict behavior is correct (a nonfinite never `==` a finite expected value, so no false green on that path), but two concrete harms:

- The exclusive acceptance record is not strict RFC JSON whenever a producer emits `NaN`/`Infinity`/`1e400` anywhere — including inside subset-counter *extra* keys where the verdict is `matched=true` by contract tolerance. On the current draft, `all_matched` can be `true` while the record file itself is unparseable by strict consumers (jq, non-Python validators). Preregistration: "Reject malformed producer data without a crash"; `NaN` is malformed producer data currently admitted into the artifact.
- On the subset counter, a document containing `NaN` anywhere is not JSON at all yet still yields `json_match=True` (draft:476-478) — a residual false green the admitted scalar-type repair does not itself close, because `json_exact` only sees keys the expectation names.

Both base and draft are affected identically; the integrated draft did not touch the decode/encode hooks.

### F2 — LOW: cache-demo decode guard asymmetric with counter (crash-class coverage gap)

Draft counter branch catches `(ValueError, TypeError, RecursionError)` (draft:469); cache-demo branch catches only `(ValueError, TypeError)` (draft:494-495 per file). A deeply nested cache-demo payload raises `RecursionError`, escapes `summarize_result`, and lands in `main`'s outer catch (draft:708) — exit 2 with the entire 18-step record unwritten rather than one failed step. Not a crash (it is caught), but malformed producer data aborts the whole acceptance record. In-scope as completeness of the named malformed-data clause; one-word fix.

### F3 — context, covered by draft: underflow/float boundary face of the admitted scalar defect

On base, `observed == expected` (base:427) made `"F2_entry": 1e-400` (decodes to `0.0`) green against expected `0` — the nonfinite-adjacent boundary of the admitted bool/int scalar confusion (`0.0 == 0` is true; the literal is not even representable). Same for `33.0`, `29.0` nested leaves, `true`/`1.0` for `evidence_gate: 1`. Draft `json_exact` (draft:373-385) gates `type(observed) is not type(expected)` recursively and closes all of these; confirmed present for exact counters (draft:473), subset counters (draft:477), and cache numeric expectations (draft:516-518). A bool-only repair would have left every float variant green — the oracle must include float vectors, not just `false`/`0`.

## Literal positive/negative vector pair (drafted)

Positive control — `r13-counter-31984f4` (exact), all other expected fields unchanged:

```json
{"F2_entry": 0, "admitted_entries": 4, "evidence_gate": 0, "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81", "sources": 33, "tiers": {"A": 29, "B": 3, "C": 1}, "statuses": {"mined": 16, "queued": 15, "rejected": 2}}
```

Expected: `matched=true` on base and draft. Secondary positive (subset `r13-counter-b576341`): `{"measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3", "admitted_entries": 6, "extra": 1.5}` → `matched=true` on both (subset tolerance is contract; finite float extra is harmless). Guards against an over-strict repair that would reject tolerated shapes — a rejected added scope.

Negative set — `r13-counter-31984f4`, identical except the named field; each must be `matched=false` on the changed implementation:

```json
{"F2_entry": false, "...": "..."}        // N1 admitted bool/int defect (base green → red)
{"F2_entry": 1e-400, "...": "..."}       // N2 underflow boundary: decodes 0.0 (base green → red)
{"F2_entry": NaN, "...": "..."}          // N3 invalid-JSON literal Python accepts; record stays strict only if decode rejects
{"F2_entry": 1e400, "...": "..."}        // N4 valid literal → inf on decode; verdict false either way, record strictness is the test
{"sources": 33.0, "...": "..."}          // N5 plain float twin of N1 (base green → red)
{"tiers": {"A": 29.0, "B": 3, "C": 1}}   // N6 nested float leaf (base green → red)
```

N3/N4's asserted outcome under the proposed repair is *strict record + red step*: `observed_json` becomes `null` (or a recorded rejection marker), the record file remains parseable by a strict JSON reader, and no `NaN`/`Infinity` token appears in record bytes. On base, N3/N4 already fail the verdict but poison the record — the before→after discriminant for F1 is record bytes, not just `matched`.

Subset-specific negative (F1 verdict face): `{"measured_commit": "b5763415...", "admitted_entries": 6, "extra": NaN}` → base/draft `matched=true` + malformed record; after repair → `matched=false` + strict record.

## Drafted minimal patch (advisory; report-only)

```diff
+import math
+
+def _reject_json_constant(token: str):
+    raise ValueError("non-JSON literal in producer output: " + token)
+
+def _finite_json_float(token: str):
+    value = float(token)
+    if not math.isfinite(value):
+        raise ValueError("nonfinite JSON number in producer output: " + token)
+    return value
+
@@ counter branch (draft:468) @@
-            observed = json.loads(stdout)
+            observed = json.loads(stdout, parse_constant=_reject_json_constant,
+                                    parse_float=_finite_json_float)
@@ cache-demo branch (draft:494) @@
-            payload = json.loads(stdout)
+            payload = json.loads(stdout, parse_constant=_reject_json_constant,
+                                    parse_float=_finite_json_float)
-        except (ValueError, TypeError):
+        except (ValueError, TypeError, RecursionError):
@@ write_exclusive (draft:546) @@
-        json.dump(payload, handle, ensure_ascii=True, indent=2, sort_keys=True)
+        json.dump(payload, handle, ensure_ascii=True, allow_nan=False,
+                  indent=2, sort_keys=True)
```

Effect: malformed/nonfinite producer output takes the existing `observed = None` → mismatch path (no crash, red verdict, strict record); `allow_nan=False` is a defense-in-depth backstop making any residual nonfinite a hard write error rather than silent corruption. Known accepted boundary: `1e400` (valid JSON, unrepresentable as finite float) is treated as malformed — a chosen stricter boundary, disclosed here; `1e-400` → `0.0` remains accepted as finite and is handled by `json_exact` at the verdict layer.

## Rejected added scope (explicit non-moves)

- Duplicate-key detection (`object_pairs_hook`), canonical/ordered JSON output, or `Decimal`/`parse_int` precision hooks — Python's documented last-wins and arbitrary-precision int behavior needs no change; nothing claimed.
- Rejecting all floats in counter documents (contract-emitted fields are int-valued, but subset extras tolerate them by design; verdict layer handles it).
- `strict=True` or JSON parsing of summary-kind stdout; executed-command authentication and malicious-producer attestation — explicitly excluded by preregistration.
- Any `numeric_leaves`/`matched_counts` shape change — diagnostics only, never gated; altering keys adds churn without verdict effect. (Optional non-required observation: floats/nonfinite remain invisible to `matched_counts`, as booleans were; harmless while `matched` ignores it.)
- F5 parser/formatter, process scanner, NAMESPACE/reap/historical exposure — held by preregistration; untouched.

## Residual risk / verification gaps

- No execution: decoder behavior is cited to Python stdlib `json` documentation (named authority permitted by preregistration), not observed. `1e-400`→`0.0` and `1e400`→`inf` are IEEE-754/documented consequences, marked `[INFERENCE]`-equivalent pending L1's acceptance run.
- Working-tree draft is mid-integration; line numbers cited against its current bytes (diff vs base reviewed: `json_exact`, `CACHE_CHECK_NAMES`, `CACHE_CASE_PHASES`, summary `not stderr` at draft:463, `RecursionError` counter guard, `int()` `ValueError` guard). Base citations via `git show 41553adb:...`.
- `xd://lsp` not mounted in this session; no semantic references/definition/diagnostics checks performed or claimed — text reads of the single named file only, per contract.
- No tools installed; no files written outside this report.
