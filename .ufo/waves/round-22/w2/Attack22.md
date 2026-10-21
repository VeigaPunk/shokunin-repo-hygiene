# Attack22 — summary/carry-invariant-probe/extra (want=False)

Seat: SoujiR22.Attack22 (scout, leaf, source-only). Target code: 4f83fd222ffbd8825340221a8c426550ef891191.

## STATUS

**Source-only result: PASS for this vector and its paired positive, PARTIAL for coverage.** Read by hand, the predicate returns `matched=False` on the vector (expected `want=False`) and `matched=True` on `positive/carry-invariant-probe` (expected `want=True`). The fixture really does feed the vector's input. What it rejects, though, is the exact-list summary comparison at `run-acceptance.py:416`. That line comes from 8513d6a, which predates R22. The R22 change to the summary branch (`and not stderr` at `:463`) has no effect on this vector, and nothing 4f83fd2 changed is reachable for steps of kind summary. So the vector is a regression control. It does not discriminate the R22 change, and it is correctly grouped as `summary-control`. I found two oracle gaps; neither does harm and both predate R22. Limits: I did not run the oracle or the runner. The only computed fact is a `sha256sum` of the two oracle input files. L1 owns the real run of all 214 decisions and the 18-step acceptance run.

## 1. Stored delta reconstructed from the pinned public record and the frozen inventory (done before reading the predicate)

- Public record (`census/round-21/final-out-S1.json:1935-1944`, under `"commands"` at `:28`, the only record with this name): `returncode: 0`, `stderr: ""`, `stdout: "SUMMARY paragraphs=400 boundary_cuts=562 midline_cuts=842 violations=0\n"`, `matched: true` at `:1922`, `summary_lines: 1` at `:1933`.
- Frozen inventory (`census/round-21/step-inventory.json:142-152`): `kind: "summary"`, `expected_summary` set to that same single line, `pass_pattern: null`, `pass_count: 0`. There is no `baseline_mismatch_count` key and no `<REV>` or `<REVISION>` token. The argv contains only `<PYTHON>` and `<ROOT>`, which `replace_revision` leaves alone.
- Vector (`tests/fixtures/r22-result-oracle.json:484-489`): stdout is the original line followed by `SUMMARY invalid synthetic summary\n`. It overrides neither `returncode` nor `stderr`.
- **Delta:** one extra line matching `SUMMARY_RE` is appended after the real summary line. Everything else is inherited from the record (`rc=0`, `stderr=""`).

## 2. Is the expected decision correct?

Yes. The inventory's expected summary is a single non-empty string, and the contract it encodes is that exactly one summary line is present and it equals that string. Emitting a second, contradictory SUMMARY line makes the producer's output ambiguous, so `want=False` is the conservative and correct literal. The extra line `SUMMARY invalid synthetic summary` does match `^(?:SUMMARY|SELFTEST)(?:\t| ).*$` (`run-acceptance.py:118`), because "SUMMARY" is followed by a space, so it reaches the comparison and is not silently ignored.

## 3. Does the fixture actually feed that input?

Yes.
- Both input hashes match the oracle header (`oracle.json:4,6`): `bc53a752…38fe` and `8b7b1cd8…1310`, computed with `sha256sum`. That means `inputs()` (`oracle.py:28-37`) does not raise `R22-ORACLE-INPUT-TAMPERED`.
- `oracle.py:67` selects the record by step name. `:68` takes `case['stdout']`. Neither `:69` nor `:72` fires, because the vector has no depth key and no `json_set`. `:83-85` deep-copies the frozen step and skips the cache-demo branch. `:87-91` passes `returncode=0` and `stderr=""` from the record, with stdout UTF-8/surrogateescape encoded (the identity transform here, since the text is ASCII).
- I compared the working tree with 4f83fd2 for all five named data and code paths (`git diff --stat`): there is no difference. The runner's live step (`run-acceptance.py:330-332`) has the same expected summary, pattern and count as the frozen inventory.

