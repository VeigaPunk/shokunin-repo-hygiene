STATUS: PASS — counter-predicate "list in place of object" boundary analyzed against baseline `41553adb139d06511dc386bb3ce4326aebfba675` (via `git show`, per L1 redirect) and the in-flight integration diff. All findings are source-inferred; no runner, fixture, or oracle was executed. No tools installed.

## Scope

Assigned boundary: the `kind == "counter"` predicate in `census/round-21/run-acceptance.py` when producer stdout decodes to a JSON **list** (or other non-object shape) instead of the expected object. Named files read: the runner (working tree + baseline revision), `census/round-21/step-inventory.json`, `census/round-14/cache-demonstration.py` (skim, for shared parse pattern only), `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`, `.ufo/waves/round-22/preregistration.txt`, `corpus/QUALITY.md`. Nothing outside the named set was opened.

## Baseline predicate shape (41553adb)

```python
elif kind == "counter":
    try:
        observed = json.loads(stdout)
    except (ValueError, TypeError):
        observed = None
    expected = step["expected_summary"]
    if step["exact_json"]:
        json_match = observed == expected                    # ~L427
    else:
        json_match = (isinstance(observed, dict)
                      and all(observed.get(key) == value
                              for key, value in expected.items()))  # ~L430-431
    observed_fields = numeric_leaves(observed) if isinstance(observed, dict) else {}
    ...
    matched = matched and json_match and not stderr          # ~L445
```

`numeric_leaves` (baseline ~L336-344) recurses dicts only, skips lists, and deliberately excludes bools (`isinstance(value, int) and not isinstance(value, bool)`) — i.e. the diagnostics already treat bool as non-numeric, while the match predicate does not.

Actual expectations located (`COUNTER_EXPECTATIONS`, baseline L120-180; mirrored in `step-inventory.json` L207+ with `"exact_json": true, "kind": "counter"`):

- `r13-counter-31984f4` — zero-leaves `F2_entry: 0`, `evidence_gate: 0` (exact).
- `r14-counter-a31642d` — zero-leaves `cache_gate`, `cache_fixture`, `boundary_fixture` all `0` (exact).
- `r14-counter-552cae4` — one-leaves `cache_gate`, `cache_fixture`, `boundary_fixture` all `1` (exact).
- `r13-counter-b576341` — partial projection `{measured_commit, admitted_entries: 6}`, `exact=False`: the subset path is a real, required semantic (the producer emits more keys than the expectation).

## Findings

### F1 — IN-SCOPE DEFECT (admitted): scalar type confusion reaches through nested objects, both paths

`observed == expected` and `observed.get(key) == value` compare with Python equality, which holds `False == 0`, `True == 1`, and `1.0 == 1`. Confusion propagates **inside nested dicts** too: `{"tiers": {"A": 29, "B": 3, "C": True}}` compares equal to `{"tiers": {"A": 29, "B": 3, "C": 1}}`. `numeric_leaves` omits the bool leaves from `observed_numeric_fields` (e.g. `r14-counter-a31642d` with all three gates `false` shows `matched_expected_fields` 9 of 12), but `matched_counts` never gates `matched` — so with rc 0 and empty stderr the step false-greens. Any repair must compare type + value recursively; a shallow key-set check is insufficient.

### F2 — BOUNDARY HOLDS, not a defect: list in place of object fails closed

Every non-object `observed` shape is rejected on baseline **and** under the integration:

| observed stdout | exact path | non-exact path | crash? |
|---|---|---|---|
| `[{…identical fields…}]` | `list == dict` → False | `isinstance(observed, dict)` short-circuits before `.get` | none |
| `[["k", v], …]` pairs | same | same | none |
| `0`, `"s"`, `true`, `null` | `scalar == dict` → False | isinstance guard | none |
| list under a leaf (`"tiers": [33,3,1]`) | `list == dict` → False | `.get` value `list == dict` → False | none |
| malformed / empty / JSONL / BOM | `observed = None` → not dict | same | none (ValueError/TypeError caught) |

`observed_fields` is likewise isinstance-guarded. Verdict is correct (producer emitted the wrong shape → step unmatched), satisfying "reject malformed producer data without a crash" for these shapes already. This boundary is a **regression control**, not an in-scope defect — the repair must not regress it.

### F3 — IN-SCOPE DEFECT (prereg "without a crash"): `except (ValueError, TypeError)` misses `RecursionError`

`json.loads` on deeply-nested (still well-formed) JSON raises `RecursionError`, which is a `RuntimeError`, **not** a `ValueError` — so it escapes the parse guard at baseline ~L421-424. A counter (or the cache-demo producer, same pattern at its `json.loads`) emitting ~1000+ nested `[[[…]]]` or `{"a":{"a":…}}` crashes `summarize_result`; the whole runner dies before writing a step record instead of marking the step unmatched. The integration diff leaves the `except` clause unchanged, so this stands **post-integration**.

Secondary same-class risk, marginal: `numeric_leaves(observed)` recurses producer-controlled dict depth outside the `try`; a payload that parses near the interpreter recursion limit can re-overflow in the recursive walk (baseline and integrated alike). Fix sketch — fail-closed guard plus iterative traversal (identical leaf semantics):

```python
try:
    observed = json.loads(stdout)
except (ValueError, TypeError, RecursionError):
    observed = None

def numeric_leaves(value, prefix=""):
    found, stack = {}, [(value, prefix)]
    while stack:
        node, base = stack.pop()
        if isinstance(node, dict):
            for key, item in node.items():
                stack.append((item, key if not base else base + "." + key))
        elif isinstance(node, int) and not isinstance(node, bool):
            found[base] = node
    return found
```

