STATUS: PASS — counter predicate null-container boundary fully mapped from named sources; one admitted-defect vector class confirmed (bool/int and float/int coercion, including inside nested containers), the counter branch's null-container behavior verified already-reject-and-retained (regression control for the repair), and one adjacent nested-null crash surfaced in the cache-demo branch that Q51's malformed-container clause covers. Source-only review; nothing executed.

Report trailers are relative to `souji-shokunin/`.

## Basis (authority read this seat)

- `census/round-21/run-acceptance.py` — read in the working tree AND re-read at base
  `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py`
  (blob stream sha256 `1141839963d04e9e1b968d123fa8ffebeef5d33438537cdc636350c970eeaa2b`).
  The counter/cache-demo predicate block (`numeric_leaves` 336–344, `summarize_result` counter
  branch 420–445, cache-demo branch 446–480) is identical at base and in the working tree;
  line numbers below are valid for both.
- `census/round-21/step-inventory.json` — frozen r20 inventory: `clean-cache-demonstration`
  expects `cases:4, checks:33` (lines 187–205); four exact counters + one subset counter
  (lines 207–337).
- `.ufo/waves/round-21/w2/AttackRunnerStepResults.md` — the three admitted OPEN defects.
- `.ufo/waves/round-22/preregistration.txt` — claim C1 scope.
- `corpus/QUALITY.md` Q51 — the round-22 criterion: "counter scalar/container types are
  exact … Covered malformed containers produce a retained mismatch, not a crash …
  bool/float, nonempty stderr, renamed checks, wrong phases and null/list nested-container
  negatives rejected." The Q51 check text explicitly names **null/list nested-container
  negatives**, which is this seat's assigned boundary.
- `census/round-14/cache-demonstration.py` — real producer shape only (it always emits a
  dict payload); not needed for the synthetic-oracle threat model but confirms which keys
  the predicate reads.

## Actual counter expectations located (the values under test)

`COUNTER_EXPECTATIONS` (run-acceptance.py:120–180), five counter steps appended by
`make_steps` (319–326) with `kind:"counter"`:

| step | file:inv.lines | exact_json | scalar fields relevant to this boundary |
|---|---|---|---|
| `r13-counter-31984f4` | inventory 207–233 | true | `F2_entry:0`, `evidence_gate:0`, `admitted_entries:4`, `sources:33`, nested `tiers.A:29/B:3/C:1`, `statuses.mined:16/queued:15/rejected:2` |
| `r13-counter-6f8ee0f` | inventory 235–262 | true | `F2_entry:1`, `evidence_gate:1`, `admitted_entries:5`, `sources:37`, nested ints |
| `r14-counter-a31642d` | inventory 263–292 | true | `cache_gate:0`, `cache_fixture:0`, `boundary_fixture:0`, `source_rows:37`, `admitted_knowledge:5`, `held_knowledge:1`, nested ints |
| `r14-counter-552cae4` | inventory 293–322 | true | `cache_gate:1`, `cache_fixture:1`, `boundary_fixture:1`, `source_rows:40`, `admitted_knowledge:5`, `held_knowledge:1`, nested ints |
| `r13-counter-b576341` | inventory 323–337 | **false** (subset) | `admitted_entries:6`, `measured_commit:"b5763415…"` |

Every exact counter contains `0`/`1` integer fields, so `False==0`/`True==1` coercion is
exercisable against all four; the subset counter's sole numeric field is `6`, attackable by
float `6.0` (below), not by `true`.

## Counter predicate: what the code does today (lines 420–445)

```python
observed = json.loads(stdout)          # any failure (incl. empty stdout) -> None
if step["exact_json"]:
    json_match = observed == expected                # L427: Python ==, type-blind
else:
    json_match = (isinstance(observed, dict)
                  and all(observed.get(key) == value # L430-431: .get == expected
                          for key, value in expected.items()))
expected_fields = numeric_leaves(expected)           # bool leaves excluded L342
observed_fields = numeric_leaves(observed) if isinstance(observed, dict) else {}
...
matched = matched and json_match and not stderr      # L445
```

