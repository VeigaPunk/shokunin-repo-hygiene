STATUS: PASS — counter-predicate duplicate-JSON-name boundary analyzed source-only against base `41553adb139d06511dc386bb3ce4326aebfba675` (`git show`; baseline runner sha256 `1141839963d04e9e1b968d123fa8ffebeef5d33438537cdc636350c970eeaa2b`, working tree `02e3b06dad7421d43f27b87a41568e6577c1ad64a89a933dc12ee8408f4bc32c`, differs: L1 integration in flight, inspected via `git diff` only). One residual boundary finding (MEDIUM), one verified-covered boundary, literal oracle pair drafted. Nothing executed.

## Axes

Calibration, operability, coverage — per the round contract, no trade permitted. Boundary question: does the counter oracle's `matched` decision track the producer's actual emitted contract (calibration), or can a malformed-but-parseable document green the step?

## Located counter expectation (actual committed vector)

`census/round-21/step-inventory.json` lines 324–336 / baseline `census/round-21/run-acceptance.py` `COUNTER_EXPECTATIONS` lines 171–179:

- step `r13-counter-b576341`, `kind: counter`, `exact_json: false`
- `expected_summary = {"measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3", "admitted_entries": 6}`

Exact-typed row for contrast: `r13-counter-31984f4` (inventory lines 208–227, `exact_json: true`, expected `F2_entry: 0`, `admitted_entries: 4`, `evidence_gate: 0`, `sources: 33`, `tiers {A:29,B:3,C:1}`, `statuses {mined:16,queued:15,rejected:2}`).

## Findings by severity

### MEDIUM — Duplicate object names shadow contradictory values before any comparison (residual on baseline AND integrated)

Baseline `run-acceptance.py:422` `observed = json.loads(stdout)` uses the default decoder. Python's documented semantics (https://docs.python.org/3/library/json.html#repeated-names-within-an-object, 3.15.1): "the names within a JSON object should be unique, but does not mandate how repeated names ... should be handled. By default, this module does not raise an exception; instead, it ignores all but the last name-value pair for a given name" — `json.loads('{"x": 1, "x": 2, "x": 3}')` → `{'x': 3}`; `object_pairs_hook` can alter this.

Consequence at baseline: `:427` `observed == expected` (exact) and `:430–431` `observed.get(key) == value` (subset) compare only the collapsed dict. A producer that emits a contradictory member *before* the honest last member is invisible to the oracle — `matched` at `:445` is True given returncode 0 and empty stderr.

Consequence on the integrated working tree: L1's `json_exact` compares `type(observed) is not type(expected)` then values — still only over the already-collapsed dict; the duplicate-pair shadow survives identically. Source-inferred from the inspected diff; not executed.

Nested members are equally affected (`object_pairs_hook`/`object_hook` semantics apply per decoded object literal). The cache-demo branch (`:448`) shares the decode: post-integration `checks.keys() == CACHE_CHECK_NAMES` blocks extra/missing names, but 33 distinct expected names plus a duplicated expected member (34 wire members → 33 keys) still passes `keys()` identity while shadowing one check's earlier value — same defect class, narrowed but not closed by check-name identity.

In-scope defect vs rejected added scope:

- IN-SCOPE to disclose as residual risk under calibration — the oracle claims a result-contract comparison and silently discards part of the record it claims to compare. Repair (`object_pairs_hook` raising a `ValueError` subclass → existing `except (ValueError, TypeError)` → `observed = None` → retained mismatch, no crash) is consistent with the preregistered "reject malformed producer data without a crash" and Q51's "covered malformed containers produce a retained mismatch, not a crash." However, Q51's check column enumerates the rejected negative classes ("bool/float, nonempty stderr, renamed checks, wrong phases and null/list nested-container negatives") and duplicate names are NOT listed — a dup-name negative is a NEW oracle vector class. Disposition: repair only if L1/oracle admits the added vector; otherwise record as an explicitly disclosed residual limit, never silently claimed exact.
- REJECTED ADDED SCOPE (do not repair, not named defects, not Q51 classes): canonical-byte/member-order-sensitive JSON comparison; `NaN`/`Infinity`/`Infinity` strictness via `parse_constant` (unreachable against all-integer/string/dict expectations anyway); nesting-depth/size limits; string↔number coercion rules; producer authentication (preregistration disclaims "arbitrary malicious-producer attestation").

