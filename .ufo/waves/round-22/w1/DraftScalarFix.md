STATUS: PASS — Scoped source-only implementation draft complete. No implementation file was changed and no code, tests, builds, formatters or probes were executed. PASS describes this draft deliverable, not acceptance results.

## Axes and scope

- **Calibration:** require recursively identical decoded types and values; reject bool/int/float substitutions and missing expected keys.
- **Operability:** one small helper, no imports/dependencies, unchanged result schema and numeric diagnostic projection.
- **Coverage:** both exact and top-level subset counter branches; nested objects/arrays, array length/order, explicit null and missing keys.

No numeric axis score or measured improvement is claimed. All proposed behavioral outcomes below are **[INFERENCE]**, derived from the observed source and Python documentation. This report does not claim that the working source was independently verified against the supplied base commit.

## Exact retained evidence

1. `census/round-21/run-acceptance.py` (observed read snapshot `A4F8`): lines 120–179 define four exact counter dictionaries and one non-exact dictionary; lines 319–326 transfer these expectations and `exact_json` into steps. Lines 420–445 decode stdout, use untyped equality at 427, and use `observed.get(key) == value` at 430–431. Lines 336–344 exclude booleans and non-integers from numeric diagnostics. Line 623 calls `summarize_result`.
2. `census/round-21/step-inventory.json` (`AB5C`): lines 207–322 retain four exact counter expectations, including nested `tiers`/`statuses`; lines 323–330 retain the top-level subset expectation (`measured_commit`, integer `admitted_entries: 6`). No inventory expectation needs to change for this draft.
3. `.ufo/waves/round-21/w2/AttackRunnerStepResults.md` (`9757`), lines 5–9: earlier source-only bool/int false-green finding. This is an advisory finding, not an executed witness.
4. `.ufo/waves/round-22/preregistration.txt` (`7B21`), full raw line 1: one calibration claim, same independent synthetic oracle and all 18 real positive controls retained; malformed producer data must be rejected; production F5 remains byte-identical and historical/reap/NAMESPACE holds remain intact.
5. `corpus/QUALITY.md` (`DCF9`), raw lines 104–114: Q45/Q47 scope restrictions, Q48 original revision binding, Q49 synthetic-only 160-byte F5 reason scope, and Q50 authority limits. No production/process/private-history surface was opened.
6. Opened public authority: <https://docs.python.org/3/library/json.html#json.JSONDecoder>, retained reader output `artifact://54772`, lines 355–407. Its default conversion table maps object/array to dict/list, integer/real numbers to int/float, true/false to True/False, and null to None. It also documents the default decoder's nonstandard NaN/Infinity acceptance; this draft does not change that policy.
7. Opened public authority: <https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex>, redirected to <https://docs.python.org/3/builtins/stdtypes.html>, retained reader output `artifact://54773`, observed numeric-types section. It states that Booleans are an integer subtype and cross-type numeric comparison behaves as comparison of exact numeric values.
8. Actual LSP availability attempt: `read xd://lsp` returned `No such tool: xd://lsp`. No LSP definitions/references/diagnostics are claimed. The source references above come from bounded reads and a search restricted to the explicitly authorized runner file.

## Minimal integration draft

Target only `census/round-21/run-acceptance.py` when L1 integrates. Insert this helper between `numeric_leaves` and `summarize_result` (currently lines 344–347):

```python
def json_equal(observed, expected) -> bool:
    """Compare decoded JSON values without numeric type coercion."""
    if type(observed) is not type(expected):
        return False
    if isinstance(expected, dict):
        return (observed.keys() == expected.keys()
                and all(json_equal(observed[key], value)
                        for key, value in expected.items()))
    if isinstance(expected, list):
        return (len(observed) == len(expected)
                and all(json_equal(item, value)
                        for item, value in zip(observed, expected)))
    return observed == expected
```

Replace the counter branch's decode/comparison prefix, currently lines 421–433, with:

```python
        try:
            observed = json.loads(stdout)
            json_parsed = True
        except (ValueError, TypeError):
            observed = None
            json_parsed = False
        expected = step["expected_summary"]
        if step["exact_json"]:
            json_match = json_equal(observed, expected)
        else:
            json_match = (
                isinstance(observed, dict)
                and all(key in observed and json_equal(observed[key], value)
                        for key, value in expected.items())
            )
        expected_fields = numeric_leaves(expected)
        observed_fields = numeric_leaves(observed) if isinstance(observed, dict) else {}
```

Keep the existing `observed_json` and `matched_counts` construction unchanged, and replace the final counter gate at current line 445 with:

```python
        matched = matched and json_parsed and json_match and not stderr
```

The parse-success bit keeps the existing diagnostic representation (`observed_json: null` after a caught decode error) while distinguishing it from a successfully decoded JSON null. It is relevant if a synthetic or future exact expectation is itself null; all five current counter expectations are dictionaries. The existing exception tuple remains unchanged.

