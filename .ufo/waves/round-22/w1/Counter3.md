STATUS: PASS — Counter exact-JSON predicate boundary analyzed against the pinned baseline blob. The `int → float` conflation is real: baseline `observed == expected` (exact branch) and `observed.get(key) == value` (subset branch) accept JSON floats where integers are expected, because Python `0 == 0.0` and `1 == 1.0` are `True`. Actual counter expectations were located; literal positive/negative oracle vectors are drafted below. In-scope mechanism is distinguished from rejected added scope. Everything is source-inferred; nothing was executed. During this review the working-tree runner changed (L1 integration landing mid-flight); all baseline claims cite the pinned blob, and the in-flight diff is reported separately without being reviewed or admitted.

Axes: calibration (typed scalar equality at the counter predicate), coverage (vectors that discriminate complete repair from bool-only patch), operability (predicate-only change, no new machinery). No trade taken: the same strict predicate serves all three.

## Baseline pins (git show @ 41553adb139d06511dc386bb3ce4326aebfba675)

| artifact | sha256 | state |
|---|---|---|
| `census/round-21/run-acceptance.py` (baseline blob) | `1141839963d04e9e1b968d123fa8ffebeef5d33438537cdc636350c970eeaa2b` | cited for every baseline line number |
| `census/round-21/run-acceptance.py` (working tree) | `02e3b06dad7421d43f27b87a41568e6577c1ad64a89a933dc12ee8408f4bc32c` | diverged mid-review: +63/−9, uncommitted, HEAD `36c78ba016bbf28548c9c7191da089b91022f8e1` |
| `census/round-21/step-inventory.json` | `8b7b1cd8d19561d9f4e8f06e797038b03379350cb3f3932edf04bda7aa7d1310` | byte-identical baseline ↔ working tree |

Baseline line numbers below are `git show` grep -n positions on the blob, not the current working file.

## The counter predicate boundary (baseline, `41553adb…:census/round-21/run-acceptance.py`)

- `COUNTER_EXPECTATIONS` at lines 120–180: 5 expectations. `exact=True`: `r13-counter-31984f4`, `r13-counter-6f8ee0f`, `r14-counter-a31642d`, `r14-counter-552cae4`; `exact=False` (subset match): `r13-counter-b576341` (line 178). Frozen twin: `step-inventory.json` lines 207–337 (`"exact_json": true` at 226/254/284/313, `false` at 329).
- `make_steps` projects them at baseline line 319–325 (`"exact_json": exact`).
- `summarize_result` counter branch, baseline lines 420–445:
  - line 427 — exact branch: `json_match = observed == expected`
  - lines 430–431 — subset branch: `all(observed.get(key) == value for key, value in expected.items())`
  - line 445 — `matched = matched and json_match and not stderr`
- `numeric_leaves` (baseline 336–344) counts only `isinstance(value, int) and not isinstance(value, bool)`; the computed `matched_counts` (lines 435–444) is diagnostic — it does **not** gate `matched`.

### Conflation analysis (source-inferred, stdlib semantics)

`json.loads` maps `0` → `int`, `0.0`/`1e0` → `float`, `false`/`true` → `bool`. Python `==` then conflates all three families: `0 == 0.0 == False`, `1 == 1.0 == True`. So at baseline line 427 a producer that emits `0.0` for expected integer `0` is accepted under a predicate named `exact_json`. The float case is the same defect class as the admitted bool/int confusion (preregistration: "JSON bool/int scalar confusion") — one mechanism, `==` type coercion, two scalar-pair witnesses.

Secondary asymmetry: `numeric_leaves` is both bool-blind **and** float-blind. An all-float substitution yields `observed_numeric_fields = {}` and `matched_expected_fields = 0` while `matched` stays `true` — identical blind spot to the bool case already recorded in `.ufo/waves/round-21/w2/AttackRunnerStepResults.md` (HIGH, lines 5–9). The diagnostic drop is observably inconsistent but non-gating; it is listed under residual risk, not counted as a separate defect.

