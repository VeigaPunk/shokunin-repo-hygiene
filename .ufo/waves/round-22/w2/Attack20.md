# Attack20 — `summary/r18-landing-pointers/extra` (want=False) + paired positive

Seat: SoujiR22.Attack20 (scout, leaf, read-only). Attacked code: `4f83fd222ffbd8825340221a8c426550ef891191` (= worktree HEAD; worktree `census/round-21/run-acceptance.py` sha256 `00d0e9c2…80a6` equals `git show 4f83fd2:` bytes).

## STATUS
**PASS (source-only).** The expected decision `want=False` is correct. The fixture really does feed the mutated stdout to the runner, and the changed summarizer gives `matched=False`. The paired positive `positive/r18-landing-pointers` gives `matched=True`, which also matches its expected value. No concrete mismatch was found.

This vector does **not** discriminate before from after: it is a control. The predicate that makes it fail, summary-line list equality, is byte-identical in the preregistered base `41553adb…`, in `ff425ab…` (the measured commit) and in `4f83fd2…`. The only change that touches it, the new `and not stderr`, cannot fire because the record's stderr is empty.

Limits: decisions are derived from reading the source; the oracle, the runner and the acceptance run were never executed. The only things run were read-only `git show`/`diff`/`sha256sum` and a stdlib `json` parse of the two named JSON files. No tools were installed or updated. `jq` on this host is `jaq 3.1.1`, and it rejected `r22-result-oracle.json` at byte offset 164988, so I used Python's `json` instead. [INFERENCE] The rejection is probably a lone-surrogate escape elsewhere in the oracle; it is not in this vector.

## 1. Stored delta reconstructed from the pinned public record (done before looking at the predicate)
- Oracle header: `source_receipt=census/round-21/final-out-S1.json` with sha256 `bc53a752…38fe`, and `frozen_inventory=census/round-21/step-inventory.json` with sha256 `8b7b1cd8…1310`. Both match the on-disk files, and the inventory also matches `git show ff425ab:` bytes.
- Pinned record `final-out-S1.json:1555-1564` (`r18-landing-pointers`): `returncode=0`, `stderr=""`, 1463-char stdout. The stdout's recomputed sha256 equals the stored `stdout_sha256 1cacb86e…e87c`. It contains exactly one SUMMARY line, `SUMMARY\ttotal=11\tfailed=0`.
- Oracle vector `r22-result-oracle.json:387-393` has keys `{id, want, group, stdout, step_name}` only, with `group=summary-control`, and the id is unique among 214 cases. Its stdout is 1497 chars, `startswith(record.stdout)` is True, and the remaining suffix is exactly **`'SUMMARY invalid synthetic summary\n'`**. So the delta is one appended line that uses a space separator. returncode and stderr are inherited from the record.
- Frozen inventory `step-inventory.json:114-125`: `expected_summary="SUMMARY\ttotal=11\tfailed=0"`, `pass_pattern="^CASE\\tPASS\\t"`, `pass_count=11`, `kind=summary`. It contains no `<REV>`, so `replace_revision` (oracle.py:40-47) leaves it unchanged.

**Is the expected decision correct?** Yes. The step's contract is exactly one SUMMARY line equal to the frozen string. A second line in SUMMARY format makes the producer's verdict ambiguous, so rejecting it is the right call. Rejecting it does not depend on the producer under test.

## 2. Does the fixture actually feed the vector?
In `tests/fixtures/r22-result-oracle.py`:
- `:66-68`: `record = records['r18-landing-pointers']` and `stdout = case.get('stdout', record['stdout'])`, so the mutated stdout is used.
- `:69-82`: the vector has no `stdout_nested_array_depth` and no `json_set` key, so neither rewrite applies.
- `:83-85`: the step is a deep copy from the frozen inventory and is not `cache-demo`, so it is not patched.
- `:87-91`: `summarize_result(step, record returncode 0, stdout.encode(surrogateescape), record stderr "".encode(), revision, ROOT)`. The stdout is pure ASCII, so the round trip is exact.
- `:97`: the check is `type(observed) is bool and observed is want`. An exception would produce observed=None and fail the vector, so an exception cannot pass as rejection.

Conclusion: the fixture feeds exactly the reconstructed input.

## 3. How the changed predicate (`4f83fd2` `census/round-21/run-acceptance.py`) handles this vector
- `:118` `SUMMARY_RE = ^(?:SUMMARY|SELFTEST)(?:\t| ).*$`, applied per line through `re.match` at `:395`. The space alternative matches `SUMMARY invalid synthetic summary`, so `summary_lines` has two entries.
- `:396` `failure_lines`: no line starts with `FAIL\t` or `CASE\tFAIL\t`, and none matches `^CASE\t[^\t]+\tFAIL(\t|$)`. The third field is always the case name, and the `vacuity-stub` line text "assertion failed: yes" does not match. The result is `[]`.
- `:410` `matched = (0 == 0) and not [] = True`.
- `:415-417`: `expected` is a string, so `summary_match = summary_lines == [expected]` is **False**. This is the single cause of rejection.
- `:432-435`: auxiliary lines `[] == []` evaluates True.
- `:446-450`: `pass_count` is 11 (the appended line does not start with `CASE`), so `pass_match` is True.
- `:463` `matched = True and False and True and not "" = False`.
- `:537`: the result is `bool(False)`.

