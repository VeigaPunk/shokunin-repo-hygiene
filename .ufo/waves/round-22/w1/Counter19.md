STATUS: PASS — Assigned boundary (counter predicate, empty stdout) analyzed against baseline bytes `41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py` (blob `1ecbad0962bca1898f94f179e2aa4d1a9a7ecd7b`) and the mid-integration working-tree runner (blob `0a9f20c967208c19fd543f1d9463e2ec8e4a3a01`). The boundary fails closed on both; no in-scope defect exists at it. All statements below are source-inferred; nothing was executed, per contract.

## Basis and freshness

| file | base blob | working tree | status |
|---|---|---|---|
| `census/round-21/run-acceptance.py` | `1ecbad0` | `0a9f20c` | DIFFERS — L1 repair integrated in tree (diff reviewed in full, 63+/9-) |
| `census/round-21/step-inventory.json` | `09c4d59` | `09c4d59` | identical to base |
| `census/round-14/cache-demonstration.py` | `b302186` | `b302186` | identical to base |

Counter-branch analysis is grounded on the baseline blob via `git show 41553adb…:census/round-21/run-acceptance.py`; the parent directive's re-grounding is satisfied. Baseline line numbers below match that blob; working-tree line numbers are the integrated file's.

## The predicate under review

Baseline `summarize_result`, `kind == "counter"` (baseline lines 420–445; WT lines ~465–482):

```python
try:
    observed = json.loads(stdout)
except (ValueError, TypeError):
    observed = None
expected = step["expected_summary"]
if step["exact_json"]:
    json_match = observed == expected            # base; WT: json_exact(observed, expected)
else:
    json_match = (isinstance(observed, dict)
                  and all(observed.get(key) == value for key, value in expected.items()))
                  # WT: key in observed and json_exact(observed[key], value)
...
matched = matched and json_match and not stderr
```

## Actual counter expectations located

- `r13-counter-31984f4` — `exact_json: true`; expected dict includes `F2_entry: 0`, `admitted_entries: 4`, `evidence_gate: 0`, `sources: 33`, `measured_commit: "31984f47…"`, nested `tiers`/`statuses` (baseline lines 122–131; `census/round-21/step-inventory.json` lines 207–227).
- `r13-counter-b576341` — `exact_json: false`; expected `{"measured_commit": "b5763415…", "admitted_entries": 6}` (baseline lines 171–179; inventory lines 323–336). This is the only non-exact counter; its expectations are the superset-match target.
- All five `COUNTER_EXPECTATIONS` entries have non-empty dict expectations; none expects `null` or a scalar.

## Boundary verdict: empty stdout fails closed

For `stdout_bytes == b""` (and whitespace-only `b" \n"`): `json.loads` raises `ValueError` → `observed = None`. Exact branch: `None == expected_dict` → `False` (base); `json_exact(None, dict)` → `type` mismatch → `False` (WT). Non-exact: `isinstance(None, dict)` → `False`. Result: `matched = False`, `all_matched = False`, exit 1 **with** a written record — an honest step failure, not a run refusal. The behavior is identical under base and integrated code because the repair changed equality of parsed values, not parse-failure handling. Every non-dict JSON top level (`null`, `[]`, `{}`, `true`, `0`, `"x"`) and every unparseable byte string (`not json`, truncated `{"a":1`) lands in the same fail-closed path. `failure_lines` cannot compensate for non-JSON stdout because any failure-marker text itself breaks `json.loads`.

## Literal vectors for the synthetic result-oracle

```text
# P1 — positive control, exact counter (MUST match on base AND changed)
step=r13-counter-31984f4 returncode=0 stderr=b""
stdout=json.dumps(expected_dict, sort_keys=True) + "\n"
  base: observed==expected → matched=True
  changed: json_exact → matched=True   (retained real positive)

# N1 — ASSIGNED BOUNDARY: empty stdout (MUST NOT match on base AND changed)
step=r13-counter-31984f4 returncode=0 stderr=b"" stdout=b""
  base:    observed=None; None==expected → matched=False
  changed: json_exact(None,dict) type-mismatch → matched=False

# N1b — companion boundary rows (same fail-closed path, all matched=False, both builds)
stdout=b"null"      # parsed null collapses to observed=None — diagnostic note F2
stdout=b" \n\t"     # whitespace-only
stdout=b"[]"        # wrong JSON type
stdout=b"{}"        # missing every expected key
stdout=b"not json"  # unparseable

# N2 — scalar-type defect discriminating row (admitted defect 1, in scope)
step=r13-counter-31984f4 returncode=0 stderr=b""
stdout = expected dict with "F2_entry": false  (all other fields identical)
  base:    False == 0 → observed==expected → matched=True   ← FALSE GREEN on base
  changed: type(bool) is not type(int) → matched=False      ← discriminates repair

# N2b — same defect through the NON-exact branch (numeric float)
step=r13-counter-b576341 returncode=0 stderr=b""
stdout={"measured_commit":"b5763415cc67ecff1e8fe56c58c39a6fb106d7a3","admitted_entries":6.0}
  base:    6.0 == 6 → matched=True   ← FALSE GREEN on base
  changed: json_exact leaf → matched=False

# P2 — non-exact superset positive (retain; proves extras stay allowed)
step=r13-counter-b576341 returncode=0 stderr=b""
stdout={"measured_commit":"b5763415cc67ecff1e8fe56c58c39a6fb106d7a3",
        "admitted_entries":6,"extra_ignored":"x"}
  base/changed: matched=True

# N3 — counter stderr contract (unchanged by repair; guard row)
step=r13-counter-31984f4 returncode=0 stderr=b"WARN producer note"
stdout=valid expected JSON
  base/changed: matched=False   (counter already required empty stderr)
```

