STATUS: PASS — counter predicate boundary analysis complete. The `returncode` leg of the
counter predicate is correct and needs no repair; the in-scope defect at this boundary is
the leaf-level `==` scalar-type coercion in both counter comparison branches (exact and
subset), which admits `false`/`true`/`6.0`/`-0.0` for integer expectations. Literal
positive/negative oracle vectors drafted below. All findings are source-inferred from the
named pinned files; nothing was executed.

Axes in play (round-22 claim C1): calibration (primary — this slice), operability (repair
must not break the frozen inventory check or the subset counter's tolerated extra keys),
coverage (literal vectors extend the admitted defect to the subset branch). No trade taken;
no axis harmed.

## 0.5. Baseline grounding (re-verified after parent directive)

All line numbers cited below are **base-blob lines**: base
`41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py`, blob
sha256 `1141839963d04e9e1b968d123fa8ffebeef5d33438537cdc636350c970eeaa2b`. Every
cited line was re-verified verbatim against that blob (source-only `git show`,
no execution). The working-tree runner now differs (sha
`02e3b06dad7421d43f27b87a41568e6577c1ad64a89a933dc12ee8408f4bc32c`): it carries
the r22 integration — a `json_exact` typed-leaf comparator applied to BOTH
counter branches, `and not stderr` added to the summary branch, named
`CACHE_CHECK_NAMES`/`CACHE_CASE_PHASES` identity for the cache-demo, and a
`ValueError` guard on the baseline-mismatch `int()` — matching the repair shape
drafted in §5. `step-inventory.json` is byte-identical at base and in the tree
(sha `8b7b1cd8d19561d9f4e8f06e797038b03379350cb3f3932edf04bda7aa7d1310`), so the
expectation literals in §2 hold on both sides. Each §5 vector's base verdict is
the defect evidence; its integrated verdict is stated, source-derived, not run.

## 1. Counter predicate boundary, as pinned

`census/round-21/run-acceptance.py`, `summarize_result`:

- Line 367 (pre-dispatch, every kind): `matched = returncode == 0 and not failures`.
- Lines 420–445 (counter branch):
  - 421–424: `json.loads(stdout)` → `observed`, `None` on `ValueError`/`TypeError`.
  - 426–428: `exact_json` → `json_match = observed == expected`.
  - 429–431: non-exact → `json_match = isinstance(observed, dict) and all(observed.get(k) == v for k, v in expected.items())`.
  - 433: `numeric_leaves` feeds `matched_counts` (informational only; `int` test at 342 already excludes `bool` — so booleans/floats silently drop out of the observed numeric-field count, revealing but never gating the anomaly).
  - 445: `matched = matched and json_match and not stderr`.
- Lines 613–619: `returncode` is `proc.returncode` (int) or `None` on `OSError`, which also
  injects synthetic stderr `"invocation failed: ..."` — the None path is rejected twice
  (`None == 0` is False; `not stderr` is False).

## 2. Located actual counter expectations (ground truth for vectors)

`COUNTER_EXPECTATIONS` (run-acceptance.py:120–180) and the frozen
`census/round-21/step-inventory.json` rows agree byte-for-byte on values (verified against
step-inventory.json:207–337):

| step | exact_json | notable expectation |
|---|---|---|
| `r13-counter-31984f4` | true | `F2_entry: 0`, `admitted_entries: 4`, `evidence_gate: 0`, `measured_commit: 31984f4...`, `sources: 33`, tiers A29/B3/C1, statuses 16/15/2 |
| `r13-counter-6f8ee0f` | true | `F2_entry: 1`, `admitted_entries: 5`, `evidence_gate: 1`, `measured_commit: 6f8ee0f...`, `sources: 37` |
| `r14-counter-a31642d` | true | `cache_gate: 0`, `cache_fixture: 0`, `boundary_fixture: 0`, `measured_commit: a31642d...` |
| `r14-counter-552cae4` | true | `cache_gate: 1`, `cache_fixture: 1`, `boundary_fixture: 1`, `measured_commit: 552cae4...` |
| `r13-counter-b576341` | **false** | `measured_commit: b576341...`, `admitted_entries: 6` (subset semantics: extra keys tolerated by design) |

Inventory constraint on any repair: `expected_summary` and `exact_json` are projected into
the frozen inventory rows (run-acceptance.py:542–543) and must equal
`step-inventory.json` or the runner refuses at line 601–602. **The fix may only change
comparison logic — never expectation values, never the `exact_json` flags.**

## 3. Finding: returncode leg is NOT the defect (boundary verified clean)

At the counter predicate boundary, "wrong returncode" is already fail-closed in every
combination:

- rc nonzero (`1`, `2`, signal `-15`) + byte-exact JSON + empty stderr → `matched=false`.
- rc `0` + exact JSON + empty stderr → `matched=true` (only correct green).
- rc `None` (OSError, lines 617–619) → rejected by `None == 0` and by injected stderr.
- `json.loads` on empty/garbage stdout → `observed=None` → `None == dict` is False → reject
  (malformed producer data already rejected without a crash, satisfying that prereg clause).

Rejected added scope at this boundary — these MUST NOT be claimed or smuggled in:

- **Per-step expected-returncode tables.** No step parameterizes an expected rc; every
  step's contract is rc==0. Inventing a nonzero "accepted refusal" rc for a counter would
  change frozen-inventory semantics and exceeds the three admitted defects.
- **Signal-returncode special-casing** (`-15` etc.): already rejected by `== 0`; interpreting
  them is scope, not repair.
- **Execution timeouts / hang bounds** on the counter `subprocess.run` (614): a hung
  counter blocks the run (no false-green possible, but unbounded). This is real residual
  risk, owned by the Q30/Q34 timeout lane — name it, don't repair it here.
- **Executed-command authentication / producer attestation**: explicitly excluded by the
  round-22 preregistration.
- **Widening the JSON parser gate**: Python `json.loads` accepts non-standard `NaN`/
  `Infinity`/`1e999`; all fail `==` against integer expectations, so it is non-admitting.
  Tightening the decoder is optional hardening, not a required fix.

## 4. In-scope defect at the boundary: scalar-type `==` (both branches)

The admitted OPEN r21 defect ("JSON bool/int scalar confusion"; `.ufo/waves/round-21/w2/
AttackRunnerStepResults.md` lines 5–9 demonstrated it for `exact_json` only) is a leaf-equality
boundary defect, and it exists identically in the **subset branch** (line 431) — a new
observation, same mechanism:

- `False == 0`, `True == 1` → `r14-counter-a31642d` `cache_gate: 0` accepts JSON `false`;
  `r14-counter-552cae4` `cache_gate: 1` accepts `true`.
- `6.0 == 6`, `-0.0 == 0`, `4.0 == 4` → float leaves admitted too. For `r13-counter-b576341`
  (`admitted_entries: 6`, exact_json=false) a bool cannot pass (`True == 6` is False) but
  `6.0` does — the subset branch false-greens via float.
- Whether float admission is inside the claim is L1's call: the goal line says "JSON scalar
  type equality" (broad), the preregistration literally names "JSON bool/int scalar
  confusion" (narrow). Recommended: include one float vector as cheap coverage; do not let
  its verdict gate the claim either way.
- `numeric_leaves` (336–344) already excludes `bool` and `float` leaves → `matched_counts.
  matched_expected_fields` would visibly drop for these inputs, but lines 435–445 make that
  count informational only — the anomaly is observable, never gating. The repair should
  close the leaf-equality hole; making the counts gate `matched` is a reasonable tightening
  but must keep `historical_counter_records`/`expected_field_count` projections stable.

Counter-branch stderr boundary is already correct (`and not stderr`, line 445) — the
admitted stderr defect (AttackRunnerStepResults §HIGH-2) is summary-branch-only. Counter
vectors can carry a non-empty-stderr row as a non-discriminating control.

## 5. Drafted literal positive/negative pair (synthetic result-oracle vectors)

Values below are literal, independently checkable against §2; `matched` verdicts are derived
from the pinned predicate source, not executed.

```text
# POSITIVE — must remain matched=true before AND after repair (positive control)
step: r13-counter-31984f4   returncode: 0   stderr: ""
stdout: {"F2_entry": 0, "admitted_entries": 4, "evidence_gate": 0,
         "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81",
         "sources": 33, "tiers": {"A": 29, "B": 3, "C": 1},
         "statuses": {"mined": 16, "queued": 15, "rejected": 2}}

# NEGATIVE-A — wrong returncode boundary (NON-discriminating: red before AND after;
#              regression control proving the rc leg stays closed)
step: r13-counter-31984f4   returncode: 2   stderr: ""   stdout: <identical to positive>
→ matched=false (line 367). Variant: returncode=None (OSError) → false.

# NEGATIVE-B — in-scope discriminating, exact branch bool/int (FALSE GREEN today)
step: r13-counter-31984f4   returncode: 0   stderr: ""
stdout: same dict, with "F2_entry": false and "evidence_gate": false
→ BASE (line 427 `observed == expected`): False == 0 → matched=true (FALSE GREEN — admitted defect)
→ INTEGRATED (`json_exact` type gate): matched=false (source-derived, not run)

# NEGATIVE-C — discriminating on subset branch, newly demonstrated here
step: r13-counter-b576341   returncode: 0   stderr: ""
stdout: {"measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3",
         "admitted_entries": 6.0, "unexpected_extra": true}
→ BASE (line 431 `==` subset): 6.0 == 6, extra keys tolerated → matched=true (FALSE GREEN)
→ INTEGRATED (`key in observed and json_exact`): type(6.0) mismatch → matched=false;
  float admission is therefore closed by the integrated repair regardless of claim wording.
# Keep-control: same stdout with "admitted_entries": 6 and the extra key → matched=true
# before AND after — repair must NOT tighten subset to exact (operability constraint).

# NEGATIVE-D — counter stderr boundary (NON-discriminating control; already red)
step: r13-counter-6f8ee0f   returncode: 0   stdout: <exact expected dict>
stderr: "warning: deprecated counter argument\n"
→ matched=false via `and not stderr` (line 445) on BASE and INTEGRATED alike.
```

Repair shape implied by the boundary (for the drafter's seat, not implemented here):
recursive typed equality on expected-vs-observed leaves (`type(obs) is type(exp)` before
`==`, or an explicit `int`-not-`bool`/no-float leaf check), applied to both the exact
dict compare and the subset `all()` loop, preserving: dict-order insensitivity, subset
extra-key tolerance for `exact_json=false`, `observed` non-dict rejection, `not stderr`,
and the unchanged expectation literals/flags.

## 6. Residual risk and verification gaps

- Source-only seat: no runner, counter, or oracle executed; all `matched` verdicts are
  predicate-source-derived. `xd://lsp` is not a mounted device; no LSP results claimed,
  no grep substitute used — the single named runner was read directly per contract.
- Unbounded `subprocess.run` (line 614): a hung counter yields no result at all — residual
  risk, not a predicate defect; belongs to the timeout axis lane.
- `numeric_leaves` drops bool/float leaves, so the counts view under-reports the anomaly it
  reveals; whether the repaired runner makes that count gating is a drafter decision.
- Tools installed: none. Fleet/census/glob/grep surfaces untouched; only the six named
  files were read.
