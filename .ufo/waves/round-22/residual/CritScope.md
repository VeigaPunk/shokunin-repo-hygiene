STATUS: PASS

# CritScope — R22 C1 no-harm/scope residual critique

Seat: SoujiR22R.CritScope-17 (critic, non-author). Target: base 41553adb139d06511dc386bb3ce4326aebfba675 vs lane `master` (81a2646d53f914a226b6faa96e69ee5d01e8d348).
Tooling: no installs or updates. Only file written: this report.

## Verdict per axis

| axis | verdict | basis |
|---|---|---|
| calibration | NO HARM | Current runner passes 225/225 and the base passes 69/225 (fail 156). The first 214 cases are unchanged. All three pinned real receipts (S1, S2 and S3) grade 18/18 on both runners. Two minor prereg-wording extensions are declared, not hidden (see below). |
| operability | NO HARM on pinned evidence | `main()`, clone/replay, `CHILD_ENV` and subprocess calls are byte-identical. 0 of 54 recorded real step results have nonempty stderr. Residual tradeoff: the 12 summary steps now inherit stderr sensitivity to the interpreter (see Counterexample). |
| coverage | NO HARM | F5 `tools/souji-proc-census.sh`, `step-inventory.json` and `final-out-S1.json` are blob-identical to base. There is no coverage claim, and SCORECARD's coverage row says "r22 no expansion claimed". |

## Observed (commands I ran)

