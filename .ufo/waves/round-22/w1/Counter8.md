STATUS: PASS — counter predicate missing-key-vs-explicit-null boundary analyzed against
`git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py`
(baseline, per L1 instruction; working tree may now carry the r22 integration).
Source-inferred only; no execution, no tests, no probes, no production edits.

# Seat scope

Counter predicate boundary: **missing key versus explicit `null`** in the JSON
`kind == "counter"` branch of `summarize_result`.

# Actual counter expectation located (grounding)

Five rows in `COUNTER_EXPECTATIONS` (baseline lines 120–180); step construction at
baseline lines 319–325 sets `"kind": "counter"`, `"exact_json": exact`.

- 4 rows with `exact_json: true` — r13-counter-31984f4, r13-counter-6f8ee0f,
  r14-counter-a31642d, r14-counter-552cae4. All expected dicts contain only
  `int`/`str` leaves and nested `tiers`/`statuses` dicts; **no `null` values**.
- 1 row with `exact_json: false` — `r13-counter-b576341` (baseline line 171–179;
  inventory census/round-21/step-inventory.json:323–337):
  `{"measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3", "admitted_entries": 6}`.
  Also **no `null` values**; non-exact mode exists to tolerate extra producer keys.

# Findings

## F-C8-1 (in-scope defect, latent): non-exact counter predicate conflates absent key with explicit `null`

Baseline line 430–431:

```python
json_match = (isinstance(observed, dict)
              and all(observed.get(key) == value for key, value in expected.items()))
```

`observed.get(key)` returns `None` for an absent key. If a declared expectation
leaf is `null`, `None == None` is `True` → **missing key passes as if the
producer had emitted `"key": null`**. The missing-key and explicit-null cases
are observationally identical to this predicate, while for every non-null leaf
the missing key correctly fails (`None == <non-null>` is `False`,
including `None == 0` and `None == False`).

- Exploitability today: **none** — all 5 committed expectations are null-free, so
  the hole is latent. It is a real predicate boundary defect of the same family
  as admitted defect #1 (Python `==` ignoring the semantic boundary the contract
  requires: type for scalars, presence for keys).
- The minimal repair is free inside the already-mandated scalar-confusion rewrite
  of the same expression:

```python
json_match = (isinstance(observed, dict)
              and all(key in observed and json_exact(observed[key], value)
                      for key, value in expected.items()))
```

  `key in observed` distinguishes `{"k": null}` (present, compare) from absent
  (reject). The integrated diff observed in the working tree already uses exactly
  this form — consistent with folding the presence guard into the scalar repair.
- Classification: **in-scope sub-case** of the predicate repair, NOT a fourth
  admitted defect. Advertising it as a claimed defect would overstate the
  preregistration; recording it as a hardened boundary inside the same edited
  expression is honest.

## F-C8-2 (no defect): `exact_json` path already separates missing key from `null`

Baseline line 427 `json_match = observed == expected`: dict `==` is
keyset-sensitive, so `{"a": 1}` ≠ `{"a": 1, "k": null}` → absent key already
fails under `exact_json: true`. Its only residual hole is the admitted scalar
confusion (`1 == True`), addressed by `json_exact`'s `type() is not type()`
guard — which also preserves the missing-vs-null separation (dict branch checks
`observed.keys() == expected.keys()`).

## F-C8-3 (no defect): `matched_expected_fields` diagnostic

Baseline lines 438–440 `observed_fields.get(key) == value`: `expected_fields`
comes from `numeric_leaves`, which emits only non-bool ints — never `None` — so
the diagnostic has no missing-vs-null conflation. (It does under-report vs the
verdict when an observed `false` satisfies expected `0` via `==`; that is the
already-admitted scalar defect surfacing in a counter, not a new hole.)

## F-C8-4 (observation, out of scope): parse-failure ≡ producer `null`

Baseline lines 421–424: unparseable stdout and stdout literally `null` both
yield `observed = None`. Verdict is identical (fail in both modes); only
`observed_json` in the report cannot distinguish them. Diagnostic granularity
gap, not a predicate defect — **do not add scope** to split them.

## F-C8-5 (adjacent boundary, flagged for the cache-demo seat): explicit `null` crashes `.get` chains

Baseline lines 455, 467: `isolation = payload.get("isolation", {})` and
`payload.get("gate", {}).get("sha256")`. A producer emitting `"isolation": null`
or `"gate": null` returns `None` from the outer `.get`, and the inner `.get`
raises `AttributeError` → **crash, not a clean FAIL**. This is the mirror of the
counter boundary (there, null is silently equal; here, null is fatally unequal)
and touches the preregistered "reject malformed producer data without a crash"
clause. Outside this seat's counter scope; recorded so the cache-demo reviewer
can confirm the integrated `gate`/`isolation` handling guards `None`.

# Literal synthetic oracle pair (boundary vectors)

Synthetic counter step appended for oracle review (not a real step):

```python
("r22-synth-null-leaf", "synthetic/emit.py", "<REV>",
 {"measured_commit": "<REV>", "held_knowledge": None}, False)
```

- **Positive (must PASS):** producer stdout
  `{"measured_commit": "<REV>", "held_knowledge": null, "admitted_entries": 0}`
  — explicit `null` present. PASS under current and repaired predicate;
  extra key `admitted_entries` still tolerated in non-exact mode.
- **Negative (must FAIL):** producer stdout
  `{"measured_commit": "<REV>", "admitted_entries": 0}`
  — `held_knowledge` absent. Current predicate → `None == None` →
  **false green**; repaired `key in observed` → FAIL. This is the literal
  boundary vector distinguishing the two predicates.
- Companion negative (already-green boundary, no new vector needed):
  `{"measured_commit": "<REV>", "held_knowledge": 1}` fails under both.

# In-scope vs rejected added scope

In scope (keep):
- `key in observed` presence guard in the non-exact counter comparison.
- `type()`-exact scalar comparison for expectation leaves equal to `null`,
  `true`, `false` (subsumed by `json_exact`).

Rejected added scope (do NOT claim or implement):
- Requiring non-exact rows to enumerate or whitelist extra producer keys —
  superset tolerance is the intentional r21 contract (`r13-counter-b576341`
  exists to admit supersets).
- Schema validation, coercion matrices, or depth limits on producer JSON beyond
  the declared expectation leaves; preregistration explicitly disclaims
  arbitrary malicious-producer attestation.
- Splitting `observed_json` to distinguish parse failure from producer `null`.
- Any claim that this missing-vs-null repair is a fourth admitted defect; it is
  a boundary-hardened sub-case of the same predicate line.

# Residual risk / verification gaps

- Source-inferred; not executed. Python `==`/`in`/`.get` semantics are certain;
  the latent status (no null in the 5 real expectations) is verified by direct
  read of baseline lines 120–180 and inventory rows 208–337.
- Working-tree repair observed via `git diff` (presence guard + `json_exact`
  present); the acceptance run that would confirm the negative vector is L1's
  seat, not mine.
- `synthetic/emit.py` in the vectors is illustrative; the actual synthetic
  oracle fixture is the round's committed one.

# Trailers

Report: souji-shokunin/.ufo/waves/round-22/w1/Counter8.md
Evidence: souji-shokunin/census/round-21/run-acceptance.py @41553adb (lines 120–180, 319–325, 336–344, 420–445, 447–481)
Evidence: souji-shokunin/census/round-21/step-inventory.json (counter rows 208–337)
Evidence: souji-shokunin/.ufo/waves/round-22/preregistration.txt (C1, malformed-data clause)
Tools installed: none.