### Verified-covered boundary (not a finding)

Baseline `observed.get(key) == value` returns `None == value` → False for missing keys *unless* an expected value were `None` — latent only (no expected contains null); the integrated `key in observed and json_exact(...)` closes it. Adjacent scalar confusions `{"admitted_entries": 6.0}` and `{"admitted_entries": true}`: baseline `6.0 == 6`/`True == 1` green; integrated `json_exact` rejects via `type(...) is not` — defect 1 covers both, matching Q51's "bool/float" named negatives.

## Literal oracle pair (draft, for the synthetic result-oracle fixture)

Counter: `r13-counter-b576341` (`exact_json: false`), rc 0, empty stderr.

Positive control — must match (extra key exercises retained subset semantics, Q51 "subset-extra-fields … accepted"):

```json
{"measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3", "admitted_entries": 6, "sources": 40}
```

Negative vector — must NOT match; currently matches on baseline and integrated (the disclosed residual):

```json
{"measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3", "admitted_entries": 0, "admitted_entries": 6}
```

Decodes to `{"admitted_entries": 6}` (last-wins) → `observed.get("admitted_entries") == 6` → green; the shadowed `0` is discarded before comparison. Exact-row variant for `r13-counter-31984f4`: insert `"admitted_entries": 99` before the true `"admitted_entries": 4` member in the literal expected object — identical false green.

Draft repair (report-only, applies to both producer-output `json.loads` sites; do NOT apply to the repo-owned `proc-agreement-pinned.json`/frozen-inventory loads at baseline `:496`/`:600`):

```python
def _reject_duplicate_names(pairs):
    seen = set()
    for key, _value in pairs:
        if key in seen:
            raise Refusal("duplicate object name: " + key)
        seen.add(key)
    return dict(pairs)

observed = json.loads(stdout, object_pairs_hook=_reject_duplicate_names)
```

`Refusal` subclasses `ValueError` (`:183`), so the existing `except` converts the raise into `observed = None` → retained mismatch, no crash; `object_pairs_hook` fires for every decoded object literal, covering nested duplicates. Real producers (`json.dumps`) cannot emit duplicate names — operability and the 18 original positive controls are untouched; coverage unchanged; calibration strictly improves. Still a scope-extension decision per the Q51 enumeration above.

## Residual risk and verification gaps

- Exploitability is bounded: `json.dumps` cannot emit duplicate names, so this false green requires a hand-rolled/malformed producer — the preregistration disclaims malicious-producer attestation; the honest-broken-producer shadowing case remains worth disclosing.
- Baseline claims rest on `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py` bytes; the working tree differs (L1 integration: `json_exact`, summary `not stderr`, `CACHE_CHECK_NAMES`/`CACHE_CASE_PHASES`, `int()` guard) — all three named repairs verified present in the inspected diff, consistent with Q51's named classes.
- Source-only review; no runner, oracle, or fixture executed (contract). `xd://lsp` is not a mounted device in this session — caller/definition checks used direct named-file reads only; no grep-as-semantic-proof claimed. No tools installed; no files read outside the contract list.

## Report trailers

- Named files read: `census/round-21/run-acceptance.py` (working tree + `git show` base), `census/round-21/step-inventory.json:207-337`, `census/round-14/cache-demonstration.py:1-63`, `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`, `.ufo/waves/round-22/preregistration.txt`, `corpus/QUALITY.md` (incl. Q51 raw row).
- Named public source: https://docs.python.org/3/library/json.html (3.15.1) — repeated-names and `object_pairs_hook` sections quoted above.
