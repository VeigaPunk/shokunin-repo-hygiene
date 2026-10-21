# Attack56: critic, vector `cache/name/isolation_confined` (want=false)

Seat: SoujiR22.Attack56 (critic, leaf, source-only). Target code: `4f83fd222ffbd8825340221a8c426550ef891191` (worktree runner bytes are identical to `git show 4f83fd2:census/round-21/run-acceptance.py`). Base for the before/after comparison: `41553adb139d06511dc386bb3ce4326aebfba675`.

## STATUS

**Source-only PASS for this vector and its paired positive.** The expected decision `want=false` is correct. The fixture really does feed the intended input: it takes the pinned public record, removes exactly one name and adds one bogus name, keeping 33 keys that are all True. The changed predicate rejects that input for the intended reason, and only that reason.

No counterexample breaks this vector. There are two caveats: one is a limit on how much a single-case run proves, and the other is a tradeoff the claim already declares out of scope. Neither one is a defect in C1.

Nothing here comes from running anything. I did not run the oracle, the runner, or any mutation. L1 still owes the actual 214-vector decisions and the 18-step acceptance run.

## 1. Rebuilding the stored delta from the pinned record (done before looking at the changed predicate)

- **Receipt binding.** `sha256sum census/round-21/final-out-S1.json` gives `bc53a752…38fe`. `step-inventory.json` gives `8b7b1cd8…1310`. Both equal the oracle header values (oracle lines 3–6). The oracle itself enforces these hashes in `r22-result-oracle.py:31-36`.
- **Original record.** The receipt has exactly one command named `clean-cache-demonstration` out of 18. Its `returncode` is 0 and `stderr` is `""`. Its raw `stdout` re-hashes to the recorded `stdout_sha256` `975d4535…db40`. The `checks` keys in that raw stdout equal `observed_json.checks` (final-out-S1 lines 2996–3030): 33 keys, all `true`, and `isolation_confined` is at line 3008.
- **Frozen inventory step** (`step-inventory.json:186-206`): kind `cache-demo`, with expected `checks: 33`, `cases: 4`, `failed_checks: []`, `producer_executions_new_policy: 3`, `inputs_unchanged_during_run: true`, `isolation_cleaned: true`, and `measured_commit: <REV>`.
- **Stored delta** (oracle json lines 1127–1174). It has one `json_set` entry at path `["checks"]`. That entry replaces the entire `checks` object. A stdlib JSON set-difference against the record gives:
  - removed: `isolation_confined`
  - added: `bogus_isolation_confined`
  - new length 33, all values `True`

  So the delta is exactly a rename that keeps the count and the all-True values. It is not a deletion, a value flip, or a type change.
- **The fixture feeds this input.** In `r22-result-oracle.py:66-91`:
  - the record's stdout is parsed
  - `at["checks"] = deepcopy(value)` replaces the whole object (`path[:-1]` is empty)
  - the result is re-serialized with `json.dumps`
  - the step comes from the frozen inventory, with `<REV>` replaced and `measured_commit` set to `ff425ab…`
  - `returncode` and `stderr` come from the record (0 and `""`)

  The re-serialized stdout is a single line with no `FAIL\t` prefix, so `failure_lines` stays empty.
- **The vector is not a later edit.** The vector and the paired positive are byte-equal, as decoded case objects, at `36c78ba` (the 212-vector landing commit), at `3223172` (the parent of 4f83fd2), and in the current file. The 4f83fd2 commit only appended the two depth vectors. Caveat: the "frozen before editing the summarizer" claim cannot be checked from git alone, because `36c78ba` landed the fixture and the implementation together. My independent rebuild above is the stronger evidence that the expectation was not derived from the implementation.
- **Is the expected decision right?** Yes. The preregistration's third defect is "cache checks counted rather than identified", and the lesson says "Cache identity means exactly33 reviewed names" (round-22.md line 7, and M3 at line 17). With this rename, the producer reports nothing under the reviewed obligation `isolation_confined`. Accepting it would reproduce the inherited defect.

## 2. Attack on the changed predicate (`run-acceptance.py`, 4f83fd2)

- **Reviewed constant.** `CACHE_CHECK_NAMES`, defined at lines 182–203, is a frozenset of 33 distinct literals, with `isolation_confined` at line 194. I compared it name by name and it equals the 33 producer names in the record exactly.
- **What happens to this vector, in order** (lines 506–526):
  1. `len(checks) == 33` passes.
  2. `len(CACHE_CHECK_NAMES) == 33` passes.
  3. `checks.keys() == CACHE_CHECK_NAMES` at line 516 is **False**, because `isolation_confined` is missing and `bogus_isolation_confined` is extra.

  So `demo_match` is False, and `matched` is `bool(False)` (lines 536–537). The oracle then compares False with `want=False`, which is a PASS (oracle line 97). Conjuncts after line 516 cannot rescue it, because this is a single `and` chain.
