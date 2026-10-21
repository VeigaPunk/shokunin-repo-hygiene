# Attack21 — summary/r16-landing-gate/extra (want=False) and its paired positive

Seat: SoujiR22.Attack21 (leaf, source-only). Code under review: `4f83fd222ffbd8825340221a8c426550ef891191`.
I confirmed the working tree is byte-identical to that commit for `census/round-21/run-acceptance.py`:
`git show 4f83fd2:` and the worktree file both hash to SHA-256 `00d0e9c2…e080a6`, and `git diff 4f83fd2` over the named inputs is empty.
No tools were installed or updated.

## STATUS

**Source-only PASS for this vector and its paired positive.**
- The stored delta reconstructs exactly from the pinned public record.
- The literal `want=False` is correct.
- The fixture really feeds that stdout to the summarizer.
- On this vector, both the changed predicate and the base predicate reject the input, through one unchanged conjunct.

I found no concrete mismatch.

Limits:
- I did not execute the runner, the oracle, the acceptance `main`, or a mutation. The decisions below are traced from source lines.
- My only computation was decoding the named JSON fixture and receipt bytes. That covered SHA-256 checks, the prefix/suffix split, line splitting, and evaluating literal copies of `SUMMARY_RE`, the `pass_pattern`, and the `failure_lines` and `INVENTORY` filters on those stored bytes.
- I did not invoke `summarize_result`, so treat every "observed" value here as `[INFERENCE]` until L1's run of all 214 vectors confirms it.

## 1. Reconstructing the delta from pinned inputs (done before reading the predicate)

**Oracle header.** The oracle header (`tests/fixtures/r22-result-oracle.json`) names:
- `source_receipt=census/round-21/final-out-S1.json`, with SHA-256 `bc53a752…38fe`. I recomputed the hash and it matches.
- `frozen_inventory=census/round-21/step-inventory.json`, with SHA-256 `8b7b1cd8…1310`. I recomputed this hash too and it matches. It is also unchanged at base `41553adb` (`git show` gives the same hash).
- `revision=ff425ab8…7045`. This equals the receipt's `measured_commit` and is an ancestor of base `41553adb`.

**Vector.** The vector is `{"id":"summary/r16-landing-gate/extra","want":false,"group":"summary-control","step_name":"r16-landing-gate","stdout":…}`. It has no `returncode`, `stderr`, `json_set` or `stdout_nested_array_depth` override.

**Pinned public record.** The record is `commands[name=="r16-landing-gate"]` in `final-out-S1.json`. It contains exactly one row:
- `returncode=0` and `stderr=''`.
- `stdout_sha256=705fc547…6426`, which I recomputed from the stored `stdout` and which matches. The stored `stderr_sha256` also matches the empty string.
- 787 characters of stdout. These are 15 `CASE\t<name>\tPASS\t…` lines followed by `SUMMARY\ttotal=15\tfailed=0\n`.
- The record says `matched=True`, with `matched_counts.summary_lines=1` and `observed_pass_lines=15`.

**Delta.** The vector's stdout is 821 characters. It equals the record stdout exactly, followed by one appended line:

```text
SUMMARY invalid synthetic summary\n
```

The appended line is space-separated, not tab-separated. The original bytes contain no CR, no non-ASCII characters and no other line-boundary characters, so `splitlines()` equals `split('\n')[:-1]`. All 12 `summary-control` vectors use this same suffix on top of their own pinned record, and all 12 are prefix-exact.

**Frozen inventory row.** `{"name":"r16-landing-gate","expected_summary":"SUMMARY\ttotal=15\tfailed=0","pass_pattern":"^CASE\\t[^\\t]+\\tPASS\\t","pass_count":15,"kind":"summary","argv":[placeholders]}`

**Expected decision.** The contract (oracle `contract`, and `corpus/lessons/round-22.md:7`) makes a summary step match only its expected summary. A second, non-contract `SUMMARY` line is a malformed summary channel, so the honest literal is `want=False`. **The expected decision is correct.**

## 2. Does the fixture actually feed this input? Yes.

All line numbers in this section are in `tests/fixtures/r22-result-oracle.py`:
- **Lines 29–37:** inputs are hash-bound. A tampered receipt or inventory raises `ValueError`, which leads to exit 2.
- **Lines 58–60:** `records` is keyed by name from the receipt. `steps` comes from the frozen inventory with `<REVISION>`/`<REV>` replaced. That replacement does nothing for this row, which only has `<PYTHON>`/`<ROOT>` placeholders.
- **Line 68:** `stdout = case.get('stdout', record['stdout'])` selects the vector's 821-character stdout.
- **Lines 69–82:** these are not taken, because the vector has no depth or `json_set` keys.
- **Lines 84–85:** these do not apply, because `kind` is `summary`, not `cache-demo`.
- **Lines 87–91:** `summarize_result(step, 0, stdout.encode('utf-8','surrogateescape'), ''.encode(...), revision, ROOT)`. The returncode and stderr come from the record. For this ASCII data, the `surrogateescape` encode here and the decode at runner line 224 round-trip exactly.
- **Line 97:** a case passes only when `type(observed) is bool and observed is case['want']`. Any exception counts as a non-pass.

The oracle grades a step taken from the frozen inventory, not from `make_steps`. This keeps it independent of the code under test. In a real run, `run-acceptance.py:656–658` refuses unless `inventory_projection(make_steps(...))` equals `frozen["steps"]`. The r16 row in `make_steps` (`run-acceptance.py:327–329`, plus `kind` defaulted at line 600) equals the inventory row, so the oracle's step matches the step a real run would use. Coverage of `make_steps` itself belongs to L1's actual 18-step acceptance, not to this vector.

