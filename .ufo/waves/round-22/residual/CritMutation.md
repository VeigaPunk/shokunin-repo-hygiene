STATUS: FAIL

Seat: SoujiR22R.CritMutation-17 (critic, residual non-author review of L1 SoujiR22R work).
Target: `census/round-22/mutation-adequacy.py` (sha256 d67e1776…f88d), receipts `mutation-adequacy-oracle214.json` (bff058fc…3924), `mutation-adequacy-oracle225.json` (00fc1c64…e710d11), `w2-dead-seat-residual.json` (af88fd7e…c3d9). Runner under test: `census/round-21/run-acceptance.py` sha256 00d0e9c2…e080a6 (matches assignment). Oracle: `tests/fixtures/r22-result-oracle.json` sha256 849a8569…a5cc.

The verdict is FAIL because a non-equivalent mutant of an r22-changed line survives all 225 vectors (finding F1). The probe's "21/21 non-equivalent killed" is complete only over the 25 mutants L1 chose to list. It does not show that the oracle is adequate for the r22-changed clauses. The probe's mechanics, the four `equivalent` labels, and the dead-seat labelling all hold up (details below).

Tooling: no installs or updates were made. Everything ran on the existing python3 3.14.8 and git. Writes: this file only. All mutants were held in memory (`python3 -B -c` with `exec(compile(...))`).

---

## Observed: the probe runs, grades in memory, and reproduces its receipts