- **Base predicate** (`41553ad`, and identically `ff425ab`). It only has `len(checks) == expected["checks"]` and `all(value is True …)`, with no name identity. The vector therefore satisfies every base conjunct, and the base observes **True**, which is a FAIL against `want=False`. Before/after, this vector discriminates exactly the line-516 change and nothing else.
- **Paired positive `positive/clean-cache-demonstration` (want=true).** Every changed-predicate conjunct holds on the raw record:

  | Conjunct | Value in the raw record | Required |
  |---|---|---|
  | `status` | `ok` | `ok` |
  | `measured_commit` | `ff425ab…` | the oracle revision |
  | `harness_revision` | `ff425ab…` | the oracle revision |
  | case phases | `initial-fresh`, `unchanged`, `dependency-modified`, `legacy-no-dependencies` | `CACHE_CASE_PHASES` at lines 204–206 |
  | `checks` keys | the 33 reviewed names, all True | equal to `CACHE_CHECK_NAMES` |
  | `failed_checks` | `[]` (list) | `[]` |
  | `producer_executions_new_policy` | int 3 | 3 |
  | `inputs_unchanged_during_run` | `True` | `True` |
  | `gate.sha256` | `dd279ba9…` | sha256 of the live `tools/souji-evidence-cache.py`, also `dd279ba9…` |
  | `isolation` | a dict with `cleaned: true`, `residue: []` | same |

  Source predicts True on both base and changed code. Because the positive and the negative differ **only** in the `checks` object, a True positive in the same run shows that the negative fails for the identity reason alone.
- **The comparison semantics.** `dict_keys == frozenset` compares as sets, so it is order-insensitive and size-exact. That is why the appended key order in the vector does not matter. [INFERENCE: standard CPython dict-view semantics; I did not re-open the Python documentation in this seat.] If this inference were wrong, line 516 would never be True, and the paired positive would fail loudly rather than mask anything.

## 3. Counterexamples: strongest available, none against this vector

- **Limit A: a single-case run proves nothing on its own.** This affects coverage and operability (no harm caused). At line 503 the predicate hashes the **live** `tools/souji-evidence-cache.py`. The oracle binds only the receipt and the inventory (oracle lines 31–36); it does not bind this file. If the gate file changes, the positive turns False, and this negative still passes, but vacuously, because it fails on line 522 instead of 516. A full 214-vector run catches this through the positive. `--case cache/name/isolation_confined` (oracle lines 53, 61–62) does not, and the receipt records only a single bool, not which conjunct failed. Smallest safe correction: treat single-case negative results as non-evidence unless `positive/clean-cache-demonstration` passes in the same receipt. A fixture change is optional: either add the gate digest to the oracle's bound inputs, or have `--case` always include the step's positive. This is not a C1 defect.
- **Tradeoff B: the predicate checks the name, not the meaning.** This affects calibration and is already declared out of scope. The producer defines `isolation_confined` as `base_real.parent == var_tmp_real and root_real.parent == base_real and no symlinks` (`cache-demonstration.py:937-941`), and it emits `isolation.under_var_tmp` separately (line 1027). The runner checks only `isolation.cleaned` and `residue == []` (lines 523–525). So a payload with `checks.isolation_confined: true` but `isolation.under_var_tmp: false` and a `base` outside `/var/tmp` is still accepted. The lesson explicitly scopes this out ("not a proof that each producer assertion executed"; no malicious-producer attestation). It is a tradeoff the canonical judge should keep out of C1, not a fixable C1 defect. Adding a cross-check would be new scope.
- **Out of scope, as declared:** a duplicate JSON key such as `"isolation_confined": false, …, "isolation_confined": true` decodes last-wins and would be accepted (round-22.md line 35 excludes duplicate keys). Other neighbours are caught: count drift (32 or 34 keys) is rejected by line 514, and non-bool or wrong-type values are rejected by line 517.

## 4. Mutation drafts (not executed; L1 to run)

| Mutation | Expected result |
|---|---|
| **M-a:** delete line 516 (`and checks.keys() == CACHE_CHECK_NAMES`) | Kills `cache/name/isolation_confined`: observed True, want False. The other 32 `cache/name/*` rename vectors die the same way (33 vectors in the `cache-names` group). `positive/clean-cache-demonstration` survives. |
| **M-b:** at line 194, replace `"isolation_confined"` with `"bogus_isolation_confined"` in `CACHE_CHECK_NAMES` | Kills **both** `positive/clean-cache-demonstration` (observed False) and `cache/name/isolation_confined` (observed True). This shows the constant is literal and that the pair is sensitive in both directions. |

## Impacted axes

- **Calibration (claimed):** confirmed for this vector. It is discriminating (base FAIL, changed PASS, by source) and correctly labelled.
- **Coverage (no harm):** Limit A only.
- **Operability (no harm):** nothing harmed; unbound live gate digest noted.

## Process record

- **Tools:** nothing was installed or updated. I used tools already present: `jaq` 3.1.1 (as `~/.local/bin/jq`; it rejected a byte in the oracle JSON, so I switched to stdlib Python), stdlib Python `json` for read-only data extraction (no runner or oracle import), `git show`/`git status`/`diff`/`cmp` on the named paths, `sha256sum`, `awk`, and `rg`.
- **Scope deviation:** for the vector-history comparison I briefly wrote two `git show` oracle snapshots to `/tmp/souji-attack56-oracle-*.json` and deleted them in the same command.
- No other files were written, no seats were contacted, and nothing was executed beyond the reads above.