## Findings by severity

**HIGH — none at this boundary.** Empty stdout cannot produce a false green in either build. The only HIGH that touches the counter predicate is the already-admitted scalar-type defect (r21 finding, `.ufo/waves/round-21/w2/AttackRunnerStepResults.md` §1): baseline `False == 0`/`6.0 == 6` greens; the integrated `json_exact` (`type(x) is` plus recursive key set equality) closes it at every depth including the non-exact leaves, which the diff confirms (`key in observed and json_exact(...)` also repairs a latent baseline hole where a missing key satisfied an expected `null` via `.get` returning `None`).

**MEDIUM — none.**

**LOW (latent, zero current exposure) — F1: parse-failure/`null` collapse at the top level.** `observed = None` conflates "unparseable/empty stdout" with stdout literally `null`. Verdict-safe today: every pinned expectation is a non-empty dict, so `matched=False` either way. It becomes a false green only under a hypothetical `exact_json` counter whose `expected_summary` is `None` (`None == None` on base; `json_exact(None, None)` on WT). Optional zero-cost hardening if the same lines are edited anyway — a module sentinel `PARSE_FAILED = object()` with `observed_json` serialized as `None` keeps the record shape; otherwise disclose and do not expand scope.

**LOW (boundary-adjacent, behavior accepted) — F2: pathological nesting aborts the whole run.** `json.loads` on deeply nested stdout raises `RecursionError` (a `RuntimeError`, not `ValueError`), which escapes the per-step `except`, is caught by `main`'s refusal handler (baseline line 652), and returns exit 2 **with no record and no traceback**. The preregistration clause "reject malformed producer data without a crash" is satisfied literally, but the granularity is whole-run refusal, not a marked step failure. Fixture vectors should bound nesting depth unless the run-refusal path itself is the vector. Per-step `RecursionError` capture is **rejected added scope**.

**INFORMATIONAL — F3: non-strict JSON constants.** Python's default decoder accepts `NaN`, `Infinity`, `-Infinity`. None can satisfy a pinned expectation (`NaN != NaN`; `Infinity` absent from all expectations; `numeric_leaves` excludes floats), so no green path exists. Strict rejection via `parse_constant` is **rejected added scope**.

**INFORMATIONAL — F4: diagnostic collapse.** `observed_json: null` is identical for `b""`, `b"null"`, and garbage stdout; the raw `stdout` text and `stdout_sha256` in the same record preserve the distinction. A parse-failure marker field is **rejected added scope**; report wording should not claim "producer emitted JSON null" from `observed_json` alone.

## In-scope defect vs rejected added scope (at this boundary)

- In-scope, exercised by N2/N2b: JSON scalar type equality (bool/int, float/int) — the counter branch is one of its two sites; vectors discriminate base vs changed.
- In-scope, preserved: counter stderr-empty requirement (N3) — already present for counter; the summary-branch repair must not weaken it.
- Boundary verdict itself (N1 family): correct fail-closed on both builds; these are **guard/regression vectors**, not defect-discriminating rows. Do not count them as `base_discriminating`.
- Rejected added scope: byte-level stdout equality for `exact_json` (canonical serialization is out of claim); strict `parse_constant` NaN/Infinity rejection; `observed_json` parse-failure marker field; per-step `RecursionError` capture; cache-demo `checks`/`cases` identity already landed in WT (`CACHE_CHECK_NAMES`, `CACHE_CASE_PHASES` — no counter-branch action needed).

## Residual risk

- If the synthetic oracle calls `summarize_result` directly, an unwary deep-nesting negative vector will raise `RecursionError` inside the fixture harness, not return a verdict — bound depth or expect the refusal path explicitly.
- `json_exact` intentionally treats `4.0` as unequal to `4` though JSON defines one numeric type; correct for the "scalar type equality" claim, but report wording should say "decoded scalar type equality," not "canonical JSON equality."
- Non-exact counter `b576341` still permits arbitrary extra keys by design; the frozen inventory records only the two expected fields — retained contract, not a defect.

## Verification gaps

Source-only review; no runner, fixture, or oracle executed (contract). `xd://lsp` is not a mounted device in this session ("No such tool" on status check); caller/definition checks therefore rest on exact reads of the named baseline blob, WT diff, and pinned inventory — no grep was substituted as semantic proof. Working-tree `run-acceptance.py` may change again before L1's acceptance run; re-verify the counter-branch hunks against the integrated blob at claim time. No tools installed, no other files written.

Report: .ufo/waves/round-22/w1/Counter19.md
Sources: census/round-21/run-acceptance.py@41553adb139d06511dc386bb3ce4326aebfba675 (blob 1ecbad0, lines 120-180, 330-345, 420-445, 555-655); census/round-21/run-acceptance.py WT (blob 0a9f20c, integrated `json_exact`/cache-identity diff); census/round-21/step-inventory.json:207-336; .ufo/waves/round-22/preregistration.txt; .ufo/waves/round-21/w2/AttackRunnerStepResults.md; corpus/QUALITY.md Q47-Q50; census/round-14/cache-demonstration.py (boundary context only).
