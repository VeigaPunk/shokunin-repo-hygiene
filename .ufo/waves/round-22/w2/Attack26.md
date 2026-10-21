# Attack26 — scalar/r13-counter-31984f4/evidence_gate/bool (want=False)

Seat: SoujiR22.Attack26, leaf, source-only. No tests, builds, runs, probes, delegation or edits besides this report. Tools installed/updated: none.

## STATUS

**Source-only PASS** for this vector and its paired positive at code `4f83fd222ffbd8825340221a8c426550ef891191`. The literal decision `want=False` is correct. The fixture really feeds `evidence_gate: false`. The only conjunct that rejects the vector is the new type-identity predicate. The paired positive keeps `matched=True`. The base summarizer at `41553adb` would admit the vector, so it is base-discriminating. The S104 and S105 admits and the S106 reject all hold against the re-opened official pages. Limits: this is reasoning over the source, not execution. Observed `matched` values are `[INFERENCE]` until L1 runs all 214 decisions and the actual 18-step acceptance. It is not malicious-producer attestation and not universal malformed-input totality.

## 1. Byte binding (observed)

The pinned commit (`git show 4f83fd2:<path>`) and the working tree have identical SHA-256 for:
- `tests/fixtures/r22-result-oracle.json`: `292442a6…`
- `tests/fixtures/r22-result-oracle.py`: `3c0776ae…`
- `census/round-21/step-inventory.json`: `8b7b1cd8…`. This equals oracle `frozen_inventory_sha256` (oracle.json:5).
- `census/round-21/final-out-S1.json`: `bc53a752…`. This equals oracle `source_receipt_sha256` (oracle.json:4).
- `census/round-21/run-acceptance.py`: `00d0e9c2…`. The base `41553adb` version is `11418399…`.

The vector is byte-identical in `36c78ba` (212-vector oracle) and `4f83fd2` (214-vector oracle). It is not mutated across the depth-vector append.

## 2. Stored delta, reconstructed before inspecting the predicate

Stored vector (oracle.json:3081-3094):
`{"id":"scalar/r13-counter-31984f4/evidence_gate/bool","want":false,"group":"scalar","step_name":"r13-counter-31984f4","json_set":[[["evidence_gate"],false]]}`. It has no `returncode`, `stderr` or `stdout` override.

Original public record (final-out-S1.json:3598-3621):
- `returncode: 0`
- `stderr: ""`
- `stdout = {"F2_entry": 0, "admitted_entries": 4, "evidence_gate": 0, "measured_commit": "31984f47…", "sources": 33, "statuses": {...}, "tiers": {...}}\n`

The frozen expectation (step-inventory.json:207-233) is `evidence_gate: 0` (an int), with `exact_json: true` and `kind: "counter"`. It matches the in-code `COUNTER_EXPECTATIONS` at run-acceptance.py:120-131.

Reconstruction follows `r22-result-oracle.py`:
- Line 67: the record is taken from the receipt by step name.
- Line 68: `stdout = record['stdout']`.
- Lines 72-82: `json.loads` decodes the record, then `payload["evidence_gate"] = False` (empty `path[:-1]`, so it writes at the top level), then `json.dumps`. The result is `{"F2_entry": 0, "admitted_entries": 4, "evidence_gate": false, ...}`.
- Lines 59-60 and 83: the step comes from the **frozen inventory**, not from `make_steps`. `replace_revision` is a no-op here because the counter step has no `<REV>`.
- Lines 87-91: `summarize_result(step, 0, <mutated bytes>, b"", revision, ROOT)` is called.

**The fixture does feed the input.** `summarize_result` decodes JSON `false`, which becomes Python `False` (a bool), while the expectation is `0` (an int). No other field changes. With returncode 0, empty stderr and no `FAIL` lines, the only remaining discriminator is `json_match`, so the vector isolates the scalar-type predicate.

**Expected decision is correct.** The oracle contract (oracle.json:8) says "Reject … decoded wrong scalar types". JSON `false` is a different JSON type from the number `0`, and S104's table decodes it to a distinct Python type. The producer's real output is the int `0` (receipt:3602). A false-for-0 substitution is exactly the false green that R22-M1 names (lessons/round-22.md:15).

## 3. Attack on the changed predicate (pinned run-acceptance.py)

