# Attack27 — scalar/r13-counter-31984f4/tiers.C/bool

Seat: SoujiR22.Attack27 (scout, leaf, source-only). Target code: `4f83fd222ffbd8825340221a8c426550ef891191`; base: `41553adb139d06511dc386bb3ce4326aebfba675`.

## STATUS

**PASS, source-only.** The expected decision `want=False` is correct. The fixture really does feed a decoded `bool` `True` into `tiers.C`, with no other reason to reject. The changed predicate rejects the vector only through the nested type-identity check. The base predicate accepts it (`True == 1`), so this vector tells the base and changed code apart. The paired positive is accepted by both. I found no concrete mismatch in the code or the oracle for this vector.

Evidence is limited to reading source, `git show`/`git diff`/`git log` of the named paths, `sha256sum`, and the two live documentation pages. I did not run the oracle or the acceptance step. The observed outcomes below are derived by tracing the source, not executed (`[INFERENCE]` from source). No tools were installed or updated.

## Axes

- Calibration (the claimed axis): the vector's literal decision, input fidelity, and the predicate's verdict.
- Operability and coverage (must do no harm): the paired positive still passes; no regression on real output.

## 1. Stored delta and its reconstruction (done before reading the predicate)

Binding checks (observed with `sha256sum`):

- `census/round-21/final-out-S1.json` = `bc53a752…38fe`, which equals `source_receipt_sha256` (oracle json line 4).
- `census/round-21/step-inventory.json` = `8b7b1cd8…1310`, which equals `frozen_inventory_sha256` (line 6).
- The working-tree `run-acceptance.py` = `00d0e9c2…80a6`, which equals `git show 4f83fd2:` of the same path.
- The working-tree oracle json = `292442a6…0651`, which equals the version at `4f83fd2`.

Stored vector (oracle json lines 3154–3168):

```json
{"id": "scalar/r13-counter-31984f4/tiers.C/bool", "want": false, "group": "scalar",
 "step_name": "r13-counter-31984f4", "json_set": [[["tiers","C"], true]]}
```

It has no `returncode`, `stderr` or `stdout` overrides, so the public record's values are used.

Public original record (`final-out-S1.json` lines 3598–3621, under `commands`):

- `returncode` is 0 and `stderr` is `""` (lines 3617–3618).
- `stdout` (line 3620) is `{"F2_entry": 0, "admitted_entries": 4, "evidence_gate": 0, "measured_commit": "31984f47…cb81", "sources": 33, "statuses": {"mined": 16, "queued": 15, "rejected": 2}, "tiers": {"A": 29, "B": 3, "C": 1}}\n`.
- The record's own `matched` is `true`.

Frozen inventory (`step-inventory.json` lines 207–233): `expected_summary.tiers.C` is the integer `1`, `exact_json` is `true`, and `kind` is `"counter"`. This agrees with `COUNTER_EXPECTATIONS` in `run-acceptance.py` lines 121–131.

Reconstruction: the original leaf `tiers.C` is the JSON integer `1`, which decodes to `int` `1`. The delta swaps in the JSON literal `true`, which decodes to `bool` `True`. That is the one adversarial bool value numerically equal to the original. The sibling bool vectors follow the same rule: `F2_entry/bool` and `evidence_gate/bool` use `false` because their originals are `0` (lines 3040–3051 and 3082–3093). Only fields whose value is 0 or 1 can carry a value-equal bool, and all three such fields in this step have one. `tiers.C/bool` is the only nested (depth-2) bool vector for this step. The delta is minimal, faithful and correctly targeted.

### Expected decision

`want=False` is correct. The oracle contract (oracle json line 8) says it must "Reject … decoded wrong scalar types". The inventory declares an `int`, and the input supplies a `bool`. The preregistration (line 1) names "JSON bool/int scalar confusion" as an admitted defect.

### Does the fixture feed this input?

Yes. Tracing `tests/fixtures/r22-result-oracle.py`:

1. Lines 58 and 67–68 take the record's `stdout` from `receipt['commands']`.
2. Lines 72–82 apply the delta: `payload = json.loads(stdout)`, then `at = payload["tiers"]`, then `at["C"] = True`, then `stdout = json.dumps(payload)`. Per the JSONEncoder table, `True` is written as `true`, giving `…"tiers": {"A": 29, "B": 3, "C": true}}`.
3. Lines 83–91: the step is a deep copy of the inventory step. `replace_revision` changes nothing because this step has no `<REV>` placeholders, and the cache-demo branch at line 84 does not apply. `returncode` is 0 and `stderr` is `""`, both from the record.
4. Line 97 grades the result with an exact identity check: `observed is case['want']`.

The only perturbation from the green public record is the `tiers.C` leaf, so nothing else confounds the rejection.

## 2. The changed predicate on this vector

`summarize_result` (`run-acceptance.py` lines 390–492, pinned):

