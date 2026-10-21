# Attack36 — `scalar/r13-counter-31984f4/admitted_entries/float` (+ paired positive)

STATUS: source-only review of the named files; no execution, no builds, no tests. Result for this vector: **PASS for the changed predicate** — expected decision `want=false` is correct, the fixture genuinely feeds the mutated input, and the changed `summarize_result` rejects for the intended reason. No actionable defect found in this vector's scope. Findings are grounded in `census/round-21/run-acceptance.py` (changed tree), `tests/fixtures/r22-result-oracle.{py,json}`, `census/round-21/step-inventory.json`, `census/round-21/final-out-S1.json`, and pinned baseline source via `git show 41553adb…:census/round-21/run-acceptance.py` (named path only).

## 1. Stored vector and delta reconstruction (before inspecting the predicate)

Oracle vector (`tests/fixtures/r22-result-oracle.json:3053-3065`):

```json
{ "id": "scalar/r13-counter-31984f4/admitted_entries/float",
  "want": false, "group": "scalar",
  "step_name": "r13-counter-31984f4",
  "json_set": [ [ ["admitted_entries"], 4.0 ] ] }
```

Reconstructed delta from the pinned public record and frozen inventory:

- Pinned receipt record `r13-counter-31984f4` (`census/round-21/final-out-S1.json:3598-3621`): `returncode` 0 (line 3617), `stderr` `""` (3618), `matched` true (3568), `stdout` the single-line JSON object ending `\n` (3620) with `"admitted_entries": 4`.
- Frozen inventory step (`census/round-21/step-inventory.json:207-234`): `kind: "counter"` (227), `exact_json: true` (226), `expected_summary.admitted_entries` is the **integer** `4` (211), `measured_commit` is the literal historical hash `31984f47…` (213) — no `<REV>`/`<REVISION>` token, so `replace_revision` (oracle.py:40-47) is a no-op here.
- The `json_set` path `["admitted_entries"]` is a top-level key of the stdout object, so the harness mutation is `payload["admitted_entries"] = 4.0` — int `4` → float `4.0`, value-preserving, type-breaking. Everything else identical.

The fixture actually feeds the mutated input. Harness mechanics (`tests/fixtures/r22-result-oracle.py`):

- `record = records[case['step_name']]` (line 67) resolves to the pinned record above; `stdout = case.get('stdout', record['stdout'])` (68) takes the pinned stdout since the case stores only `json_set`.
- `json_set` handling (72-82): `payload = json.loads(stdout)` → `at[path[-1]] = copy.deepcopy(4.0)` → `stdout = json.dumps(payload)`. Python decodes `4.0` as `float` and re-encodes it as `4.0` (trailing `.0` preserved), so the runner receives a real decoded `float` — not a string, not a truncated int.
- The call (87-91) passes `returncode` 0, the mutated stdout, empty stderr, oracle revision, ROOT. Step lookup `steps['r13-counter-31984f4']` (59-60, 83) succeeds.
- Decision check (92, 97): `observed = result['matched']`; `passed = type(observed) is bool and observed is case['want']` — literal-bool comparison, honest.

So the input reaching `summarize_result` is exactly: real record, one leaf `admitted_entries` decoded as `float(4.0)` vs expected `int(4)`.

## 2. Expected decision vs changed predicate

Changed code path (`census/round-21/run-acceptance.py`):

- `matched` starts `returncode == 0 and not failures` → `True` (rc 0, no FAIL lines in JSON stdout; `failure_lines` only matches `FAIL\t`/`CASE…FAIL` prefixes, lines 356-359, 396, 410).
- `kind == "counter"` branch (466): `observed = json.loads(stdout)` succeeds (468).
- `step["exact_json"]` is `true` → `json_match = json_exact(observed, expected)` (472-473).
- `json_exact` (375-387): dict branch requires `observed.keys() == expected.keys()` (all keys preserved by the mutation → passes), then recurses per key. At `admitted_entries`: `type(4.0) is not type(4)` → `float is not int` → **False at line 377-378**, before any value comparison at 387.
- `matched = matched and json_match and not stderr` (492) → `True and False and True` → `False`; `result["matched"] = bool(matched)` → `False` (537).

`want=false` is **correct**, and it is correct for the *intended* reason: the mutation is numerically equal (`4.0 == 4`) but type-unequal; only the type-identity gate at line 377 kills it. This is exactly the admitted repair for R22-M1 (`corpus/lessons/round-22.md:15` "decoded scalar type identity"; oracle contract line 8: "Reject … decoded wrong scalar types"). Confirmed against pinned base `41553adb…`: baseline counter branch was `json_match = observed == expected` — dict `==` is value equality, `4.0 == 4` is `True`, so the baseline would **false-green** this vector; the vector genuinely discriminates base vs changed. A mutant that loosens line 377 (`==`, `isinstance`, numeric coercion) is killed by this vector; a mutant that always-rejects is killed by the paired positive. The vector is load-bearing, not redundant.

No bypass found in scope:
- The type check precedes value comparison, so `4.0`/`4e0`/any numeric-equal float is rejected.
- `matched` does not depend on `matched_counts` diagnostics; the diagnostic cannot flip the decision.
- `bool` exclusion is irrelevant here (no `admitted_entries/bool` sibling exists; the bool siblings cover `F2_entry`, `evidence_gate`, `tiers.C`).
- `not stderr` is honored: case inherits record stderr `""`, and the changed counter branch still requires it (492).

## 3. Paired positive — `positive/r13-counter-31984f4` (want=true)

Oracle `r22-result-oracle.json:3012-3017`: no `json_set`, `stdout`, `returncode`, or `stderr` overrides → the harness replays the pinned record verbatim (stdout line 3620, rc 0, stderr `""`). Against the inventory `expected_summary` (exact match of the decoded object, ints everywhere): `json_exact` returns `True`; `matched = True and True and True` → `True` → `want=true` holds, and `result['matched']` agrees with the receipt's stored `matched: true` (line 3568). The positive pins the other side of the gate: the same dict shape with correct int types must still be accepted, so the type gate cannot be a blanket reject. Pairing is honest — same step, same record, only the synthetic leaf type differs.

## 4. Residual observations (below defect threshold for this vector)

- **Diagnostic elision, LOW/informational:** `numeric_leaves` (362-372) collects only `isinstance(current, int) and not bool` leaves. On the mutated run, `admitted_entries: 4.0` is dropped from `observed_numeric_fields` entirely — `matched_counts` reports 9/10 fields matched without naming the float leaf as a *type* violation (482-491). Decision unaffected (`matched` never reads these counts); reviewers reading only `matched_counts` lose one bit of causal precision. Not a contract violation.
- `except (ValueError, TypeError, RecursionError)` at 468-470 now also catches `RecursionError` — consistent with the lesson's malformed-result repair; irrelevant to this vector but confirms the counter branch cannot crash on this input.
- The `is` check in `passed` (oracle.py:97) is safe: `result['matched']` is materialized via `bool(matched)` (537), so a truthy non-bool cannot pass.

## 5. Residual risk and verification gaps

- Source-only verdict; no execution was performed (per contract). The base-vs-changed discrimination claim rests on the pinned baseline diff shown above, not a rerun.
- Scope is this vector plus its paired positive; sibling scalar vectors on this step (`F2_entry`, `evidence_gate`, `sources`, `tiers.*`, `statuses.*`, array-malformed, exit) follow the same machinery but are other seats' scope.
- No tooling installs performed; pacman transactions untouched.
