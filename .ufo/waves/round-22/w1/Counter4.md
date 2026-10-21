STATUS: PARTIAL — source-only advisory review of the counter predicate boundary (nested exact bool
confusion) in `run-acceptance.py`. Findings verified against the baseline blob
`git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py` per parent
directive; nothing executed, no files probed beyond contract-named paths. All verdicts below are
source-inferred, not observed decisions.

Axes: calibration (does `matched` mean what the name says), operability (malformed input never
crashes the summarizer), coverage (every expectation leaf actually bound). The defect sits on
calibration; operability holds; coverage is complete-but-weakly-typed.

## Findings (by severity)

### HIGH — Exact counter predicate uses Python `==`: bool (and float) leaves confuse at any depth

Baseline `run-acceptance.py` line 427:

```python
json_match = observed == expected
```

Python `dict.__eq__` recurses with `==` on values, and `False == 0`, `True == 1`, `1.0 == 1`
(bool is an int subclass; numeric equality crosses int/float). JSON `true` parses to `True`, so an
observed boolean substitutes for any expected `0`/`1` leaf — **including nested leaves**, which is
the boundary this seat was asked to isolate. The non-exact branch (lines 430–431,
`all(observed.get(key) == value ...)`) has the identical `==` confusion for its compared keys.

Located expectation surface — `COUNTER_EXPECTATIONS` (baseline 120–180), frozen identically in
`step-inventory.json` (baseline blob lines 207–340). Count of bool-substitutable leaves (expected
value `0` or `1`) across the four exact counters:

| step | top-level 0/1 leaves | nested 0/1 leaves |
|---|---|---|
| `r13-counter-31984f4` | `F2_entry:0`, `evidence_gate:0` (2) | `tiers.C:1` (1) |
| `r13-counter-6f8ee0f` | `F2_entry:1`, `evidence_gate:1` (2) | `tiers.C:1` (1) |
| `r14-counter-a31642d` | `cache_gate:0`, `cache_fixture:0`, `boundary_fixture:0`, `held_knowledge:1` (4) | `tiers.C:1` (1) |
| `r14-counter-552cae4` | `cache_gate:1`, `cache_fixture:1`, `boundary_fixture:1`, `held_knowledge:1` (4) | `tiers.C:1` (1) |

16 substitutable leaves total; 4 of them nested (`tiers.C`). The prior attack finding
(`.ufo/waves/round-21/w2/AttackRunnerStepResults.md` §HIGH-1) demonstrated only top-level
`F2_entry`/`evidence_gate`; the nested `tiers.C` → `true` substitution is the same defect
confirmed at depth, and `held_knowledge:1` is a further unlisted top-level instance. Any single
substitution (e.g. *only* `"tiers": {"A":29,"B":3,"C":true}`) leaves `observed == expected` true.

The non-exact `r13-counter-b576341` (`exact_json: false`, expected `admitted_entries: 6`) cannot be
bool-confused (`True != 6`) but **is** float-confused: `observed.get("admitted_entries")` of `6.0`
equals `6`. The float sibling therefore reaches both branches; bool reaches only 0/1 leaves.

### HIGH — Same-family defect: `numeric_leaves` diagnostic sees the confusion but never gates it

Baseline 336–344 excludes bools (`isinstance(value, int) and not isinstance(value, bool)`), so under
the N1/N2 substitutions below `observed_numeric_fields` *loses* the substituted leaf and
`matched_expected_fields` (baseline 438–441) drops by exactly the substituted count — a visible
diagnostic that the comparison went wrong. But `matched` (baseline 445,
`matched and json_match and not stderr`) never consults any `matched_counts` field, so the record
shows a degraded count while the verdict stays green. This is evidence the confusion is real and
detectable in-band, not a second defect class; the repair belongs at the `==` gate, not at the
diagnostic (see rejected scope).

### LOW — Boundary behaviors that are already correct and must be preserved

Verified on the baseline source:

- Malformed JSON (`json.loads` raises) → `observed = None`, `json_match` false, no crash
  (422–424). Satisfies "reject malformed producer data without a crash".
- Non-dict observed (`null`, `[]`, `0`, `"x"`, `true`) → `==` against expected dict is false;
  non-exact `isinstance(observed, dict)` guard false. No crash, no match. JSON `NaN`/`Infinity`
  parse to floats; `NaN != anything` and neither equals an int — rejected.
- `failure_lines` (330–333) cannot false-positive inside valid JSON stdout: every emitted line
  starts with a JSON token (`{`, `"`, `}`, `]`…), never `FAIL\t`.
- Counter branch already gates `not stderr` (445) — the summary-only stderr gap in the attack doc
  does not apply here.
- Exact comparison is key-order insensitive (dict `==`), which is correct for JSON objects.
- Frozen-inventory pin (600–602, `inventory_projection != frozen["steps"]` → Refusal) means any
  repair must keep `expected_summary` dicts and `exact_json` flags byte-semantically identical —
  the predicate is the only legal change surface, not the expectations.

### Boundary note — duplicate JSON keys (not a defect, not in scope)

`json.loads` applies last-wins to duplicate keys; a producer emitting `"F2_entry":false,
"F2_entry":0` parses to the in-spec value. The raw stdout and `stdout_sha256` are retained in the
record, and C1 claims no producer attestation — recorded as a boundary so the repair does not get
credited/blamed for canonicalization it does not perform.

## Draft literal positive/negative vectors (for the committed result-oracle fixture)

Assumed per-vector step conditions unless stated: `returncode == 0`, `stderr == ""`. Decisions are
source-inferred under (a) baseline `==` predicate, (b) repaired strict-type predicate.

**P1 (positive control — exact `r13-counter-31984f4`, verbatim expectation, must stay green):**

