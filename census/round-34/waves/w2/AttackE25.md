## Status

Source-level adversarial review; no fixture or counter execution performed. Finding: E25 is a real frozen measurement/statement-binding defect, not evidence that the underlying capability counter is wrong. The W1 diagnosis is supported; an honest route to agreement is not apparent under frozen rules.

## Evidence

- Frozen E25 row, `census/round-34/c1-items.tsv:70` (list revision `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`): expected exit 0 and exact statement `SUMMARY k1=0 k2=0 mismatches=0 rows=18 pointers=10`; argv runs `tools/souji-capability-agreement.py` at revision `7b16731fcd8ab9b95220b50603314aa8dc92b2ec`, base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`, list revision `d4928ec86b667e3d1ed0adb07fb088e500cf1631`.
- The frozen do-nothing receipt `w1/deliver-c1-do-nothing-check.txt:59` reports E25 `rc=0`, but bound last digit-bearing line is `KINDS value=0 shape=0 rc=0 (diagnostic; not part of the target)`, thus predicate fails. This is consistent with the frozen rule that bare predicates bind to the LAST digit-bearing line, preregistration lines 41-47.
- W1’s 60-item run also shows the same last line and E25 mismatch (`w1/SwarmExecutor13.md:60`). The counter does not count that diagnostic as its target statement.
- The preregistration lines 48-57 permit only appended restatement with a same-value or corrected argv, full ancestor cause, and cause executed (value change parent-to-cause, or argv correction when cause wrote row and row argv already failed). Line 55 says prior same-item correction makes it agree.

## Findings

1. **Real statement-binding mismatch; no honest frozen correction route identified (inference from source and receipts).** The target summary exists as an earlier output line, but E25's predicate is bare and therefore applied to the last digit-bearing line instead. The latter is explicitly diagnostic, not the target. As the frozen argv exits 0 and its target summary appears correct, this is not a demonstrated underlying tool-output correctness failure; it is a row-vs-instrument binding failure.
2. Merely changing the statement to the diagnostic would not honestly preserve the original SCORECARD claim: the diagnostic is labeled “not part of the target,” and the row claims the SUMMARY counters. A same-value correction cannot cure a last-line mismatch. An argv correction must still run this row's own script and must be justified by a cause where the original argv failed; no such cause is evidenced here. These constraints leave no honest route in the frozen contract, rather than a benign alternative explanation for the observed mismatch.
3. **Counter-evidence / limitation:** no independent execution was done, and the original output is evidenced only by committed W1 receipts. I cannot claim exact reproduction beyond those receipts. W1's interpretation that this specific measurement failure makes the overall target unreachable is stronger than needed for this seat: this review confirms E25 mismatch mechanism, not a full reachability proof across other items.

## Attack log

- Read frozen C1 row and preregistration, including restatement, predicate, cause, and Q76 clauses.
- Compared E25 target statement and argv with committed do-nothing receipt and W1 mismatch table.
- No command/probe executed; no lane files changed.

## Deliveries

- This report: `.ufo/waves/round-34/w2/AttackE25.md`.
- Revisions referenced: base `9c76c7222a8abff027af42e37f0d160d52526bba`; frozen list/counter repair re-pin `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`; E25 argv's pinned tool revision `7b16731fcd8ab9b95220b50603314aa8dc92b2ec`.
