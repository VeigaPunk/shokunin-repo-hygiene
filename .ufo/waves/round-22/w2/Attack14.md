# Attack14 — `summary/revision-helper-selftest/extra` (want=False) + paired positive

Seat: SoujiR22.Attack14 (leaf, source-only). SUT: `4f83fd222ffbd8825340221a8c426550ef891191` (HEAD; working-tree
`census/round-21/run-acceptance.py` sha256 `00d0e9c2…80a6` == `git show 4f83fd2:` bytes). Baseline per
preregistration: `41553adb139d06511dc386bb3ce4326aebfba675`.

## STATUS

**PASS (source-only), with one oracle-coverage PARTIAL.** I reconstructed the vector's delta exactly from the
pinned public record. The expected decision (False) is correct. The fixture really feeds this vector's stdout
into `summarize_result`. I traced the changed runner by hand: it rejects the extra-summary vector and accepts the
paired positive. I found no mismatch between the oracle and the code. Gap: this vector cannot calibrate C1. Its
False decision comes from a strict summary-line comparison that has been in the runner since `8513d6a`, before
the baseline. Every multi-summary vector also appends the bad line *after* the real summary, so a
"last summary line wins" mutation would survive the whole oracle. Limits: static reasoning only. I did not
execute the runner, the oracle, or any mutation; L1 owns the 214-decision run.

## 1. Delta reconstruction (before predicate inspection)

- Oracle inputs are pinned and match: `final-out-S1.json` sha256 `bc53a752…38fe`, `step-inventory.json`
  `8b7b1cd8…1310` (equal to `r22-result-oracle.json` lines 3–6).
- Public record `final-out-S1.json:398-407`: `returncode` 0, `stderr` "", stdout = 11 `CASE\tpass\t…` lines +
  `SUMMARY total=11 failed=0\n`; recorded `stdout_sha256` 428a3217… recomputes equal.
- Frozen inventory `step-inventory.json:21-32`: `kind` "summary", `expected_summary` "SUMMARY total=11 failed=0",
  `pass_pattern` `^CASE\tpass\t`, `pass_count` 11; no `baseline_mismatch_count`, no `<REV>`/`<REVISION>` tokens.
- Stored delta (`r22-result-oracle.json:99-105`): keys only `{id, want, group, step_name, stdout}`. I checked it
  with stdlib `json` string equality on fixture data, without importing the runner or the oracle:
  `case.stdout == record.stdout + "SUMMARY invalid synthetic summary\n"` → **True**. There is no returncode or
  stderr override, so the vector inherits rc 0 and stderr "". Single-axis mutation: one appended SUMMARY line.
- The same exact append holds for all 12 `summary/*/extra` vectors.

## 2. Is the expected decision correct?

Yes. The summary contract is exact equality on the list of summary lines (`run-acceptance.py:416`
`summary_lines == ([expected] if expected else [])`). A second `SUMMARY ` line makes the producer's summary
ambiguous, so rejecting it is right. Under the hand trace, False is the only possible result:
- `SUMMARY_RE` (`:118`, `^(?:SUMMARY|SELFTEST)(?:\t| ).*$`) matches both `SUMMARY total=11 failed=0` and
  `SUMMARY invalid synthetic summary`. The list has 2 elements, which is not `[expected]`, so `summary_match` is False.
- Every other conjunct is True, which isolates the cause. `failure_lines` (`:356-359`) finds no FAIL lines. The
  pass count from `re.findall(^CASE\tpass\t, MULTILINE)` is 11 == 11 (`:446-450`). There are no auxiliary lines,
  so the `INVENTORY` list is `[] == []` (`:432-435`). The baseline-mismatch check is skipped (`:440`). stderr is
  "", so `not stderr` is True (`:463`).
- So `matched` = rc0 ∧ no failures ∧ **summary_match=False** … → `bool(False)` (`:537`), and it agrees with want=False.

## 3. Does the fixture actually feed it?

