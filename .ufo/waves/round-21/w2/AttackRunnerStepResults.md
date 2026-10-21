STATUS: PARTIAL — The pinned C2 runner has source-visible false-green paths in result summarization, so its `all_matched` result is weaker than the stated acceptance checks. This is a source-only advisory review; no runner, matrix, or fixture was executed.

## Findings (by severity)

### HIGH — Exact counter JSON accepts booleans in place of integer fields

Pinned `census/round-21/run-acceptance.py`, `summarize_result` (counter branch, lines 420–445), compares exact counter output with Python `observed == expected` at line 427. Python considers `False == 0` and `True == 1`; it does not enforce JSON scalar types. The pinned step inventory marks the four r13/r14 counters exact, including `r13-counter-31984f4` with integer `F2_entry: 0` and `evidence_gate: 0` (`census/round-21/step-inventory.json`, lines 207–227).

Concrete false-green: for that counter, a JSON result with those two fields `false` (and all other expected values unchanged) compares equal to the expected dict. `numeric_leaves` excludes booleans, so `matched_counts` would expose the missing numeric leaves, but lines 435–445 do not make that count gate `matched`; with return code 0 and empty stderr, the counter can still be marked matched. Thus “exact JSON” does not currently mean exact JSON types/values.

### HIGH — Summary steps can pass with arbitrary error text on stderr

`failure_lines` at lines 330–333 recognizes only `FAIL\t`, `CASE\tFAIL\t`, and the corresponding `CASE … FAIL` form. In the summary branch (lines 367–419), `matched` requires return code 0, no recognized failure line, expected summary/counts, and auxiliary checks—but never requires empty stderr. The counter and cache-demo branches explicitly reject non-empty stderr (lines 445 and 480), making this a summary-only gap.

Concrete false-green: the pinned `auditor-selftest` expects `SELFTEST\tpass=118\tfail=0` and 118 `PASS\t` lines. If a summary-step process returns code 0 with exactly those stdout lines but stderr `ERROR: self-test could not complete`, `failure_lines` is empty and the summary branch marks it matched. The record retains stderr, but `all_matched` can still be true. This means a failed diagnostic that is not in the narrow marker vocabulary is not reliably surfaced as a failed step.

### MEDIUM — Cache demonstration checks are counted, not identified or tied to case content

For the pinned `clean-cache-demonstration` inventory row, expected checks=33 and cases=4 (`step-inventory.json`, lines 187–205). The cache branch at `run-acceptance.py` lines 456–480 checks `len(checks) == 33`, that every value is exactly `True`, and `len(case_rows) == 4`; it does not validate check names or case-row contents.

Concrete false-green: a payload with four arbitrary case rows and 33 uniquely named, unrelated checks all set to `true`, plus the required top-level fields, matching gate SHA, cleaned isolation, return code 0, and empty stderr satisfies `demo_match`. One omitted required check can therefore be replaced by a bogus check without making this step fail. The frozen inventory records only these count/summary expectations, not the check-name set.

### LOW — `source_unchanged` overstates the state actually sampled

`source_state` at lines 524–533 records HEAD and, for non-bare sources, `git status --porcelain --untracked-files=no`; for bare sources it records HEAD and an empty status. The runner compares this sample before/after (lines 564, 617–619) and then unconditionally writes `source_unchanged: true` (line 623). This does not prove the entire source repository was unchanged: untracked additions/deletions are omitted, non-HEAD refs in a bare source are omitted, and transient changes reverted before the final sample are not observed. The matrix has a refs hash but likewise omits untracked paths (`replay-matrix.sh`, lines 27–32).

Wording note: the runner's `scope` text says “source HEAD/tree not measured” (line 635), although HEAD and tracked status are sampled; the accurate limitation is that it does not hash/measure the complete source state or require source HEAD to equal `--rev`. Avoid treating either that sentence or `source_unchanged: true` as proof of whole-repository byte identity.

## Matrix / residual risk

Pinned `replay-matrix.sh` compares a stable, ordered tuple per command—name, return code, observed summary, matched counts, and matched flag (line 54)—and requires three signatures for `summaries_equal` (line 61). This is comparable for those selected summary fields, but it is not equality of complete command records: it omits stderr, raw stdout, and `observed_json`. In particular, the summary-stderr false-green above can leave matrix signatures equal despite different stderr. No independent matrix mismatch was established beyond that limitation; its output should be described as selected-summary parity, not full-output parity.

## Verification gaps

The pinned runner, matrix, frozen inventory, and replay-boundaries fixture were read; no acceptance command or target code was executed, as required. Therefore there are no observed exit codes or runtime summary lines to report. `xd://lsp` is not a mounted device in this session (the availability check returned “No such tool”); no LSP caller/definition/diagnostic results are claimed, and no grep fallback was used. No tools were installed.