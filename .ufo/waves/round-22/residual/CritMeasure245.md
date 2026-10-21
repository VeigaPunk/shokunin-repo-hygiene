STATUS: PARTIAL

# CritMeasure245: non-author residual review of the souji round-22 C1 245-vector extension

Reviewer: SoujiR22-2.CritMeasure245. Date: 2026-10-21. Python 3.14.8, hard stack limit unlimited, default soft limit 8192 KiB.
Everything ran read-only. Historical oracle bytes and the base runner were piped in through process substitution and graded in memory: the probe's module `Path` was swapped for an object that returns the piped bytes, and the runner source went through `sys.stdin`. I wrote no files apart from this report and installed nothing.

All headline numbers reproduce, and every hash binding holds. The verdict is PARTIAL because the stack condition is stated incorrectly (findings 1 and 2), and because the C1 before→after delta gains only +1 discriminating vector, from a defect class the oracle already covers (finding 3).

## Reproduced numbers (observed)

| Claim | Reproduced | Receipt equality |
|---|---|---|
| 245 oracle: changed 245/245 | 245/245, exit 0 | `oracle245-changed.json` results identical |
| 245 oracle: base 88/245, 7 exceptions (8192 KiB) | 88/245; 7 exceptions: gate null/array, isolation null/array (AttributeError), oversized-count (ValueError), 2 × decoder-depth-100000 (RecursionError) | `oracle245-baseline.json` byte-equal as parsed JSON (`d == ref` True) |
| probe 38/45 killed, 7 equivalents, exit 0 (8192 KiB) | 38 killed, 7 survived (nonexact-keyin-get, failed-checks-to-eq, names-len-constant, phases-len-constant, baseline-guard-pass, checks-len-drop, caserows-len-drop); none disagreeing; exit 0 | `mutation-adequacy-oracle245.json` equal (`d == ref` True) |
| sweep at 8192/14336/15360 KiB: 88, 245, 38/45 | same | `stack-sweep-oracle245.txt` rows reproduce |
| sweep at 16384/unlimited KiB: 90, 245, 36/45, disagreeing counter-recursion,cache-recursion | same (also at 20480 and 32768) | reproduces under the default environment only (see finding 1) |
| 214 oracle (`b912328`): 60/214 → 214/214 | 60/214 (5 exceptions) → 214/214 | `oracle214-baseline.json`, `oracle214-changed.json` results identical |
| 225 oracle (HEAD): 69/225 → 225/225 | 69/225 (7 exceptions) → 225/225 | `oracle225-changed.json` identical; `oracle225-baseline.json` same verdicts, but 2 rows differ in exception text (finding 4) |
| listed-45 probe on the 225 oracle | 23 killed, 15 disagreeing | `mutation-adequacy-listed45-oracle225.json` mutant rows identical |

Commands (all run from the lane directory):

- `python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py`
- `git show 41553adb…:census/round-21/run-acceptance.py | python3 -B census/round-22/mutation-adequacy.py --grade-stdin`
- `python3 -B census/round-22/mutation-adequacy.py`
- The same three commands inside `( ulimit -s S; … )` for S in 1024, 2048, 4096, 6144, 8192, 12288, 14336, 15360, 15600, 15679, 15680, 15681, 15685, 15690, 15700, 15872, 16000, 16128, 16256, 16384, 20480, 32768, unlimited.

## Hash bindings (observed, all hold)

- The oracle bytes hash to `63de539f…5795`. That matches `oracle_sha256` in `oracle245-changed.json`, `oracle245-baseline.json`, `mutation-adequacy-oracle245.json` and the header of `stack-sweep-oracle245.txt`.
- Runner hashes match: changed `00d0e9c2…80a6` equals both the working tree and HEAD (the runner is unchanged against HEAD), and base `11418399…a2b` equals `git show 41553adb…`.
- `source_receipt_sha256` `bc53a752…38fe` matches `final-out-S1.json`, and `frozen_inventory_sha256` matches `step-inventory.json`.
- All 45 `mutant_sha256` values match my in-memory `mutate()` output. There are no duplicate mutant sources, and no mutant equals the pristine source. The listed-45/225 receipt carries the same 45 hashes.
- HEAD oracle `849a8569…` and `b912328` oracle `292442a6…` match their receipts.
- Prefix claim: the first 187903 bytes are equal (sha `e165834a…` for both). Structurally, the non-case keys equal HEAD, `cases[:225]` equals HEAD's 225 cases, HEAD's `cases[:214]` equals `b912328`'s cases, and all 245 ids are unique.
- Binding gap: none of the probe receipts records the hash of `mutation-adequacy.py` itself (`f584503a…` in the working tree), so the receipt does not bind the mutant list and expectation labels. The per-mutant hashes bind only the mutated sources.