1. `python3 -B census/round-22/mutation-adequacy.py` → EXIT=0. Pristine `{"exit":0,"pass":225,"fail":0}`. Summary `{"mutants":25,"killed":21,"survived":4,"disagreeing_with_expect":[]}`. The survivors are exactly nonexact-keyin-get, failed-checks-to-eq, names-len-constant and phases-len-constant.
2. Byte-for-byte reproduction: probe `main()` stdout captured in memory equals `mutation-adequacy-oracle225.json` (`byte-equal receipt: True`).
3. The 214 receipt was reproduced without a scratch file. I fed the historical oracle bytes (`git show b912328d…:tests/fixtures/r22-result-oracle.json`, sha256 292442a6…0651, equal to the receipt's `oracle_sha256`) into the oracle module as an in-memory object. Pristine 214/214. `rows == receipt['mutants']`: True, so the 13 disagreeing ids match L1's claim.
4. In-memory grading was checked with an audit hook. `sys.addaudithook` logged write-mode `open` calls plus `os.remove/rename/mkdir/chmod`, `subprocess.Popen`, `os.system/exec/posix_spawn/fork` across both full probe runs (225 and 214). Result: `write/spawn audit events: []`. In source, `grade()` (mutation-adequacy.py:104-122) patches `oracle_mod.load_runner` to `exec(compile(source,'<r22-mutant>','exec'))` and redirects stdout into a `StringIO`. The oracle's own `runner_sha256` field hashes the on-disk runner (r22-result-oracle.py:103), not the mutant. The probe drops that field and records `mutant_sha256` separately (line 157). In `--grade-stdin` mode it overwrites the field with the stdin hash (line 137). Both are honest.
5. Base-runner identity: `git show 41553adb…:census/round-21/run-acceptance.py | sha256sum` = 1141839963…aa2b, equal to `oracle225-baseline.json` `runner_sha256`.
6. Oracle prefix: `git diff b912328d… -- tests/fixtures/r22-result-oracle.json` has one hunk, `@@ -4102,0 +4103,127 @@`, with 0 deleted lines. The decoded first 214 cases equal the historical cases, the non-`cases` keys are equal, and all 11 appended cases are `group: adequacy`.

## Observed: each anchor mutates what its id names

I read each replacement pair against the runner lines and the base diff (`git diff 41553adb… -- census/round-21/run-acceptance.py`). Every anchor is unique: `mutate()` raises if the count is not 1, and the run did not exit 2. Mapping:

- summary-stderr → line 463, drops `and not stderr` (added in r22). json-exact-type → lines 377-378. json-exact-dict-keys → line 380. json-exact-list-len → line 384. exact-json-to-eq → line 473. nonexact-to-eq and nonexact-keyin-get → line 477. producer-exec-to-eq → lines 519-520. failed-checks-to-eq → line 518. cache-names → line 516. cache-phases → line 513. names-len-constant → line 515. phases-len-constant → line 512. gate-isinstance → line 522, prefix only. isolation-isinstance → line 523. baseline-int-guard → lines 430-431, re-raises.
- counter-recursion and cache-recursion → `RE` occurrence 0 (line 469) and occurrence 1 (line 496). The runner contains exactly two occurrences, so the indices are correct.
- Pre-existing: summary-last-only → line 416. counter-stderr → line 492. cache-stderr → line 536. gate-sha → line 522. isolation-cleaned-drop and isolation-cleaned-eq → line 524. isolation-residue → line 525.
- Origin labels agree with the base diff. The `stderr`-in-summary, `RecursionError`, `json_exact`, CACHE_* and isinstance(gate/isolation) clauses are r22 additions. The counter/cache `not stderr`, `is` cleaned, `residue == []`, the gate digest compare and the summary-line equality appear unchanged in the base. gate-sha is labelled "pre-existing clause": the clause's text was rewritten in r22, but its semantics existed in the base, so the label is acceptable.

## Per-survivor verdicts (the 4 `equivalent` marks)

Method: I ran an exhaustive in-memory differential, comparing `summarize_result` on the original runner against each mutant, with the pinned step from `census/round-21/step-inventory.json` (revision substituted exactly as the oracle does it).

| survivor | verdict under the pinned steps | distinguishing decoded-JSON input |
|---|---|---|
| nonexact-keyin-get (line 477) | EQUIVALENT, conditionally | None found: 1,091 inputs, 0 diffs |
| failed-checks-to-eq (line 518) | EQUIVALENT, conditionally | None found: 883 cache inputs, 0 diffs |
| names-len-constant (line 515) | EQUIVALENT, unconditionally; the conjunct is redundant | None possible (proof below) |
| phases-len-constant (line 512) | EQUIVALENT, unconditionally; the conjunct is redundant | None possible (proof below) |

- **nonexact-keyin-get.** The only non-exact counter is `r13-counter-b576341`, with expected `{"measured_commit": "b576…a7d3", "admitted_entries": 6}`. I tried every combination of absent/present × 19 values (null, true/false, 0/1/6/6.0/-6/7/10**30, "6", [], [6], {}, {"x":6}, the correct and an upcased commit, NaN), times 3 extra-key variants, plus eight non-dict top-level documents including a 5,000-deep array: 0 diffs. The reason: `json_exact(None, v)` is False for every non-null `v`, and no step expectation contains a null leaf (`null leaves in any step expected_summary: []`). The step is reachable only from constants: `make_steps` plus the frozen-inventory equality at run-acceptance.py:657. So the equivalence holds as deployed. Function-level counterexample (not reachable today): step expected `{"k": null}` with stdout `{}` gives orig False, mutant True. **Conditional on the invariant "no null expected leaf"**, which nothing enforces.
- **failed-checks-to-eq.** The expected value is the literal `[]` (run-acceptance.py:341). For decoded JSON, `x == []` holds iff `x` is an empty list, which is exactly when `json_exact(x, [])` holds. Differential: 14 failed_checks values × 7 checks variants × 9 cases variants, plus an absent key: 0 diffs. Function-level counterexample (not reachable): expected `[1]` with observed `[true]` or `[1.0]` gives orig False, mutant True. **Conditional on `failed_checks` being expected `[]`.**
- **names-len-constant.** Proof: `len(checks) == E ∧ checks.keys() == CACHE_CHECK_NAMES` ⇒ `len(CACHE_CHECK_NAMES) == len(checks) == E`. So the removed conjunct is implied by the two conjuncts that remain, for any step and any stdout, and removing it changes no exception path. Observed with an altered step, E ∈ {32, 33, 34, 33.0, true}: orig and mutant agree every time.
- **phases-len-constant.** Proof: `len(case_rows) == E ∧ case_phases == list(CACHE_CASE_PHASES)` (where `case_phases` has the same length as `case_rows`) ⇒ `len(CACHE_CASE_PHASES) == E`. Same altered-step check: they agree every time.
- The redundancy is symmetric. Dropping the pre-existing `len(checks) == expected["checks"]` or `len(case_rows) == expected["cases"]` instead also survives all 225 vectors (observed: `checks-len-drop`, `caserows-len-drop` SURVIVED). The two "constant-length invariants" are dead conjuncts, not guards. [INFERENCE] They read as a cross-check between the reviewed constant and the inventory, but they cannot change the result.

## F1 (defect, FAIL): non-equivalent r22-changed mutants survive the 225 oracle

I graded unlisted in-memory mutants with `probe.grade()` against the 225 oracle:

- **json-exact-leaf-true** (r22-new line 387, `    return observed == expected` → `    return True`): **SURVIVED, 0 killing vectors.** Concrete distinguishing inputs, decoded from pinned stdout with one leaf changed (orig → mutant):
  - `r13-counter-31984f4` with `F2_entry: 1`: False → True. With `sources: 34`: False → True. With `measured_commit: "000…0"`: False → True.
  - `r14-counter-552cae4` with `tiers.A: 0`: False → True.
  - `r13-counter-b576341` with `admitted_entries: 7`: False → True.
  - `clean-cache-demonstration` with `producer_executions_new_policy: 4`: False → True.
  - Cause: the `scalar` group (62 vectors) only varies the type at the same numeric value (float/bool). No vector anywhere puts a wrong value of the right type in a counter or in `producer_executions_new_policy`. The summarizer's most basic contract, that counts equal the expected counts, is unpinned. A runner that type-checks but never compares values passes 225/225.
- **case-row-isinstance-drop** (r22-new line 504, `row.get("phase") if isinstance(row, dict) else None` → `row.get("phase")`): **SURVIVED.** Distinguishing input: cache payload with `cases: [1,2,3,4]` gives orig False, mutant `AttributeError: 'int' object has no attribute 'get'`. With `cases` set to four phase strings, the mutant raises AttributeError on `str`. This contradicts claim C1's "malformed nested shapes … become a mismatch, not an exception": the one r22 guard that implements that property for case rows has no killing vector. `cache/cases/empty-objects` uses `{}` rows, which never reach the non-dict branch.
- **nonexact-isinstance-drop** (pre-existing line 476 guard): SURVIVED. Stdout `null` or `7` for `r13-counter-b576341` gives orig False, mutant `TypeError`. The existing `counter/r13-counter-b576341/array` vector does not kill it, because `key in list` is False rather than an error.
- **baseline-guard-pass** (r22 line 431, `summary_match = False` → `pass`): SURVIVED, and EQUIVALENT under the pinned step. The oversized-count stdout gives False/False, because `baseline_mismatch_count: True` already forces `None == int` to False. This is a redundant assignment, not a gap.

Impacted axes: calibration (the adequacy claim), premature saturation (lesson R22-M6/line 82 says "All 21 non-equivalent mutants are killed", which is true only of the chosen set), and C1's malformed-shape claim.

**Smallest safe correction:**
1. Append adequacy vectors (append-only, keeping the 225 prefix): one same-type wrong value per exact counter and per `producer_executions_new_policy` (for example `F2_entry: 1`, `producer_executions_new_policy: 4`, want false), and `cases: [1,2,3,4]` (want false).
2. Add `json-exact-leaf-true` and `case-row-isinstance-drop` to `MUTANTS` with expect `killed`.
3. Reword the lesson and receipt claim as "21/21 of the 25 listed mutants". Optionally add `null`/scalar stdout for the non-exact counter.
4. Optionally delete the two redundant length conjuncts or relabel them "redundant (implied)". That is a maintainability tradeoff, not a correctness defect.

## Scope note: pre-existing clauses with no killing vector (outside C1's changed lines)

Each of these survived the 225 oracle, and each has an observed concrete distinguishing input (orig False → mutant True):

- status-drop: `status: "failed"`.
- measured-commit-drop: `measured_commit` = 40 zeros.
- harness-revision-drop: `harness_revision` = 40 zeros.
- inputs-unchanged-eq: `inputs_unchanged_during_run: 1`.
- inputs-unchanged-drop: `inputs_unchanged_during_run: false`.
- isolation-residue-falsy (`== []` → `not …`): `isolation.residue: null`.
- failures-drop: auditor-selftest stdout with an appended `FAIL\tsynthetic`.
- aux-drop: an extra `INVENTORY\tx` line.
- bm-count-drop: an extra `BASELINE_MISMATCH\tsynthetic` on r20-input-binding.
- violation-drop: a `VIOLATION\tsynthetic` line on carry-invariant-probe.

Lesson R22-M6 lists "seven pre-existing" survivors. That is the set L1 mutated, not every pre-existing clause. These are tradeoffs for the judge, since they are not regressions introduced by r22.

## Dead-seat residual: labelled honestly, with one mislabelled summary key

- The `note` reads: "L1-executed mechanical residual … Not a seat replacement and not an independent review: observations come from census/round-22/oracle225-*.json and mutation-adequacy-oracle225.json." The lesson agrees at round-22.md:23 ("not an independent review") and :89. The label is honest.
- Observed cross-check: 26 rows and 26 unique seats (Attack04–06, 30–35, 37–49, 61–64), matching `dead_seats: 26`. For every row, `want`, `baseline_observed`, `baseline_exception`, `changed_observed`, `changed_pass`, `killed_by_mutants` and `stored_delta` equal the oracle case and the receipts: 0 mismatches. Every row has baseline pass=false and at least one attributing mutant.
- Defect (minor, labelling): `summary.single_mutant_attributed: 26` is false as written. The `killed_by_mutants` length histogram is `{1: 12, 2: 14}`; for example, Attack30 through Attack49 cite both `json-exact-type` and `exact-json-to-eq`. Smallest correction: rename the key to `mutant_attributed: 26`, or record the histogram. The lesson wording "each has an attributing mutant" is already accurate.

## Commands run (all read-only)

- `python3 -B census/round-22/mutation-adequacy.py` (EXIT=0, output above).
- `git diff 41553adb… -- census/round-21/run-acceptance.py`; `git diff [-U0|--stat] b912328d… -- tests/fixtures/r22-result-oracle.json`; `git show <rev>:<path>` piped into sha256sum or a python reader; `git log`; `git status --porcelain` on the target paths (clean).
- `python3 -B -c` one-liners: receipt reproduction under an audit hook, survivor differentials, unlisted-mutant grading, distinguishing-input checks, and the residual cross-check. All read and print only.
