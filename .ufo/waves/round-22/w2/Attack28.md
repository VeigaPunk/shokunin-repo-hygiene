# Attack28 — vector `scalar/r13-counter-6f8ee0f/F2_entry/bool` (want=False)

Seat: SoujiR22.Attack28 (scout, leaf, source-only). Target code: `4f83fd222ffbd8825340221a8c426550ef891191` (repo HEAD equals this commit). No tests, builds, probes, or delegation were used. No tools were installed or updated.

## Input binding (observed)

I checked that the working-tree bytes equal `git show 4f83fd2:<path>` for each named file:

| path | sha256 |
|---|---|
| census/round-21/run-acceptance.py | 00d0e9c2…e080a6 |
| tests/fixtures/r22-result-oracle.py | 3c0776ae…a604 |
| tests/fixtures/r22-result-oracle.json | 292442a6…0651 |
| census/round-21/step-inventory.json | 8b7b1cd8…1310 (equals oracle `frozen_inventory_sha256`, oracle.json:6) |
| census/round-21/final-out-S1.json | bc53a752…38fe (equals oracle `source_receipt_sha256`, oracle.json:4) |

The vector id appears exactly once in the oracle (count=1).

## 1. Stored delta and reconstruction, done before reading the predicate

- **Stored delta** (oracle.json:3254-3266): `want: false`, `group: scalar`, `step_name: r13-counter-6f8ee0f`, `json_set: [[["F2_entry"], true]]`. The case has no `returncode`, `stderr` or `stdout` override.
- **Pinned public record** (final-out-S1.json:3835-3858): `returncode: 0`, `stderr: ""`, and stdout `{"F2_entry": 1, "admitted_entries": 5, "evidence_gate": 1, "measured_commit": "6f8ee0f3…", "sources": 37, "statuses": {"mined": 20, "queued": 15, "rejected": 2}, "tiers": {"A": 33, "B": 3, "C": 1}}\n`.
- **Frozen inventory step** (step-inventory.json:236-261): `expected_summary.F2_entry` is `1`, a JSON integer. The step has `exact_json: true` and `kind: counter`. Its argv uses the literal hash `6f8ee0f…`, with no `<REV>`/`<REVISION>` placeholder, so `replace_revision` (oracle.py:40-47, 59-60) leaves the step unchanged.
- **Reconstructed mutated input** (oracle.py:67-82): the oracle loads the record stdout and walks `path=["F2_entry"]`. Because `path[:-1]` is empty, `at` is the top-level payload, and `payload["F2_entry"] = True`. It then re-serialises with `json.dumps` in the same key order and without a trailing newline: `{"F2_entry": true, "admitted_entries": 5, …}`. The returncode is 0 (from record, oracle.py:88) and stderr is "" (from record, oracle.py:90).
- **Does the fixture actually feed the input?** Yes. The key already exists, so the mutation replaces an existing int leaf with a bool and does not add a key. No other field changes. stdout gets no SUMMARY or FAIL lines, so the only difference from the positive control is the type of `F2_entry`.

## 2. Is want=False correct? Yes.

- The contract claims "Type-exact means decoded int/float/bool values remain distinct, including nested counters" (lessons/round-22.md:7). The preregistration calls out "JSON bool/int scalar confusion" (preregistration.txt:1). S104 grounds this: the JSON decoder maps integer→`int` and true→`True` as separate translations.
- The frozen expected value is the integer `1`, and a counter (`F2_entry` count) is not a boolean. JSON `true` is therefore a contract mismatch.
- The vector is designed to discriminate the baseline. `True == 1` holds in Python (S105, bool is an int subclass), so the baseline `json_match = observed == expected` (pre-36c78ba line, shown in the `git show 36c78ba` diff) yields a false green. Across the whole fixture, bool vectors exist only for int fields whose value is 0 or 1, and each uses the value-equal bool (`true` for 1, `false` for 0). Examples are oracle.json:3040 (31984f4 F2_entry=0 → false) and :3254 (6f8ee0f F2_entry=1 → true). This is exactly the equality-collision set.

## 3. Changed predicate traced for this vector (run-acceptance.py @4f83fd2)

1. **Lines 393-396:** stdout starts with `{`, so it has no `SUMMARY_RE` lines. `failure_lines` (356-359) returns nothing because stdout and stderr have no `FAIL\t` / `CASE\tFAIL` lines.
2. **Line 410:** `matched = (0 == 0) and not [] = True`.
3. **Lines 466-470:** `json.loads` succeeds and gives a dict with `F2_entry is True`. The new `RecursionError` arm (469) does not apply.
4. **Lines 472-474:** `exact_json` is True, so the code calls `json_exact(observed, expected)` (375-387):
   - dict is dict, so the type check passes.
   - `observed.keys() == expected.keys()` is True, because dict-keys equality is set-like (order: expected has `tiers` before `statuses`, observed has the reverse).
   - `all(...)` iterates `expected.items()`, with `F2_entry` first. `json_exact(True, 1)` checks `type(True) is bool` against `type(1) is int`, and line 377 returns False. The `all()` short-circuits, so `json_match` is False.
