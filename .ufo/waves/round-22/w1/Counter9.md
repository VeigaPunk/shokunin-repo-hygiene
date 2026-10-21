STATUS: PASS — Counter-predicate malformed/odd-document boundary analyzed source-only on the pinned base blob `41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py`. Ordinary malformed documents are already rejected correctly; the exploitable boundary is scalar-type equality in `json_match`, plus one adjacent deep-nesting `RecursionError` path that converts a single bad counter document into a whole-run refusal with no record. All verdicts below are source-inferred (language semantics + code reading); nothing was executed.

## Evidence basis

- Base runner: `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py` (blob sha256 `1141839963d04e9e1b968d123fa8ffebeef5d33438537cdc636350c970eeaa2b`). The working-tree runner differs (in-flight R22 integration: adds `json_exact`, `CACHE_CHECK_NAMES`, summary `not stderr`, cache case-phase/check-name gating); every finding below cites the base blob, not the working tree.
- `census/round-21/step-inventory.json` working copy is byte-identical to base (`8b7b1cd8d19561d9f4e8f06e797038b03379350cb3f3932edf04bda7aa7d1310`), so working-tree line numbers are base line numbers.
- `census/round-14/cache-demonstration.py` was not opened: the assigned predicate is the counter branch only; the cache-demo branch belongs to a sibling seat.

## Predicate boundary map (base blob, `summarize_result` counter branch)

- L421–424: `observed = json.loads(stdout)`, `except (ValueError, TypeError): observed = None`.
- L426–427 exact: `json_match = observed == expected` — Python `==`, not JSON-typed equality.
- L430–431 non-exact: `isinstance(observed, dict) and all(observed.get(key) == value for key, value in expected.items())` — subset match, extra keys permitted by design.
- L433: `observed_fields = numeric_leaves(observed)` — diagnostic only; L342–343 exclude bools.
- L435–445: `matched_counts` is a report record; it does not gate `matched`.
- L445: `matched = matched and json_match and not stderr` — counter branch already requires empty stderr (the admitted summary-stderr defect does not apply here).
- L367: base `matched = returncode == 0 and not failures`; `failures` (L353) scans stdout+stderr for `FAIL\t`/`CASE…FAIL` markers.

## Boundary verdicts — document classes (base behavior)

| Document on stdout (rc=0, stderr="") | Base `matched` | Crash-free? |
|---|---|---|
| Not JSON / truncated (`{"F2_entry": 0, "admitted_ent`) | False (`observed=None`) | Yes |
| Well-formed non-object: `null`, `true`, `0`, `[...]`, `"..."` | False | Yes |
| Empty stdout / whitespace-only | False | Yes |
| Valid JSON + trailing garbage on a later line | False (`json.loads` raises) | Yes |
| Object missing an expected key | False (`None == value` fails; dict identity fails exact) | Yes |
| Non-exact counter with extra keys | True — **by design** (subset predicate), not a defect | Yes |
| Same values but int→bool/float scalars (`false` for `0`, `33.0` for `33`) | **True — false green** (in-scope defect) | Yes |
| Duplicate keys, last value equal to expected | True — RFC-ambiguous; permissive-parser behavior | Yes |
| `NaN`/`Infinity`/`6e0`/`0.0` scalar forms | `NaN`: False. `6e0`/`0.0` where int expected: **True** (float `==` int) | Yes |
| Deeply nested document (≳1000 levels) | Whole-run refusal, exit 2, **no record written** | **No** |
| JSON string line starting `FAIL\t` inside a scalar | False (false-negative via `failure_lines`) | Yes |

## Actual counter expectations (authoritative anchor)

From base `COUNTER_EXPECTATIONS` L120–180 and frozen inventory (byte-identical to base):

- `r13-counter-31984f4` (exact, inventory L207–234): `{"F2_entry": 0, "admitted_entries": 4, "evidence_gate": 0, "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81", "sources": 33, "tiers": {"A": 29, "B": 3, "C": 1}, "statuses": {"mined": 16, "queued": 15, "rejected": 2}}`
- `r13-counter-6f8ee0f` (exact): same shape; `F2_entry: 1, evidence_gate: 1, admitted_entries: 5, sources: 37, tiers {"A":33,"B":3,"C":1}, statuses {"mined":20,...}`.
- `r14-counter-a31642d` (exact): `cache_gate: 0, cache_fixture: 0, boundary_fixture: 0, source_rows: 37, admitted_knowledge: 5, held_knowledge: 1`, same tiers/statuses as 6f8ee0f.
- `r14-counter-552cae4` (exact): gates `1,1,1`; `source_rows: 40`; `tiers {"A":36,...}`; `statuses {"mined":23,...}`.
- `r13-counter-b576341` (**non-exact**, inventory L323–337): `{"measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3", "admitted_entries": 6}`.

