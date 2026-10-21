# Attack29 — `scalar/r13-counter-6f8ee0f/evidence_gate/bool`

Seat: SoujiR22.Attack29 (scout, leaf, source-only). Target code: `4f83fd222ffbd8825340221a8c426550ef891191`.

## STATUS

**PASS (source-only).** The expected decision `want=False` is correct, and the fixture really does feed a JSON boolean `true` into `evidence_gate`. On the pinned runner, this vector is rejected only by the strict type test in `json_exact`, so it resolves to `observed=False`, which agrees with the oracle. The paired positive resolves to `observed=True`, which also agrees. I found no mismatch between the oracle and the code for this pair.

The main limit is that the predicate that decides this vector, `json_exact`, did not change in `4f83fd2`. The code that did change (the iterative `numeric_leaves` rewrite and the added `RecursionError` catches) is not involved in the `matched` decision here. So this vector calibrates the unchanged strict-type predicate, not the round-22 change. Nothing was executed: no oracle run, no acceptance run, no mutation run. L1 still owns all runtime evidence.

## Pin integrity (observed)

I compared `git show 4f83fd2:<path> | sha256sum` against the working-tree file for each named input. They are identical:

| path | sha256 |
|---|---|
| `census/round-21/run-acceptance.py` | `00d0e9c2…e080a6` |
| `tests/fixtures/r22-result-oracle.json` | `292442a6…dcd0651` |
| `tests/fixtures/r22-result-oracle.py` | `3c0776ae…697a604` |
| `census/round-21/step-inventory.json` | `8b7b1cd8…7d1310` (equals oracle `frozen_inventory_sha256`) |
| `census/round-21/final-out-S1.json` | `bc53a752…5738fe` (equals oracle `source_receipt_sha256`) |

This means the oracle's tamper check (`r22-result-oracle.py:31-36`) would accept both inputs.

## Stored delta, and its reconstruction from the public inputs (done before reading the predicate)

Stored vector, from `r22-result-oracle.json:3296-3308`:

- `want: false`, `group: scalar`, `step_name: r13-counter-6f8ee0f`
- `json_set: [[["evidence_gate"], true]]`
- It has no `stdout`, `stderr`, or `returncode` override, so the harness falls back to the record values (`r22-result-oracle.py:67-68,88-90`).

Original public record, from `final-out-S1.json:3835-3858` (the only `name == r13-counter-6f8ee0f` entry):

- `returncode: 0` (line 3854), `stderr: ""` (line 3855)
- `stdout` (line 3857): `{"F2_entry": 1, "admitted_entries": 5, "evidence_gate": 1, "measured_commit": "6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6", "sources": 37, "statuses": {"mined": 20, "queued": 15, "rejected": 2}, "tiers": {"A": 33, "B": 3, "C": 1}}\n`
- The original `evidence_gate` value is a JSON **integer** `1`.

Frozen inventory step, from `step-inventory.json:236-262`:

- `kind: counter`, `exact_json: true`
- `expected_summary.evidence_gate: 1` (int)
- `measured_commit` is a literal, and the step contains no `<REVISION>`/`<REV>` token, so `replace_revision` (`r22-result-oracle.py:40-47,59-60`) leaves it unchanged.
- This matches the runner's own `COUNTER_EXPECTATIONS` entry (`run-acceptance.py:133-143`, `exact=True`), so the oracle step and the real acceptance step agree.

Reconstructed fed input (`r22-result-oracle.py:72-82`):

1. `json.loads(record.stdout)` produces a dict.
2. The path `["evidence_gate"]` has length 1, so `at = payload` and `payload["evidence_gate"] = True`.
3. `json.dumps(payload)` produces the same seven keys in the same insertion order, with only one difference: `"evidence_gate": true`. The trailing `\n` is dropped.

Two conclusions follow:

- **The fixture really feeds the input.** It is a top-level key, the only value that changes, and the type changes from int to bool while the value stays truthy and `True == 1` in Python. That is exactly the case a value-only comparison would miss.
- **The expected decision is correct.** `exact_json: true` with an int expectation, together with the oracle contract ("Reject … decoded wrong scalar types", `r22-result-oracle.json:8`), requires rejection. JSON `true` and the number `1` are different JSON types. The public producer record emits an int. I could not read `count-claims.py` under the contract, so I did not check that the producer can never emit a bool; the claim rests on the public record.

