STATUS: PASS — the assigned predicate boundary (counter `matched` = `returncode == 0 and not failures and json_match and not stderr`, with `json_match` the bool/int-scalar-equality surface) is repaired in the integrated candidate. Source-only review; nothing executed. Reviewed code is the working-tree `census/round-21/run-acceptance.py` (713 lines, committed at 36c78ba016bb "round-22: enforce typed acceptance results and cache identity"); baseline claims cite `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py` (659 lines), not the changing tree.

Axes named: calibration (verdict truth of `matched`), operability (crash-free rejection of malformed producer data, diagnosable `matched_counts`), coverage (what the predicate can still miss). No axis traded.

# Scope of this seat

Counter predicate boundary: the `kind == "counter"` branch of `summarize_result`, its new shared scalar comparator `json_exact`, and the `returncode`/`stderr` edges of `matched`. Adjacent summary-stderr and cache-identity diff hunks verified only where they share the comparator or guard shape.

# Actual counter expectations located (anchors for the oracle)

`COUNTER_EXPECTATIONS` (new file, lines 120–180; unchanged from baseline) wires 5 counters via `make_steps` (lines 345–352). The four `exact_json: true` rows carry integer gate leaves at their boundary values:

- `r13-counter-31984f4` (inventory `step-inventory.json:207–234`): `F2_entry: 0`, `evidence_gate: 0`, `admitted_entries: 4`, `sources: 33`, `tiers.A: 29, B: 3, C: 1`, `statuses: mined 16, queued 15, rejected 2`, `measured_commit` string.
- `r13-counter-6f8ee0f` (lines 235–262): same shape, `F2_entry: 1`, `evidence_gate: 1` — the True↔1 boundary pair.
- `r14-counter-a31642d` (lines 263–292): `cache_gate: 0`, `cache_fixture: 0`, `boundary_fixture: 0`, `source_rows: 37`, `admitted_knowledge: 5`, `held_knowledge: 1`.
- `r14-counter-552cae4` (lines 293–322): `cache_gate: 1`, `cache_fixture: 1`, `boundary_fixture: 1`, `source_rows: 40`, `tiers.A: 36`.
- `r13-counter-b576341` (lines 323–337): `exact_json: false`, subset expectation `{measured_commit, admitted_entries: 6}`.

Cache-demo identity literals (new lines 182–207): `CACHE_CHECK_NAMES` frozenset of 33 names — verified name-for-name against the producer's `checks` dict literal at `cache-demonstration.py:879–979` (33/33, no missing, no extra); `CACHE_CASE_PHASES` = `("initial-fresh", "unchanged", "dependency-modified", "legacy-no-dependencies")` — verified against the four `make_case("phase", …)` call sites in emitted order (`cache-demonstration.py:595–596, 613–614, 654–655, 794–795`).

# The defect, in-scope, and its repair

Baseline counter gate (base lines 421–445):

```python
if step["exact_json"]:
    json_match = observed == expected            # Python == conflates False==0, True==1, 0.0==0
else:
    json_match = (isinstance(observed, dict)
                  and all(observed.get(key) == value for key, value in expected.items()))
matched = matched and json_match and not stderr
```

Python `==` answers `True` for `False == 0`, `True == 1`, `0.0 == 0`, recursively inside nested dicts. So every integer leaf in the four exact counters — including the boundary `F2_entry: 0`/`evidence_gate: 0` and `cache_gate: 1` triple — accepted a JSON `false`/`true`/`0.0` substitute. `numeric_leaves` excluded the bool leaves from `matched_counts`, but `matched_counts` never gated `matched`, so the step went green (admitted HIGH in `.ufo/waves/round-21/w2/AttackRunnerStepResults.md:5–9`). This is the in-scope defect.

Integrated repair (new lines 373–385, used at 470–476 and 516–518):

```python
def json_exact(observed, expected) -> bool:
    """Compare decoded JSON types and values, including nested scalar leaves."""
    if type(observed) is not type(expected):
        return False
    if isinstance(expected, dict):
        return (observed.keys() == expected.keys()
                and all(json_exact(observed[key], value)
                        for key, value in expected.items()))
    if isinstance(expected, list):
        return (len(observed) == len(expected)
                and all(json_exact(item, value)
                        for item, value in zip(observed, expected)))
    return observed == expected

# counter branch
if step["exact_json"]:
    json_match = json_exact(observed, expected)
else:
    json_match = (isinstance(observed, dict)
                  and all(key in observed and json_exact(observed[key], value)
                          for key, value in expected.items()))
matched = matched and json_match and not stderr
```

Line-by-line, this closes the admitted defect and nothing else:

- `type(observed) is not type(expected)` rejects `bool`-for-`int`, `float`-for-`int`, `null`-for-`int`, `str`-for-`dict` at every depth, before `==` ever runs on a conflatable pair.
- dict recursion via `.keys()` set-equality is order-insensitive (correct JSON-object semantics, identical to baseline `==` shape) and exact on key membership.
- list arm is length- and element-exact; only same-type leaves reach `==`, where `==` is type-correct by construction (`nan == nan` fails closed as a bonus).
- Subset branch keeps `exact_json: false`'s tolerated-extra-keys semantics while enforcing strict types on the expected keys — `r13-counter-b576341`'s `admitted_entries: 6` still tolerates extra fields but rejects `6.0`.
- `returncode` edge unchanged and correct: `matched = returncode == 0 and not failures` (line 408). `OSError` invocation failure records `returncode = None` with diagnostic stderr (lines 671–673), and `None == 0` is False — fail-closed, no crash. `not stderr` on the counter line was already present at baseline; the summary branch now carries the same edge at line 461.

# Literal positive/negative oracle pairs

Anchor counter `r13-counter-31984f4` (exact) and `r13-counter-b576341` (subset). Decisions stated as base → integrated.

Positive P1 (positive control, must stay green): returncode 0, empty stderr, stdout byte-equal to the inventory's expected object — `"F2_entry":0,"admitted_entries":4,"evidence_gate":0,"measured_commit":"31984f473ce4bdab61a99b16cca194b28108cb81","sources":33,"tiers":{"A":29,"B":3,"C":1},"statuses":{"mined":16,"queued":15,"rejected":2}`. Expected: matched in both.

Negative N1 (bool-for-int, the admitted HIGH): P1 with `"F2_entry":false,"evidence_gate":false`. Baseline: `false == 0` twice → `json_match` True, returncode 0, stderr empty → **matched (false green)**. Integrated: `type(False) is not int` → `json_exact` False → **unmatched**. This is the scalar-equality defect repaired.

Negative N2 (nested bool leaf): `r14-counter-552cae4` expected with `"cache_gate":true` (top level, `true`≈1) or `r13-counter-31984f4` with `"tiers":{"A":29,"B":3,"C":true}` (nested, `true`≈1). Baseline: **matched**. Integrated: `json_exact` descends into `tiers` and type-checks `C` → **unmatched**.

Negative N3 (float-for-int, same defect family): P1 with `"admitted_entries":4.0`. Baseline: `4.0 == 4` → **matched**. Integrated: `float is not int` → **unmatched**. "JSON scalar type equality" covers this; it was silently co-admitted at baseline and is correctly co-repaired.

Negative N4 (subset step): `r13-counter-b576341`, expected `{measured_commit, admitted_entries: 6}`, stdout `{"measured_commit":"b5763415…","admitted_entries":true,"extra":42}`. Baseline: `true == 6` is False → unmatched either way; retarget the leaf to `{"admitted_entries":6.0}` → baseline `6.0 == 6` **matched**, integrated **unmatched**. Extra `extra: 42` correctly stays tolerated under `exact_json: false`.

Negative N5 (returncode/stderr edges): (a) same stdout as P1, returncode 1 → unmatched both revisions (`returncode == 0`); (b) returncode 0, stdout P1, stderr `"warning: fallback path"` → unmatched both revisions (`not stderr`); (c) unparseable stdout `"not json"` → `observed = None`, `json_exact(None, dict)` False → unmatched, no exception. All unchanged-boundary behavior, confirmed fail-closed in the new source.

Draft synthetic-vector skeleton for the round-22 oracle fixture (positive + one negative per conflation class):

```python
# expects summarize_result(step, returncode, stdout_bytes, stderr_bytes, revision, root)
vec = dict(name="r13-counter-31984f4", argv=[], expected_summary=EXPECTED_31984F4,
           exact_json=True, kind="counter")
P1 = (vec, 0, EXPECTED_JSON_BYTES, b"")          # matched True
N1 = (vec, 0, EXPECTED_JSON_BYTES.replace(b'"F2_entry":0', b'"F2_entry":false'), b"")
N2 = (vec, 0, EXPECTED_JSON_BYTES.replace(b'"C":1', b'"C":true'), b"")
N3 = (vec, 0, EXPECTED_JSON_BYTES.replace(b'"admitted_entries":4', b'"admitted_entries":4.0'), b"")
N5 = (vec, 1, EXPECTED_JSON_BYTES, b"")          # returncode edge
```

# Adjacent changes sharing the boundary (verified, no defect found)

