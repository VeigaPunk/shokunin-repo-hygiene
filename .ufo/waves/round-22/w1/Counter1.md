STATUS: PASS — counter zero→false predicate boundary located, bound to an actual committed expectation, and a literal positive/negative oracle pair drafted. All findings are source-inferred from `git show 41553adb139d06511dc386bb3ce4326aebfba675:<path>` reads of the named files; nothing was executed. Report trailers are relative to souji-shokunin.

## 1. Boundary location (base `41553adb`, named runner only)

`census/round-21/run-acceptance.py`, `summarize_result` counter branch:

- Line 422: `observed = json.loads(stdout)` — the Python decoder maps JSON `false`→`False`, `true`→`True`, `0`→`0`, `0.0`→`0.0`.
- Line 427 (exact path): `json_match = observed == expected`.
- Line 431 (non-exact path): `all(observed.get(key) == value for key, value in expected.items())`.
- Line 445: `matched = matched and json_match and not stderr`; line 367 requires `returncode == 0 and not failures`.

The boundary is the `==` predicate itself: Python's `bool` is an `int` subclass, so `False == 0` and `True == 1`, and `dict.__eq__` recurses with `==`. An expected **integer `0` leaf is satisfied by the observed JSON literal `false`** (likewise `1` by `true`, and any int `n` by float `n.0`). This is the admitted OPEN r21 defect "JSON bool/int scalar confusion" (`.ufo/waves/round-21/w2/AttackRunnerStepResults.md` lines 5–9), inside preregistration's three named repairs — in scope.

`numeric_leaves` (lines 336–344) excludes bools, so a `false` observed leaf is absent from `observed_numeric_fields` and `matched_expected_fields` undercounts — but `matched_counts` is diagnostic only and never gates `matched` (lines 435–445). The gate is solely `json_match`. Confirmed the diagnostic-exposure-without-enforcement shape noted by the r21 attacker.

## 2. Actual counter expectation/value bound

`COUNTER_EXPECTATIONS` (base lines 120–180) holds five rows; `make_steps` (lines 319–326) marks `exact_json` per row. Zero-valued integer leaves — the only expectations exposing the exact `0`→`false` boundary:

| step | zero leaves | mode |
|---|---|---|
| `r13-counter-31984f4` | `F2_entry: 0`, `evidence_gate: 0` | exact |
| `r14-counter-a31642d` | `cache_gate: 0`, `cache_fixture: 0`, `boundary_fixture: 0` | exact |

Mirror/twin boundaries (same `==` predicate, not literal `0`→`false`):
- `r13-counter-6f8ee0f`, `r14-counter-552cae4` (exact): `1` leaves admit `true`/`1.0`.
- `r13-counter-b576341` (non-exact, `exact_json=False`): only `admitted_entries: 6`; bools never equal 6, but `6.0` does — a float-only boundary, latent, no zero leaf.

Non-exact asymmetry worth stating: a **missing** key yields `observed.get(key)` → `None`, and `None == 0` is False, so absence fails while a *present* `false` passes. The boundary rewards presence-with-wrong-type, not omission.

## 3. Drafted literal oracle pair (synthetic `summarize_result` input)

Bind to `r13-counter-31984f4` step spec: `returncode=0`, `stderr=b""`, argv fixed by `COUNTER_EXPECTATIONS[0]`; verdict asserted on `result["matched"]`.

**Positive control — must stay `matched: true` on base and changed** (stdout, compact JSON, integer `0`s):

```json
{"F2_entry": 0, "admitted_entries": 4, "evidence_gate": 0, "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81", "sources": 33, "tiers": {"A": 29, "B": 3, "C": 1}, "statuses": {"mined": 16, "queued": 15, "rejected": 2}}
```

**Negative — base marks `matched: true` (false green via `False == 0`); changed must mark `matched: false`.** Single-leaf mutation isolates the `0`→`false` boundary:

```json
{"F2_entry": false, "admitted_entries": 4, "evidence_gate": 0, "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81", "sources": 33, "tiers": {"A": 29, "B": 3, "C": 1}, "statuses": {"mined": 16, "queued": 15, "rejected": 2}}
```

Same construction applies to `evidence_gate` and to the three `r14-counter-a31642d` zero leaves; the `1`→`true` twins cover `r13-counter-6f8ee0f`/`r14-counter-552cae4`. These payloads contain no `FAIL\t`/`CASE…FAIL` lines, so `failure_lines` stays empty and only `json_match` decides — clean isolation of the predicate under test.

## 4. Predicate-boundary note for the repair (source-level)

The discriminator must be **exact type identity**, not `isinstance`: `isinstance(False, int)` is `True`, so an `isinstance`-based "is it an int" check preserves the false green. Scalar-type-exact recursive equality (`type(a) is type(b)` before `==`, recursing dict/list) is the minimal predicate that separates `0` from `false` while keeping the positive control green and requiring no change to `COUNTER_EXPECTATIONS`, step count, or `all_matched` (which must all stay byte/behavior identical per preregistration).

## 5. In-scope defect vs rejected added scope

**In scope (admitted, named):**
- `0`→`false` and `1`→`true` scalar confusion at base lines 427 and 431 — this report's pair.

**Adjacent, rejected as added scope for this claim:**
- Int↔float (`29`→`29.0`, `6`→`6.0`): same `==` line and a type-exact comparator subsumes it for free, but the admitted wording is "bool/int scalar confusion"; oracle coverage of floats is optional, not required by the claim.
- `matched_expected_fields` undercount on bool leaves: diagnostic only, never gated `matched`; recording it unchanged is honest, hardening it is extra.
- `json.loads` accepting `NaN`/`Infinity` literals: separate producer-grammar question; non-equal to any int so it already fails closed; "reject malformed producer data without a crash" is satisfied without touching it.
- Summary-stderr and cache check-identity defects: separately owned; not restated here.
- Malicious-producer attestation, executed-command authentication, expectation/step-inventory edits: explicitly disclaimed or forbidden.

## 6. Verification gaps

- No code executed (contract); verdicts are source-derived from `==`/`json.loads` semantics per Python documentation, cited as this round's authorized source authority.
- `xd://lsp` is not a mounted device in this lane (`lsp` status returned no such tool); no LSP references/definitions/diagnostics claimed. Text citations are to `git show` of the named base files only.
- Working-tree runner was initially read before the parent's baseline-read directive; the cited line numbers were re-verified against `git show 41553adb:...` and are identical in the regions cited (24–26, 118–180, 330–344, 415–482, 555–659).
- No tools installed. No files written outside this report. No delegation, no background jobs.
