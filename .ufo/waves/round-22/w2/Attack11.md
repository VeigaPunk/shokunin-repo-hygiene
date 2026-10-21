# Attack11 — `stderr/r19-revision-pin-fixture/error` (want=False) + paired positive

Seat: SoujiR22.Attack11 (leaf, source-only, no execution, no delegation). Target code `4f83fd222ffbd8825340221a8c426550ef891191`; base `41553adb139d06511dc386bb3ce4326aebfba675`.

## STATUS

**PASS (source-only).** The expected decision `want=False` is correct under the round-22 contract. The fixture really does feed the overridden stderr into the summarizer. In the changed predicate, the only conjunct that can be false for this vector is the new `and not stderr`, so the vector discriminates base from changed. The paired positive, `positive/r19-revision-pin-fixture` with want=True, stays True. I found no concrete mismatch.

Limits: I traced decisions by reading source only and ran nothing. L1's 214-vector run and the real 18-step acceptance are still the runtime evidence. Under the contract I could not read the producer `tests/fixtures/r19-rev-pin.py` (see the gaps section).

## Input bindings (observed)

These hashes were computed with `sha256sum`. That is reading bytes, not running anything under test.

- `census/round-21/final-out-S1.json` = `bc53a752…38fe`. This equals the oracle's `source_receipt_sha256` (`r22-result-oracle.json:4`).
- `census/round-21/step-inventory.json` = `8b7b1cd8…1310`. This equals the oracle's `frozen_inventory_sha256` (`:6`).
- The working-tree `run-acceptance.py` = `00d0e9c2…80a6`, which equals `git show 4f83fd2:census/round-21/run-acceptance.py`.
- The working-tree oracle `.json` = `292442a6…0651` and `.py` = `3c0776ae…a604`, both equal to `git show 4f83fd2:` for the same paths.
- The vector is byte-identical at the original freeze commit `36c78ba` (line 504). The `36c78ba..4f83fd2` oracle diff (+14/+4) has no lines matching `r19-revision-pin`.
- Not verified: that the vector existed in the pre-edit 209-vector draft. The `bindings-before` artifact is not a named input.

## 1. Stored delta and reconstruction (done before reading the predicate)

The stored delta is at `r22-result-oracle.json:503-509`. It overrides only `stderr = "ERROR: synthetic producer incomplete\n"`. It has no `returncode`, `stdout`, `json_set` or depth key.

The oracle driver builds the input in `r22-result-oracle.py`:

- **Record lookup (`:58`, `:67`):** `records[step_name]`. The receipt has a top-level `commands` list (`final-out-S1.json:28`), and `"name": "r19-revision-pin-fixture"` appears exactly once (`:2128`).
- **stdout (`:68`):** taken from the record, `final-out-S1.json:2136`. It contains 19 `CASE` lines plus `SUMMARY total=13 failed=0 base_discriminating=6`. Its SHA-256 `b966…e77c` is recorded at `:2137`.
- **returncode (`:88`):** taken from the record, `0` (`:2133`).
- **stderr (`:90`):** `case.get('stderr', …)`, which returns the override. The override is UTF-8 encoded with surrogateescape, and the runner's `decode_exact` (`run-acceptance.py:223-224`) round-trips it exactly.
- **Step (`:59-60`, `:83`):** a deep copy of the frozen inventory entry (`step-inventory.json:154-168`): `kind=summary`, `expected_summary="SUMMARY total=13 failed=0 base_discriminating=6"`, `pass_pattern="^CASE\tpass\t"`, `pass_count=13`. `replace_revision` touches only `<REV>`/`<REVISION>`. The `<PYTHON>`/`<ROOT>` argv placeholders feed only `shlex.join`, which does not affect the decision.
- **Frozen step equals live step for decision fields:** `make_steps` (`run-acceptance.py:333-335`) holds the same three values. An absent `kind` defaults to `summary` (`:411`, `:600`). The live run refuses if the projection differs from the frozen inventory (`:657-658`).

**Expected decision:** False. The contract says summary stderr must be zero bytes (`corpus/lessons/round-22.md:7`). R22-M2 says to reject any nonempty summary stderr rather than expand marker spellings (`:16`). Preregistration C1 names the defect "summary stderr accepted despite success" (`preregistration.txt:1`). The original real record has `stderr ""` with SHA-256 `e3b0c442…b855` (the empty-string digest), at `final-out-S1.json:2134-2135`. So the only difference between the positive and this vector is the injected stderr. **The expected decision is correct, and the fixture does feed that input.**