Yes. `r22-result-oracle.py:67-68` takes the record by `step_name`, then `stdout = case.get('stdout', …)`. That is
the delta string. The `json_set` and nested-depth branches are absent. `:83` deep-copies the inventory step
(`replace_revision` is a no-op here). The step is not `cache-demo`. `:87-91` passes rc 0 and stderr "" from the
record, encoded with UTF-8/surrogateescape (ASCII, so the round trip is exact) to `module.summarize_result`. `:97`
requires `type(observed) is bool and observed is want`. The runner's own `make_steps` row (`:304-305`) is
identical to the frozen inventory row, so the oracle's step equals the step that acceptance itself uses.

## 4. Attack on the changed predicate

- **What changed vs. baseline:** `git log -L` shows the summary-list equality and `SUMMARY_RE` unchanged since
  `8513d6a` (baseline `41553ad` has identical lines 118/373). `36c78ba` only adds `and not stderr`
  (`:463`). `4f83fd2` touches only `numeric_leaves` and the counter/cache `RecursionError` catches. Neither
  change is reachable in a way that alters this vector.
- **Discrimination:** I expect baseline and changed both to return False for this vector [INFERENCE: baseline
  `:417` lacks `not stderr`, but stderr here is ""]. It is a **non-discriminating no-harm control**, not C1
  calibration evidence. Counting it as a before→after improvement would be an overclaim.
- **Paired positive `positive/revision-helper-selftest` (want=True):** the record is fed unmodified. One summary
  line equals expected, the pass count is 11, there are no FAIL lines, auxiliary is `[]`, and stderr is "", so
  matched is True. No mismatch. Base and changed are both True, so this is a no-harm control too. The changed
  `not stderr` cannot harm it because the recorded stderr is zero bytes (`final-out-S1.json:404-405`, sha256
  e3b0c442… = empty).

### Drafted mutations (not executed)

| mutation at `:416` | extra (want F) | positive (want T) | killed by this vector? |
|---|---|---|---|
| M1 `expected in summary_lines` | T | T | **yes** |
| M2 `summary_lines[:1] == [expected]` | T | T | **yes** |
| M3 `summary_lines[-1:] == ([expected] if expected else [])` | F | T | **no** |
| M4 dedupe `list(dict.fromkeys(summary_lines)) == …` | F | T | **no** |

- **M3 survives the whole oracle [INFERENCE, static enumeration over fixture data].** I scanned every
  summary-kind vector. The only vectors with more than one summary line are the 11 non-empty `/extra` controls,
  and each one puts the real summary first and the injected line last. `summary/agreement-pin-check/extra`
  (expected "") has one line and stays False under M3. A vector that **prepends** the bad line, for example
  `SUMMARY invalid synthetic summary\n` + record stdout, would kill M3. Expected decision for it: want False.
- **M4 also survives.** No vector repeats the identical expected summary line twice, for example a record whose
  `SUMMARY total=11 failed=0` line is duplicated. Exact list equality rejects that output today, but the oracle
  does not pin that behaviour.
- Both are mutation-coverage gaps in the oracle, not defects in the `4f83fd2` code. The current code (exact list
  equality) rejects both proposed inputs.

## 5. Out-of-scope residuals (not falsifications)

- Non-`SUMMARY_RE` lookalikes are ignored by design, so an extra `SUMMARY:` line or a lowercase `summary …` line
  would be accepted. The lessons file (`corpus/lessons/round-22.md:32`) excludes "arbitrary stdout failure-marker
  semantics", so this is not a falsification.
- Line-model split: `splitlines()` (summary and FAIL lines) honours `\r`, `\x0b`, `\x1c`, U+2028 and similar,
  while the pass count uses `re` `^` with MULTILINE (`\n` only). This is not exploitable to hide an extra summary
  line: any separator still yields a second summary line. Noted only.

## Tooling

No installs or updates. I used the existing `jq` (jaq 3.1.1, `~/.local/bin`); it failed to parse the oracle
fixture at byte 164988, which looks like the lone-surrogate stderr vector at line 4081. I fell back to
`python3 -B -I` with stdlib `json`, comparing fixture data only. I did not import or execute the runner or the
oracle.
