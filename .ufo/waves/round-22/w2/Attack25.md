# Attack25 — scalar/r13-counter-31984f4/F2_entry/bool (want=False)

Seat: SoujiR22.Attack25 (leaf, source-only). Target code: 4f83fd222ffbd8825340221a8c426550ef891191 (= HEAD; the five named files below are byte-identical between `git show 4f83fd2:<path>` and the working tree).

| path | sha256 (pinned = worktree) |
|---|---|
| census/round-21/run-acceptance.py | 00d0e9c2fda2fde2d21cb74b1a1dd5b1db7b1ea679cdfd4239d91aa186e080a6 |
| tests/fixtures/r22-result-oracle.py | 3c0776ae1df8cd487380a8a94203848e3a24c5bc910762a23f63fc335697a604 |
| tests/fixtures/r22-result-oracle.json | 292442a6ec078b7cc20526b4ba7ab1300eb08bc9cc4dbaf9894472120dcd0651 |
| census/round-21/step-inventory.json | 8b7b1cd8d19561d9f4e8f06e797038b03379350cb3f3932edf04bda7aa7d1310 (= oracle `frozen_inventory_sha256`) |
| census/round-21/final-out-S1.json | bc53a75285a4fafdb6f4f8c2de0a4068fa87494c2745faa1ef6af11ec25738fe (= oracle `source_receipt_sha256`) |

Base for before/after: `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py` (sha256 1141839963d04e9e1b968d123fa8ffebeef5d33438537cdc636350c970eeaa2b).

## STATUS

**PASS for the assigned vector's decision; PARTIAL for how well the vector isolates what it tests.** Source-only: no runner/oracle execution, no tests. The stored expectation `want=False` is correct. The fixture really feeds a decoded `False` into the changed predicate. The changed predicate rejects it for the intended reason (type identity), and the paired positive is still accepted. A concrete calibration gap remains: every scalar vector differs from its positive control in two ways, not one. The scalar is mutated, and the trailing newline is also dropped by re-serialization. So a one-line mutant that restores the bool/int defect survives all 214 vectors (see the Mutation section). No runtime evidence is claimed.

## 1. Delta reconstruction (before reading the changed predicate)

- Stored delta, `tests/fixtures/r22-result-oracle.json:3040-3052`: `{"id": "scalar/r13-counter-31984f4/F2_entry/bool", "want": false, "group": "scalar", "step_name": "r13-counter-31984f4", "json_set": [[["F2_entry"], false]]}`. The id is unique (1 of 214 cases).
- Frozen inventory, `census/round-21/step-inventory.json:208-227`: `expected_summary.F2_entry` is `0`, a JSON integer. The step has `"exact_json": true` and `"kind": "counter"`, and its `expected_summary` has no `<REV>`/`<REVISION>` placeholders, so `replace_revision` (oracle.py:40-47) leaves the integer unchanged.
- Pinned public record, `census/round-21/final-out-S1.json:3598-3621`: `returncode` 0, `stderr` "", `stdout` = `{"F2_entry": 0, "admitted_entries": 4, "evidence_gate": 0, "measured_commit": "31984f47…", "sources": 33, "statuses": {...}, "tiers": {...}}\n` (record `matched: true`, 10/10 numeric fields).
- Reconstructed input: the oracle (oracle.py:67-82) takes `record['stdout']`, `json.loads` it, sets `payload["F2_entry"] = False`, and re-emits `json.dumps(payload)`, which yields `"F2_entry": false` with no trailing `\n`. Returncode 0 and stderr "" come from the record (oracle.py:87-90). Every other field stays equal to the frozen expectation.

**Is the expected decision correct?** Yes. Contract: the round-22 preregistration ("JSON bool/int scalar confusion") and `corpus/lessons/round-22.md:7` ("Type-exact means decoded int/float/bool values remain distinct"). The frozen inventory declares an integer `0`, and the producer instead emits the JSON boolean `false`. `want=False` follows from the contract, not from the implementation.

**Does the fixture actually feed that input?** Yes. `records[case['step_name']]` resolves through `receipt['commands']`, which has exactly one entry named `r13-counter-31984f4`. `steps[...]` resolves through `inventory['steps']`, also exactly one entry. The `json_set` path `["F2_entry"]` is a top-level key that exists. The runner then decodes `false` back to `False` (S104 table). The mutated value reaches `summarize_result` as a Python `bool`.

## 2. Attack on the changed predicate (4f83fd2)