Trace for the vector:
- Line 410: `matched = 0 == 0 and not []`, which is True.
- Line 466: the counter branch. Line 468: `json.loads` returns a dict, and `false` decodes to `False`.
- Line 472: `exact_json` is True, so line 473 evaluates `json_exact(observed, expected)`.
- Lines 375-387, `json_exact`: at line 377 both top-level values are `dict`. At line 380 the key sets are equal (7 keys). Recursion reaches `json_exact(False, 0)`. At line 377, `type(False) is bool` and `type(0) is int`, so `bool is not int` holds and it returns False. `all()` short-circuits and `json_match` is False.
- Line 492: `matched = True and False and not ""`, which is False. Line 537: `bool(False)` gives False.
- Oracle line 97: `type(False) is bool and False is False` gives `pass`. `[INFERENCE]`, not run.

**Base comparison.** Base `41553adb` used `json_match = observed == expected` (shown by the diff hunk at base ~line 427). `{…"evidence_gate": False…} == {…"evidence_gate": 0…}` is True because `False == 0` (S105). The base therefore reports matched=True against want=False. The vector discriminates base from changed, as intended.

**Paired positive** (`positive/r13-counter-31984f4`, want=True, oracle.json:3012-3017):
- There is no delta, so the stdout is the original bytes with a trailing `\n`. `json.loads` tolerates trailing whitespace.
- Every leaf type matches: int vs int, str vs str, and nested dicts `statuses`/`tiers` with equal key sets.
- Line 387 `observed == expected` holds for each leaf, so `json_match` is True and `matched` is True.

The new predicate does not over-reject the real output. `numeric_leaves` (lines 362-372) is diagnostic only and does not affect `matched`. For the bool vector it omits `evidence_gate`, giving 9/10 matched fields, which is correct diagnostically.

**Concrete mismatches found for this vector or its positive: none.**

Drafted mutations (not executed) and the expected killing vector:
- **M1**, at line 377: replace `type(observed) is not type(expected)` with `not isinstance(observed, type(expected))`. Then `isinstance(False, int)` is True, the leaf falls through to `False == 0` (True), and matched becomes True. **Killed by this vector**, and by `F2_entry/bool` and `tiers.C/bool`. The `*/float` vectors do not kill it, because `isinstance(0.0, int)` is False. This vector is the one that discriminates isinstance-equality from type identity.
- **M2**: replace it with `not isinstance(expected, type(observed))`. This rejects observed bool and float when the expected value is an int. It is an **equivalent mutant** under the current inventory: no counter or cache `json_exact` expectation is a bool, and cache-demo uses `is` for bool fields. It survives, but it is not a defect.

Residual outside this vector, stated for scope only:
- The frozen-inventory guard at run-acceptance.py:657 uses ordinary `!=`, which is not type-exact.
- An in-code mutation at line 126, `evidence_gate: 0` to `False` (or `4` to `4.0`), would pass that guard (`[INFERENCE]` from S105 and the numeric-comparison rule).
- The oracle cannot see that mutation, because it reads the frozen inventory, not `make_steps`.
- It would make the real `r13-counter-31984f4` output fail `json_exact(0, False)` in L1's actual 18-step acceptance. It is therefore detected there, and it cannot produce a false green. No harm.

## 4. Re-opened official sources (2026-10-21; both pages render "Python 3.15.1 documentation")

- **S104 admit, holds.** https://docs.python.org/3/library/json.html, Encoders and Decoders, `class json.JSONDecoder`. Located quote: "Performs the following translations in decoding by default:". The table maps `number (int) → int`, `number (real) → float`, `true → True`, `false → False`. Bounded to this vector: the JSON `false` that the fixture writes decodes to `False`, a distinct entry from int. This grounds a decoded-type comparison and nothing about execution provenance.
- **S105 admit, holds.** https://docs.python.org/3/builtins/stdtypes.html, Boolean Type – `bool`. Located quote: "`bool` is a subclass of `int` (see Numeric Types — int, float, complex). In many numeric contexts, `False` and `True` behave like the integers 0 and 1, respectively." The quote recorded in lessons/round-22.md:26 matches verbatim. Bounded to this vector: this is exactly why the base `observed == expected` admitted `False` for `0`, and why line 377 must use type identity rather than `isinstance`.
- **S106 reject, holds and applies.** https://docs.python.org/3/library/json.html, the `JSONDecoder` `strict` parameter. Located quote: "If strict is false (`True` is the default), then control characters will be allowed inside strings." `json.loads` with the default `strict=True` decodes this vector's payload without error. Strict decoding therefore cannot reject a bool-for-int substitution, and the independent result comparison (`json_exact`) is required. The same page says "Repeated names within an object are accepted, and only the value of the last name-value pair is used". Duplicate keys stay out of scope (lessons/round-22.md:35), and nothing in this vector relies on them.

## Remaining unknowns

- Runtime `matched` values for base and changed code are unobserved. They belong to L1's run of all 214 decisions.
- `SOURCES.md:124-126` points at the same URLs and sections. Recheck cadence `on-release` is unchanged.
