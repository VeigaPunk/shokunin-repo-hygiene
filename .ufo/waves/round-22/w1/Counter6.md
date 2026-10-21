STATUS: PASS — Counter predicate int→float boundary analyzed: the false green exists on base 41553adb139d06511dc386bb3ce4326aebfba675 (source-inferred, unexecuted) and the integrated `json_exact` repair closes the entire scalar-type class, not only the named bool/int pair. One residual risk row (new summary-step stderr gate is unexercised; could false-red positive controls). Source-only review; no execution, no tools installed.

## Axes

- **calibration** — does the counter pass/fail predicate decide on real scalar types (the round's lowest axis and this seat's only defect class).
- **operability** — does any repair/vector keep all 18 real acceptance steps and 5 counter rows honest without new refusals or crashes.
- **coverage** — does the literal vector set pin the int→float leaf (top-level and nested) in addition to the admitted bool/int leaf.

No trade is proposed: moves below improve calibration and coverage and harm no axis.

## Named evidence (all source-inferred, nothing executed)

- Base runner: `git show 41553adb…:census/round-21/run-acceptance.py` — counter branch `summarize_result`: `exact_json` path compares `observed == expected` (line 427 on base); non-exact path compares `observed.get(key) == value` (line 431); `numeric_leaves` admits `isinstance(value, int) and not isinstance(value, bool)` only, silently dropping float leaves (base lines 336–344); gate is `matched = matched and json_match and not stderr` (base line 445).
- Working-tree file `census/round-21/run-acceptance.py` now differs from base (sha256 base `11418399…` vs worktree `02e3b06d…`; parent notice confirmed L1 integrating mid-review). The counter/predicate ranges I cite were re-verified against base bytes via `git show`, not the moving tree.
- `COUNTER_EXPECTATIONS` (identical on base and worktree): `r13-counter-31984f4` expects `admitted_entries: 4`, `F2_entry: 0`, `evidence_gate: 0`, `sources: 33`, nested `tiers: {"A": 29, "B": 3, "C": 1}` and `statuses: {"mined": 16, "queued": 15, "rejected": 2}`, `exact_json=True`; `r13-counter-b576341` is the non-exact counter (`exact_json=False`) expecting `admitted_entries: 6` plus a string `measured_commit`.
- `census/round-21/step-inventory.json:207-227` freezes the same expected values and `"exact_json": true` for `r13-counter-31984f4`.
- `AttackRunnerStepResults.md` (r21 w2) admits the bool/int confusion HIGH (its line 5–9 block); int→float is the unexamined sibling leaf of the same `==` predicate.
- Preregistration C1: defect class named "JSON bool/int scalar confusion"; authority = Python JSON decoder conversion docs and bool subclass/equality semantics; malformed producer data must refuse without crash; no malicious-producer attestation, no executed-command authentication, no new axis claim.

## Finding: int→float is a live false green on base — in-scope of the admitted scalar defect, not added scope

Python semantics (source-inferred): `json.loads` produces `float` for JSON `4.0`/`4e0`; Python `4.0 == 4` and `{"a": 4.0} == {"a": 4}` are `True`. Therefore on base:

- `json_match` (`observed == expected`) is `True` when a producer emits `admitted_entries: 4.0` for the expected integer `4`, top-level or nested (`tiers.A: 29.0`).
- `matched` becomes `True` (returncode 0, empty stderr), so `all_matched` can be `True` — a false green of the same severity as the admitted bool/int vector.
- `matched_counts` honestly exposes it only as a diagnostic: `numeric_leaves` drops `float`, so `matched_expected_fields` falls to 9 of 10 (`admitted_entries` unmatched), but that count never gates `matched`. Same signature as the bool case.

Stronger boundary form, same predicate, no expectations file change needed to establish the mechanism: for values beyond 2^53, `9007199254740993 == 9007199254740992.0` is `True` — `==` accepts not merely the wrong type but a numerically *different* value. No current counter field reaches that magnitude, so it is latent, not a vector against today's rows; it is recorded to show the correct repair is type-exactness, not magnitude tolerance.

**Scope ruling.** C1 names "bool/int scalar confusion" because that was the reviewed witness; the defective predicate is `==` on decoded JSON scalars. A repair that only excludes `bool` (e.g. bool-only type checks, mirroring `numeric_leaves`) would leave this live false green inside the very predicate being repaired — an incomplete fix of the admitted defect, not restraint. Covering the full scalar-type pair set {int→float, float→int, bool→int, int→bool, any scalar↔str/null} is the honest completion of defect 1; it claims no new axis, no producer attestation, no executed-command authentication. A rejected reading that would treat float vectors as "added scope" is noted and refuted here: the false green demonstrably exists on base and the preregistered authority (JSON decoder conversion + equality semantics) covers every scalar conversion pair, not only bool.