Observed False equals want False, so the vector passes.

Before/after: `diff` of `summarize_result` between `41553adb`/`ff425ab` and `4f83fd2` shows the summary-kind changes are only (a) `:463` adding `and not stderr` and (b) `:428-431` adding `try/except ValueError` around `int(group)`, which is only reachable when `expected_summary` is a dict. Neither changes this vector. On the base it is also False, at base line `:417 matched = matched and summary_match and pass_match`. It is correctly classified as a non-discriminating control.

## 4. Paired positive `positive/r18-landing-pointers` (want=True, `r22-result-oracle.json:347-351`)
- It uses the record's stdout, returncode 0 and stderr "" unchanged.
- `summary_lines == ["SUMMARY\ttotal=11\tfailed=0"] == [expected]`, failures are `[]`, auxiliary lines are `[]`, and `pass_count` is 11.
- The changed predicate `:463` evaluates `not ""` as True, so `matched` is True, which matches want.
- The new stderr gate does not break the real positive.

## 5. Mutations (drafted, not executed) and which vector should kill them
- **M-A, aimed at this vector.** Mutation: `:416` → `summary_match = expected in summary_lines` (or `summary_lines[:1] == [expected]`).
  - Expected killed vector: `summary/r18-landing-pointers/extra` (observed True vs want False).
  - The positive is unaffected.
- **M-B, aimed at this vector.** Mutation: `:118` → `^(?:SUMMARY|SELFTEST)\t.*$` (drop the space branch).
  - Expected killed vector: this vector, because the extra line is no longer collected and the vector comes out True.
  - [INFERENCE] `revision-helper-selftest` positives (expected summary `SUMMARY total=11 failed=0`, space-separated) would also flip to False.
- **M-C, the changed predicate.** Mutation: delete `and not stderr` at `:463`.
  - This vector is **not** killed: it survives, because stderr is empty.
  - The killing vectors are `stderr/r18-landing-pointers/{error,blank,pass,warning}` (`r22-result-oracle.json:359-386`). None of their stderr strings produces a failure line; for example, `PASS\t…` and `\n` are not FAIL markers. So `not stderr` is the sole cause of rejection for each.
  - The changed predicate is therefore exercised for this step by those siblings, not by `/extra`.

## 6. Residual observations (not mismatches; outside this vector's claim)
- **Trailing junk is accepted.** Appending a non-SUMMARY, non-`CASE`, non-FAIL junk line (for example `garbage\n`) to this step's stdout would still give `matched=True`, because no predicate covers arbitrary stdout content. `corpus/lessons/round-22.md:35` explicitly leaves "arbitrary stdout failure-marker semantics" unclaimed, so this is consistent with scope.
- **Line-splitting semantics differ.** `summary_lines` and `failure_lines` use `str.splitlines()`, which also splits on `\r`, `\x0b`, `\x0c`, `\x1c-\x1e`, `\x85`, `\u2028` and `\u2029`. `pass_count` uses `re.findall(..., re.MULTILINE)`, where `^` anchors only after `\n`.
  - [INFERENCE] A producer that separates lines with `\r` could therefore make the SUMMARY or FAIL view disagree with the PASS-count view.
  - No oracle vector exercises this, and it does not affect `/extra` (ASCII with `\n` only).
- **Naming overlap.** The `/extra` id (summary-control, want=False) is distinct from the oracle contract's "subset extra-field control" (counter kind, an accepted extra-fields case). The ids differ, so this is only a naming overlap with no decision impact.

## Evidence index
- `souji-shokunin/census/round-21/run-acceptance.py` @4f83fd2: `:118`, `:390-417`, `:432-450`, `:463`, `:537`
- `souji-shokunin/tests/fixtures/r22-result-oracle.py`: `:29-37`, `:40-47`, `:66-97`
- `souji-shokunin/tests/fixtures/r22-result-oracle.json`: `:1-6`, `:347-351`, `:359-393`
- `souji-shokunin/census/round-21/step-inventory.json`: `:114-125`
- `souji-shokunin/census/round-21/final-out-S1.json`: `:1555-1564`
- `souji-shokunin/.ufo/waves/round-22/preregistration.txt:1` (base `41553adb…`)
- `souji-shokunin/corpus/lessons/round-22.md`: `:7`, `:16`, `:35`