## Finding 1 (IN-SCOPE, admitted defect 1 — extended evidence): scalar equality is
type-blind across the whole container, not just top level

Severity: HIGH (this is the calibration claim's core).

- `observed == expected` (L427) uses Python `==`: `False==0`, `True==1`, and — not
  named in the r21 attack but the same root cause — `6.0==6`, `1.0==1`. JSON `6.0`/`1e0`
  parse to `float`; the float path is a false-green on **every** integer field, including
  the subset step's `admitted_entries:6`, which has no 0/1 field and was therefore not
  attackable by the bool vector. Q51's check line names "bool/float" negatives, so the
  float case is in-scope, not added scope.
- The confusion is **transitive through nested containers**: `{"tiers":{"A":false,"B":3,
  "C":1}}` compares equal to expected `{"A":29,"B":3,"C":1}`? No — value differs. But
  `{"tiers":{"A":29.0,...}}` or any bool substituted for a `0`/`1`-valued nested leaf
  compares equal, because dict `==` recurses with the same `==`. A repair that only
  type-checks top-level values leaves nested `tiers`/`statuses` coercion intact; Q51's
  "scalar/container types are exact" requires a **recursive** strict comparison.
- Subset path same defect: `observed.get(key) == value` (L431) — `{"admitted_entries":6.0}`
  matches `6` today. Note `observed.get(key)` returns `None` for a missing key AND for an
  explicit `null` value; today that conflation is harmless only because no expectation is
  `null` (see Finding 3).

## Finding 2 (boundary verdict — counter null container is already reject-and-retained;
it is a regression CONTROL, not a defect)

For every null-container input to the counter branch, current behavior is already the
required post-repair behavior — these must be pinned as controls so the strict-equality
repair cannot regress them:

| synthetic stdout (rc 0, stderr "") | today | required after repair |
|---|---|---|
| `null` (JSON literal) → `observed is None` | `json_match` False both paths; record retained with `observed_json:null` | identical |
| `[]` / `[0]` (list container) | False; `observed_fields={}` since not dict | identical |
| `{}` (empty object, missing keys) | False — exact: `dict!=dict`; subset: `None==6` False | identical — repair MUST keep missing-key rejection; a `.get(key, expected-default)` or null-normalizing fix would false-green here |
| `{"F2_entry":null, …}` (null in place of int 0) | False — `None!=0`, `None!=False` | identical — `null` must never equal `0`, `false`, `""` under strict compare |
| `{"measured_commit":"b5763415…","admitted_entries":null}` subset | False — `None==6` False | identical |
| truncated/garbage stdout `{` | `json.loads` → `observed=None` → False, no crash | identical |
| stdout `true` / `0` (scalar root) | False (not dict / `!=` dict) | identical |
| subset extra field incl. null: `{…,"extra":null}` | **True** — `all()` iterates expected keys only | **still True** — Q51 keeps "subset-extra-fields … controls accepted" |

One diagnostic ambiguity survives and is NOT a defect: `observed_json:null` in the record
cannot distinguish "producer emitted `null`" from "unparseable stdout" (both collapse to
`None` at L422–424). `matched:false` is correct either way; distinguishing them is rejected
added scope (below).

## Finding 3 (latent boundary, materializes only under repair): missing-vs-null conflation
in the subset path

`observed.get(key) == value` (L431) cannot tell "key absent" from "key present with `null`".
Harmless today (no `null` in any expectation), but if the repair rewrites this as a strict
compare it must keep "absent" rejected — e.g. `key in observed and strict_equal(observed[key],
value)` or a `_MISSING` sentinel — and define `null` semantics explicitly (strict-equal only
to `null`). Flagging so the fix is specified, not merely implied.

## Finding 4 (adjacent — outside the three admitted defects but inside Q51's check text):
nested null/list container crashes the cache-demo branch instead of a retained mismatch

Severity: MEDIUM; routed to L1 for disposition — it is covered by Q51's "null/list
nested-container negatives rejected" + "Covered malformed containers produce a retained
mismatch, not a crash", but it is NOT one of the admitted three.

Lines 467–469:

