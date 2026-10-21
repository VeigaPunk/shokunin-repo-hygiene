STATUS: PASS — the counter predicate's zero→false boundary subset is bounded, the reachable expectation leaves are named, the integrated repair closes the subset at source level, and a literal positive/negative oracle pair is drafted. All claims are source-inferred from named files; nothing was executed, installed, or probed.

## Scope of this seat

One axis slice: the `kind == "counter"` predicate in `census/round-21/run-acceptance.py` `summarize_result`, restricted to the boundary where an expected numeric `0` (and its mirror `1`) is compared against the JSON literal `false` (`true`), plus the immediately adjacent scalar edges (`null`, `0.0`, missing key, wrong container) that determine whether the subset is fully closed. In-scope defect: r21 admitted HIGH finding "exact counter JSON accepts booleans in place of integer fields" (`.ufo/waves/round-21/w2/AttackRunnerStepResults.md:5-9`), folded into the r22 claim as "JSON bool/int scalar confusion" (`.ufo/waves/round-22/preregistration.txt`). Not in this seat: the summary-stderr and cache-check-identity repairs (sibling seats).

## Actual expectations carrying the boundary (located, not hypothetical)

`COUNTER_EXPECTATIONS` at `census/round-21/run-acceptance.py:120-180` feeds `make_steps` (:345-352) with `exact_json` flags; the frozen inventory `census/round-21/step-inventory.json` confirms the same values.

Reachable zero→false leaves (expected `0`, so observed `false` collides at baseline):

| step | exact_json | zero-valued leaves | one-valued leaves (true mirror) |
|---|---|---|---|
| r13-counter-31984f4 (:126) | true | `F2_entry`, `evidence_gate` | — |
| r14-counter-a31642d (:151) | true | `cache_gate`, `cache_fixture`, `boundary_fixture` | `held_knowledge: 1` (:155) |
| r13-counter-6f8ee0f (:138) | true | — | `F2_entry`, `evidence_gate` |
| r14-counter-552cae4 (:164) | true | — | `cache_gate`, `cache_fixture`, `boundary_fixture`, `held_knowledge` |
| r13-counter-b576341 (:177) | false | — | — |

Precision on reachability: Python `False == 0` and `True == 1` are the only bool↔int collisions, so bool confusion can only false-green on leaves whose expected value is `0` or `1`. All other numeric leaves (`admitted_entries: 4/5/6`, `sources: 33/37`, `tiers`, `statuses`, `source_rows`, `admitted_knowledge`) are unreachable by `false`/`true` — `False == 2` is `False`. No nested leaf in any expectation is `0`/`1`, so the defect is a top-level-leaf defect on the real table (the repaired comparator still recurses correctly for synthetic nested cases). The non-exact step `r13-counter-b576341` carries no `0`/`1` leaf, so it is unreachable by bool confusion but reachable by float confusion (`6.0 == 6` is `True`).

## Defect at baseline (41553adb139d06511dc386bb3ce4326aebfba675)

Diffing `git show 41553adb…:census/round-21/run-acceptance.py` against the working tree confirms the baseline predicate:

- exact path: `json_match = observed == expected` — `{"F2_entry": false, …} == {"F2_entry": 0, …}` is `True` because dict equality delegates to `False == 0`.
- subset path: `all(observed.get(key) == value …)` — same collision per leaf.
- `numeric_leaves` (:336-344) excludes bools and floats alike (`isinstance(value, int) and not isinstance(value, bool)`; `float` is not `int`), so a `false` leaf simply vanishes from `observed_numeric_fields`, lowering `matched_expected_fields` — a diagnostic asymmetry the baseline never gates on (`matched` ignores the count, :435-445 baseline).
- Result at baseline: `matched = returncode == 0 and not failures and json_match and not stderr` → with rc 0, clean stderr, and a `false`-for-`0` payload, `matched` is `True`. False green confirmed at source level, matching the admitted r21 HIGH.

## Repair assessment for this subset (working tree, source-inferred)

The integrated change adds `json_exact` (:373-383 of working tree): `type(observed) is not type(expected)` → `False`; dicts compare key-set equality plus per-key recursion; lists compare length plus zipped recursion; scalars fall through to `==`.

- `{"F2_entry": false}` vs `0`: `type(False) is bool`, `type(0) is int` → `False`. Subset closed. `True` vs `1` symmetric.
- `{"F2_entry": 0.0}` vs `0`: `float is not int` → `False`. Baseline `0.0 == 0` was `True`, so float is also discriminating — and it is *in scope*, not added scope: Q51 (`corpus/QUALITY.md:120`) names "bool/float … negatives rejected" as oracle vectors, and the preregistration's "JSON bool/int scalar confusion" is repaired by exact scalar typing, of which float is the same class.
- `{"F2_entry": null}`: `NoneType is not int` → `False`; baseline `None == 0` was already `False`. Non-discriminating, correct both ways.
- Malformed/non-dict `observed` (`json.loads` failure → `None`, or top-level list/scalar): `type(...) is not type(dict)` → `False`; subset path's `isinstance(observed, dict)` guard retained. Q51's "covered malformed containers produce a retained mismatch, not a crash" holds for this branch.
- Subset path rewrite `all(key in observed and json_exact(observed[key], value) …)` preserves the declared contract: expected keys required, extra observed keys allowed (Q51: "subset-extra-fields … accepted"). The `key in` guard replaces `.get` losslessly — the only divergence would be observed `null` vs expected `null`, which no expectation uses, and even there both forms agree.
- `numeric_leaves`/`matched_expected_fields` is unchanged and still non-gating; post-repair its direction now agrees with the verdict (a `false`/`0.0` leaf drops out of the observed count = reads as unmatched). Minor fidelity nit, not a decision defect — see residual risk.

