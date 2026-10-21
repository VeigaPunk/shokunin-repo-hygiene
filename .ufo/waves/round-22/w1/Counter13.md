STATUS: PASS — Counter predicate boundary (exact vs. subset, extra-key tolerance) mapped from source; literal positive/negative oracle vectors drafted below. Source-only; nothing executed. Cited lines verified against `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py` (byte-identical to working tree in the cited ranges, same line numbering).

Axes: calibration, operability, coverage — no trade taken.

## Boundary statement

`census/round-21/run-acceptance.py` counter branch (base lines 420–445) selects on the fifth tuple element of `COUNTER_EXPECTATIONS` (lines 120–180), surfaced as `step["exact_json"]` by `make_steps` (lines 319–326):

- `exact_json=True` (4 rows): `json_match = observed == expected` (line 427). Deep dict equality: an extra key at any depth fails; a missing key fails. Already key-set exact.
- `exact_json=False` (1 row, `r13-counter-b576341`, lines 171–179): `json_match = isinstance(observed, dict) and all(observed.get(key) == value for key, value in expected.items())` (lines 430–431). **Top-level-key subset only**: extra top-level keys are accepted by design; expected values are still compared with `==` (so a dict-valued expected field would require full equality inside it — the tolerance is one level deep at the top, not recursive).

Precise extra-key rule: extra keys are tolerated only at the top level of a subset-mode row, for key names absent from `expected`. Everywhere else they already fail.

## Actual counter expectation/value located

- `r13-counter-b576341` (inventory `census/round-21/step-inventory.json` lines 323–337; runner lines 171–179): expected `{"measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3", "admitted_entries": 6}`, `exact_json: false`. The subset design exists because this pinned historical producer's full output carries fields beyond the two pinned expectations `[INFERENCE: producer source not in named files; inferred from the deliberate `False` flag — if the producer emitted exactly these keys, exact mode would suffice]`.
- Scalar-confusion-exploitable fields in the four exact rows: `F2_entry`, `evidence_gate` (`r13-counter-31984f4`, =0→`false`); `F2_entry`, `evidence_gate`, `tiers.C` (`r13-counter-6f8ee0f`, =1→`true`); `cache_gate`, `cache_fixture`, `boundary_fixture` (`r14-counter-a31642d`, =0→`false`); `cache_gate`, `cache_fixture`, `boundary_fixture`, `tiers.C` (`r14-counter-552cae4`, =1→`true`). On `r13-counter-b576341` the only numeric expectation is `admitted_entries: 6`, unreachable by `true`/`false` but reachable by `6.0` (`6.0 == 6`).

The counter branch already gates `not stderr` (line 445) and `failure_lines` covers both streams (line 353): the summary-stderr defect does not apply to this predicate. Malformed producer JSON fails closed: `json.loads` failure → `observed = None` → `json_match` False in both modes, no crash (lines 421–424, 430–431).

## Literal oracle vectors (stdout / returncode / stderr; expected `matched` per base and repaired)

Positive pair member — subset extra-key tolerance is load-bearing (must stay `matched=true` on both):

```json
{"step": "r13-counter-b576341", "returncode": 0, "stderr": "",
 "stdout": "{\"admitted_entries\": 6, \"extra_untracked_field\": \"present\", \"measured_commit\": \"b5763415cc67ecff1e8fe56c58c39a6fb106d7a3\", \"sources\": 38}"}
```

base → `matched: true`; repaired → `matched: true`. If the repair flips this to `false`, it broke a retained positive control (preregistration: "retain all 18 original real acceptance-step positive controls").

Negative pair member — extra key inside an exact row (already correct; regression guard, non-discriminating):

```json
{"step": "r13-counter-31984f4", "returncode": 0, "stderr": "",
 "stdout": "{\"F2_entry\": 0, \"admitted_entries\": 4, \"evidence_gate\": 0, \"measured_commit\": \"31984f473ce4bdab61a99b16cca194b28108cb81\", \"sources\": 33, \"tiers\": {\"A\": 29, \"B\": 3, \"C\": 1}, \"statuses\": {\"mined\": 16, \"queued\": 15, \"rejected\": 2}, \"phantom_field\": 0}"}
```