```python
payload.get("gate", {}).get("sha256")          # "gate":null/[]/"x"/0 -> AttributeError
isolation = payload.get("isolation", {})        # "isolation":null/[]/0 -> None/non-dict
isolation.get("cleaned") ...                    # AttributeError
```

`dict.get(key, {})` defaults only on an **absent** key. An explicit `"gate": null` or
`"isolation": null` (or any non-dict value — list, int, string, bool) yields `None`/non-dict,
and the chained `.get` raises `AttributeError`. `AttributeError` is absent from main's
handler tuple `except (OSError, ValueError, RuntimeError, Refusal, KeyError)` (L652), so the
runner dies with an interpreter traceback and writes no record — the opposite of "retained
mismatch, not a crash". The counter branch has no such surface (every container access is
`isinstance`-gated); `checks`/`cases`/`status`/`failed_checks`/`measured_commit`/
`producer_executions_new_policy`/`inputs_unchanged_during_run` null or wrong-type inputs all
short-circuit `demo_match` to False without crashing. The crash surface is exactly `gate`
and `isolation`. Worth noting for the repair template: the same branch already does
type-strict bool checks via `is` on `inputs_unchanged_during_run` (L466) and
`isolation.cleaned` (L468) — the counter branch is the inconsistent one, not the model.

## Rejected added scope (explicitly NOT findings)

- Splitting `observed_json:null` into parse-error vs JSON-null diagnostics — cosmetic;
  verdict identical. Rejected.
- Producer duplicate keys (`{"admitted_entries":999,"admitted_entries":6}`) — JSON spec
  leaves duplicates undefined; Python last-wins is a defensible contract. Rejected.
- Top-level non-dict expectations / `null` leaves in `expected_summary` — none exist in
  `COUNTER_EXPECTATIONS`; specifying behavior for unshipped shapes is speculative. Rejected
  (Finding 3 specifies only the boundary the repair must preserve).
- Gating `matched` on `matched_expected_fields == expected_field_count` — a possible repair
  shape, not a requirement; the record's counts are informational and Q51 requires exact
  comparison, not a particular mechanism. Not a defect.
- Producer execution authentication, exec-attestation, malicious-producer modeling —
  preregistration disclaims it. Rejected.
- stderr handling on counter steps — already `not stderr` at L445; the admitted stderr
  defect is `kind:"summary"`-only (summary branch never checks stderr, L367–419). Other
  seats own it.

## Draft literal oracle vectors (synthetic counter producer; contract: print JSON to
stdout, set exit code, write stderr)

Positive pair — must remain `matched:true` on base AND repaired runner:

```
# POS-1 (r13-counter-31984f4, exact)  rc=0  stderr=""
{"F2_entry":0,"admitted_entries":4,"evidence_gate":0,"measured_commit":"31984f473ce4bdab61a99b16cca194b28108cb81","sources":33,"tiers":{"A":29,"B":3,"C":1},"statuses":{"mined":16,"queued":15,"rejected":2}}

# POS-2 (r13-counter-b576341, subset + extra null field — subset-extra control)  rc=0  stderr=""
{"measured_commit":"b5763415cc67ecff1e8fe56c58c39a6fb106d7a3","admitted_entries":6,"unexpected_extra":null}
```

Negative vectors — expected `matched:false` with the result record retained and no crash.
Class B (bool/int), F (float/int — same root cause), N (null-container boundary controls),
X (malformed):