- Line 410: `matched` starts true, because `returncode == 0` and `failure_lines` finds no `FAIL` line in the JSON stdout.
- Line 468: `json.loads` returns `tiers.C` as `bool` `True` (S104 table). No exception occurs, so the `RecursionError` addition does not apply.
- Lines 472–473: because `exact_json` is true, `json_exact(observed, expected)` is called. Inside `json_exact` (lines 375–387):
  - At the top level both values are dicts with equal key sets (`F2_entry`, `admitted_entries`, `evidence_gate`, `measured_commit`, `sources`, `statuses`, `tiers`; order is irrelevant because `keys()` are compared as sets).
  - It recurses into `tiers`: both are dicts with keys `{A, B, C}`.
  - For `C`, `type(True) is bool` and `type(1) is int`, so the check at line 377 returns `False`.
- Line 492: `matched = True and False and not ""`, which is `False`. Line 537 gives `bool(False)`.
- **Changed verdict:** observed is `False` and want is `False`, so the vector passes. The sole cause is the type check at line 377.

Base predicate (`git show 41553adb:` lines 420–432): `json_match = observed == expected`. Dict equality compares values, and `True == 1` holds (S105), so the base returns `matched=True`. The base observation is `True` against a want of `False`, so the base fails this vector. The vector is discriminating and does test the claimed repair.

Side diagnostic (not part of the decision): `numeric_leaves` (lines 362–372) skips the `bool` at line 370. As a result `observed_numeric_fields` lacks `tiers.C` and `matched_expected_fields` is 9 of 10. That is consistent and does not feed `matched`.

### Paired positive: `positive/r13-counter-31984f4` (lines 3012–3017, want `true`)

This vector has no delta. The stdout is the record bytes verbatim, including the trailing `\n`, which `json.loads` accepts. Every leaf has the same type and value as the inventory, so `json_exact` returns `True`. With `returncode` 0 and empty `stderr`, the changed code gives `matched=True`, which equals the want. The base gives `observed == expected`, also `True`. This matches the record's own `matched: true` at `final-out-S1.json` line 3568. No harm to operability or coverage.

### Attack attempts that did not land

- **Shallow type check.** A mutation that type-checks only depth-1 leaves, for example `all(type(observed[k]) is type(v) and observed[k] == v …)`, would still reject `F2_entry/bool`. It would accept `tiers.C/bool`, because the `tiers` dict passes the type check and then `{..."C": True} == {..."C": 1}`. Draft mutation: replace the recursive body of `json_exact` with that one-level form. Expected killed vector: `scalar/r13-counter-31984f4/tiers.C/bool` (observed `True`, want `False`). The nested float vectors `tiers.*` and `statuses.*` would also kill it. Not executed.
- **Subclass-tolerant type check.** Mutating line 377 to `if not isinstance(observed, type(expected))` accepts `bool` as an `int`. Expected killed vector: this one (observed `True`, want `False`), alongside the `F2_entry/bool` and `evidence_gate/bool` vectors. The positive is unaffected. Not executed.
- **Non-exact branch** (lines 475–478, `key in observed and json_exact(...)`): not reached, because `exact_json` is true for this step.

### Residuals outside this vector's scope

- **Repeated keys.** A producer stdout such as `{"tiers": {"C": true, "C": 1}}` decodes last-wins (json docs, "Repeated Names Within an Object") and would be accepted. The fixture cannot express this, because it re-serialises a dict. The lesson's S106 note says "No duplicate-key/NaN policy change is smuggled". This is a gap in scope, not a defect against C1.
- **Freeze order is not provable from git.** `git log` shows the oracle json first appears in `36c78ba` (212 cases), the same commit that introduced `json_exact`. At `4f83fd2` it has 214 cases, and this vector is identical in both. The claim that it was "frozen before editing" (lesson line 33) therefore rests on `bindings-before.json`, which is outside my read contract and I did not verify. The vector's content is independently reconstructable from the pinned receipt and inventory, as shown in section 1, so its literal decision does not depend on the changed code.

## 3. Documentation reopened (live, Python 3.15.1, 2026-10-21)

- **S104: ADMIT.** Page: https://docs.python.org/3/library/json.html, section "Encoders and Decoders", `class json.JSONDecoder`. Located quote: "Performs the following translations in decoding by default:". The table maps `number (int)` to `int`, `number (real)` to `float`, `true` to `True` and `false` to `False`. The JSONEncoder table also maps `True` to `true`, which grounds the fixture's round-trip. Scope: decoded type identity only, not execution provenance.
- **S105: ADMIT.** Page: https://docs.python.org/3/builtins/stdtypes.html, section "Boolean Type - `bool`". Located quote: "`bool` is a subclass of `int` (see Numeric Types — int, float, complex). In many numeric contexts, `False` and `True` behave like the integers 0 and 1, respectively." Scope: this is why the base's `observed == expected` accepts the vector and why `type(...) is` is required.
- **S106: REJECT stands.** Same json page, JSONDecoder `strict` parameter. Located quote: "If strict is false (`True` is the default), then control characters will be allowed inside strings." `strict` governs control characters inside strings, not typed field equality, so it cannot substitute for `json_exact` on this vector.

## Confidence and remaining unknowns

Confidence that the vector's decision, its input fidelity, and the changed and base verdicts are as stated: high, by source trace. Unknowns: no executed observation (L1 runs all 214 vectors); freeze order before `36c78ba` is unverified; a duplicate-key input is unrepresentable in this fixture.
