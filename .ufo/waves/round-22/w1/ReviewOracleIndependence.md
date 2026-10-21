STATUS: PASS — independent oracle designed before opening the implementation; all three repaired predicates match the pre-locked vectors; base 41553adb confirmed to carry all three admitted false greens, so every red control is base-discriminating; no red control is regenerable from the implementation. Source-only seat: nothing was executed.

# ReviewOracleIndependence — round22 C1 calibration, oracle independence seat

Claim under review (preregistration C1): strengthen the acceptance summarizer against the three admitted OPEN r21 predicate defects — JSON bool/int scalar confusion; summary stderr accepted despite success; cache checks counted rather than identified — with literal independently reviewed decision vectors, all 18 positive controls retained, malformed producer data rejected without a crash.

## Method and ordering (oracle-first)

The decision vectors below were fixed from four sources before `census/round-21/run-acceptance.py` was opened in this session:

1. `.ufo/waves/round-22/preregistration.txt` — claim scope, "literal independently reviewed vectors", malformed-data rejection, source authority (Python JSON decoder conversion doc; bool subclass/equality semantics).
2. `.ufo/waves/round-21/w2/AttackRunnerStepResults.md` — the independent adversarial finding set that defined the three defects (counter `observed == expected`; summary branch without stderr gate; cache count-only).
3. `census/round-21/step-inventory.json` — frozen expectations: 18 steps; four `exact_json: true` counters with int leaves (`F2_entry: 0`, `evidence_gate: 0`, `tiers.C: 1`, …); cache-demo row `cases=4, checks=33, failed_checks=[], producer_executions_new_policy=3`; one retained `exact_json: false` counter (`r13-counter-b576341`).
4. `census/round-14/cache-demonstration.py` (producer bytes) — the independent identity ground truth: 33 literal check names (counted from the `checks = {…}` literal, producer lines 879–934) and 4 ordered case phases (`initial-fresh`, `unchanged`, `dependency-modified`, `legacy-no-dependencies`; appends at producer lines 594/612/653/793), top-level `isolation.cleaned` inside the `isolation` dict, `inputs_unchanged_during_run` top-level, `status = "ok" if all(checks.values()) else "red"`.

The changed implementation was read only after the vectors were locked; base bytes were read on parent instruction via `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py` (659 lines).

## Independent oracle vectors (locked before implementation read)

Decision rule under test: per-step `matched`, and therefore `all_matched`. All vectors are constructed from committed fixture material only (inventory rows + producer contract); none uses implementation internals.

### V — exact-JSON bool/int scalar controls (claim 1)

Discriminating requirement: base `==` semantics (Python `False == 0`, `True == 1`) must be GREEN (the admitted false green); changed must be RED.

| id | step | mutation of genuine output | base expected | changed expected |
|---|---|---|---|---|
| V1 | r13-counter-31984f4 | `F2_entry: false`, `evidence_gate: false` (expected ints 0) | GREEN (false green) | RED |
| V2 | r13-counter-31984f4 | `tiers.C: true` (expected int 1) | GREEN (false green) | RED |
| V3 | r13-counter-6f8ee0f | `F2_entry: true`, `evidence_gate: true`, `tiers.C: true` (expected ints 1) | GREEN (false green) | RED |
| V4 | r14-counter-a31642d | `cache_gate: false`, `cache_fixture: false`, `boundary_fixture: false`, `held_knowledge: true` | GREEN (false green) | RED |
| V5 | r14-counter-552cae4 | `cache_gate: true`, `cache_fixture: true`, `boundary_fixture: true` | GREEN (false green) | RED |

Scope note locked in advance: claim scope is bool/int confusion; exact float/int discrimination (`1.0` vs `1`) is a permitted superset, not a pass requirement. `r13-counter-b576341` (`exact_json: false`) has no expected 0/1 leaf, so it carries no bool-discriminating vector; its per-field comparison must still reject a missing key and a wrong value.

### S — summary stderr controls (claim 2)