## 2. Changed predicate traced for this vector (`run-acceptance.py` @4f83fd2)

| Step | Lines | Value for this vector |
|---|---|---|
| `summary_lines` | 395, `SUMMARY_RE` 118 | `["SUMMARY total=13 failed=0 base_discriminating=6"]` |
| `failures` | 396, 356-359 | `[]`. The stderr line does not start with `FAIL\t`/`CASE\tFAIL\t`. The `CASE\tdiscriminates\t…\texit=0` and `CASE\tpass\t…` lines do not match `^CASE\t[^\t]+\tFAIL(\t\|$)`. |
| `matched` (initial) | 410 | `0 == 0 and not []`, which is True |
| `summary_match` | 416, 432-435 | `[expected] == summary_lines` is True. `INVENTORY` lines: `[] == []`. No `baseline_mismatch_count` key. |
| `pass_match` | 446-450 | `re.findall(^CASE\tpass\t, MULTILINE)` gives 13 (8 named cases + 5 `wiring/…`), which equals 13. This agrees with the record's `observed_pass_lines: 13` (`final-out-S1.json:2124`). |
| **changed conjunct** | **463** `and not stderr` | `stderr = "ERROR: synthetic producer incomplete\n"` is truthy, so the conjunct is **False** |
| carry-probe clause | 464-465 | not applicable (different step name) |
| result | 537 | `matched = False`, which equals want False, so the vector passes |

- **Base (`41553adb`, from the diff):** line 463 was `matched = matched and summary_match and pass_match`, with no stderr term. `failure_lines` is unchanged. Base observes True, which does not equal want, so the vector fails on base. This is a genuine before/after discriminator, and the decisive term is the changed conjunct alone. Every other conjunct is True on both base and changed.
- **Paired positive (`r22-result-oracle.json:491-495`):** there is no override, so stderr comes from the record as `""`. `not ""` is True and every other conjunct is as in the table above, so the result is True, which equals want True on both base and changed. Strict stderr does no harm to this real r21 output.

## 3. Attacks on the predicate

1. **Byte strictness.** `not stderr` tests the decoded string. Surrogateescape maps every nonzero-length byte string to a nonzero-length string, so the test is exactly "zero bytes". This covers whitespace and invalid UTF-8, as claimed at lesson `:7`. For this vector, nothing is ambiguous.
2. **Scope of the change.** Only the `summary` branch changed. The `counter` (`:492`) and `cache-demo` (`:536`) branches already had `not stderr` at base, since the diff shows no change on those lines. There is no regression there.
3. **Diagnostics retained.** `result["stderr"]` and `stderr_sha256` are still recorded (`:403`, `:405`), so nothing is suppressed, as R22-M2 requires.
4. **Weak isolation as a single vector (observation, not a defect).** A rejected-approach mutant would also make this vector observe False: one that expands marker spellings, for example adding `ERROR` to `failure_lines`. So this vector alone does not separate "strict empty stderr" from "expanded markers". The sibling vectors do separate them: `/blank` (`"\n"`), `/warning` and `/pass` (`"PASS\tsynthetic stderr\n"`) at `r22-result-oracle.json:510-530`. Group-level coverage is adequate.
5. **Live feed.** The child runs with `stderr=PIPE` and its stderr goes straight to `summarize_result` (`:670-679`). An `OSError` substitutes nonempty stderr with `returncode=None`, which is false anyway.

## Mutation drafted (not executed)

- **M11-1:** at `run-acceptance.py:463`, delete `and not stderr`, restoring the base line.
  - Expected killed vector: `stderr/r19-revision-pin-fixture/error`, which would observe True against want False.
  - The paired positive survives (True against True), and the other three stderr siblings for this step are also killed.
- **Survivor note:** `and not stderr.startswith("ERROR")` is not killed by this vector, but it is killed by `/blank`, `/warning` and `/pass`.

## Remaining unknowns / gaps

- **Producer stderr in the live run:** I could not read `tests/fixtures/r19-rev-pin.py` (not a named input). Whether it, or the git grandchildren that inherit its piped stderr, can write warnings during the real 18-step replay is unknown. The only evidence is the r21 public record, where stderr was empty. If they do write warnings, the strict predicate will correctly turn this positive False. That is an operability risk, and only L1's actual acceptance run settles it.
- **Draft freeze:** I did not verify that the vector predates the summarizer edit beyond commit `36c78ba`.
- **Tools:** none installed or updated.