- Summary branch `not stderr` (new line 461): closes the admitted stderr false-green. Integration-watch item only: if any of the 18 real producers emits informational stderr, this tightens green→red — that is the intended recalibration; L1's acceptance run is the check, not a source defect.
- `isinstance(gate, dict)` / `isinstance(isolation, dict)` guards (new lines 498–499, 520–522): baseline `payload.get("gate", {}).get("sha256")` crashed with `AttributeError` on `"gate": null` (the dict exists, the value is null) — now cleanly `demo_match` False → recorded fail. Also fixes baseline's `isolation.get("cleaned")` crash on `"isolation": null`. This is the "reject malformed producer data without a crash" requirement realized at the two real crash sites.
- `try/except ValueError` around `int(baseline_match.group(group))` (new lines ~426–430): dead-safe — the regex group is `(\d+)` and cannot fail `int()` — but converts a hypothetical crash into a recorded fail; harmless hardening, in the spirit of the claim.
- Cache identity (`checks.keys() == CACHE_CHECK_NAMES`, `case_phases == list(CACHE_CASE_PHASES)`, plus `len(...) == expected[...]` self-consistency guards, lines 502–523): closes the counted-not-identified MEDIUM. `matched_counts.matched_gate_checks` now counts only named checks — diagnostics consistent with the gate.
- `json_exact` applied to `failed_checks`/`producer_executions_new_policy` (lines 516–518): `[]` vs `[false]` and `3` vs `3.0`/`true` conflations closed.

# Distinguishing in-scope defect from rejected added scope — correctly held

- No step keys added → `inventory_projection` (new lines ~592–606, unchanged) still equals the frozen r20 `step-inventory.json`; all 18 original positive controls retained verbatim; `EXPECTED_COMMANDS`/5-counter inventory guard unchanged. Rejected scope: editing the frozen inventory or re-deriving check names — held; names are pinned literals with a comment (`# Do not derive these expectations from the producer being graded`).
- Producer-faithfulness beyond structure (e.g., `producer_executions_new_policy: 3` is still producer-attested): correctly not claimed — preregistration disclaims "arbitrary malicious-producer attestation or executed-command authentication."
- No subprocess timeout on the 18 steps, unbounded stdout/JSON size, `json.loads` non-strict constants (`NaN`/`Infinity`, duplicate keys), `RecursionError`→Refusal exit-2 on deeply nested payloads: all baseline-identical residual limits; none can produce a false green under `json_exact` (NaN≠NaN, `inf` type-fails ints, dup-keys fold before comparison, recursion aborts to refusal not green). Not in the claim; appropriately not touched.
- `numeric_leaves`/`matched_counts` remain informational (bool and float leaves excluded from numeric maps): no longer a false-green path now that `json_match` is type-strict; counts are diagnostic color only. Changing them would be added scope — correctly left.
- Deeper `cases[]` row content beyond `phase` is producer-internal detail: pinning phase identity answers the admitted "counted rather than identified" defect; binding every row field would be new claim — correctly not made.

# Findings by severity

None actionable in scope. The three admitted predicate defects are each closed at source on this boundary; no new defect introduced by the diff was found.

# Residual risk

- Source-inferred only: `json_exact` decisions are reasoned from predicate source, never observed. [INFERENCE] until L1's synthetic-oracle run.
- `not stderr` tightening on 12 summary steps could red a producer that legitimately logs to stderr; that is calibrated behavior, flagged for L1's green run.
- `json_exact` recursion on adversarially deep JSON raises `RecursionError` → main's `except ... RuntimeError` → Refusal, exit 2, no record — aborts the whole acceptance rather than failing one step; acceptable, unchanged class of behavior.
- `payload.get("measured_commit") == revision` and `status` remain `==` on strings — safe (no scalar conflation possible against string literals).

# Verification gaps

- No execution, no tests, no probes per contract; every verdict above is source-verified.
- `xd://lsp` is not mounted in this session (no device in inventory); caller/definition checking done by direct reading of the single file — `json_exact` call sites are lines 471, 475, 516–518; `summarize_result` sole caller line 677; all intra-file and confirmed.
- Working tree is clean at 36c78ba; baseline comparisons used `git show 41553adb139d06511dc386bb3ce4326aebfba675:…` per coordinator directive.
- No tools installed (all pacman transactions paused; nothing needed).
- Scratch diff artifacts written only under `/var/tmp` and removed.

# Report trailers

- Named files read: census/round-21/run-acceptance.py (base via git show + integrated working tree), census/round-21/step-inventory.json, census/round-14/cache-demonstration.py, .ufo/waves/round-21/w2/AttackRunnerStepResults.md, .ufo/waves/round-22/preregistration.txt, corpus/QUALITY.md.
- Report: .ufo/waves/round-22/w1/Counter18.md