## 4. Hand trace of `summarize_result` (`run-acceptance.py:390-465`)

| Line | Vector | Paired positive |
|---|---|---|
| 395 `summary_lines` | `[L1, "SUMMARY invalid synthetic summary"]` | `[L1]` |
| 396 `failures` | `[]` | `[]` |
| 410 `matched = rc==0 and not failures` | True | True |
| 416 `summary_lines == [expected]` | **False** | True |
| 432-436 auxiliary `[]==[]` | True, so summary_match stays False | True |
| 440 `baseline_mismatch_count` | absent, skipped | absent, skipped |
| 446-450 pass_pattern None, `0==0` | True | True |
| 463 `… and not stderr` | False (stderr `""` makes no difference) | True |
| 464-465 no `VIOLATION\t` line | False | True |
| Result versus want | False vs False: **agree** | True vs True: **agree** (also matches public `matched: true`) |

## 5. Attack on the changed predicate

- **36c78ba, `:463` (`and not stderr`):** the vector's stderr is `""`, so this term is True and has no effect. Remove it and the vector still returns False because of `:416`. Under the pre-36c78ba runner (blame on `:416` gives 8513d6a) the vector also returns False. **The vector does not discriminate the R22 change.** The positive's stderr is `""` too, so `:463` costs it nothing.
- **4f83fd2:** it rewrote `numeric_leaves` (`:362-372`, only called on the counter path at `:472-482`) and added `RecursionError` to the `except` clauses at `:469` and `:496`, which belong to the counter and cache-demo branches. None of these lines run for a summary-kind step. No harm and no change for either vector.
- I found no concrete mismatch between the oracle's expected value and the code's decision for either vector.

## 6. Coverage gaps (none introduced by R22; recorded for L1)

1. **The extra summary line is always appended last.** All 12 occurrences of `invalid synthetic summary\n` in the oracle are the final line of their stdout, and they correspond to the 12 summary-control vectors (12 summary-kind steps). Two mutants of `:416` survive every summary-control, positive, exit and stderr vector:
   - **M-last:** `summary_lines[-1:] == ([expected] if expected else [])`. On this vector it returns False (the last line is the invalid one), which agrees with the oracle. It would wrongly accept `SUMMARY invalid…\nSUMMARY <expected>`.
   - **M-dedup:** `sorted(set(summary_lines)) == ([expected] if expected else [])`. On this vector it returns False, which agrees. It would wrongly accept the expected line repeated twice. No vector feeds a duplicate identical summary line.
2. **The carry-specific `VIOLATION\t` guard (`:464-465`, from 8513d6a) is untested.** A grep of the oracle JSON finds no `VIOLATION` string. Deleting lines 464-465 survives all 214 vectors [INFERENCE from that grep and the 214 group total: 5+33+1+18+14+20+62+49+12].

## 7. Drafted mutation (not executed)

- **M1 (killed):** change `run-acceptance.py:416` to `summary_lines[:1] == ([expected] if expected else [])`. Expected killed vector: `summary/carry-invariant-probe/extra`, which would observe True against want False. The positive stays True. (`expected in summary_lines` is killed the same way.)
- **Survivors M-last, M-dedup and the deletion of `:464-465`:** each needs a new vector to kill it. Respectively: an invalid SUMMARY line placed before the real one; the expected line doubled; and the original stdout plus `VIOLATION\tsynthetic\n` with want=False. I am not adding any of these, since this seat edits nothing outside its report.

## Tools and scope

I installed or updated no tools. Commands used, all read-only: `git show` and `git blame` on the named paths at 4f83fd2 and 36c78ba, `git diff --stat` comparing the working tree with 4f83fd2 for the named paths, `sha256sum` of the two oracle inputs, and `rg` on the named oracle JSON and receipt. I made no runs or probes, delegated nothing, and contacted no peers.
