# Attack15 — `summary/r20-audit-contract/extra` (want=False) and paired `positive/r20-audit-contract`

Seat: SoujiR22.Attack15 (leaf, source-only). Code under attack: `4f83fd222ffbd8825340221a8c426550ef891191` (HEAD; named files have no working-tree delta vs this commit). Preregistered base: `41553adb139d06511dc386bb3ce4326aebfba675`. Oracle revision field: `ff425ab835614f38205426330b9cdb93fd267045`.

## STATUS

**Source-only PASS for this vector pair; PARTIAL as calibration evidence.** The literal expectation `want=False` is correct, and the fixture really does feed the stored stdout into `summarize_result`. The changed code returns False for the extra vector and True for the positive, both derived from source. However, the vector isolates the summary-line equality predicate. That predicate is byte-identical in the base, the oracle revision and the changed commit, so this pair is a regression guard rather than evidence for any R22-changed predicate. It also leaves two weakened forms of that predicate unkilled across all 214 vectors (see Finding 3). That gap is a coverage note outside the three defects claimed by C1, and it does not harm C1. Nothing was executed: I did not run the runner, the oracle, tests or a mutation. All values are derived from source or computed with read-only JSON/regex parsing of the pinned data files.

## 1. Stored delta, reconstructed before inspecting the predicate

Inputs (read-only, digests recomputed):

- `census/round-21/final-out-S1.json` sha256 `bc53a752…38fe` matches oracle `source_receipt_sha256` (`r22-result-oracle.json` line 4). The oracle enforces this at `r22-result-oracle.py:31-35`.
- `census/round-21/step-inventory.json` sha256 `8b7b1cd8…1310` matches `frozen_inventory_sha256` (line 6).
- The record `commands[name=r20-audit-contract]` has `returncode=0`, `stderr=''` (`stderr_sha256` = empty-string digest), and a 79-line stdout whose sha256 recomputes to the stored `stdout_sha256` `78d90ab3…443c`. It contains 78 `^CASE\tPASS\t` lines, exactly one SUMMARY line (`SUMMARY\ttotal=78\tpass=78\tfail=0\tbase_discriminating=11`), no `INVENTORY\t` lines, no `BASELINE_MISMATCH\t` lines, no FAIL-pattern lines, no CR or other `splitlines` separators, and a trailing `\n`. In the record itself, `matched=True` and `observed_summary` has one element.
- The frozen inventory step `r20-audit-contract` has `kind:"summary"`, the string `expected_summary` `SUMMARY\ttotal=78\tpass=78\tfail=0\tbase_discriminating=11`, `pass_pattern:"^CASE\\tPASS\\t"` and `pass_count:78`. It has no `<REVISION>` placeholder, no auxiliary lines and no `baseline_mismatch_count`. This is identical to `make_steps` at `run-acceptance.py:306-308`.

Vector (`r22-result-oracle.json` lines 147-153): keys `id, want=false, group=summary-control, step_name, stdout`. It has no `returncode`, `stderr`, `json_set` or `stdout_nested_array_depth` override. The vector's `stdout` (7902 chars) equals the record stdout byte-for-byte as a prefix, followed by exactly one appended line, `SUMMARY invalid synthetic summary\n` (unified diff: `@@ -79,0 +80 @@`). All 12 summary-control vectors use this same appended suffix.

**Does the fixture feed it?** Yes. `r22-result-oracle.py:67` binds `record` to `records['r20-audit-contract']`. Line 68 takes `case['stdout']` because the key is present. Lines 69-82 are skipped because neither mutation key is present. Line 83 deep-copies the frozen step (the substitution in `replace_revision` at lines 59-60 is a no-op for this step), and line 84 does not apply because the kind is `summary`. Lines 87-91 pass `returncode=0` and `stderr=''` inherited from the record, and the stdout encoded with surrogateescape. Lines 92 and 97 require `type(observed) is bool and observed is False`.

**Is want=False correct?** Yes. The step's contract is one exact summary line. A producer that emits a second `SUMMARY …` line has violated the single-summary output shape, so it MUST NOT be accepted as matched. The pinned real run emitted only one summary line, so the appended line is a pure fabricated deviation with a single cause: returncode, stderr, pass count, failure lines and auxiliary lines are all unchanged from a matched record.

## 2. Predicate trace at `4f83fd2`

`run-acceptance.py`:

- Line 118: `SUMMARY_RE = ^(?:SUMMARY|SELFTEST)(?:\t| ).*$`. Because of the space branch, the injected `SUMMARY invalid synthetic summary` line matches.
- Line 395: `summary_lines` is `[expected, 'SUMMARY invalid synthetic summary']`.
- Line 396: `failure_lines` returns `[]`, and line 410 gives `matched = (0 == 0) and True`, which is True.
- Lines 412-416: `expected` is a str, so `summary_match = summary_lines == [expected]` is **False**.
- Lines 432-435: the auxiliary lists are `[] == []`. `baseline_mismatch_count` is absent, so lines 440-444 are skipped. Lines 446-450 give `pass_count` 78 == 78.
- Line 463: `matched = True and False and True and not ''`, which is **False**. Line 537 gives `bool(False)`, so observed is `False is want`, and the vector **passes**.