## Findings

### 1. The stack condition is misstated: the flip happens below 16384 KiB, and soft limit alone does not determine it

**Counterexample (observed):**

- Under the default environment, base on the 245 oracle gives 88 at 15360 KiB but 90 at 15872, 16000, 16128 and 16256 KiB. All of those are below the stated "≥16384".
- Bisection puts the base flip at 15679/15680 KiB, and the point is not deterministic:
  - At 15679 KiB, base returned 88 in 7 of 8 runs and 90 in 1.
  - At 15680 KiB, base returned 90 in 6 of 8 runs.
  - At 15680 KiB, the probe exited 1 in 5 of 6 runs; at 15681 KiB, in 5 of 6 runs; at 15679 KiB it exited 0 in 6 of 6.
  - From 15685 KiB upward, the probe exited 1 in 6 of 6 runs.
- The environment shifts the threshold:
  - At `ulimit -s 16384` with about 960000 bytes of extra environment (8 variables of 120000 bytes each), base returns 88/245 with 2 RecursionErrors, yet the receipt still records `stack_soft_limit: 16777216`.
  - With 480000 bytes of extra environment the result stays 90, and at 20480 KiB it stays 90 even with 1920000 bytes.
- Command: `( ulimit -s 16384; git show $B | env PAD1=<120000 x> … PAD8=… python3 -B census/round-22/mutation-adequacy.py --grade-stdin )`.

**What actually determines the result:**

- [INFERENCE] The real determinant is the main thread's free C stack. That is the soft limit minus the initial stack consumed by argv, environment and auxv, plus stack placement jitter, which Python 3.14 checks when the 100000-deep decode runs.
- The probe's grading path flips at a slightly different point (15680–15685) than `--grade-stdin` (15679–15680), which is consistent with call depth mattering.
- The `stack_soft_limit` field and the source comment "record the soft limit" are therefore an incomplete proxy.

**Correct statement:** 88/245, probe 38/45 and exit 0 hold when the 100000-deep decode overflows. That was observed at every soft limit ≤15360 KiB with an ordinary environment, and at 16384 KiB with a ≥960 KB environment. 90/245, probe 36/45 and exit 1 were observed from about 15680 KiB upward with an ordinary environment. The boundary is a band of about 15679–15685 KiB that varies from run to run.

**Smallest safe correction:**

- Replace "≥16384 KiB" with the observed condition above.
- Make each receipt record the condition that actually decides the result: whether `adequacy/*/decoder-depth-100000` raised RecursionError on the pristine/base run (for example, a boolean or the count of base RecursionErrors). The soft limit alone is not enough.

**Impacted axes:** measurement reproducibility and false provenance (a receipt field implies a condition it does not capture).

### 2. The historical 225 number is also stack-conditional, and its receipt has no stack field

- Observed: base on the HEAD 225 oracle gives 69/225 at 8192 KiB but 71/225 at 16384 KiB and unlimited.
- `oracle225-baseline.json` and `mutation-adequacy-oracle225.json` carry no `stack_soft_limit`, so "69/225 → 225/225" is unconditioned in its own receipt.
- The 214 oracle has no 100000-deep vector, and its base result is 60/214 at every stack tested.

**Correction:** annotate the 225 historical numbers as measured at 8192 KiB, with 71/225 at ≥16384 KiB.

**Impacted axis:** provenance.

### 3. The 245 extension changes C1's before→after mostly by raising base's pass count, adding only one discriminating vector

- Observed: all 20 new vectors want False and the changed runner returns False on all of them. Base returns False, with no exception, on 19 of the 20.
- Only `adequacy/residual/malformed/cache/case-rows-int` discriminates the two runners.
- The C1 delta therefore moves from 156 discriminating vectors on 225 (225 − 69) to 157 on 245 (245 − 88). The rise in base pass rate, from 30.7% to 35.9%, is an artifact of 19 non-discriminating vectors. It is not a change in base behavior.
- The before ratios are not comparable across oracle versions. Only the discriminating count is.

**Breakdown of base's 157 failures (observed):** 150 false greens (observed True, want False), 7 exceptions and 0 false reds.