### F4 — Latent adjacent boundary, already closed by the integration

`observed.get(key) == value` treats a **missing** key as `None`; a `None`-valued expectation would silently accept an absent field. No committed counter expectation has a `None` leaf, so this is latent, not a live defect. The integrated non-exact branch (`key in observed and json_exact(...)`) already closes it — worth retaining, not a new claim.

## Rejected added scope (do not claim or "fix")

- **Subset semantics of the non-exact path** (`r13-counter-b576341`): extra producer keys allowed by design; forcing full equality breaks the real historical positive control. Keep.
- **Duplicate keys / last-wins** in `json.loads`, and **NaN/Infinity** decoder tolerance: wire-byte authenticity is producer attestation, explicitly excluded ("no arbitrary malicious-producer attestation"). Both still fail the match anyway (deep `NaN` type-mismatches int; duplicate keys only collapse values).
- **Key-order insensitivity** of `dict ==` / `json_exact`: correct JSON-object semantics, not a defect.
- **`matched_counts` not gating `matched`**: diagnostic surface by design; the oracle judges `matched`.
- **`failure_lines` scanning JSON stdout**: a `FAIL\t`/`CASE…FAIL` line can only appear at line-start outside valid JSON (real newlines are illegal inside JSON strings), so it is at worst a false-red on already-rejected malformed output — no false-green.
- **Dotted-name collisions** in `numeric_leaves` (`{"a.b":1}` vs `{"a":{"b":1}}`): diagnostic-only ambiguity, unchanged by this round.

## Literal vector pair — boundary "list in place of object"

Step `r14-counter-a31642d`, argv `count-claims.py a31642d14006830ec62edf40b0354c3699728c4a`, rc 0, stderr `""` in both.

**NEG (control — must stay unmatched on baseline and post-repair):**

```json
[{"measured_commit": "a31642d14006830ec62edf40b0354c3699728c4a", "cache_gate": 0, "cache_fixture": 0, "boundary_fixture": 0, "source_rows": 37, "tiers": {"A": 33, "B": 3, "C": 1}, "statuses": {"mined": 20, "queued": 15, "rejected": 2}, "admitted_knowledge": 5, "held_knowledge": 1}]
```

Identical field content wrapped in a one-element array → `matched=false` before and after. Companion NEGs for the same class: `[["cache_gate", 0], …]` pair-encoding, and `{"cache_gate": [0], …}` (list under a leaf).

**POS (real shape — must stay matched):**

```json
{"measured_commit": "a31642d14006830ec62edf40b0354c3699728c4a", "cache_gate": 0, "cache_fixture": 0, "boundary_fixture": 0, "source_rows": 37, "tiers": {"A": 33, "B": 3, "C": 1}, "statuses": {"mined": 20, "queued": 15, "rejected": 2}, "admitted_knowledge": 5, "held_knowledge": 1}
```

`matched=true` before and after. The pair isolates container-vs-object with byte-identical content, so it exercises exactly my assigned boundary and nothing else.

## Literal discriminating vector — in-scope scalar defect (F1)

Same step, same rc/stderr; only the three gate leaves flipped to bool:

```json
{"measured_commit": "a31642d14006830ec62edf40b0354c3699728c4a", "cache_gate": false, "cache_fixture": false, "boundary_fixture": false, "source_rows": 37, "tiers": {"A": 33, "B": 3, "C": 1}, "statuses": {"mined": 20, "queued": 15, "rejected": 2}, "admitted_knowledge": 5, "held_knowledge": 1}
```

Baseline: `False == 0` per leaf → `matched=true` (false green). Required post-repair decision: `matched=false`. Nested-dict twin (keeps all top-level leaves intact): `"tiers": {"A": 33, "B": 3, "C": true}` — same discrimination via the nested `==`. `true`-for-`1` variant: step `r14-counter-552cae4` with `cache_gate: true, cache_fixture: true, boundary_fixture: true`.

## Integration-diff check (working tree vs 41553adb, observed via `git diff`)

`json_exact(observed, expected)` was added: `type() is not type()` gate, dict key-view equality + recursion, list length + `zip` recursion, scalar `==`. Applied at both counter sites (`exact_json` path and the non-exact `all()`, now with `key in observed`). Verified by diff-read, not execution:

- bool/int/float confusion closed at top level **and** recursively — covers F1 fully for counters.
- list-in-place-of-object still fails closed (type gate fires before dict/list descent) — F2 preserved.
- subset semantics for `b576341` preserved — required behavior retained.
- F3 unchanged: `except (ValueError, TypeError)` still catches no `RecursionError`; `numeric_leaves` still recursive. **Open against the integration.**

## Residual risk / verification gaps

- F3's crash is source-inferred from documented CPython decoder semantics (deep nesting → `RecursionError`); not executed, per contract. Recommended oracle probe is source-reviewable only; L1 runs acceptance.
- `xd://lsp` is not mounted in this session (per the w2 attack report's identical observation); citations are direct named-file reads, not LSP references. No grep was used for semantic claims.
- The working tree changed mid-review (L1 integration, announced by parent); baseline claims rest on `git show 41553adb…:census/round-21/run-acceptance.py`, integration claims on the observed diff hunk `@@ -424,11 +468,12 @@`. Integrated line numbers are approximate.
- Nothing was executed, installed, or mutated; sole write is this report.
