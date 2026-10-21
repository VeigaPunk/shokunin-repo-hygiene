# Attack07 — vector `stderr/landing-gate-selftest/error` (want=False)

Seat: SoujiR22.Attack07 (leaf, source-only). Target code `4f83fd222ffbd8825340221a8c426550ef891191`; base `41553adb139d06511dc386bb3ce4326aebfba675`.
I did not run the runner, the oracle harness, a test, a build or a mutation. Tools used: Read/Grep, plus `sha256sum`, `git show`/`git diff` for the named paths, `jq`/`awk` field counts on the public receipt, and a `python3 -B -c` JSON parse of the oracle fixture (data parse only; the SUT was not imported). No installs or updates.

## STATUS

**PASS, source-only.** The literal decision want=False is correct under the round contract. The fixture really feeds the synthetic stderr into `summarize_result`. Base accepts the vector (observed True, so the base runner fails it); changed rejects it (observed False, so it passes). The paired positive keeps want=True under the changed predicate. I found no concrete mismatch for this vector.

Limits: none of this was executed; L1's run of all 214 vectors and the 18-step acceptance is the authority. My claim covers this vector and its positive only. It is not a malicious-producer attestation, and the F5, reap, NAMESPACE, exposure and K5 holds are unchanged.

## 1. Reconstructing the stored delta from pinned public inputs (before looking at the predicate)

Input pins, observed by `sha256sum`:
- The working-tree `census/round-21/final-out-S1.json` hashes to `bc53a752…38fe`, which equals the oracle's `source_receipt_sha256` (oracle json lines 3–4). `git show` returns the same bytes at both base and `4f83fd2`.
- The working-tree `census/round-21/step-inventory.json` hashes to `8b7b1cd8…1310`, which equals `frozen_inventory_sha256` (line 6). It is also identical at base and pinned.
- The working-tree `census/round-21/run-acceptance.py` equals `git show 4f83fd2:` byte for byte (`00d0e9c2…80a6`).

Vector (oracle json lines 311–317): `{"id":"stderr/landing-gate-selftest/error","want":false,"group":"stderr","step_name":"landing-gate-selftest","stderr":"ERROR: synthetic producer incomplete\n"}`. Its keys are exactly `group, id, stderr, step_name, want`. There is no stdout, returncode or json_set override. The 214 case ids are all unique.

Original public record (`final-out-S1.json` `commands[]`, name `landing-gate-selftest`, around lines 1351–1373):
- returncode 0
- stderr `""` (`stderr_sha256` is the empty-string hash `e3b0c442…`)
- `failure_lines []`, `observed_summary ["SELFTEST\tpass=65\tfail=0"]`, `matched true`
- the stdout bytes re-hash to the stored `stdout_sha256` `fa10064c…7c14`
- stdout has 66 lines: 65 match `^CASE\tpass\t`, 1 is the SELFTEST line, and there are 0 FAIL-marker lines, 0 `INVENTORY\t` lines and 0 `BASELINE_MISMATCH\t` lines. It ends with `…fail=0\n`.

Frozen step (inventory lines 100–112): kind `summary`, `expected_summary "SELFTEST\tpass=65\tfail=0"` (a string), `pass_pattern ^CASE\tpass\t`, `pass_count 65`. There is no `baseline_mismatch_count`.

The stored delta is therefore exactly one field: stderr goes from `""` to `"ERROR: synthetic producer incomplete\n"`. Returncode, stdout, step and revision all come from the pinned record and inventory.

## 2. Does the fixture actually feed that input?

Yes. In `tests/fixtures/r22-result-oracle.py`:
- Line 67 resolves `records[case['step_name']]` from `receipt['commands']`; the receipt's top-level key `commands` is at line 28, and the name is unique.
- Line 68 keeps the record stdout.
- Line 88 takes `case.get('returncode', record['returncode'])`, which is 0.
- Line 90 takes `case.get('stderr', record['stderr'])`, which is the synthetic ERROR text, encoded with `surrogateescape`.
- Lines 59–60 load the step from the hash-checked inventory; `replace_revision` touches only `<REVISION>`/`<REV>`.
- Line 97 is `observed is case['want']` (bool identity).

The ASCII stderr round-trips through `decode_exact` (runner line 223–224) unchanged and non-empty.