**Rejected added scope (held out):** NaN/Infinity handling beyond noting `json.loads`'s Python-specific extension produces `float('nan')` which can never equal an expected numeric (fails even under `==`); string↔number confusion (already fails under `==`); numeric axis score rubrics (preregistration forbids inventing them); authenticating producer identity or executed commands; widening `numeric_leaves` to count floats (would blur the diagnostic boundary — keep it int-only).

## Draft literal positive/negative pair (for the shared synthetic result-oracle fixture; payload = full stdout JSON of step `r13-counter-31984f4`, returncode 0, stderr empty)

Positive control — byte shape identical to the frozen expected record; expected decision **PASS**:

```json
{"F2_entry": 0, "admitted_entries": 4, "evidence_gate": 0, "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81", "sources": 33, "tiers": {"A": 29, "B": 3, "C": 1}, "statuses": {"mined": 16, "queued": 15, "rejected": 2}}
```

Negative — single leaf `admitted_entries` retyped int→float (JSON literal `4.0` or `4e0`); expected decision **FAIL** (`matched` false; `all_matched` false). On base this is a false green (`matched` true, `matched_expected_fields` 9/10):

```json
{"F2_entry": 0, "admitted_entries": 4.0, "evidence_gate": 0, "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81", "sources": 33, "tiers": {"A": 29, "B": 3, "C": 1}, "statuses": {"mined": 16, "queued": 15, "rejected": 2}}
```

Coverage-additive, harm-free companion vectors (same defect, deeper leaves and the non-exact path — each improves coverage, harms nothing):

- Nested leaf: `"tiers": {"A": 29.0, "B": 3, "C": 1}` → **FAIL** (base: green; dict `==` recurses with `==`).
- Non-exact counter: `r13-counter-b576341` stdout `{"measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3", "admitted_entries": 6.0}` → **FAIL** (base: `observed.get(key) == value` accepts `6.0 == 6`, extra-key tolerance unchanged and intended).
- Bool-sibling regression pin: `"evidence_gate": false` → **FAIL** (the admitted witness; keeps the pair honest across both scalar confusions).

## Check of the integrated repair (working-tree diff, advisory — verdict, not admission)

The diff under integration replaces the `==` predicate with recursive `json_exact(observed, expected)`: `type(observed) is not type(expected) → False`, then dict key-set equality plus per-key recursion, list length plus pairwise recursion, else `==`. Assessed against the int→float boundary:

- `type(4.0) is type(4)` is `False` → negative vector above now **FAILs** on both exact and non-exact paths; nested `29.0` fails before recursion; the >2^53 value-confusion form is dead because the type gate fires before `==`.
- Key-set equality `observed.keys() == expected.keys()` in the exact path keeps key coverage exact (string-only keys from `json.loads` — the `True`/`1` Python-key edge is unreachable here).
- Non-exact path `key in observed and json_exact(...)` preserves missing-key→False and extra-key tolerance; same-identity rerouting confirmed.
- Malformed JSON still parses to `None` → `type(None) is not dict` → False, no crash; `nan`/producer extensions degrade to False, fail-closed. Consistent with "reject malformed producer data without a crash."
- Same scalar class also repaired in cache-demo scalars (`failed_checks`, `producer_executions_new_policy` via `json_exact`) and cache check identity via `checks.keys() == CACHE_CHECK_NAMES` — noted only as the boundary's extent; not this seat's scope to adjudicate.
- One canonical runtime: a single `json_exact` serves exact, non-exact and cache-demo comparisons — no duplicate predicate introduced.

## Residual risk and verification gaps

1. **MEDIUM (operability, unexercised):** the integrated summary-branch change `matched = … and not stderr` newly fails any summary step whose child writes *any* stderr (deprecation/interpreter warnings included). If a positive-control child emits warning text under `CHILD_ENV`, the fix converts false green to false red. All 18 controls must be observed clean on the L1 acceptance run; I did not run it.
2. `numeric_leaves` remains int-only; `matched_expected_fields` under a defeated float substitution reports the honest 9/10 diagnostic — desired, but consumers of the record should not read 10/10 as proof of type fidelity. [INFERENCE: diagnostic semantics, not gate]
3. `isolation.get("residue") == []` in cache-demo relies on `==`; JSON-produced lists are plain `list` so `is` is unnecessary — no defect, recorded boundary.
4. `int(baseline_match.group(group))` now guards `ValueError`; unreachable under the pinned `(\d+)` regex — harmless malformed-producer hardening consistent with preregistration.
5. Verification gaps: nothing executed (contract); `xd://lsp` not mounted — no LSP caller/diagnostic checks performed and none claimed; working tree moved during review (L1 integration), so all base claims cite `git show 41553adb…` bytes; the final verdict on `all_matched` awaits L1's post-integration acceptance run.

## Tooling

No tools installed; no pacman/uv/binary transactions. Files read: the five named contract paths plus `git show` of the named runner at base.