5. **Lines 475, 480:** the `numeric_leaves` diagnostics leave out bool (line 370 `not isinstance(current, bool)`). `F2_entry` is absent from `observed_fields`, so `matched_expected_fields` is 9 of 10. This is diagnostic only and does not feed `matched`.
6. **Line 492:** `matched = True and False and not "" = False`. **Line 537:** `result["matched"] = False`.
7. **Oracle grading (oracle.py:97):** `type(False) is bool and False is False` gives pass=True. An exception would set `observed=None` and fail even for want=False, so a crash cannot masquerade as a rejection.

The rejection is attributable solely to the type check at line 377. stdout re-serialisation, stderr and returncode are all neutral.

**4f83fd2 delta impact on this vector: none.**
- The iterative `numeric_leaves` (362-372) pushes `reversed(items)` onto a LIFO stack. It pops keys in forward DFS preorder, building the same paths (`key if not path else path+"."+key`, with the same empty-prefix rule) in the same insertion order as the former recursion. Later-wins collisions also behave identically. It only feeds `matched_counts`.
- The added `RecursionError` catches (469, 496) are not reached.

## 4. Paired positive `positive/r13-counter-6f8ee0f` (want=True, oracle.json:3227-3231)

- stdout is the verbatim record including the trailing `\n`, which `json.loads` tolerates. Returncode is 0 and stderr is "".
- `json_exact`: the key sets are equal. Every leaf is int↔int or str↔str with an equal value (`measured_commit` str equals the expected str). Nested `statuses`/`tiers` dicts have equal key sets and int leaves. Result: True.
- So `matched = True and True and True`, giving True and pass. This agrees with the public receipt's own `"matched": true` (final-out-S1.json:3805), whose `observed_numeric_fields` match all 10 expected fields (:3821-3833).

## 5. Concrete mismatches found

**None for this vector or its positive.** The expected decision is correct, the fixture feeds the stated input, and the changed predicate rejects it for the claimed reason while still accepting the positive.

## 6. Residual (latent, not a defect in this vector; outside the summarizer predicate)

- **Bool/int equality in the inventory binding.** `run-acceptance.py:657` binds `make_steps` to the frozen inventory with plain Python `!=` over `json.loads(json.dumps(row))` (604-608). That comparison conflates bool and int, which is the same defect class as R22-M1.
  - If `COUNTER_EXPECTATIONS` (line 138) were ever edited to `"F2_entry": True`, or `exact_json` to `1`, the inventory gate would still pass.
  - Summarization would then grade against the bool expectation, and a producer that emits `true` would green in real acceptance even though the frozen inventory says `1`.
  - Today line 138 is the int `1` and line 143 is `True`, so nothing is live.
  - The oracle cannot detect this: it grades frozen-inventory steps (oracle.py:59-60, 83) and never calls `make_steps`.
  - Confidence that this is latent only: high. Severity: low.

## 7. Drafted mutation (NOT executed)

- **Mutation:** at run-acceptance.py:377, change `if type(observed) is not type(expected):` to `if not isinstance(observed, type(expected)):`.
- **Expected effect:** `isinstance(True, int)` is True, so the code falls through to `observed == expected`, which gives `True == 1` = True.
- **Expected killed vector:** `scalar/r13-counter-6f8ee0f/F2_entry/bool` (observed True ≠ want False). The sibling bool-on-int vectors should die too: the 6f8ee0f `evidence_gate/bool` and `tiers.C/bool`, plus the others listed in §2.
- **Expected survivors:**
  - `scalar/r13-counter-6f8ee0f/F2_entry/float`, because `isinstance(1.0, int)` is False and it is still rejected.
  - `positive/r13-counter-6f8ee0f`, which stays True.
- This mutation isolates bool-subclass leakage (S105) from float confusion. A blunt revert to `observed == expected` would kill both and so would not tell the two apart.

## STATUS

**PASS, source-only.**
- The vector's literal want=False is correct against the frozen int expectation and the round-22 type-exact contract.
- The fixture really feeds `F2_entry: true` with returncode 0 and empty stderr.
- At 4f83fd2, `summarize_result` returns `matched=False` solely through `json_exact` line 377.
- The paired positive returns True. The 4f83fd2 deltas (iterative `numeric_leaves`, `RecursionError` catches) are neutral for both vectors.

**Evidence:** pinned byte digests plus line-cited trace. **Limits:**
- No run was performed. L1 owns the actual 214-decision and 18-step execution.
- Python semantics are cited from S104/S105, not re-executed.
- Residual §6 is latent, not exercised.
- This is not malicious-producer attestation or malformed-input totality.

Report: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/w2/Attack28.md