## In-scope defect (admitted: JSON scalar type equality)

Python `==` makes `False == 0`, `True == 1`, and `0.0 == 0` (and `{"A": 29.0} == {"A": 29}`) true, so `observed == expected` at L427 does not implement JSON scalar type equality. The bool substitution is exploitable at the 0/1-valued gate fields above; the float substitution at **every** integer leaf, including nested `tiers`/`statuses`. For the non-exact counter, `observed.get(key) == value` at L431 admits `6.0` for `6` (bool cannot hit `6`, so float is the non-exact vector). `matched_counts` (L435–443) does record the type shift — `numeric_leaves` drops bools — but is diagnostic only and cannot gate.

## Literal positive/negative vectors (stdout payloads; all assume rc=0, stderr="")

**Positive (must stay matched in base and after repair):**
```json
{"F2_entry": 0, "admitted_entries": 4, "evidence_gate": 0, "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81", "sources": 33, "tiers": {"A": 29, "B": 3, "C": 1}, "statuses": {"mined": 16, "queued": 15, "rejected": 2}}
```
Base decision: matched. Required decision: matched.

**Negative N1 — malformed document (already correct; regression guard for the "reject malformed producer data without a crash" claim):**
```
{"F2_entry": 0, "admitted_ent
```
Base decision: not matched, no crash, record written. Required: identical.

**Negative N2 — scalar-typed document (in-scope defect, base false green):**
```json
{"F2_entry": false, "admitted_entries": 4, "evidence_gate": false, "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81", "sources": 33.0, "tiers": {"A": 29, "B": 3, "C": 1}, "statuses": {"mined": 16, "queued": 15, "rejected": 2}}
```
Base decision: **matched (false green)** — `False == 0` at L427. Required: not matched. A float-only variant (`33.0` alone, or `"A": 29.0` nested) exercises the same defect without bools.

**Negative N3 — non-exact scalar vector (`r13-counter-b576341`):**
```json
{"measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3", "admitted_entries": 6.0}
```
Base decision: **matched (false green)** — `6.0 == 6` at L431. Required: not matched. (Extra-key superset documents remain matched by design — see rejected scope.)

**Negative N4 — depth-boundary document (adjacent risk, see below):**
```json
{"x": {"x": {"x": { … ~1500 nested levels … }}}}
```
Base decision: `json.loads` (L422) or `numeric_leaves` (L433) raises `RecursionError` — not caught by `except (ValueError, TypeError)` at L423, but is caught as `RuntimeError` by main's handler (base L652) → whole-run refusal, exit 2, **no result file**. Required: per-step `matched: false` with the record still written (e.g., catch `RecursionError` alongside `ValueError` and bound the `numeric_leaves` walk). This is a denial-of-record, not a false green; it sits inside the preregistration sentence "reject malformed producer data without a crash" but is not one of the three admitted predicate defects — flagging as residual boundary risk for the repair to avoid inheriting.

## Rejected / added scope — do not fold into this repair

- **Non-exact superset acceptance** (L430–431): `r13-counter-b576341` is frozen `exact_json: false`; accepting extra keys is the declared historical contract. Tightening to exact identity changes the r13 expectation, not a defect repair.
- **Duplicate keys**: `json.loads` is a permissive RFC-8259 parser (last wins). Rejecting duplicates needs `object_pairs_hook`; not an admitted defect.
- **Non-strict scalars** `NaN`/`Infinity`: accepted by Python `json`, never equal any expected leaf → always rejected already. Strict-JSON parsing is added scope.
- **`FAIL\t` line inside a JSON string scalar**: false *negative* (over-reject), not a false green; a robustness note only.
- **Type-insensitive `matched_counts` diagnostics** (`observed_fields.get(key) == value`, bool leaves dropped): report-only fields, already never gate `matched`; not the predicate.
- Summary-stderr and cache-check-identity predicates are separate admitted defects owned by sibling seats; the counter branch already gates `not stderr` at L445.

## Verification gaps

- Source-only review; no runner, fixture, or Python expression was executed. All base/required decisions are language-semantics inferences from the cited base lines.
- The working tree is mid-integration (diff observed); this report deliberately cites only the base blob and does not re-review the in-flight repair. The in-flight `json_exact` helper, if it lands, would close the in-scope defect and N2/N3; N4 (RecursionError) is not addressed by `json_exact` alone — the local `except` and `numeric_leaves` recursion remain the fix points.
- `xd://lsp` is not mounted in this session; all caller/line citations are direct blob reads, not LSP semantics.
- No tools installed; no files other than this report written.

Base: 41553adb139d06511dc386bb3ce4326aebfba675
Report: .ufo/waves/round-22/w1/Counter9.md