base → `matched: false`; repaired → `matched: false`.

Discriminating negative — in-scope scalar defect, top level:

```json
{"step": "r13-counter-31984f4", "returncode": 0, "stderr": "",
 "stdout": "{\"F2_entry\": false, \"admitted_entries\": 4, \"evidence_gate\": false, \"measured_commit\": \"31984f473ce4bdab61a99b16cca194b28108cb81\", \"sources\": 33, \"tiers\": {\"A\": 29, \"B\": 3, \"C\": 1}, \"statuses\": {\"mined\": 16, \"queued\": 15, \"rejected\": 2}}"}
```

base → `matched: true` (false green via `False == 0`); repaired → `matched: false`.

Discriminating negative — same defect at depth (forces the fix to be recursive, not top-level-only):

```json
{"step": "r14-counter-552cae4", "returncode": 0, "stderr": "",
 "stdout": "{\"measured_commit\": \"552cae4204b3ab818419ad8adbfef3a4da29a3e0\", \"cache_gate\": 1, \"cache_fixture\": 1, \"boundary_fixture\": 1, \"source_rows\": 40, \"tiers\": {\"A\": 36, \"B\": 3, \"C\": true}, \"statuses\": {\"mined\": 23, \"queued\": 15, \"rejected\": 2}, \"admitted_knowledge\": 5, \"held_knowledge\": 1}"}
```

base → `matched: true` (`True == 1` inside `tiers`); repaired → `matched: false`.

Discriminating negative — scalar defect reaching the subset row (only float can reach `admitted_entries: 6`):

```json
{"step": "r13-counter-b576341", "returncode": 0, "stderr": "",
 "stdout": "{\"admitted_entries\": 6.0, \"measured_commit\": \"b5763415cc67ecff1e8fe56c58c39a6fb106d7a3\", \"sources\": 38}"}
```

base → `matched: true` (`6.0 == 6`); repaired → `matched: false` under a type-exact comparator. This is the only vector proving the subset path is repaired too.

## In-scope defect vs. rejected added scope

- **In scope (admitted)**: scalar type equality in both `==` paths — `false`/`0`, `true`/`1`, and by the same JSON-decoder type confusion `6.0`/`6` (floats decode to `float`, not `int`). The goal statement names "JSON scalar type equality"; the preregistration's narrower phrase "JSON bool/int scalar confusion" is the same defect class — a `type()`-exact comparator closes both at once, so the float vector above is recommended, not scope creep.
- **Rejected added scope**: (a) requiring key-set equality in subset mode — the `r13-counter-b576341` tolerance is deliberate and breaking it violates the positive-control retention clause; (b) rejecting duplicate JSON object names (`json.loads` last-wins) — not among the three admitted defects and would need an `object_pairs_hook` change; (c) check-name identity for cache `checks` — that is the cache lane's admitted defect, not the counter predicate's; (d) `matched_counts` gating — `numeric_leaves` exclusion of bools is diagnostic only (lines 435–444 do not gate `matched`); making it gate would be a design change beyond the named repair.

## Residual risk and verification gaps

- Source-only analysis per contract; no runner, fixture, or producer executed. All `base →`/`repaired →` decisions are derived from the cited predicates; `repaired →` assumes a type-exact deep comparator (e.g., key-set equality plus `type(a) is type(b)` recursion) — a bool-only patch would leave vector 5 green and vector 4 green if implemented top-level-only, which is exactly why those two vectors exist.
- `count-claims.py` is outside the named file set; the b576341 producer's actual extra keys are unverified (see INFERENCE above). The subset-tolerance vector is still valid: it tests predicate behavior on synthetic stdout, independent of what the real producer emits.
- `xd://lsp` is not a mounted device in this session; no semantic caller/definition checks were run. None were needed: `COUNTER_EXPECTATIONS` has exactly one consumer (`make_steps` line 319) and `exact_json` exactly one consumer (line 426), both verified by direct read of the same named file — no grep used as semantic proof.
- Working-tree file matched base bytes in all cited ranges (`git show` comparison); numbering cited is valid at base.
- No tools installed; no files written outside this report. L1's base-anchor instruction (read via `git show`) followed.