## Changed predicate, as applied to this vector

The pinned diff `32231727 → 4f83fd2` for `run-acceptance.py` (observed via `git show`) changes three things:

- `numeric_leaves` goes from recursive to an explicit stack (`run-acceptance.py:362-372`).
- `except (ValueError, TypeError)` becomes `except (ValueError, TypeError, RecursionError)` in the counter decode (line 469) and the cache-demo decode (line 496).
- `json_exact` (`375-387`) is byte-identical to the parent at lines 373-386.

Trace of `summarize_result` for the mutated vector (`run-acceptance.py`):

1. Lines 393-396: no `SUMMARY`/`SELFTEST` lines and no `FAIL` lines.
2. Line 410: `matched = (0 == 0) and not [] = True`.
3. Lines 466-470: `json.loads` succeeds and gives `observed["evidence_gate"] is True`. The new `RecursionError` catch is not reached.
4. Lines 472-473: `exact_json` is true, so `json_match = json_exact(observed, expected)`. The dict types match (377) and the key sets match (380). Iterating the `expected` keys, `F2_entry` and `admitted_entries` pass, then `evidence_gate` gives `type(True) is bool`, which is not `int`, so line 377 returns `False`. The `all(...)` short-circuits to `False`.
5. Line 492: `matched = True and False and not "" = False`. Line 537 gives `bool(False)`.
6. Harness line 97: `type(False) is bool and False is False`, so the vector passes.

The changed `numeric_leaves` only affects the diagnostics:

- For the bool, the check `isinstance(current, int) and not isinstance(current, bool)` (370) leaves `evidence_gate` out of `observed_numeric_fields`. That gives `matched_expected_fields = 9` of `expected_field_count = 10`.
- This feeds `matched_counts` only (482-491), never `matched`.
- The stack order is `reversed(items)` pushed and then popped, which gives the same order and dotted keys as the recursive version, so there is no behavioural difference for this payload.
- The dropped trailing `\n` and the different `stdout_sha256` do not matter, because the counter branch decodes JSON and never compares the stdout bytes.

## Paired positive: `positive/r13-counter-6f8ee0f` (`want: true`, `r22-result-oracle.json:3227-3231`)

1. It uses the record `stdout`, `returncode 0`, and `stderr ""` unchanged. `json.loads` accepts the trailing `\n`.
2. `json_exact`: every leaf type matches (int/int, str/str, dict/dict), the keys are equal, and the values are equal, including `measured_commit` against the inventory literal. So it returns `True`.
3. Line 492 gives `matched = True`, which agrees with `want` and passes.
4. The diagnostics would be 10/10, consistent with the public record's `matched_counts` (`final-out-S1.json:3806-3833`).

The pair isolates exactly one variable: the JSON type of `evidence_gate`.

## Kill power (drafted, not executed)

Bounded mutation: on `run-acceptance.py:377`, replace `if type(observed) is not type(expected):` with `if not isinstance(observed, type(expected)):`.

- `isinstance(True, int)` is `True`, and `True == 1` at line 387, so `json_exact` would return `True` and `matched` would become `True`.
- **Expected killed vector:** `scalar/r13-counter-6f8ee0f/evidence_gate/bool`, with `observed=True` against `want=False`.
- The paired positive still passes, so the pair discriminates the mutation.
- Dropping the type check entirely, or comparing whole dicts with `observed == expected`, would also be killed by this vector for the same reason.

## Findings and unknowns

- **Fact:** the oracle expectation is correct, the input is really fed, and the vector and its positive both agree with the pinned runner by source trace. Confidence: high.
- **Fact:** the vector does not exercise any line changed in `4f83fd2` on its `matched` path. Its calibration value is the unchanged `json_exact` strict type identity.
- **[INFERENCE]** The producer `count-claims.py` emits ints for `evidence_gate`. This is based only on the public record, because the producer source is outside the contract.
- **Unresolved:** I have no runtime confirmation. L1's run of all 214 decisions and the actual 18-step acceptance is still required. I did not assess malicious-producer behaviour or universal malformed-input totality.

Tools: none installed or updated.
