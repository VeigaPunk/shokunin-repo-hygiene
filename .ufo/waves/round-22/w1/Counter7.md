STATUS: PASS — source-only review of the counter-kind predicate boundary in `census/round-21/run-acceptance.py` (base `41553adb139d06511dc386bb3ce4326aebfba675` minus-side of the current working-tree diff). The subset branch's acceptance of extra top-level fields is legitimate required behavior, not a defect; the in-scope scalar-equality defect and its repair are verified below with the actual pinned expectation `r13-counter-b576341`. Nothing was executed; all findings are source-inferred.

## Authority and scope

Named sources only: `census/round-21/run-acceptance.py` (base blob `1ecbad0` minus-side of current diff `1ecbad0..0a9f20c`, captured via `git diff 41553adb…`), `census/round-21/step-inventory.json`, `census/round-14/cache-demonstration.py`, `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`, `.ufo/waves/round-22/preregistration.txt`, `corpus/QUALITY.md`. Working-tree-vs-base sha256 comparison: `step-inventory.json`, `cache-demonstration.py`, `QUALITY.md` byte-identical to base; `run-acceptance.py` already carries the in-flight r22 repair (base side verified from the diff minus-side, matching an earlier direct read of the file). No tools installed; no tests/probes run; LSP device not mounted (consistent with the r21 attack report's note).

## Actual counter expectation located

`COUNTER_EXPECTATIONS` (base lines 120–180) holds five rows; exactly one is subset-mode:

- `r13-counter-b576341` — `census/round-13/count-claims.py @ b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`, `exact_json=False`, pinned subset `{"measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3", "admitted_entries": 6}` (base lines 171–179; frozen `census/round-21/step-inventory.json:323-337`, `"exact_json": false`).
- The four exact rows (`r13-counter-31984f4`, `r13-counter-6f8ee0f`, `r14-counter-a31642d`, `r14-counter-552cae4`) pin complete dicts including bool-confusable 0/1 leaves: `F2_entry`/`evidence_gate` (r13) and `cache_gate`/`cache_fixture`/`boundary_fixture` (r14).

## Boundary: subset extra top-level fields — LEGITIMATE, must not be "fixed"
Base subset predicate (line 430–431): `isinstance(observed, dict) and all(observed.get(key) == value for key, value in expected.items())`. This is a deliberate partial pin: `exact_json=false` exists alongside four `exact_json=true` rows precisely because the two-key dict is not the producer's complete output — [INFERENCE from the mode distinction; `count-claims.py` itself is outside the named read set]. Rejecting extra top-level fields would therefore break the historical outcome projection the claim requires retaining ("exact historical outcome projections"). The repaired code (`all(key in observed and json_exact(observed[key], value) …)`) preserves top-level extras by iterating only pinned keys. Confirmed legitimate at source.

Boundary shape (both base and repair): subset is shallow at the top level only. A pinned value that is itself a dict requires exact nested key-set equality — nested extras are rejected under both. Today inert (b576341 pins only scalars) but it defines the contract: "extra fields allowed" = top level of `exact_json=false` steps only. For the four `exact_json=true` counters, extra top-level fields were and remain correctly rejected (`observed.keys() == expected.keys()` inside `json_exact`).

Minor defensive delta: `key in observed` replaces `observed.get(key) == value`. Semantically different only when a pinned value is `None` (missing key previously compared equal to `None`); no pinned expectation contains `null` → inert today, strictly more correct.

## In-scope defects vs. the repair (verdicts)

1. JSON scalar type equality — REPAIRED at source. Base `observed == expected` (line 427) and `observed.get(key) == value` (line 431) admit `False == 0`, `True == 1`, and `6.0 == 6`. New `json_exact` uses `type(observed) is not type(expected)` then recursive dict/list comparison — rejects bool/int, int/float, and `6` vs `"6"` in both branches and at every nesting level. `NaN`/`Infinity` literals from `json.loads` compare unequal → still reject; no new false-green path introduced.
2. Summary stderr — REPAIRED at source. Base line 417 `matched = matched and summary_match and pass_match` had no stderr gate (counter/cache branches already had `not stderr`, lines 445/480); repair adds `and not stderr`, aligning the branch with the other two kinds.
3. Cache checks counted not identified — REPAIRED at source. New `CACHE_CHECK_NAMES` (33-name frozenset) verified verbatim, element-for-element, against the producer's `checks` literal at `census/round-14/cache-demonstration.py:880-978`; `len(CACHE_CHECK_NAMES) == expected["checks"]` (33 == 33, `step-inventory.json:192`) guards the runner constant itself. `case_phases == list(CACHE_CASE_PHASES)` verified against producer emission order `initial-fresh` → `unchanged` → `dependency-modified` → `legacy-no-dependencies` (producer lines 596, 614, 655, 795). `isolation.cleaned`/`residue` originate in `cleanup()` merged at producer line 1201 — `isinstance(isolation, dict)` + `.get` checks are satisfied by real output. `matched_gate_checks` now counts `checks.get(name) is True` over named keys (identity, not count).

Note on claim wording: the preregistration names "bool/int" confusion; the same `==`-class defect also admits int/float (`6.0 == 6`). `json_exact` closes both — the float case is the only scalar confusion actually triggerable on the subset vector (see pairs below). In-scope, no scope inflation.

## Literal positive/negative pairs (synthetic result-oracle vectors)

Step under test: `r13-counter-b576341`, `kind="counter"`, `exact_json=false`; `returncode=0`, `stderr=""` in all four.

- POSITIVE (must stay matched — extra top-level fields legitimate):
  `{"measured_commit":"b5763415cc67ecff1e8fe56c58c39a6fb106d7a3","admitted_entries":6,"sources":33,"F2_entry":0,"tiers":{"A":29,"B":3,"C":1},"unrelated":[1,2]}`
  Expected: `matched=true`. Acceptance-defining control: any repair that rejects this vector breaks the retained historical projection.
- NEGATIVE A (base false-green → repair must reject):
  `{"measured_commit":"b5763415cc67ecff1e8fe56c58c39a6fb106d7a3","admitted_entries":6.0}`
  Base: `matched=true` (`6.0 == 6`). Repaired: `matched=false` (`float is not int`). This is the actual subset-path trigger; the bool variant is NOT triggerable here (`True == 6` is False) — bool confusion lives on the exact vectors.
- NEGATIVE B (companion exact-mode vector, `r13-counter-31984f4`): expected dict with `"F2_entry":false,"evidence_gate":false`, all other fields unchanged. Base: `false == 0` → `matched=true` (the r21 attack HIGH finding). Repaired: `matched=false`.
- NEGATIVE C (boundary, both versions reject — regression control): `{"measured_commit":"b5763415cc67ecff1e8fe56c58c39a6fb106d7a3"}` (missing pinned key) and `{"measured_commit":"b5763415cc67ecff1e8fe56c58c39a6fb106d7a3","admitted_entries":7}` (wrong value). Expected `matched=false` before and after.

## In-scope defect vs. rejected added scope

- In-scope (claimed, now closed): scalar type equality in counter comparisons; summary stderr gating; cache check identity (name set + case-phase sequence).
- Legitimate behavior to preserve (not defects): top-level extra fields on `exact_json=false` counters; non-pinned top-level payload fields in cache-demo (`advisories`, `executions`, `record`, `dependency_mutation`, extra `isolation`/`gate` keys — e.g. `sha256_after` appended at producer line 1207) remain unpinned and accepted; `matched_counts` stays informational, non-gating.
- Rejected added scope (per preregistration, correctly not attempted): malicious-producer attestation, executed-command authentication, semantic binding of case-row contents beyond `phase`, check-value semantics beyond `is True`, any claim about the producer's internal correctness. The 33-name set is a reviewed expectation constant duplicated in the runner, not derived from the producer (diff comment), and I verified it verbatim — but it binds names, not producer honesty.

## Residual risk

- Source-inferred only, pending L1 acceptance run: `not stderr` on summary steps can false-red a real step emitting benign stderr (e.g. a warning). For the 13 summary steps this is only observable at execution; counter/cache branches already had the gate, so historical emptiness is established there but not provable for summary steps from source alone.
- `len(CACHE_CHECK_NAMES) == expected["checks"]` ties the frozen inventory's `33` to the runner constant; if either side drifts without the other, the step fails closed (honest, intended).
- The subset predicate remains shallow (nested dicts exact). If a future counter expectation pins a nested dict under `exact_json=false`, nested extras are rejected — an asymmetry to document at that time, not a defect now.
- New `int(baseline_match.group(group))` ValueError guard (summary branch) is unreachable with the pinned `(\d+)` regex — harmless hardening consistent with "reject malformed producer data without a crash".
- Pre-existing, unchanged by this diff: counter stdout must decode as one JSON document (prefix/suffix junk → parse fail → reject); non-dict JSON (`null`, `[]`, scalar) rejects via `isinstance` guards with no crash path; `matched_counts` remains diagnostic-only.

## Verification gaps

No code was executed per lane contract; no exit codes, stderr bytes, or runtime decisions were observed — every decision attribution above is source-inferred from the base bytes and the current diff. The L1-run acceptance on `41553adb139d06511dc386bb3ce4326aebfba675` versus the changed implementation remains the required empirical confirmation, including the "same committed synthetic result-oracle fixture" before→after projection.

Tools installed: none (no installs or updates performed).
