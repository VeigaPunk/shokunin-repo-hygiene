## Status
STATUS: PARTIAL — recurrence mapped against frozen r34 design; no counters executed and no landing/tip run claimed.

## Evidence
- Read r34 preregistration (`census/round-34/preregistration.txt`, frozen rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8), both counter docstrings, C1 item header and all C2 leg definitions.
- Read `corpus/lessons/round-28.md` and round-28 verifier spot-check; rounds 29–33 lessons and verifier spot-checks where present.
- Source quote: `corpus/lessons/round-29-verifier-spotcheck.md` §Step-1 defects: “D1 — evidence cited before it landed.” Source quote: `corpus/lessons/round-33-verifier-spotcheck.md` §Routed defects: “D4: `r33-c1-counter` and `r33-c2-counter` are registered as `gate` with ‘no embedded selftest’.” Frozen source quote: `census/round-34/preregistration.txt` §C1: “the before-state is the counter's own reading at the base revision under the do-nothing control (nothing changed), never a hand count.”
- No runtime/counter command was executed; these findings are a design exposure analysis, not a result.

## Findings
1. Recurring classes evidenced across r28–r33: stale premise/conformance; number or measurement drift; reference/evidence drift and premature citations; landing/carry/disposition defects; vacuous/constants-fixture acceptance; moving/flaky anchors; contract mismatches. Round assignments and evidence pointers are listed in `deliver-recurrence.txt`.
2. Moving anchor risk is materially addressed: C1 binds frozen item/list revisions, executed causes and append-only bytes; C2 N4 requires two identical adjacent base readings, a rev match, flock/load record and a bounded retake. It does not prove invariance to all host states.
3. Premature wave-path citation remains outside the frozen checks: neither C1 nor C2 requires each wave path to resolve at the record-landing commit. r29 D1/r30 recurrence establishes this is a demonstrated failure mode.
4. Uncommitted gate readings remain a reporting risk. The counters bind their own measured lines, but no frozen clause here enforces that final report readings are committed receipts before reporting. The r33 verifier recorded D2, where report claim diverged from the committed run.
5. Constants/stub falsification is substantially stronger but bounded to named attacks: C1 ties statements to last digit-bearing output, fixed exit, nonvacuous immutable RESULTS and own-script corrections; C2 adds work witnesses, self-tracing cases, junk control and guards. Novel cheats remain suitable first falsifiers.
6. Before-state is improved: C1 explicitly defines counter-derived do-nothing reading and requires mismatches; C2 defines absent-file CNE control with feasibility evidence. The design does not itself commit every future report's pre-data claim receipt.

## Attack log
Not an attack reproduction. This is a scoped recurrence/design review; no frozen predicate or item was challenged by execution.

## Deliveries
- `.ufo/waves/round-34/w1/deliver-recurrence.txt`