```
# NEG-B1 (r13-counter-31984f4)  base TRUE (false green) -> repaired FALSE
{"F2_entry":false,"admitted_entries":4,"evidence_gate":false,"measured_commit":"31984f473ce4bdab61a99b16cca194b28108cb81","sources":33,"tiers":{"A":29,"B":3,"C":1},"statuses":{"mined":16,"queued":15,"rejected":2}}

# NEG-B2 nested-container coercion (r14-counter-a31642d)  base TRUE -> repaired FALSE
# defeats any repair that type-checks top level only
{"measured_commit":"a31642d14006830ec62edf40b0354c3699728c4a","cache_gate":0,"cache_fixture":0,"boundary_fixture":0,"source_rows":37,"tiers":{"A":33,"B":3,"C":1},"statuses":{"mined":20.0,"queued":15,"rejected":2},"admitted_knowledge":5,"held_knowledge":1}

# NEG-F1 float coercion (r13-counter-b576341, subset)  base TRUE -> repaired FALSE
{"measured_commit":"b5763415cc67ecff1e8fe56c58c39a6fb106d7a3","admitted_entries":6.0}

# NEG-N1 null root container (any exact counter)  base FALSE -> must stay FALSE
null

# NEG-N2 empty object / missing keys (r13-counter-b576341)  base FALSE -> must stay FALSE
{}

# NEG-N3 explicit null field vs expected int (r14-counter-552cae4)  base FALSE -> must stay FALSE
{"measured_commit":"552cae4204b3ab818419ad8adbfef3a4da29a3e0","cache_gate":null,"cache_fixture":1,"boundary_fixture":1,"source_rows":40,"tiers":{"A":36,"B":3,"C":1},"statuses":{"mined":23,"queued":15,"rejected":2},"admitted_knowledge":5,"held_knowledge":1}

# NEG-N4 list root container  base FALSE -> must stay FALSE
[1,2,3]

# NEG-X1 malformed stdout (any counter)  base FALSE, no crash -> must stay FALSE, no crash
{"measured_commit":
```

Adjacent routed vectors (Finding 4 — only valid if the oracle covers cache-demo nested
keys; L1 disposition):

```
# CACHE-NEG-GATE-N1  base: interpreter AttributeError, no record -> required: retained matched:false
payload = valid demo payload except  "gate": null          # also "gate": [], "gate": 0
# CACHE-NEG-ISO-N1   base: interpreter AttributeError, no record -> required: retained matched:false
payload = valid demo payload except  "isolation": null     # also "isolation": [], "isolation": "x"
```

## Source-inferred repair sketch for the counter branch (draft only; DraftScalarFix owns)

```python
def strict_json_equal(observed, expected, subset):
    if isinstance(expected, dict):
        if not isinstance(observed, dict):
            return False
        if not subset and set(observed) != set(expected):
            return False
        return all(key in observed and strict_json_equal(observed[key], val, subset)
                   for key, val in expected.items())
    if isinstance(expected, list):
        return (isinstance(observed, list) and len(observed) == len(expected)
                and all(strict_json_equal(o, e, subset) for o, e in zip(observed, expected)))
    if isinstance(expected, bool) or expected is None or isinstance(expected, (int, float, str)):
        return type(observed) is type(expected) and observed == expected
    return observed == expected
```

`type(observed) is type(expected)` rejects `False` vs `0`, `6.0` vs `6`, `null` vs `0`/`""`
in one rule; recursion covers `tiers`/`statuses`; `key in observed` keeps missing-vs-null
distinct; subset mode preserves the extra-fields control (POS-2).

## Verification gaps / provenance

- Source-only review per contract: no acceptance command, oracle, or producer executed;
  all "base TRUE/FALSE" labels are source-inferred, not observed. `xd://lsp` is not a
  mounted device in this session — no LSP diagnostics claimed; call sites traced by reading
  the one named file (counter branch has exactly one caller, `main` L623).
- Baseline authority: `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/
  run-acceptance.py` sha256 `1141839963d04e9e1b968d123fa8ffebeef5d33438537cdc636350c970eeaa2b`;
  predicate block identical to working tree.
- `git status` of the lane was not needed and not taken beyond the named `git show`; no git
  mutation, no installs, no delegation, no writes outside this report.

## Trailers (paths relative to souji-shokunin/)

Sources: census/round-21/run-acceptance.py; census/round-21/step-inventory.json;
census/round-14/cache-demonstration.py; .ufo/waves/round-21/w2/AttackRunnerStepResults.md;
.ufo/waves/round-22/preregistration.txt; corpus/QUALITY.md (Q51).
Attempted-inference rejected: treating `observed_json:null` ambiguity as a defect (verdict
identical — cosmetic); treating `numeric_leaves` bool exclusion as the defect (it is
correctly type-strict; the equality check is the gap).
