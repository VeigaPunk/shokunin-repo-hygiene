## Status
PARTIAL — W1’s E07 blockage is independently supported by its committed control and rule/source inspection; no alternate conforming route is identified. This is evidence review, not a new execution.

## Evidence
- Frozen list revision: `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`; base: `9c76c7222a8abff027af42e37f0d160d52526bba`.
- Frozen row `census/round-34/c1-items.tsv:47`: E07 pins exit 2, predicate `SUMMARY findings=2`, script `tools/souji-landing-gate.py`, argv uses `--rev 6cb22dc20c9fdb3c7a49eaa1accabca339054c17 --round 27`.
- `census/round-34/records/controls-c1-do-nothing.txt:31` records E07 as MISMATCH at base: rc=2 but last line is `COULD-NOT-EVALUATE ... at 6cb22dc...`, not `SUMMARY findings=2`.
- W1’s `deliver-c1-E07.md:38-63` reports parent/cause executions and base invocation: the pinned revision has no committed reports; its own row-writing cause and parent both fail the original predicate. The W1 base run’s corrected argv succeeds with rc=0 and reports `SUMMARY findings=0 ... checked_reports=94` (`:53-61`).
- Frozen rules in `census/round-34/preregistration.txt:48-57`: a correction must be an appended restatement; argv corrections require the cause to have written the row and the row’s own argv to have already failed there; `same` corrections require parent-holds/cause-fails. Prior binding corrections are honored only when one exists. W1’s `deliver-c1-E07.md:29-36` says its search found no prior correction binding `SCORECARD.md:31`.
- `census/round-34/c1-counter.py:243-300` implements these branch conditions; lines 301-313 evaluate the corrected run and require the quoted statement to equal its last digit-bearing output line.

## Findings
1. **W1’s correction is rule-conforming; the alleged blockage is not real (source-level determination).** The frozen clause asks that the cause wrote the row and that the row’s original argv already failed at the cause. W1 identifies `c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0` as the row-writing cause, and reports the original argv fails at both its parent and cause (`deliver-c1-E07.md:40-50`). The corrected argv runs the same script, changes its measured revision to the base, and produces rc 0 plus an exact last digit-bearing summary (`:53-61`). Counter source `census/round-34/c1-counter.py:262-300` confirms argv corrections do not require the parent-holds/cause-fails transition (that check applies only to `same`). W1’s scratch simulation reports AGREE (`deliver-c1-E07.md:71-78`). This seat did not rerun it, so that result is attributed to W1 rather than independently reproduced.
2. **No alternate route is required.** The `same` route would need a parent-holds/cause-fails transition, which W1 says is absent; the valid route is the argv correction above. The initial mismatch is corroborated by `census/round-34/records/controls-c1-do-nothing.txt:31`, so there is no indication it is a measurement artifact.
3. **Measurement-artifact concern not supported by available evidence.** Independent do-nothing record corroborates the initial mismatch; W1’s correction simulation is an observed committed report claim, but this seat did not rerun it, so it is not a new reproduction.

## Attack log
- Read frozen row, preregistration correction contract, counter judge source, base do-nothing receipt, and W1 E07 deliverable.
- No new counter, fixture, or cause execution performed; no execution output is claimed.
- Adversarial clause check: the reported correction satisfies the argv branch’s distinctions on its face (row-own script, cause writes row, original argv fails at cause); `same`-route transition is irrelevant to that argv correction.

## Deliveries
- `.ufo/waves/round-34/w2/AttackE07.md`
- No lane files or frozen artifacts changed.