1. Byte identity. Each pair below is the `git rev-parse <rev>:<path>` blob for base and then master:
   - `tools/souji-proc-census.sh`: a1bddfee… / a1bddfee…
   - `census/round-21/step-inventory.json`: 09c4d591… / 09c4d591…
   - `census/round-21/final-out-S1.json`: eb385ba2… / eb385ba2… (sha256 bc53a752…38fe, equal to the oracle's `source_receipt_sha256`)
   - `census/round-21/run-acceptance.py`: 1ecbad09… → a62d67d5…. Worktree sha256 is 00d0e9c2…e080a6, equal to `git show master:` | sha256sum.
2. Runner diff scope (`git diff -U0 41553adb… master -- census/round-21/run-acceptance.py`). Every hunk header falls inside the `COUNTER_EXPECTATIONS` tail (new `CACHE_CHECK_NAMES` and `CACHE_CASE_PHASES` constants), `numeric_leaves` (iterative walk), the new `json_exact`, or `summarize_result`. There are 73 insertions and 17 deletions.
   - The tail from `def main` to EOF has the same sha256 on base and current: f482304c…691c. The tail from `def write_exclusive` to EOF also matches: 2f931d42…3775. The head up to `COUNTER_EXPECTATIONS` also matches: abe0a7c6…f8ee.
   - Therefore `main()`, clone/checkout, `CHILD_ENV` (current runner lines 108–116), and every `subprocess.run` call (current lines 274, 561, 582, 628, 637, 641 and 670) are unchanged.
   - `grep` shows that `numeric_leaves`, `json_exact`, `CACHE_CHECK_NAMES` and `CACHE_CASE_PHASES` are referenced only at current lines 473–533 inside `summarize_result`. `summarize_result` is called only at line 679, which is unchanged context.
3. Oracle on the current runner (`python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py`): exit 0 with pass 225 / fail 0, and no vector raised an exception.
   - Groups: positive 20/20, exit 18, stderr 49, scalar 62, cache-names 33, cache-cases 5, cache-value 1, malformed 14, summary-control 12, adequacy 11.
   - The positive group is the 18 real steps plus 2 synthetic tolerance controls: `subset-extra-fields` and `cache-transient-path-and-time`.
4. Base graded in memory (`git show 41553adb…:census/round-21/run-acceptance.py | python3 -B census/round-22/mutation-adequacy.py --grade-stdin`): pass 69, fail 156, finding `R22-RESULT-CONTRACT`, runner sha256 1141839…eaa2b.
5. Oracle prefix. Canonical JSON of `cases[:214]` equals `git show b912328…:tests/fixtures/r22-result-oracle.json` `cases` (True). The non-case keys are equal, and the 11 appended cases are all `group: adequacy`.
6. Real-receipt regrade. I loaded both runners in memory and fed every recorded step of `final-out-S1/S2/S3.json` (all measured at ff425ab8…, all `all_matched: true`) through `summarize_result`, using the oracle's step construction: S1, S2 and S3 each grade base 18/18 and current 18/18.
   - S2 and S3 are extra real-replay samples that the oracle does not consume, since it pins S1 only.
7. Stderr in the pinned receipts. S1, S2 and S3 each have 0 steps with nonempty `stderr` and 0 steps with a nonzero return code: 0 of 54 step results.
8. Typing in the pinned receipts.
   - The 5 counter steps pass `json_exact` against the frozen expectations (4 `exact_json`; `r13-counter-b576341` is subset mode with 5 extra observed keys, which is accepted).
   - The frozen expectations contain no float or `None` leaves, so the `.get` → `key in` change cannot flip a real step.
   - In the cache demo, the set of check names equals `CACHE_CHECK_NAMES` (33), the phases equal `CACHE_CASE_PHASES` in order, `failed_checks` is `[]` (list), and `producer_executions_new_policy` is `3` (int).
   - These results hold in S1, S2 and S3.
9. Compile-time warning scan. I compiled all 16 `<ROOT>/*.py` producers from the step argv, at both ff425ab8 and master, with `warnings.simplefilter('always')` under Python 3.14.8: 0 warnings.

## Counterexample (strongest found): interpreter-drift stderr RED

The pinned receipt records `argv[0] = /usr/bin/python3` but not its version. `CHILD_ENV` (current runner lines 108–116) does not set `PYTHONWARNINGS`, and `-B` with `PYTHONDONTWRITEBYTECODE=1` means producers recompile on every run.

[INFERENCE] Suppose a future host interpreter emits a `SyntaxWarning` or `DeprecationWarning` in any of the 12 summary-kind producers, without the FAIL-marker vocabulary `failure_lines` scans for. The base runner would stay GREEN and the current runner would turn RED (current line 463, `and not stderr`).

Why this is a tradeoff, not harm:
- The 6 counter and cache-demo steps already had exactly this sensitivity at base (base lines 445 and 480 were `not stderr`), so the change unifies an existing contract.
- The R22-M2 lesson and Q51 choose "reject any nonempty summary stderr rather than suppress warnings", and the lesson keeps diagnostics in the result.
- No pinned receipt and no compile-time scan shows a current trigger.

The impacted axis is operability (replay robustness across host upgrades). Smallest safe correction: a doc-only note in the SKILL `r21-acceptance` row or the round-22 lesson. It should say that a summary-stderr RED after an interpreter change is a contract RED that needs diagnosis, not a false RED to suppress. It should also say that replay receipts do not record the interpreter version. Adding the interpreter version to receipts would touch `main()` and belongs in a separate claim, not C1.

## Claims beyond the three defects and the malformed boundary?

There is no runner-behavior overclaim. Two prereg-wording extensions are declared in the docs:

- Preregistration 29c1f7e8 names "JSON bool/int scalar confusion". The implementation and docs (Q51, the SKILL row, lesson line 7) also reject int/float, such as `3.0` vs `3`. That is the same type-identity repair carried one step further, and it is declared.
- Preregistration says "cache checks counted rather than identified". The implementation also pins the four ordered phase labels (`CACHE_CASE_PHASES`, current lines 204 and 512–513). This is declared in Q51, the SKILL row and lesson line 42, and it passes on all three real receipts.
- The iterative `numeric_leaves` walk, the `RecursionError` catches (lines 469 and 496), the `int()` overflow catch (lines 428–431) and the `isinstance(gate/isolation, dict)` guards all fall under the preregistered "Reject malformed producer data without a crash". The lesson explicitly disclaims arbitrary resource exhaustion (line 71), and S107 marks the depth threshold as an interpreter observation.
- SCORECARD calibration claims mutation adequacy 21/21 and the Q52 criterion. These are claims about oracle adequacy, not runner behavior, and they stay on the calibration axis.
- SCORECARD operability says "r22 no separate operability claim", and coverage says "r22 no expansion claimed". The lesson (line 84) correctly says the real 18-step replay was not run this round and that empty pinned stderr is "evidence about those outputs, not a fresh replay".
- "Positive controls 20/20" is accurately split elsewhere into 18 real steps plus 2 synthetic controls, so it is not presented as 20 real steps.

## Not checked

- I did not run the real acceptance `main()`, the replay matrix, or any producer, as the assignment forbade it. Runtime-only warnings (`DeprecationWarning` raised during execution, not compilation) are therefore unobserved.
- I did not review the adequacy-vector semantics or mutation-probe correctness; those belong to the ResidAdequacy and CritMutation seats.