**Is any flip a false green on base?** Every non-exception flip is a base false green. The 7 exception flips are not false greens; they would refuse or crash end to end:

- [INFERENCE, code reading] The 4 AttributeErrors are not in `main()`'s except tuple, so base would crash with a traceback and exit 1 without writing a record.
- The ValueError and the RecursionError are caught (RecursionError is a subclass of RuntimeError; observed `issubclass` True), so base would refuse with exit 2.
- The 2 RecursionError flips are stack artifacts: at ≥15680 KiB base handles those vectors correctly (False).

No `want` label among the new vectors looked wrong on inspection.

**Mutant coverage of the new vectors:**

- Every new vector kills at least one mutant.
- 15 mutants are killed only by new vectors.
- `json-exact-leaf-true` is killed by 6 value vectors.
- `gate-self-consistency`, `isolation-residue-falsy`, `inputs-unchanged-eq` and `case-row-isinstance-drop` are each killed by exactly one vector.

**Correction:** state C1's after-gain as 157 discriminating vectors on 245 (+1 over 225, same defect class as existing vectors), not as a ratio comparison.

**Impacted axis:** meaning of the claim, through premature saturation of the before→after delta.

### 4. `case-rows-int` is a genuine base false green, but not a new class

- Observed by calling base `summarize_result` in memory with the pinned cache stdout and `cases = [1, 2, 3, 4]`:
  - base: `matched` is `True` (type `bool`), no exception;
  - changed: `False`;
  - unmodified pinned stdout: True on both runners.
- Cause: base checks only `isinstance(case_rows, list) and len(case_rows) == expected["cases"]` (4). It has no phase check (base diff: no `case_phases` and no `CACHE_CASE_PHASES`).
- The same base defect is already exposed on 225 by `cache/cases/empty-objects` (`[{}, {}, {}, {}]`) and `cache/case-identity/0..3`.
- Its new function is killing `case-row-isinstance-drop`. That kill comes through an exception in the mutant (`int.get`), not through a False result. It also adds a 6th killer for `cache-phases`.

### 5. Exception text is not byte-stable (minor)

- My in-memory regrade of `oracle225-baseline.json` differs from the receipt only in two exception strings: "Stack overflow (used 8140 kB)" against the receipt's "8144 kB".
- Verdicts are identical. The kB figure depends on call depth, so byte-level receipt comparisons that include exception text are path-dependent.

### 6. Out of scope: the depth vectors certify a branch the real runner cannot write

- [INFERENCE: in-memory `json.dump` plus code reading; the real `main()` was not run]
- At depth 1200 (the existing `malformed/*/decoder-depth` vectors), the decode succeeds and `summarize_result` returns False. `result["observed_json"]` then holds the 1200-deep list.
- `write_exclusive` uses `json.dump(..., indent=2)`, and that raised RecursionError in memory at depths 1200, 2000 and 5000 (900 worked).
- `main()` catches RecursionError as RuntimeError and prints "refused with no new result". By then `write_exclusive` has already opened the output with O_CREAT|O_EXCL and may have written partial JSON.
- The same applies to the 100000-deep vectors at a free stack of ≥15680 KiB.
- This is fail-closed, not a false green, and it was not introduced by the 245 extension. But the oracle grades only `summarize_result` and does not cover this end-to-end path.
- **Smallest safe correction (for a later round):** cap or omit `observed_json` when the payload is not a dict, or serialize before creating the exclusive file.

## Equivalence claims spot-checked (observed against the pinned inventory)

- `baseline-guard-pass`: the only step with `baseline_mismatch_group` is `r20-input-binding`, and it sets `baseline_mismatch_count: True`. So a None count still forces False. Equivalent.
- `nonexact-keyin-get`: the only non-exact counter, `r13-counter-b576341`, has no None-valued expected keys. Equivalent.
- `failed-checks-to-eq`: expected is `[]`, and only a list compares equal to it. Equivalent.
- `checks-len-drop` and `caserows-len-drop`: implied by exact name/phase identity plus the constant-length lines. Equivalent.
- `names-len-constant` and `phases-len-constant`: 33 and 4 match the inventory. Equivalent under the pinned inventory only.

No counterexample was found for any of these.

## Scope and bounds

- Only this report file was written. I did not mutate git or jj state.
- I did not run the real `main()`, the replay, or any producer.
- I did not read `/proc` or `operator-sweep-20261019`.
