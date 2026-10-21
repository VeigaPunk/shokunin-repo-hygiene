# Attack12 — `stderr/agreement-pin-check/error` (want=False) vs changed summarizer 4f83fd2

Seat: SoujiR22.Attack12. Leaf, source-only. No tests, builds, oracle runs, or empirical probes.
No tools installed or updated.

## STATUS

**Source-only PASS. No concrete mismatch found.** Expected decision `want=False` is correct under
the round-22 contract. The fixture does feed the stored stderr delta into `summarize_result`
for the frozen `agreement-pin-check` step. Reading the source, the changed predicate yields
`matched=False` for this vector and `matched=True` for the paired positive. The base summarizer
41553adb yields `matched=True` for this vector, so the vector discriminates base from changed.
Limits: these observed values are derived from reading source, not from running anything. L1's
214-decision run is the runtime authority. The producer `census/round-19/verify-agreement-pin.py`
is outside the named read set, so I did not check its real stderr behaviour. The
`record_checks: 1` provenance is out of claim scope (lesson round-22.md:35).

## 1. Stored delta, reconstructed from pinned public bytes (before predicate inspection)

Oracle vector (`tests/fixtures/r22-result-oracle.json:551-557`):
`{"id":"stderr/agreement-pin-check/error","want":false,"group":"stderr","step_name":"agreement-pin-check","stderr":"ERROR: synthetic producer incomplete\n"}`.
The only delta is `stderr`. There is no `returncode`, `stdout`, `json_set` or depth override.

Pins: oracle header (`r22-result-oracle.json:3-7`) binds `source_receipt_sha256=bc53a752…38fe` and
`frozen_inventory_sha256=8b7b1cd8…1310`, with revision `ff425ab8…7045`. On-disk sha256 of
`census/round-21/final-out-S1.json` and `census/round-21/step-inventory.json` equals those values
exactly. `git status` is clean for both files and for the oracle files. The oracle file at HEAD
4f83fd2 hashes to `292442a6…0651`. The diff 36c78ba→4f83fd2 adds 14 lines to the oracle JSON and
does not touch any agreement-pin vector. Byte-identical vector text exists at
36c78ba:`r22-result-oracle.json:552-556`. The case count is 214, which is the lesson's 212 plus the
two later depth controls.

Reconstructed input tuple (oracle.py:67-91):
- record: `final-out-S1.json:2321-2328`, the only `agreement-pin-check` entry in `commands` (grep count 1).
  `returncode=0`, `stdout=""`, `stderr=""` (sha256 e3b0c442…, which is the empty-string hash), `matched=true`.
- step: `step-inventory.json:169-185`, the only entry. `kind="summary"`, `expected_summary=""`,
  `pass_pattern=null`, `pass_count=0`, `record_checks=1`. `replace_revision` (oracle.py:40-47,59-60) is a
  no-op here because there is no `<REV>`/`<REVISION>` token. The argv `<PYTHON>`/`<ROOT>` placeholders reach only
  `result["argv"]`/`shlex.join` (run-acceptance.py:399-400), never the decision.
- fed call: `summarize_result(step, 0, b"", b"ERROR: synthetic producer incomplete\n", revision, ROOT)`.
  `case.get('stderr', record['stderr'])` at oracle.py:90 selects the case value. stdout is the record's `""`
  (oracle.py:68), and returncode is the record's `0` (oracle.py:88).

The frozen step matches the runner's live step on every field the predicate reads.
`run-acceptance.py:336-337` has `expected_summary ""`, `pass_pattern None`, `pass_count 0` and
`record_checks 1`. It has no `kind`, so it defaults to `"summary"` at :411.
**The fixture feeds the intended input.** The only changed variable from the real green record is
a nonempty stderr on an exit-0, empty-stdout summary step.

**Expected decision is correct.** The preregistration names "summary stderr accepted despite success" as an
admitted defect. Lesson round-22.md:7 says summary stderr "must be zero bytes". R22-M2 at :16 says to
"reject any nonempty summary stderr". `agreement-pin-check` is one of the twelve summary-kind
steps (run-acceptance.py:302-337). Rejection is the literal contract outcome.