Paired `positive/r20-audit-contract` (want=True, no overrides): the stdout is the raw record. `summary_lines == [expected]` is True, the auxiliary lists match, the pass count is 78, and stderr is empty, so line 463 gives **True** and the vector passes.

## 3. Attack on the changed predicate and the vector's discriminating power

**Finding 1 (observed): this vector does not exercise any R22-changed predicate.**

- `git diff ff425ab 4f83fd2 -- census/round-21/run-acceptance.py` shows the summary branch's only change: `matched = matched and summary_match and pass_match` became `... and not stderr` (now line 463).
- `git diff 41553ad ff425ab` on the same path touches only `source_state` and `main`, not `summarize_result`.
- At the base, the identical predicate sits at lines 118 (`SUMMARY_RE`), 352, 367, 373 (`summary_match = summary_lines == ([expected] if expected else [])`) and 417.

The extra vector has `stderr=''`, so the new conjunct is True and inert. The base and changed code therefore both return False for the extra vector and both return True for the positive. Neither vector is a before/after discriminator. That is consistent with their role (keep the 18 originals valid, keep the extra-line rejection), but they MUST NOT be counted as calibration gain. The changed conjunct is killed by the `stderr/*` group instead. Inverting it to `and stderr` would be killed by this positive, because the empty stderr would make matched False.

**Finding 2 (observed): mutations killed by this vector (drafted, not executed).**

- M-K1: change line 416 to `summary_match = (expected in summary_lines) if expected else not summary_lines`. Expected kill: `summary/r20-audit-contract/extra` with expected False and observed True. The positive is unaffected.
- M-K2: change line 416 to `summary_match = summary_lines[:1] == ([expected] if expected else [])` (first summary wins). Expected kill: the same vector, observed True.
- Deleting `summary_match` from the conjunction on line 463 is also killed by this vector.

**Finding 3 (observed from oracle data, inference about outcome): two weakened forms of line 416 survive every one of the 214 vectors.**

Read-only parsing of all 214 cases with the runner's own `SUMMARY_RE` gives three facts:

- In every summary-control vector, the extra line comes *after* the expected summary. The expected summary sits at position 0 for the 11 non-empty steps. For `agreement-pin-check` (expected `""`) the extra line is the only summary line.
- No vector for a string-expected summary step has the right number of summary lines with the wrong text. The query for `len(summary_lines) == (1 if expected else 0)` together with `summary_lines != ([expected] if expected else [])` returned zero cases.
- The only summary-text probe for a regex-expected step is `summary/r20-input-binding/oversized-count`.

Mutations that therefore survive [INFERENCE from the traced predicate and these data facts; not executed]:

- M-S1 (last summary wins): `summary_match = summary_lines[-1:] == ([expected] if expected else [])`. For every extra vector, the last line is `SUMMARY invalid…`, so the result is False and the decision is unchanged. Single-line positives are unchanged. This would accept stdout where a spurious summary line *precedes* the real one, which the exact contract rejects.
- M-S2 (count only): `summary_match = len(summary_lines) == (1 if expected else 0)`. Extra vectors have 2 lines (or 1 against an expected 0), so the result is False and the decision is unchanged. Positives are unchanged. This would accept a single wrong summary such as `SUMMARY\ttotal=78\tpass=78\tfail=3\tbase_discriminating=11`. The `fail=3` text is not a FAIL-pattern line under `failure_lines` (lines 356-359), and the 78 pass lines still count. So the pass-count check would not catch it either.

Neither mutation touches code changed in R22, and C1 claims only scalar typing, summary stderr and cache identity. This is a pre-existing oracle coverage gap, not a C1 falsification and not harm to any claimed axis. To close it, add two summary-control vectors: one with `SUMMARY invalid synthetic summary\n` *prepended* to the record stdout (kills M-S1), and one replacing the single summary text, for example `fail=0` changed to `fail=3` with everything else exact (kills M-S2). Both would have want=False. They would not change the 214-vector before/after comparison, since base and changed behave alike here.

**No concrete mismatch** was found between the stored delta, the pinned record or inventory, the fixture plumbing, the literal expectation and the changed predicate for this pair.

## Limits

- I did not run the runner, oracle, tests or mutations. The observed/expected outcomes above are traced from source. The data facts come from read-only parsing of the hash-verified JSON files, and the decisions about mutation survival are inference.
- Scope is this vector, its paired positive, and summary-line-equality coverage across the oracle. Other groups were not audited. This is not malicious-producer attestation or universal malformed-input totality. F5, reap, NAMESPACE, exposure, certification and K5 holds are unchanged.
- Read-only git used: `diff`/`show` on exact named paths, and `log`/`status`/`cat-file`. No mutations.
- Tooling installs: none.