Precision note: `int == float` on huge magnitudes can false-negative (e.g. `2**53+1` vs `9007199254740993.0`), so `==` is neither reliably strict nor reliably loose — only a type-strict predicate is well-defined.

## Literal oracle vectors (draft; for independent review per preregistration)

All vectors: `returncode = 0`, `stderr = ""` — the scalar predicate is isolated from the already-present counter stderr gate (baseline line 445).

**P1 — positive control, `r13-counter-31984f4`** (exact literal of `step-inventory.json:209-225`; required decision `matched=true`, baseline `matched=true`):

```json
{"F2_entry": 0, "admitted_entries": 4, "evidence_gate": 0,
 "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81",
 "sources": 33, "tiers": {"A": 29, "B": 3, "C": 1},
 "statuses": {"mined": 16, "queued": 15, "rejected": 2}}
```

**N1 — int→float negative, single field** (required `matched=false`; baseline `matched=true` — false green). As P1 except:

```json
"F2_entry": 0.0
```

**N1b — int→float negative, maximal** (required `matched=false`; baseline `matched=true` plus the diagnostic blind spot: `observed_numeric_fields={}`, `matched_expected_fields=0` of `expected_field_count=10`). Every integer leaf emitted as a float literal:

```json
{"F2_entry": 0.0, "admitted_entries": 4.0, "evidence_gate": 0.0,
 "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81",
 "sources": 33.0,
 "tiers": {"A": 29.0, "B": 3.0, "C": 1.0},
 "statuses": {"mined": 16.0, "queued": 15.0, "rejected": 2.0}}
```

**N0 — bool/int negative (the admitted class), kept paired** (required `matched=false`; baseline `matched=true`). As P1 except `"F2_entry": false, "evidence_gate": false`. Needed to prove the repair is not over-fit to floats alone.

**N2 — subset-branch negative, `r13-counter-b576341`** (`exact_json=false`, `step-inventory.json:323-337`; required `matched=false`; baseline `matched=true`):

```json
{"measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3",
 "admitted_entries": 6.0}
```

**P2 — exactness control already correct at baseline** (key-set discipline: P1 minus `evidence_gate`, or with an extra key; required `matched=false`; baseline already `matched=false` via dict equality). Retains the guarantee that exact means exact key set.

Discrimination purpose of N1/N1b: a narrow repair that special-cases only `bool` (e.g. `isinstance(x, bool)` guard while keeping `==`) passes N0 yet still fails N1 — the float vectors are the minimal discriminator between "admitted-defect patch" and "complete scalar-type-strict predicate".

## In-scope vs rejected added scope

**In scope (same mechanism as the admitted defect):** type-strict scalar equality for counter JSON — `bool↔int`, `int↔float`, `bool↔float`, in both exact and subset branches, top-level and nested. Repair requires only a strict predicate; no inventory, expectation, argv, or control changes. Malformed producer output stays refused-not-crashing (`json.loads` → `None` → mismatch), per preregistration.

**Rejected as added scope:**

- Float tolerance/epsilon matching — would *worsen* type blur; no counter needs it.
- `NaN`/`Infinity` literal handling — nonstandard JSON; no expectation contains them; `==` already refuses them (`0.0 != nan`); declaring a class is unneeded.
- Duplicate JSON keys in producer stdout — `json.loads` last-wins semantics is a distinct decoder property, not scalar-type confusion; recorded as residual risk only.
- Text-level float formatting equivalence (`"0.0"` vs `"0"`) — that *is* the defect, not a second claim.
- Applying strict equality to `summary`-kind steps — summary expectations are strings/regex over stdout lines, no JSON scalar surface.
- Extending this seat's claim into the `cache-demo` check-identity defect — separate admitted defect, owned by the cache seats; noted only because the integration diff touches it.
- New counters, changed expected values, or inventory edits — frozen artifact; byte-identical confirmed.
- Producer authentication / executed-command attestation — explicitly excluded by preregistration.