| id | step | mutation of genuine output | base expected | changed expected |
|---|---|---|---|---|
| S1 | auditor-selftest | rc 0, stdout exactly `SELFTEST\tpass=118\tfail=0` + 118 `PASS\t` lines, stderr = `ERROR: self-test could not complete` | GREEN (false green) | RED |
| S2 | any summary step | stdout genuine, stderr = `"\n"` (nonempty, no diagnostic content) | GREEN (false green) | RED |
| S3 | landing-gate-selftest | stdout genuine, stderr = `WARNING: degraded` (non-FAIL vocabulary text) | GREEN (false green) | RED |
| G1 | all 13 summary steps | genuine stdout, stderr exactly empty | GREEN | GREEN (positive control retained) |

The rule, fixed in advance: any stderr with length > 0 must be RED for `kind: summary`, regardless of content vocabulary; only `""` is GREEN. (Failure-marker vocabulary on stdout remains a separate, retained red path.)

### W — cache check-identity controls (claim 3)

All keep `len(checks) == 33`, every value `True`, `len(cases) == 4`, status/commit/gate/isolation fields genuine.

| id | mutation | base expected | changed expected |
|---|---|---|---|
| W1 | rename `legacy_fresh_digests` → `legacy_digests_fresh` (33 names, all true) | GREEN (false green) | RED |
| W2 | drop `isolation_confined`, add `extra_check` (33 names, all true) | GREEN (false green) | RED |
| W3 | case phases permuted (`unchanged` first) or one phase renamed | GREEN (false green) | RED |
| W4 | `producer_executions_new_policy: true` (bool, expected int 3) | GREEN (false green; `True == 3` is False — value red, so W4 is red-on-base too; the bool-typed strictness is additional, not discriminating) | RED |
| G2 | genuine producer payload (33 exact names, 4 exact ordered phases, all fields genuine) | GREEN | GREEN (positive control retained) |
| G3 | count controls retained: 32 checks / one check `false` / `failed_checks` nonempty / `status: "red"` | RED | RED (existing predicate preserved) |

### M — malformed producer data (no crash)

| id | input | base expected | changed expected |
|---|---|---|---|
| M1 | cache stdout not JSON (truncated) | RED, no traceback | RED, no traceback |
| M2 | counter stdout = `[1, 2]` (array, not object) | RED | RED |
| M3 | cache `checks` a JSON list, not object | RED | RED |
| M4 | counter exact-JSON observed `null` | RED | RED |

Crash rule: a malformed step yields a per-step RED decision inside the normal record; the runner must not exit via an unhandled exception path.

## Implementation comparison (evidence chain)

Changed file: working-tree `census/round-21/run-acceptance.py` (713 lines) as captured during this session's reads; L1 integration was in flight, so line numbers are cited from that capture. Base: `git show 41553adb…` line numbers exact.

**Claim 1 — JSON scalar type equality.** Changed adds `json_exact` (capture L373–391): `type(observed) is not type(expected) → False`, recursive over dicts (key-set equality) and lists, scalar `==` only within an identical type. Counter exact branch gates on it: `matched = matched and json_match and not stderr` (capture L490); counts remain diagnostic only (`matched_counts`, capture L478–489), closing the r21 gap where counts did not gate. Base L427 is `json_match = observed == expected` — `False == 0`/`True == 1` compare equal, so V1–V5 are base-GREEN, changed-RED exactly as the oracle requires. The non-exact branch changed from `observed.get(key) == value` (base L430–431) to `key in observed and json_exact(observed[key], value)` (capture, counter branch) — per-field type discipline; b576341's two fields remain value-checked. `numeric_leaves` still excludes bools (capture L407–419), so diagnostics cannot launder a bool back into a numeric match.

**Claim 2 — summary stderr.** Changed summary gate: `matched = matched and summary_match and pass_match and not stderr` (capture L461). Base L417 has the same expression without `and not stderr` — S1–S3 are base-GREEN, changed-RED; G1 stays GREEN. Counter and cache branches retain `and not stderr` (capture L490, L534; base L445, L480), so the strictness is now uniform across kinds without weakening anything.