## 2. Changed predicate on this vector (4f83fd2 `census/round-21/run-acceptance.py`)

The only edit on this path is :463, `matched = matched and summary_match and pass_match and not stderr`.
Base had `matched = matched and summary_match and pass_match` (git diff 41553adb..4f83fd2).

Trace, changed:
- :393-394 decode with `surrogateescape`, giving stdout `""` and stderr `"ERROR: synthetic producer incomplete\n"`.
- :395 `SUMMARY_RE` (:118 `^(?:SUMMARY|SELFTEST)(?:\t| ).*$`) gives `summary_lines=[]`.
- :396/356-359 `failure_lines` on the stderr text: `"ERROR:"` matches none of `FAIL\t`, `CASE\tFAIL\t` or `CASE\t…\tFAIL`, so it returns `[]`.
- :410 `matched = (0 == 0) and not [] = True`.
- :416 expected is `""`, so `summary_match = [] == []`, which is True. :432-436 auxiliary `[] == []` is True.
  :440 `baseline_mismatch_count` is absent. :446-450 pattern None gives 0 == 0, True.
- :463 `not stderr` is False, so `matched=False`. :537 `bool(False)`.
- oracle.py:97 `observed is want` (False is False) gives **pass**.

Base trace is identical up to the final line, which lacks `and not stderr`, so it gives `matched=True` and the vector **fails at base**.
The vector discriminates in the preregistered before→after direction.

Bypass attempts on `not stderr` for this channel:
- Encoding: `surrogateescape` decode is total and length-preserving for non-empty bytes, so no non-empty
  bytes value decodes to `""`. Whitespace-only and invalid UTF-8 are rejected, consistent with lesson :7.
- Exception path: no `.get` or `int()` is reachable for a summary step with a string `expected_summary`, so the
  vector cannot be "rejected" by a crash. oracle.py:97 would count a crash as failed regardless.
- Ordering: :464-465 (`carry-invariant-probe` special case) runs after :463 and can only further AND, so it cannot re-green.

## 3. Paired positive `positive/agreement-pin-check` (want=True, `r22-result-oracle.json:538-543`)

Same trace with `stderr=""` from the record: :410 True, summary/aux/pass all True, and :463 `not ""` is True,
giving `matched=True`. That matches `want` and the historical `matched: true` at final-out-S1.json:2308. Base gives True as well.
No no-harm regression on this control.

Non-mismatch weakness (recorded, not claimed as a finding against C1): the positive acceptance condition
for this step is only "exit 0, no stderr, no SUMMARY/SELFTEST/INVENTORY/FAIL-marker lines on stdout".
Any other stdout text (for example `MISMATCH …`) would still be green. `record_checks: 1` is only echoed into
`matched_counts` at :461 and is never checked. The lesson at :35 explicitly excludes "agreement record_checks
provenance" and "arbitrary stdout failure-marker semantics", so this is in-scope-excluded, not a defect of 4f83fd2.

## 4. Drafted mutations (not executed)

- **MUT-A** (:463) delete `and not stderr`, which restores the base predicate. Expected to be killed by
  `stderr/agreement-pin-check/error` (observed True, want False), and by every other summary-step stderr vector.
- **MUT-B** (:463) `… and pass_match and (not stderr or not step["expected_summary"])`, an exemption for
  empty-expected-summary steps. `agreement-pin-check` is the only summary step with a falsy `expected_summary`
  (:302-337), so MUT-B survives every other summary stderr vector. It is expected to be killed only by the four
  `stderr/agreement-pin-check/{error,blank,pass,warning}` vectors, with this vector among them. This shows the
  agreement-pin stderr group is non-redundant. Within the group, `/error` alone is not a unique killer, since any one of the four kills MUT-B.

## Remaining unknowns

- Runtime confirmation that the oracle observes `False`/`True` for this pair is left to L1's 214-decision run.
- Real `verify-agreement-pin.py` stderr behaviour on success or failure was not read (outside the named paths).