Fixture provenance: the oracle `.json` and `.py` are absent at base (`git diff --stat` shows both added, +4105 and +118 lines). "Same committed fixture on base and changed" therefore means the pinned fixture run with `--runner <base runner>`. That is valid because base `summarize_result` has the identical signature (diff context at runner line 390).

## 3. Is want=False correct?

Yes. The oracle contract (json line 8) says "Reject nonempty summary stderr". Preregistration defect #2 is "summary stderr accepted despite success". `corpus/lessons/round-22.md` line 7 says "Summary stderr must be zero bytes", and line 16 (R22-M2) says to reject any non-empty summary stderr rather than expand marker spellings. This vector is step kind `summary` with exit 0, so want=False follows literally.

## 4. Base behaviour, which shows the vector discriminates

Base line `matched = matched and summary_match and pass_match` (confirmed by `git show 41553ad:`) has no stderr term. `failure_lines` (runner lines 356–359) matches only `FAIL\t`, `CASE\tFAIL\t` and `CASE\t…\tFAIL`. The combined text (line 396) is stdout, a `"\n"`, then `ERROR: synthetic producer incomplete`, and the ERROR line matches none of those markers. So `failures` is `[]`.

Walking the base predicate: returncode 0, then `summary_lines == [expected]` (line 416, via `SUMMARY_RE` at line 118), auxiliary `[] == []`, `pass_count 65 == 65`. Base observes True, which is not want=False, so base fails the vector. That is the intended "before" kill.

## 5. Changed predicate, attacked for this vector

The only change in the summary branch is line 463: `matched = matched and summary_match and pass_match and not stderr`. The `try/except ValueError` at lines 427–431 is unreachable here because `expected_summary` is a string.
- Here `stderr` is a non-empty str, so `not stderr` is False, matched is False, and `bool(False)` at line 537 gives observed False. The vector passes.
- `surrogateescape` decoding never maps non-empty bytes to an empty str, so no non-empty byte input can slip through the conjunct. This also covers the sibling `blank` (`"\n"`) vector.
- The gate is not order-dependent: `not stderr` is a pure conjunct evaluated after `summary_match` and `pass_match`, and nothing in the summary branch can raise on this input.
- The `carry-invariant-probe` special case (lines 464–465) does not apply to this step name.
- `result["stderr"]` keeps the raw text (line 403), so diagnostics are retained, not suppressed, matching lesson line 7.

## 6. Paired positive `positive/landing-gate-selftest` (want=True)

This uses the record unchanged:
- returncode 0, `failures []` (0 marker lines).
- Summary `["SELFTEST\tpass=65\tfail=0"]` equals expected.
- Auxiliary `[]`, pass_count 65.
- stderr `""`, so `not stderr` is True.

Observed True, which equals want, so there is no harm to the positive control. This agrees with the public record's `matched: true` and `matched_counts` (pass 65/65, summary_lines 1).

## 7. Drafted mutation (not executed)

- **M-07a:** delete `and not stderr` from runner line 463, which restores base. Expected killed vector: `stderr/landing-gate-selftest/error` (observed True ≠ False). The positive stays True. All 4 stderr vectors for this step, and the stderr vectors of every other summary step, die too.
- **M-07b, specific to this vector:** replace it with `and not (stderr.strip() == "" and stderr)`, i.e. reject only whitespace-only stderr. Expected killed vectors: `/error`, `/pass` and `/warning`. `/blank` survives.

## Observations (no decision mismatch)

- **O1:** the strict stderr rule cites no external source row. S104–S106 in `SOURCES.md` cover JSON typing and bool equality; stderr strictness rests on internal Q51/R22-M2 lessons. This is consistent with the preregistration's source scope and not a defect.
- **O2:** the operability no-harm question for the 18 real steps depends on live children emitting zero stderr. `CHILD_ENV` (runner lines 107–113) does not set `PYTHONWARNINGS`, so a future interpreter warning would turn a step red. That is a fail-closed, intended direction, and the public receipt shows `stderr ""` for this step. [INFERENCE] There is no runtime evidence either way for the new code; L1's actual 18-step acceptance decides it.
- **O3:** `matched_counts` has no field recording a stderr-caused rejection. The reason is only derivable from `result.stderr`. This is diagnostic-only.

## Remaining unknowns

The actual observed values for base and changed on all 214 vectors, and the real 18-step acceptance under the changed runner. Both are reserved to L1.