## 3. Tracing this vector through the changed predicate (`run-acceptance.py` at `4f83fd2`)

| line | conjunct | value for this vector |
|---|---|---|
| 118 | `SUMMARY_RE = ^(?:SUMMARY\|SELFTEST)(?:\t\| ).*$` | matches both `SUMMARY\ttotal=15\tfailed=0` and `SUMMARY invalid synthetic summary`, because of the space alternative |
| 395 | `summary_lines` | `['SUMMARY\ttotal=15\tfailed=0', 'SUMMARY invalid synthetic summary']` |
| 396, 356–359 | `failure_lines` | `[]`, since no line is a `FAIL\t`, `CASE\tFAIL\t` or `CASE\t…\tFAIL` line; the `exit=1` text inside CASE lines is not a marker |
| 410 | `returncode == 0 and not failures` | True |
| 415–417 | string expected: `summary_lines == [expected]` | **False** (a two-element list compared with a one-element list) |
| 432–436 | `INVENTORY\t` lines vs `[]` | `[] == []`, True, which leaves `summary_match` False |
| 440 | `baseline_mismatch_count` | absent from the step, so skipped |
| 446–450 | `pass_count`, via `findall(^CASE\t[^\t]+\tPASS\t, M)` | 15 == 15, True |
| 463 | `matched and summary_match and pass_match and not stderr` | **False** |
| 464 | carry-invariant special case | not this step |

**Predicted result.** `observed=False` (a bool, no exception), which equals `want=False`, so the case passes `[INFERENCE: traced, not run]`. Exactly one conjunct kills the vector: the list equality at line 416, which depends on the `(?:\t| )` alternative at line 118.

**Paired positive (`positive/r16-landing-gate`, want=True).**
- Inputs are the record stdout, `rc=0` and `stderr=''`.
- `summary_lines == ['SUMMARY\ttotal=15\tfailed=0']` equals `[expected]`.
- The auxiliary lines are `[] == []`.
- The pass count is 15. I counted the 15 CASE names; the last one is `vacuity-stub`, whose `stub rc=0 …` line still matches `pass_pattern`.
- Failures are empty and stderr is empty.

Predicted `matched=True`, consistent with the receipt's own `matched=True` and `matched_counts` `[INFERENCE: traced, not run]`.

## 4. What changed versus base, and what that means for calibration

I compared `git show 41553adb:census/round-21/run-acceptance.py` and `git show ff425ab:…` against `4f83fd2`. Every element this vector touches is byte-identical across all three:
- `SUMMARY_RE` at line 118.
- `summary_lines` (base line 352).
- The list equality (base line 373).
- The `INVENTORY` filter (base lines 386–387).
- `pass_count` (base line 401).
- The r16 step row (base lines 301–303).

The only change on the summary branch is the `and not stderr` conjunct (base line 417 becomes line 463), and it is inert here because stderr is empty. The other changes (`try/except ValueError` at 428–431, `json_exact`, the `RecursionError` handling, `CACHE_CHECK_NAMES`) are on paths this vector does not reach.

So this vector is expected False on both base and changed bytes. It is a no-harm, coverage-only control. It is not evidence for any of the three C1 repairs (scalar type confusion, summary stderr, cache identity). Any before→after table should count it under unchanged decisions, not as a repaired defect.

## 5. Mutation draft (one bounded mutation, not executed)

**Mutation M21.** At `run-acceptance.py:416`, change the right-hand side to keep only the first summary line:

```python
summary_match = summary_lines[:1] == ([expected] if expected else [])
```

**Effects.**
- **Killed vector:** `summary/r16-landing-gate/extra`. It would observe True while `want=False`: `summary_lines[:1]` is `[expected]`, and every other conjunct is True.
- **Paired positive:** `positive/r16-landing-gate` is unaffected and stays True. In fact, none of the 18 real positives can kill M21, because each has exactly one summary line.
- **Other summary-control vectors:** the 10 others whose `expected_summary` is a non-empty string, whose real summary comes first, and whose other conjuncts are all True would also flip to True and be killed.
  - `agreement-pin-check` has `expected=""`, so `[:1] == []` is False whenever an extra line exists. It stays False and would not kill M21.
  - `r20-input-binding` uses a dict `expected_summary` (regex branch at 419), so M21 does not reach it.

**Why this target.** The `summary-control` group is the only part of the oracle that discriminates between "exactly one summary" and "first summary matches". The paired positive cannot detect this mutation, which is why this vector is necessary.

**Rejected mutation (not unique).** Narrowing line 118 to tab-only, `(?:\t)`, would also flip this vector to True. Positives with space-separated summaries would catch it too (for example `SUMMARY total=11 failed=0` at line 305, and `SUMMARY total=4 …` at line 321), so it is not a vector-specific kill.

## 6. Residual unknowns and non-findings

- **Ordering gap:** the fabricated extra line always comes *after* the real summary, and is always space-separated. No vector inserts the extra line before the real summary, or tab-separated, or as a repeat of the exact expected line. The list equality at line 416 would reject all three `[INFERENCE]`, so this is a coverage-breadth note, not a defect.
- **Pass-line identity:** repeated pass-line identity, such as 15 copies of the same `CASE` name, is explicitly out of scope (`corpus/lessons/round-22.md:35`). I did not test it.
- **Unread named files:** I did not read `census/round-14/cache-demonstration.py` or `corpus/SOURCES.md`, because they are not on this summary-kind path.
- **Runtime confirmation:** pending L1's run of all 214 vectors and the actual 18-step acceptance.