The relevant path in `census/round-21/run-acceptance.py`:
- 410: `matched = returncode == 0 and not failures` evaluates to True. `failure_lines` (356-359) finds no `FAIL\t` or `CASE…FAIL` lines.
- 466-470: `observed = json.loads(stdout)` gives a dict with `F2_entry` set to `False`. The `except (ValueError, TypeError, RecursionError)` branch is not taken.
- 472-473: `exact_json` is True, so `json_match = json_exact(observed, expected)`.
- 375-387 `json_exact`: both values are dicts, so `type(...)` matches; `observed.keys() == expected.keys()` holds for the same 7 keys (key views compare as sets, so order doesn't matter). Recursing into `json_exact(False, 0)` gives `type(False) is bool`, which is not `int`, so it returns **False**. `all(...)` is therefore False, and `json_match` is False.
- 492: `matched = matched and json_match and not stderr` is False. 537: `result["matched"] = False`.
- oracle.py:97: `type(False) is bool and False is False` passes.

Diagnostics only (no effect on the decision): `numeric_leaves` (362-372) excludes bools, so `observed_numeric_fields` lacks `F2_entry` and `matched_expected_fields` is 9.

**Paired positive, `positive/r13-counter-31984f4` (oracle.json:3013-3017, want=True, no delta).** Raw pinned stdout decodes to integers, `json_exact` holds at every leaf, returncode is 0 and stderr is "", so `matched` is True and the case passes. The positive is not damaged.

**Before/after discrimination.** At base 41553adb, line 427 was `json_match = observed == expected`. Under S105 and the stdtypes comparison rule ("A comparison between numbers of different types behaves as though the exact values of those numbers were being compared"), `False == 0`, so dict equality held and base `matched` was True. Base therefore fails this vector, which makes it discriminating. This is [INFERENCE] from source; L1's run is authoritative.

**No mismatch** between expectation, fixture input and changed-predicate behavior for this vector.

## 3. Concrete calibration gap: a surviving mutant

Static enumeration of the 214 cases (data-only parse, below):
- All 32 `scalar/*` vectors target `exact_json: true` counter steps (31984f4, 6f8ee0f, a31642d, 552cae4), and all are `json_set`. Each is re-serialized by `json.dumps` at oracle.py:82, which drops the trailing `\n` that every pinned counter stdout ends with (5/5 counter records end in `}\n`).
- The only want=True counter vector that goes through re-serialization is `positive/subset-extra-fields`, on `r13-counter-b576341`, which has `exact_json: false`. No want=True vector re-serializes an exact-JSON step's stdout.

Drafted mutation (not executed). Change `run-acceptance.py:473` to:
`json_match = observed == expected and stdout.endswith("\n")`

Predicted outcomes [INFERENCE, source-only]:
- **This vector:** `False == 0` makes `==` true, but there is no trailing newline, so `matched` is False and the vector **passes**. It does not detect the regression.
- **All 32 scalar vectors** pass for the same reason.
- **Positives for exact steps** keep raw `\n`-terminated stdout and pass.
- **Non-exact-branch cases** (`subset-extra-fields`, the b576341 cases) are untouched and pass.
- **exit, array and decoder-depth cases** are rejected anyway and pass.
- **Expected killed vector: none.** The mutant survives all 214 while reintroducing R22-M1 for any real producer that emits `{"F2_entry": false, …}\n`.

Either bounded addition would kill it:
- (a) `positive/r13-counter-31984f4/reserialized`: `json_set [[["F2_entry"], 0]]`, want True. This is an identity re-serialization control, so the bool vector differs from a passing input only in the scalar.
- (b) A raw `stdout` override carrying `"F2_entry": false` with a trailing `\n`, want False.

Severity: medium-low. The mutant is contrived (newline gating is not a natural implementation choice). The real gap is that the vector set cannot attribute a rejection to type identity alone.

Adjacent, outside this vector, reported for L1: no scalar type vector exercises the `exact_json: false` branch (run-acceptance.py:476-478). Reverting line 477 to the base `observed.get(key) == value` would survive all 214. b576341's only vectors are positive, exit, array and subset-extra-fields, and each decides the same way under either predicate.

## 4. Sources re-opened (Python 3.15.1 docs, 2026-10-21)

- **S104: ADMIT.** https://docs.python.org/3/library/json.html, section "Encoders and Decoders", class `JSONDecoder`. Located quote: "Performs the following translations in decoding by default:"; the table rows include "number (int) | int", "number (real) | float", "true | True", "false | False". Bounded scope: the default decoder's output types, which is how `false` reaches the predicate as `bool`. It does not cover execution provenance.
- **S105: ADMIT.** https://docs.python.org/3/builtins/stdtypes.html, section "Boolean Type - bool". Located quote: "`bool` is a subclass of `int` (see Numeric Types — int, float, complex). In many numeric contexts, `False` and `True` behave like the integers 0 and 1, respectively." This grounds why base `==` accepted this vector, and why the changed `type(...) is` check is needed. Corroboration on the same page, Numeric Types: "A comparison between numbers of different types behaves as though the exact values of those numbers were being compared." Bounded scope: equality semantics only.
- **S106: REJECT (correct as recorded).** https://docs.python.org/3/library/json.html, `JSONDecoder` strict parameter. Located quote: "If strict is false (`True` is the default), then control characters will be allowed inside strings." `strict` governs control characters inside strings only and says nothing about scalar type or expected-field equality. The rejection inference in `corpus/SOURCES.md:126` is correctly scoped. Not applicable as an admit for this vector.
- `corpus/SOURCES.md:124-126` rows match the located sections.

## Method, limits, tooling

- **Reads:** the named files, plus `git show` of the exact named paths at 4f83fd2 and base 41553adb (hashes and line ranges), plus the two official Python documentation URLs.
- **Data-only parses:** `python3 -B -c` (Python 3.14.8) ran `json.load` on the named receipt, inventory and oracle JSON to enumerate cases, count keys and check trailing newlines. These parses did not import or execute the runner or the oracle, and spawned no child processes.
- **Not done:** no runner execution, no tests, no edits outside this report, and no delegation.
- **Not covered:** `census/round-14/cache-demonstration.py`, which is not on this vector's path (counter kind).
- **Installs/updates:** none.
