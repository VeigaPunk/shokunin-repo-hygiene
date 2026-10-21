STATUS: FAIL

# CritAdequacy245: residual non-author review of the 245-vector oracle (souji lane, round 22, claim C1, calibration)

Seat: `SoujiR22-2.CritAdequacy245` (critic). Reviewed author: `SoujiR22-2` (replacement L1).

Reviewed artefacts (uncommitted working tree, observed sha256):
- oracle `tests/fixtures/r22-result-oracle.json`: `63de539f…1795`
- probe `census/round-22/mutation-adequacy.py`
- runner under test `census/round-21/run-acceptance.py`: `00d0e9c2…80a6` (unchanged against HEAD)

Host: Python 3.14.8, soft stack 8192 KiB. No tool was installed or updated. The only file written is this report. Every mutant and alternate input was held in memory (`python3 -B -` reading a heredoc on stdin, `exec(compile(...))`, and the probe's own `mutate()`/`grade()`).

## Verdict

The narrow claim holds. On the 245 oracle, all 38 listed mutants marked `killed` are killed, and the 7 listed equivalents survive. This holds only at a soft stack of at most 15360 KiB (see "What holds" below).

The Q52 claim does **not** hold. I enumerated the r22-changed conjuncts from the diff and built unlisted literal mutants for them. Non-equivalent survivors remain in r22-changed clauses:
- **N1:** reverting the r22 iterative `numeric_leaves` to the base recursive code.
- **N2:** making the phase comparison order-insensitive, although Q51 itself says the phase labels are *ordered*.
- **N3:** weakening the exact key-set comparison in `json_exact`.
- **N4:** deleting `ValueError` from the two rewritten `except` tuples.

Survivors also remain in retained conjuncts that the changed lines re-assert (R1 to R6). By Q52's own wording ("every changed predicate clause … has an executed literal mutant killed"; the mutant inventory is "enumerated from the diff's conjuncts"), the claim is not met.

## What holds (observed)

- `python3 -B census/round-22/mutation-adequacy.py` exits 0.
  - Pristine runner: 245/245.
  - Summary: `mutants 45, killed 38, survived 7, disagreeing []`, `stack_soft_limit 8388608`.
  - Its stdout is byte-equal to `census/round-22/mutation-adequacy-oracle245.json` (`cmp`).
- The oracle .py run against the current runner is byte-equal to `oracle245-changed.json`.
- Base `41553adb…` graded through `--grade-stdin` gives 88/245, with decisions equal to `oracle245-baseline.json` (0 differing ids).
- The first 187903 bytes are unchanged. The sha256 of `head -c 187903` is the same for the working tree and for `git show HEAD:` (`e165834a…e7f4`); the HEAD file is 187910 bytes.
- `mutation-adequacy-listed45-oracle225.json` shows the 45 listed mutants on the 225 bytes: 23 killed and 15 disagreeing. This matches lesson R22-M10.
- The stack dependence reproduces. Under `ulimit -s 16384`, the probe reports `killed 36`, disagreeing `counter-recursion, cache-recursion`, and base reports 90/245. This matches `stack-sweep-oracle245.txt`. So "38/38" needs the qualifier "at a soft stack ≤15360 KiB, Python 3.14.8". R22-M11 states that qualifier for the 225 numbers. The 245 sentence in R22-M10 and in the target claim omits it.
- Each of the 20 new vectors is a single-cause delta:
  - The six stdout vectors differ from the pinned record by exactly one line (`difflib` check). For example, `missing-pass-line` deletes `PASS\tgrant-clone-negated-prose`, and `fail-line` appends `FAIL\tsynthetic`.
  - Each new vector kills the mutant it is meant to kill.
  - 15 listed mutants are killed only by the new vectors (`json-exact-leaf-true`, `case-row-isinstance-drop`, `nonexact-isinstance-drop`, `gate-self-consistency`, `status-drop`, `measured-commit-drop`, `harness-revision-drop`, `inputs-unchanged-drop`, `inputs-unchanged-eq`, `isolation-residue-falsy`, `failures-drop`, `aux-drop`, `bm-count-drop`, `pass-match-drop`, `violation-drop`).

## Conjunct inventory (r22-changed lines and the predicates they re-assert that can change `result['matched']`, including by raising)

Line numbers refer to the current `census/round-21/run-acceptance.py`. "Listed" means a mutant in the probe's MUTANTS list. "Extra" means a mutant I built and graded with `probe.grade()` on the 245 oracle.

| # | conjunct / branch (line) | origin | listed mutant(s) | extra mutant(s) → result on 245 |
|---|---|---|---|---|
| 1 | `numeric_leaves` iterative walk (362-372; drives `observed_fields`, 480) | r22-changed | none | `numeric-leaves-recursive-base` (base body restored) → **SURVIVED (N1)**; `numeric-leaves-no-reversed` → survived, equivalent (E5) |
| 2 | `json_exact` `type(o) is not type(e)` (377) | r22 | json-exact-type | `je-type-isinstance` → killed (16) |
| 3 | `json_exact` dict branch `isinstance(expected, dict)` (379) | r22 | none | `je-dict-branch-false` → killed (60) |
| 4 | `json_exact` dict `keys() ==` (380) | r22 | json-exact-dict-keys | `je-keys-superset` (`>=`) → killed (1); `je-keys-subset` (`<=`) → **SURVIVED (N3)** |
| 5 | `json_exact` dict recursion `all(json_exact(observed[key], …))` (381-382) | r22 | (json-exact-leaf-true is indirect) | `je-dict-recurse-eq` → killed (60); `je-dict-all-drop` → killed (64) |
| 6 | `json_exact` list branch `isinstance(expected, list)` (383) | r22 | none | `je-list-branch-false` → survived, equivalent (E1) |
| 7 | `json_exact` list `len ==` (384) | r22 | json-exact-list-len | — |
| 8 | `json_exact` list element recursion (385-386) | r22 | none | `je-list-recurse-drop`, `je-zip-empty` → survived, equivalent (E1) |
| 9 | `json_exact` leaf `observed == expected` (387) | r22 | json-exact-leaf-true | `je-leaf-is` → killed (6) |
| 10 | summary group guard `group is not None and summary_match` (426), which keeps the r22 `try` body from raising | retained, re-asserted | none | `sum-group-guard-drop` → **SURVIVED (R1)** |
| 11 | r22 `try/except ValueError: summary_match = False` (428-431) | r22 | baseline-int-guard, baseline-guard-pass (eq) | `sum-except-broad` (`except Exception`) → survived, equivalent (E2) |
| 12 | summary `matched … and summary_match and pass_match and not stderr` (463) | r22 (`not stderr`) + retained | summary-stderr, pass-match-drop | `sum-stderr-strip` → killed (12); `sum-summarymatch-drop` → killed (16) |
| 13 | carry-invariant VIOLATION (465) | retained | violation-drop | — |
| 14 | counter `except (ValueError, TypeError, RecursionError)` (469) | r22-changed line | counter-recursion | `ctr-except-no-valueerror` → **SURVIVED (N4)**; `ctr-except-no-typeerror` → survived, equivalent (E3) |
| 15 | counter `if step["exact_json"]` (472) | retained, governs r22 lines | none | `ctr-exact-branch-true` → killed (2); `ctr-exact-branch-false` → killed (1) |
| 16 | exact `json_exact(observed, expected)` (473) | r22 | exact-json-to-eq | — |
| 17 | non-exact `isinstance(observed, dict)` (476) | retained | nonexact-isinstance-drop | — |
| 18 | non-exact `all(key in observed and json_exact(observed[key], value))` (477-478) | r22 | nonexact-to-eq, nonexact-keyin-get (eq) | `ctr-nonexact-any` → killed (2); `ctr-nonexact-inner-eq` → killed (1) |
| 19 | `observed_fields … if isinstance(observed, dict) else {}` (480) | retained | none | `ctr-fields-guard-drop` → survived, equivalent (E4) |
| 20 | counter `matched and json_match and not stderr` (492) | retained | counter-stderr | `ctr-jsonmatch-drop` → killed (75); `ctr-stderr-strip` → **SURVIVED (R5)** |
| 21 | cache `except (ValueError, TypeError, RecursionError)` (496) | r22-changed line | cache-recursion | `cache-except-no-valueerror` → **SURVIVED (N4)** |
| 22 | `gate = … if isinstance(payload, dict) else None` (500) | r22 | none | `cache-gate-guard-drop` → killed (2) |
| 23 | `isolation = … if isinstance(payload, dict) else None` (501) | r22 | none | `cache-isolation-guard-drop` → killed (2) |
| 24 | `case_phases` row guard `isinstance(row, dict)` (504) | r22 | case-row-isinstance-drop | `cache-phase-subscript` (`row["phase"]`) → killed (1) |
| 25 | `case_phases` outer guard `if isinstance(case_rows, list) else None` (505) | r22 | none | `cache-phases-list-guard-drop` → killed (2) |
| 26 | `demo_match` `isinstance(payload, dict)` (507) | retained | none | `cache-payload-isinstance-drop` → killed (2) |
| 27 | status / measured_commit / harness_revision (508-510) | retained | status-drop, measured-commit-drop, harness-revision-drop | `cache-status-default` (`.get("status","ok")`) → **SURVIVED (R4)** |
| 28 | `isinstance(case_rows, list) and len(case_rows) == E` (511), which guards the r22 phase conjunct | retained, re-asserted | caserows-len-drop (eq) | `cache-caserows-isinstance-drop` → **SURVIVED (R2)** |
| 29 | `len(CACHE_CASE_PHASES) == E` (512) | r22 | phases-len-constant (eq) | — |
| 30 | `case_phases == list(CACHE_CASE_PHASES)` (513) | r22 | cache-phases | `cache-phases-sorted`, `cache-phases-set` → **SURVIVED (N2)**; `const-phase-swap` (constant reordered) → killed (2) |
| 31 | `isinstance(checks, dict) and len(checks) == E` (514) | retained | checks-len-drop (eq) | `cache-checks-isinstance-drop` → killed (1) |
| 32 | `len(CACHE_CHECK_NAMES) == E` (515) | r22 | names-len-constant (eq) | — |
| 33 | `checks.keys() == CACHE_CHECK_NAMES` (516) | r22 | cache-names | `cache-names-subset` (`<=`) → survived, equivalent (E6); `const-name-replace` → killed (2) |
| 34 | `all(value is True …)` (517) | retained | checks-all-true-drop | `cache-checks-eq-true` → killed (1); `cache-checks-truthy` → killed (1) |
| 35 | `json_exact(failed_checks, [])` (518) | r22 | failed-checks-to-eq (eq) | — |
| 36 | `json_exact(producer_executions_new_policy, E)` (519-520) | r22 | producer-exec-to-eq | `cache-producer-literal` (`…, 3)`) → survived, equivalent (E7) |
| 37 | `inputs_unchanged_during_run is E` (521) | retained | inputs-unchanged-drop, inputs-unchanged-eq | — |
| 38 | `isinstance(gate, dict) and gate.get("sha256") == gate_sha` (522) | r22-changed line | gate-isinstance, gate-sha, gate-self-consistency | `cache-gate-sha-default` (`.get("sha256", gate_sha)`) → **SURVIVED (R3)** |
| 39 | `isinstance(isolation, dict)` (523) | r22 | isolation-isinstance | — |
| 40 | `isolation.get("cleaned") is E` (524), now bound to the r22 guarded `isolation` | retained, re-asserted | isolation-cleaned-drop, isolation-cleaned-eq | `cache-cleaned-default` (`.get("cleaned", True)`) → **SURVIVED (R3)** |
| 41 | `isolation.get("residue") == []` (525), same binding | retained, re-asserted | isolation-residue, isolation-residue-falsy | `cache-residue-default` (`.get("residue", [])`) → **SURVIVED (R3)** |
| 42 | `matched_counts` guards (530-534; 533 is r22-changed) can raise | r22 + retained | none | `cache-mc-gate-guard-drop` → killed (4); `cache-mc-cases-guard-drop` → killed (2); `cache-mc-producer-guard-drop` → killed (2) |
| 43 | cache `matched and demo_match and not stderr` (536) | retained | cache-stderr | `cache-demomatch-drop` → killed (62); `cache-stderr-strip` → **SURVIVED (R5)** |
| 44 | `matched = returncode == 0 and not failures` (410) | retained | failures-drop, returncode-drop | — |
| 45 | summary aux / baseline-count / summary-line equality (416, 435-444) | retained | aux-drop, bm-count-drop, summary-last-only | — |

In total I built 50 extra mutants: 47 in the first battery and 3 constant/zip mutants. 29 were killed and 21 survived. Of the 21 survivors, 7 are equivalent (E1 to E7, counting each family once) and the rest are non-equivalent survivors N1 to N4 and R1 to R5, listed below.

How the distinguishing inputs were checked: I loaded the original runner and each mutant in memory and called `summarize_result` directly. Each call used the frozen inventory step with the oracle's own `replace_revision` and the pinned `final-out-S1.json` record, with one field modified. The base column is the `41553adb` runner, also loaded in memory.

## Non-equivalent survivors in r22-changed clauses (findings)

**N1: the `numeric_leaves` iterative rewrite has no witness.** Impacted axes: calibration and false provenance of a repair.

- Mutant: replace the body at 364-371 with the base recursive body (from `git show 41553adb…`). Result on the 245 oracle: survived, with 0 killing vectors.
- Distinguishing input 1: `r13-counter-b576341`, pinned stdout plus one extra key `"x"` whose value is an 1100-deep `{"a":…}` dict. That is a valid subset result with an extra field.
  - Changed runner: `True`. Mutant: `RecursionError: maximum recursion depth exceeded`. Base: the same `RecursionError`.
- Distinguishing input 2: `r13-counter-31984f4` with stdout `'{"a":'*1200+'0'+'}'*1200`.
  - Changed runner: `False`. Mutant and base: `RecursionError`.
- Lesson round-22.md:70-72 claims "numeric leaf collection uses an iterative walk … rather than producer-controlled Python call depth" as part of C1.
- Mechanism (observed): the oracle's depth vectors are arrays only (`stdout_nested_array_depth`), so the top-level value is not a dict and `numeric_leaves(observed)` is never called on deep data.
- This is a base-discriminating repair with no executed witness. Q52's last sentence ("A repair witness counts only after it has been run against the base") is violated.
- The threshold depends on `sys.getrecursionlimit()` (1000 here), not on the C stack. The 1100/1200-deep decode itself succeeded at 8192 KiB.

**N2: phase order is unpinned, though Q51 declares it.** Impacted axes: calibration and contract fidelity.

- Mutants: `case_phases == list(CACHE_CASE_PHASES)` → `sorted(map(str, case_phases)) == sorted(CACHE_CASE_PHASES)`, or → `set(case_phases) == set(CACHE_CASE_PHASES)`. Both survived the 245 oracle.
- Distinguishing input: the cache-demo pinned payload with `cases[0]` and `cases[1]` swapped.
  - Changed runner: `False`. Mutant: `True`. Base: `True`. So this is also a base-discriminating r22 behaviour with no vector.
- The working-tree QUALITY Q51 says "cache check names plus **ordered** phase labels are independent reviewed expectations". The listed `cache-phases` mutant (drop the conjunct) is killed only by vectors that replace phase values, never by a reordering.

**N3: the missing-key direction of the exact key-set is unpinned.** Impacted axis: C1's "malformed shape becomes a mismatch, not an exception".

- Mutant: `observed.keys() == expected.keys()` → `observed.keys() <= expected.keys()`. Survived, with 0 killing vectors. (The `>=` direction is killed by `adequacy/exact-json/…/extra-key`.)
- Distinguishing input 1: `r13-counter-31984f4` with `sources` deleted. Changed runner: `False`. Mutant: `KeyError: 'sources'`. Base: `False`.
- Distinguishing input 2: `r14-counter-552cae4` with `tiers.C` deleted. Changed runner: `False`. Mutant: `KeyError: 'C'`.
- No vector in the 245 deletes an expected key from an exact counter.

**N4: `ValueError` in the two rewritten `except` tuples is unpinned.** Impacted axis: C1's malformed-result boundary.

- Mutants: `except (ValueError, TypeError, RecursionError)` → `except (TypeError, RecursionError)`, at occurrence 0 (counter, line 469) and occurrence 1 (cache, line 496). Both survived.
- Distinguishing input, counter: `r13-counter-31984f4` with an empty stdout `""`. Changed runner: `False`. Mutant: `JSONDecodeError: Expecting value`. Base: `False`.
- Distinguishing input, cache: an empty stdout, or the pinned stdout truncated to 100 characters. Changed runner: `False`. Mutant: `JSONDecodeError`.
- No vector feeds non-JSON stdout to a counter or the cache step. An empty stdout with exit 0 is the most ordinary producer failure. The listed `counter-recursion` and `cache-recursion` mutants only cover the newly added member.

## Non-equivalent survivors in retained conjuncts that the changed lines re-assert

None of these is a regression introduced in r22. Each still counts against Q52's "every retained conjunct it re-asserts".

- **R1: summary group guard (line 426).** Mutant: `if group is not None and summary_match:` → `if group is not None:`.
  - Input: `r20-input-binding` with stdout `""`, or the pinned stdout with its SUMMARY line removed.
  - Changed runner: `False`. Mutant: `IndexError: list index out of range`. Base: `False`.
  - The r22 `try` block catches only `ValueError` and relies on this guard.
- **R2: `isinstance(case_rows, list)` (line 511).** The r22 phase conjunct sits behind this guard. Mutant: drop the guard.
  - Input: the cache payload with `cases: null` or `cases: 4`.
  - Changed runner: `False`. Mutant: `TypeError: object of type 'NoneType' has no len()`.
  - The oracle has null/array shape vectors for `checks`, `gate` and `isolation`, but not for `cases`.
- **R3: missing-key defaults in the gate/isolation conjuncts (lines 522, 524, 525).** These conjuncts are evaluated on the r22 guarded `gate`/`isolation` bindings.
  - Mutants: `.get("sha256", gate_sha)`, `.get("cleaned", True)`, `.get("residue", [])`.
  - Inputs: `gate: {}` or `gate` with `sha256` deleted; `isolation` with `cleaned` deleted; `isolation` with `residue` deleted.
  - Changed runner: `False`. Mutant: `True`. Base: `False`.
  - No vector removes a key inside `gate` or `isolation`.
- **R4: status default (line 508).** Mutant: `.get("status", "ok")`. Input: payload with `status` deleted. Changed runner: `False`. Mutant: `True`.
- **R5: whitespace stderr on counter/cache (lines 492, 536).** Mutant: `not stderr` → `not stderr.strip()`.
  - Input: `r13-counter-31984f4` or cache with stderr `"\n"`. Changed runner: `False`. Mutant: `True`. Base: `False`.
  - The summary kind has `stderr/*/blank` vectors (the summary strip mutant is killed by 12), but the counter and cache kinds have only a `WARNING` stderr vector. Q51 says stderr must be empty "without stripping", but its literal scope is summary stderr.
- **R6: missing-key class (meta-finding).** N3, R3 and R4 share one cause. The oracle's `json_set` can only set values; no vector deletes a key. A missing field is the classic shape of a stale or partial producer, and it is unpinned across all kinds.

## Equivalent survivors (with reasons)

- **E1: `je-list-branch-false`, `je-list-recurse-drop`, `je-zip-empty`.** These are equivalent under the pinned inventory only. The only list leaf in any `expected_summary` is `failed_checks: []` (checked by dumping `step-inventory.json`, and `make_steps` is equality-checked against it). With `type(o) is list` and `len(o) == 0`, the element recursion is vacuous, and `o == []` equals `json_exact(o, [])`.
  - Function-level counterexample (not reachable from the pinned inventory): expected `[1]`, observed `[True]`.
- **E2: `sum-except-broad`.** The `try` body can only raise `ValueError`. Once `summary_match` is true, `baseline_match` is a non-None fullmatch of the same regex; `group` is 1 and exists; `int()` of `\d+` raises only `ValueError` (the digit limit).
- **E3: `ctr-except-no-typeerror`.** `json.loads(str)` never raises `TypeError`, and `stdout` is always a `str` (`decode_exact` returns `data.decode(...)`). The same holds for the cache tuple.
- **E4: `ctr-fields-guard-drop`.** The iterative `numeric_leaves` returns `{}` or `{"": int}` for non-dict input and never raises. The result only feeds `matched_counts`.
- **E5: `numeric-leaves-no-reversed`.** It changes only the insertion order and path-collision winner in `matched_counts`, never `matched`.
- **E6: `cache-names-subset`.** `len(checks) == E`, `len(CACHE_CHECK_NAMES) == E` and subset together imply equality.
- **E7: `cache-producer-literal`.** Equivalent under the pinned inventory: expected is the constant 3.
- I re-checked the 7 listed equivalents and they hold:
  - `names-len-constant`, `phases-len-constant`, `checks-len-drop` and `caserows-len-drop` are implied conjuncts.
  - `baseline-guard-pass` is equivalent because the only `baseline_mismatch_group` step also sets `baseline_mismatch_count`, so `None == int` already forces `False`.
  - `nonexact-keyin-get` and `failed-checks-to-eq` are equivalent conditionally on the pinned inventory: no null expected leaf, and `failed_checks` is `[]`.

## Attack: do the new vectors encode implementation behaviour as specification?

- None of the 20 wants contradicts the contract, and none was flipped to match the changed runner.
- 19 of the 20 also pass on base (base observed `False`). They are regression pins of behaviour that already existed.
- The one base-discriminating vector, `malformed/cache/case-rows-int` (base observed `True`), is grounded in Q51 ("wrong phases … rejected"; "malformed containers produce a retained mismatch").
- 15 wants are derivable from the frozen inventory or the contract text:
  - typed values against `expected_summary`;
  - `status`, `measured_commit` (`<REV>`), and `inputs_unchanged_during_run: true` (the `1` vector is the contract's "decoded wrong scalar types");
  - `pass_count`, `auxiliary_lines` and `baseline_mismatch_count`;
  - a `null` counter document.
- **Finding I1 (minor, provenance).** Five wants have their only authority in runner code that exists in both base and current, not in the oracle's `contract` string, Q51 or the frozen inventory:
  - `cache/harness-revision-wrong`: the inventory has no `harness_revision` field.
  - `cache/gate-both-slots-wrong`: the gate digest is bound to the live `tools/souji-evidence-cache.py`, currently `dd279ba9…39d6`, which the oracle never hashes (ResidAdequacyB B2).
  - `cache/isolation-residue-null`: the inventory has no residue expectation; `residue == []` exists only in the runner.
  - `summary/auditor-selftest/fail-line`: comes from `failure_lines`.
  - `summary/carry-invariant-probe/violation-line`: comes from the runner's name-keyed special case.

  These are conservative rejections and I judge them correct. But they codify current behaviour as specification. The oracle's `contract` string is inside the frozen 187903-byte prefix and cannot be updated, so this needs a disclosure: label them "retained-behaviour pins (authority: runner code)" in the lesson. It is a tradeoff for the judge, not a wrong decision.

## Smallest safe correction

1. Append reviewed vectors after the 245 cases, keeping the prefix:
   - **N1:** `r13-counter-31984f4` with stdout `'{"a":'*1200+'0'+'}'*1200`, want false (base raises, so it discriminates). Optionally also the b576341 deep extra-field variant, want true. State the interpreter and `sys.getrecursionlimit()`.
   - **N2:** cache with `cases[0]`/`cases[1]` swapped, want false (base `True`, so it discriminates).
   - **N3:** `r13-counter-31984f4` with `sources` removed, as literal `stdout`, want false.
   - **N4:** counter and cache with stdout `""`, want false.
   - **Optional, R1 to R5:** `r20-input-binding` with empty stdout; cache `cases: null`; `gate: {}`; `isolation` without `cleaned` / without `residue`; payload without `status`; counter and cache stderr `"\n"`.
2. Add the N and R mutants above to `MUTANTS` with expect `killed`, and E1 to E7 with expect `equivalent` plus their reasons.
3. Restate the claim as "38/38 of 45 listed, at a soft stack ≤15360 KiB on Python 3.14.8". Do not state Q52 as met until the diff-enumerated inventory above has no unexplained survivor.
4. Disclose I1 in lesson R22-M10.

## Commands run (all read-only)

- `git -C … diff 41553adb… HEAD -- census/round-21/run-acceptance.py`
- `git diff HEAD -- census/round-22/mutation-adequacy.py corpus/QUALITY.md corpus/SOURCES.md`
- `git show HEAD:tests/fixtures/r22-result-oracle.json | head -c 187903 | sha256sum`
- `python3 -B census/round-22/mutation-adequacy.py`, compared with `cmp` to the receipt.
- `python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py`, compared with `cmp` to the receipt.
- `git show 41553adb…:census/round-21/run-acceptance.py | python3 -B census/round-22/mutation-adequacy.py --grade-stdin`
- `(ulimit -s 16384; …probe…; …grade-stdin…)`
- `python3 -B -` heredoc scripts that import the probe and the oracle, then:
  - build mutants with `probe.mutate()`;
  - grade them with `probe.grade()` against a freshly loaded oracle module;
  - run differentials on original, mutant and base through `summarize_result`.

  They only read and print. The base-runner source was read through `git show` inside the differential.