```json
{"F2_entry": 0, "admitted_entries": 4, "evidence_gate": 0,
 "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81", "sources": 33,
 "tiers": {"A": 29, "B": 3, "C": 1},
 "statuses": {"mined": 16, "queued": 15, "rejected": 2}}
```

baseline: matched=true; repaired: matched=true.

**N1 (top-level bool confusion — false-green today):** P1 with `"F2_entry": false,
"evidence_gate": false`. baseline: matched=true (**defect**); repaired: matched=false.

**N2 (nested bool confusion — the seat's isolation vector):** P1 with only `"tiers": {"A": 29,
"B": 3, "C": true}`. baseline: matched=true (**defect**, `numeric_leaves` shows
`matched_expected_fields` 8/9 yet verdict green); repaired: matched=false.

**P2 (non-exact positive control — `r13-counter-b576341` subset semantics must stay accepted per
Q51 "subset-extra-fields … controls accepted"):**

```json
{"measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3",
 "admitted_entries": 6, "extra_unpinned_key": true}
```

baseline: matched=true; repaired: matched=true. Locks in the subset boundary so the repair is not
allowed to tighten non-exact into full equality.

**N3 (float sibling, non-exact branch — proves the confusion is not bool-only, per Q51 "bool/float
negatives rejected"):** P2 with `"admitted_entries": 6.0`. baseline: matched=true (**defect**);
repaired: matched=false.

**N4 (nested-container negative — regression control, already rejected, must stay rejected):** P1
with `"tiers": null` (or `"tiers": [29,3,1]`). baseline: matched=false; repaired: matched=false.
Covers Q51 "null/list nested-container negatives" against any over-loose repair (e.g. comparing
only flattened leaves).

**N0 (malformed producer control):** stdout `[1,2` → both baseline and repaired: matched=false, no
exception.

## Draft repair (call-site-only; keeps inventory projection byte-identical)

```python
def json_exact(observed, expected) -> bool:
    """JSON-value equality with exact scalar types (bool/int/float never conflated)."""
    if isinstance(expected, bool) or isinstance(observed, bool):
        return isinstance(expected, bool) and isinstance(observed, bool) \
            and observed == expected
    if isinstance(expected, (int, float)) or isinstance(observed, (int, float)):
        return type(observed) is type(expected) and observed == expected
    if isinstance(expected, dict):
        return (isinstance(observed, dict)
                and observed.keys() == expected.keys()
                and all(json_exact(observed[k], expected[k]) for k in expected))
    if isinstance(expected, list):
        return (isinstance(observed, list)
                and len(observed) == len(expected)
                and all(json_exact(o, e) for o, e in zip(observed, expected)))
    return observed == expected  # str / None; type differs → False
```

Exact branch (baseline 427): `json_match = json_exact(observed, expected)`.
Non-exact branch (430–431): `all(k in observed and json_exact(observed[k], v) for k, v in
expected.items())` — the `k in observed` guard preserves today's missing-key rejection and makes
the subset boundary explicit. Nothing else in the counter branch changes; `matched_counts`
diagnostics, stderr gate, and `expected_summary` payloads untouched, so the frozen r20 inventory
stays byte-identical and all real positive controls are unaffected (no real counter emits
bool/float at these leaves — they are `int` producers' own printed JSON).

## In-scope defect vs rejected added scope

In scope (C1 "JSON scalar type equality", Q51 bool/float + null/list-container negatives):
strict recursive scalar typing at the `==` gate, covering top-level and nested leaves, both exact
and non-exact branches.

Rejected added scope — do not bundle:

- **Gating `matched` on `matched_counts`** (e.g. `matched_expected_fields == expected_field_count`)
  as the fix: it would not catch bool confusion inside list leaves and duplicates the same check
  poorly; the diagnostic stays informational. The `==` gate is the defect site.
- **Tightening `exact_json: false` to full equality** or pinning `b576341`'s extra keys: Q51
  requires subset-extra-fields controls to be *accepted*; the frozen inventory pins the flag.
- **Changing `expected_summary` literals, `COUNTER_EXPECTATIONS`, or `step-inventory.json`**:
  frozen projection Refusal (baseline 600–602) — any such edit is a contract violation, not a fix.
- **Duplicate-key canonicalization / raw-byte comparison**: producer-attestation territory,
  excluded by preregistration.
- **Recomputing or authenticating counter values against census data**: executed-command/output
  authentication is not claimed; the predicate binds literal expectations only.
- **Summary-stderr and cache-identity repairs**: sibling claims in the same round, not this seat's
  diff surface; flagged here only so the counter diff does not accidentally subsume them.

## Residual risk

- Post-repair, `matched` still trusts the producer for values the expectation does not pin
  (non-exact extra keys, `measured_commit` strings — pinned per-step already). Accepted by
  preregistration.
- `numeric_leaves` annotation says `dict[str, int]` but observed float leaves are silently
  excluded alongside bools; after repair this only affects diagnostics, not verdicts.
- Worktree instability observed mid-review: the working-tree file changed between reads (659 →
  713 lines; `git diff 41553adb` non-empty), consistent with L1 integrating. All line citations
  above are against the baseline blob, which is the claim's before-side authority; nothing here
  judges the in-flight changed implementation.

## Verification gaps

No tests, probes, or runner invocations were executed (contract: source/draft only); every
before/after decision above is source-inferred from the baseline blob plus Python `bool`/`int`/
`float` equality semantics, not an observed `matched` value. `lsp` is not a mounted device in this
session (no `xd://lsp` in the tool inventory), so no semantic references/diagnostics were run; the
findings cite the exact predicate source lines directly, which is stronger than grep-for-absence.
`census/round-14/cache-demonstration.py` was not needed for the counter scope and was left unopened.
No tools installed (pacman transactions paused host-wide; none needed).