**Claim 3 — cache check identity.** Changed gates (capture L505–524): `checks.keys() == CACHE_CHECK_NAMES` (L514) with a literal 33-name `frozenset` (L184–203), `case_phases == list(CACHE_CASE_PHASES)` (L511) over the literal ordered 4-phase tuple (L204–206), `all(value is True …)` (L515), `json_exact` on `failed_checks` and `producer_executions_new_policy` (L516–518), `inputs_unchanged_during_run is True` (L519), `gate.sha256 == gate_sha` (measured gate bytes), `isolation.cleaned is True` and `isolation.residue == []` (L521–523). Base L456–470 checks only counts (`len(case_rows) == 4`, `len(checks) == 33`, values `is True`) — W1–W3 are base-GREEN, changed-RED; G2/G3 hold. I independently derived the 33 names and 4 phases from producer bytes before opening the runner; the runner's literals match my derivation name-for-name (set-equal, order-equal for phases). The runner's own comment (capture L182–183) states the expectations are "separate from the frozen r20 inventory" and not derived from the producer being graded.

**Malformed data.** Both versions guard `json.loads` (base L421–424/L447–450; capture L465–468/L492–495) and all downstream access with `isinstance` checks; M1–M4 produce per-step RED in both. Incidental hardening, outside the three claims: base L385 `int(baseline_match.group(group))` could raise into the runner's refusal path (exit 2, no record); the capture wraps it and marks the step RED instead (capture L345–351). No positive control is affected: genuine output always supplies the digit group.

**Positive controls retained.** All 18 steps are present with unchanged expected summaries/patterns/counts (capture `make_steps`, L296–356 region; `EXPECTED_COMMANDS = 18` L30; `len(COUNTER_EXPECTATIONS) != 5` refusal L648 region), and `inventory_projection(…) != frozen["steps"]` refuses drift against `step-inventory.json` — the same frozen file this oracle read independently. The repaired predicates only add constraints that genuine outputs satisfy (int leaves decode as JSON ints; genuine stderr is empty; the producer emits exactly the 33 names and ordered phases).

## Red-control independence (cannot be regenerated from implementation)

- Every expected decision above is a literal derived from claim semantics + frozen inventory + producer contract, fixed before the implementation was opened in this session; the base-side GREEN expectations come from base predicate bytes (`==` at L427; no stderr gate at L417; count-only at L456–470), not from the changed code.
- All runner-side expectations remain literals: `COUNTER_EXPECTATIONS` tuples, `CACHE_CHECK_NAMES`, `CACHE_CASE_PHASES`, per-step `expected_summary`. The decision path compares observed bytes/JSON against those literals; no expectation is computed from the implementation's own output, no double-execution/self-diff oracle, no producer callback.
- The single computed expectation is `gate_sha = sha256(tools/souji-evidence-cache.py)` from the measured clone tree (capture L501). This binds the payload's gate claim to measured input bytes; it is input-bound, not output-derived, and identical in base (L454). Disclosed, not a tautology.
- A fixture that regenerated expectations by executing the graded summarizer (or by diffing base vs changed) would be self-oracular; the vectors above are expressible without any runner invocation, which is the property this seat was asked to establish.

## Red-control draft (fenced, NOT executed — draft only)