## Draft predicate sketch (report-only; L1 integrates)

```python
def json_exact(observed, expected) -> bool:
    """Decoded-JSON equality with strict scalar types (bool/int/float distinct)."""
    if type(observed) is not type(expected):
        return False
    if isinstance(expected, dict):
        return (observed.keys() == expected.keys()
                and all(json_exact(observed[key], value)
                        for key, value in expected.items()))
    if isinstance(expected, list):
        return (len(observed) == len(expected)
                and all(json_exact(o, e) for o, e in zip(observed, expected)))
    return observed == expected

# exact branch:      json_match = json_exact(observed, expected)
# subset branch:     json_match = (isinstance(observed, dict)
#                     and all(key in observed and json_exact(observed[key], value)
#                             for key, value in expected.items()))
```

`type() is not type()` first splits `bool`/`int`/`float`/`str`/`None` before any value comparison; `int`/`int` retains exact big-integer semantics. Alternative shape (canonical `json.dumps` comparison) also separates `0`/`0.0`/`false` at the text level but inherits NaN asymmetries; the typed predicate is preferred.

## In-flight integration observation (source-inferred, NOT reviewed/admitted)

The uncommitted working-tree diff against baseline (observed via `git diff` grep of `+`/`-` lines; ~40 sampled hunk lines) adds a `json_exact` helper with a leading `type(observed) is not type(expected)` check, replaces both counter comparisons, adds `and not stderr` to the summary branch, and replaces cache `len(checks)`/`checks.values()` counting with a `CACHE_CHECK_NAMES` key-set identity plus `json_exact` on `failed_checks`/`producer_executions_new_policy`. If that implementation is what lands, N1/N1b/N2 flip to `matched=false` and P1/P2 stay green — the float boundary is covered by the typed-predicate shape, not by a float-specific clause. This seat reviewed the boundary and vectors only; the diff itself is L1's integration and has not been examined for correctness beyond the sampled lines.

## Residual risk

- Duplicate-key producer stdout (`{"F2_entry": 1, "F2_entry": 0}`) — decoder keeps the last key; unrelated to scalar type, no repair proposed, flagged only.
- `numeric_leaves` remains float/bool-blind for `matched_counts` diagnostics; non-gating. If kept, its field names ("numeric") silently exclude real float leaves — a cosmetic rename or documented caveat is optional, not required.
- `float` vs `int` equivalence at magnitude > 2^53 under `==` is undefined-feeling in both directions; the typed predicate removes the ambiguity entirely.
- The exact branch's dict `keys()` comparison is already exact at baseline (P2); no regression risk from the typed predicate.

## Verification gaps

- No runner, fixture, or target code was executed (contract); all decisions are source-inferred from the pinned blob plus documented `json`/equality semantics.
- The working tree mutated during review (file hash and length changed between reads; `git status` shows uncommitted changes). Baseline claims rest on blob `11418399…`; inventory on byte-identical blob `8b7b1cd8…`.
- `xd://lsp` is not a mounted device ("No such tool"); no LSP references/definition/diagnostics are claimed. Callers of `summarize_result`/`numeric_leaves` were confirmed only within the named file; the counter branch consumes `step["exact_json"]`/`step["expected_summary"]` produced by `make_steps` from `COUNTER_EXPECTATIONS` (baseline lines 319–325), matching the inventory rows.
- Named files read: `census/round-21/run-acceptance.py` (working tree + baseline blob), `census/round-21/step-inventory.json`, `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`, `.ufo/waves/round-22/preregistration.txt`, `corpus/QUALITY.md`. `census/round-14/cache-demonstration.py` was not opened — out of this seat's counter-predicate scope.
- No tools installed (parent directive: no new tools authorized; nothing was needed). Files written: this report only. No git/index mutation, no delegation, no background jobs.