No actionable defect found inside this subset in the changed code. Verdict is a recommendation to keep the repair for this slice; admission is the integrator's.

## Drafted literal oracle pair (zero→false subset)

Vectors are step-level `(stdout, returncode, stderr)` triples for step `r13-counter-31984f4`; decision column is `result["matched"]`.

Positive control (must match — the real r13 counter output, retained verbatim):

```json
{"F2_entry": 0, "admitted_entries": 4, "evidence_gate": 0, "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81", "sources": 33, "tiers": {"A": 29, "B": 3, "C": 1}, "statuses": {"mined": 16, "queued": 15, "rejected": 2}}
```
with `returncode=0`, `stderr=""` → baseline `matched=True`, changed `matched=True`. Preserves the r22 requirement that all 18 original positive controls stay green.

Negative vector (minimal single-field flip of the positive — must NOT match):

```json
{"F2_entry": false, "admitted_entries": 4, "evidence_gate": 0, "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81", "sources": 33, "tiers": {"A": 29, "B": 3, "C": 1}, "statuses": {"mined": 16, "queued": 15, "rejected": 2}}
```
with `returncode=0`, `stderr=""` → baseline `matched=True` (the false green), changed `matched=False`. This is the discriminating vector for the zero→false subset.

Companion boundary vectors (same shape, same triples), each isolating one edge:

| vector field change | baseline | changed | class |
|---|---|---|---|
| `"F2_entry": 1` (expected 0) | red | red | retained negative (wrong value, right type) |
| `"F2_entry": null` | red | red | retained negative (null scalar) |
| `"F2_entry": 0.0` | **green** | red | discriminating — float subset of the same scalar-type repair |
| `"evidence_gate": false` | **green** | red | discriminating — second reachable zero leaf |
| `"F2_entry": "0"` | red | red | retained negative (string type, already rejected) |
| key `F2_entry` absent | red | red | retained negative (exact key-set) |
| r14-counter-552cae4 `"held_knowledge": true` | **green** | red | discriminating — the `1`→`true` mirror |
| r13-counter-b576341 `"admitted_entries": 6.0` (subset path) | **green** | red | discriminating — float on non-exact path |
| r13-counter-b576341 plus `"extra": "x"` | green | green | positive — subset-extra-fields control per Q51 |

## In-scope defect vs rejected added scope

In scope (this subset): bool-for-`0`/`1` confusion on both exact and subset counter paths; the float sibling under the same exact-typing repair; rejection of null/list/missing-key scalars without a crash; retention of all five real counter positives including the subset-extra-fields contract.

Rejected added scope (not claimed, not required by Q51 or the preregistration): authenticating the counter producer's execution or argv; validating `measured_commit` against real git history beyond the existing literal-hex comparison; JSON canonicalization (duplicate-key policy, key order) — object key-set equality is correct JSON semantics; schema validation of undeclared fields; any change to `numeric_leaves` diagnostics beyond consistency; any stderr/stdout shaping for counter steps (stderr is already gated at :445/`not stderr`, unchanged).

## Residual risk / bounded notes

- `json.loads` deep nesting can raise `RecursionError` (a `RuntimeError`, outside the `except (ValueError, TypeError)` at :423) in both baseline and changed code; a pathological nested payload crashes rather than returning a retained mismatch. Pre-existing, shared by both revisions, outside the "covered malformed containers" wording — disclosed, not scored.
- A producer emitting multi-line JSON containing a string with an embedded `\nFAIL\t…` line would be rejected via `failure_lines` before JSON parse, regardless of content. Pre-existing shared edge; only matters for pretty-printed JSON, which no counter produces; disclosed.
- `matched_expected_fields` still reports a `false`/`0.0` leaf as "not observed" rather than "type-mismatched" (bool/float are dropped by `numeric_leaves` before the `==`). Diagnostic fidelity only; the match decision is correct. Optional improvement, not a defect.
- The `int(baseline_match.group(group))` `ValueError` guard added in the summary branch (:424-427 working tree) is adjacent diff context, not part of this subset; noted only to mark the diff boundary.

## Verification gaps

No runner, oracle, fixture, or producer was executed — all verdicts are source-inferred against the named files, per contract. `xd://lsp` is not mounted in this session (consistent with the r21 seat report); findings rest on direct reads of the named files, not grep-as-semantic-proof. Baseline comparison used `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py` diffed against the working tree per L1 instruction. No tools installed; no writes outside this report.

Report: souji-shokunin/.ufo/waves/round-22/w1/Counter5.md