```python
# Draft literal vectors for the committed synthetic result-oracle fixture.
# Decisions are per-step `matched`; "genuine" = the pinned fixture's real output.

V1 = {"op": "json-substitute", "step": "r13-counter-31984f4",
      "sub": {"F2_entry": False, "evidence_gate": False},
      "expect": {"base_41553adb": "GREEN", "changed": "RED"}}
V3 = {"op": "json-substitute", "step": "r13-counter-6f8ee0f",
      "sub": {"F2_entry": True, "evidence_gate": True, "tiers": {"C": True}},
      "expect": {"base_41553adb": "GREEN", "changed": "RED"}}
S1 = {"op": "stderr-inject", "step": "auditor-selftest",
      "stdout": "SELFTEST\tpass=118\tfail=0\n" + "PASS\tcase-%d\n" * 118,
      "stderr": "ERROR: self-test could not complete", "returncode": 0,
      "expect": {"base_41553adb": "GREEN", "changed": "RED"}}
S2 = {"op": "stderr-inject", "step": "landing-gate-selftest",
      "stderr": "\n", "expect": {"base_41553adb": "GREEN", "changed": "RED"}}
W1 = {"op": "check-rename", "step": "clean-cache-demonstration",
      "from": "legacy_fresh_digests", "to": "legacy_digests_fresh",
      "expect": {"base_41553adb": "GREEN", "changed": "RED"}}
W2 = {"op": "check-swap", "step": "clean-cache-demonstration",
      "drop": "isolation_confined", "add": "extra_check",
      "expect": {"base_41553adb": "GREEN", "changed": "RED"}}
W3 = {"op": "phase-permute", "step": "clean-cache-demonstration",
      "phases": ["unchanged", "initial-fresh", "dependency-modified",
                 "legacy-no-dependencies"],
      "expect": {"base_41553adb": "GREEN", "changed": "RED"}}
M1 = {"op": "stdout-truncate", "step": "clean-cache-demonstration",
      "expect": {"base_41553adb": "RED-no-crash", "changed": "RED-no-crash"}}
G  = {"expect": "all 18 genuine fixture outputs stay GREEN on changed"}
```

## Divergences and bounded findings

1. **Residual limit, within claim scope (disclosed):** cache case-row *contents* (`gate_exit`, `reusable`, `executions_after`, retained origins) are still not graded; the repair identifies check names and case phases, which is what C1 claims ("checks counted rather than identified"). Deep case-content grading remains unclaimed, consistent with "no arbitrary malicious-producer attestation is claimed".
2. **Superset strictness (harmless):** `json_exact` also rejects float-for-int (`1.0` vs `1`) and requires exact key sets; no committed expectation involves floats, so no positive control regresses. Above claim minimum, disclosed.
3. **Boundary choice (matches oracle):** whitespace-only stderr (`"\n"`) is RED under the changed gate; the oracle's S2 pre-locked that reading. Genuine tool runs must write nothing to stderr — the operative behavioral change L1's acceptance run will exercise.
4. **Incidental hardening (outside claims, kept):** malformed `baseline_mismatch_group` now yields per-step RED instead of a runner-level refusal (base L385 vs capture L345–351). No effect on the 18 controls.
5. **b576341** carries no bool-discriminating leaf (no expected 0/1); its retention as `exact_json: false` with per-field type-checked comparison is unchanged behavior, verified compatible with `json_exact`.

## Process record

- No tools installed or updated (none needed). No tests, builds, formatters, or probes executed; every statement above is source-inferred from the six named files plus the parent-authorized `git show` of the base runner. L1 runs the acceptance.
- Reads: preregistration.txt; AttackRunnerStepResults.md; step-inventory.json; cache-demonstration.py (targeted ranges); corpus/QUALITY.md; working-tree run-acceptance.py (captured mid-integration); `git show 41553adb…:census/round-21/run-acceptance.py` (exact base bytes). No lane/fleet/census-root directory reads; no broad grep/glob; no writes except this report.
- Caveat: changed-file line numbers reflect the working tree as captured during this session's reads; if L1's integration lands further edits, re-check line anchors but the predicate symbols cited (`json_exact`, `CACHE_CHECK_NAMES`, the three `matched =` gates) are the reviewed content.

Confidence: high on claims 1–3 predicate equivalence and base discrimination (both sides read at exact bytes); high on oracle independence (pre-locked vectors, literal expectations, no self-oracle path); historical outcome projections are inventory-pinned and verified structurally (projection-vs-frozen refusal), not executed.