### Preserved subset contract

**[INFERENCE]** Subset means only that additional top-level observed keys are permitted. Every expected key must exist, and its entire selected value is compared recursively and exactly. Nested objects do **not** become recursive subsets. Object ordering remains irrelevant; arrays retain exact length, ordering and element types. Explicit membership, rather than `.get`, distinguishes a missing key from a present null. The helper compares string-keyed dictionaries produced by the default JSON decoder and trusted JSON-shaped expectations; it is not an arbitrary Python object comparator.

The helper's initial exact-type check prevents Python numeric equality from admitting `False` for `0`, `True` for `1`, `0.0` for `0`, or the reverse substitutions, including inside any selected list/object. Container checks recurse rather than falling back to Python container equality. No serialization, normalization, coercion, extra result field or copied container is introduced.

## Literal review vectors for L1's independent oracle

These are **unexecuted expected decisions**, not test output. Each `expected` and valid `stdout` cell is JSON text. For counter-result decisions, assume return code 0 and empty stderr. The independent oracle owner should retain literal decisions, not compute its expectation using `json_equal`.

| Mode | Expected | Stdout | Draft decision |
|---|---|---|---|
| exact | `{"n": 0}` | `{"n": false}` | reject |
| exact | `{"n": 0}` | `{"n": 0.0}` | reject |
| exact | `{"n": true}` | `{"n": 1}` | reject |
| exact | `{"n": 1.0}` | `{"n": 1}` | reject |
| exact | `{"x": [{"n": 1}]}` | `{"x": [{"n": true}]}` | reject |
| exact | `{"x": [{"n": 1}]}` | `{"x": [{"n": 1.0}]}` | reject |
| exact | `{"x": [1, 2]}` | `{"x": [1]}` | reject |
| exact | `{"x": [1, 2]}` | `{"x": [2, 1]}` | reject |
| exact | `{"a": 1, "b": [null, true, 1.0]}` | `{"b": [null, true, 1.0], "a": 1}` | accept |
| exact | `{"x": null}` | `{}` | reject |
| exact | `{"x": null}` | `{"x": null, "extra": 1}` | reject |
| exact | `null` | `null` | accept |
| exact | `null` | empty/whitespace stdout, not a JSON document | reject |
| subset | `{"n": 6}` | `{"n": 6, "extra": true}` | accept |
| subset | `{"n": 6}` | `{"n": 6.0, "extra": true}` | reject |
| subset | `{"x": [{"n": 1}]}` | `{"x": [{"n": true}], "extra": 1}` | reject |
| subset | `{"x": {"n": 1}}` | `{"x": {"n": 1, "extra": 2}}` | reject |
| subset | `{"x": {"n": 1}}` | `{"x": {"n": 1}, "extra": 2}` | accept |
| subset | `{"x": {"n": null}}` | `{"x": {}}` | reject |
| subset | `{"x": null}` | `{}` | reject |
| subset | `{"x": null}` | `{"x": null, "extra": 1}` | accept |
| subset | `{}` | `{"extra": null}` | accept |
| subset | `{}` | `null` | reject |

## Bounded findings, risks and handoff

- **[INFERENCE]** The exact and subset equality defects share one fix: compare types at every decoded value and require presence for selected keys. Existing positive dictionaries use the same types/values, so their counter match decisions and numeric diagnostic projection should be preserved. Actual 18-step/historical parity remains for L1 to execute after integration.
- Rejected inference: equal Python values, equal numeric-leaf counts, or a green selected-summary projection prove exact JSON types. They do not. Nor does the default decoder imply strict RFC JSON validation or original-text identity.
- This is decoded-value equality, not byte/lexical identity: whitespace, object order and same-type equivalent float spellings remain immaterial. Default duplicate-key, nonfinite-number and float-rounding behavior is unchanged.
- The recursive helper does not establish general malformed/deep-input totality or impose resource bounds. Decoder exception policy, summary stderr rejection and exact cache check identity are outside this scalar draft; their assigned owners/L1 must integrate the full round claim. No arbitrary malicious-producer attestation is claimed.
- No production/F5 file was edited or inspected; this seat makes no new F5 byte-identity measurement. The 160-byte synthetic-only repair and historical/reap/NAMESPACE assessment stay outside this move and HELD as contracted.
- L1 checks to run after all drafts land: the same committed independent scalar/oracle vectors on base and integrated implementation, all original 18 real acceptance positive controls, and exact historical outcome projections. This seat ran none of them.
- Implementation blockers: none for the scoped draft. Tooling limitation: LSP unavailable as observed above. Installs/updates: none.

Files changed by this seat: only this advisory report; all proposed code is fenced above. No Git index, production source, sibling file, process state or external substrate was changed.

Report: .ufo/waves/round-22/w1/DraftScalarFix.md
