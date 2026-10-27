## Status
STATUS: PARTIAL — identified five concrete semantic counterexamples from frozen source; no scratch reproduction or counter execution performed.

## Evidence
- `read census/round-34/preregistration.txt` at frozen list revision 2b0171e2071fdc9c16a69bed12b0d040e574d8c8: N4 is specified as load-stable; N3 says pinned bytes untouched; W1-W4 require strace create evidence; J1 is the stub control.
- `read census/round-34/c2-counter.py:134-203,207-233`: witness tracing and create regex, N3 pin check, and G6 committed-blob hash.
- `read tests/fixtures/r34-sandbox-junk.py:44-53,76-126`: J1 uses fixed echo/printf argv and checks failed-leg IDs.
- `read corpus/lessons/round-33-verifier-spotcheck.md` `## Routed defects` items 4-6 and `census/round-34/records/closure-sweep.txt:32-36,50-52`: defects routed to this claim.
- No command executions or scratch reproductions; no run output or load measurement claimed.

## Findings
1. **Witness can attest irrelevant work.** `census/round-34/c2-counter.py:155-179,199-203`: W1 accepts a fake tool that prints the real final line and creates irrelevant files in TMPDIR to meet the threshold. Routed issue: r33 spotcheck Routed defect 4. Smallest safe correction: bind evidence to tool-specific effects or add irrelevant-create mutant and narrow the claim.
2. **Strace matcher misses creation mechanisms / pre-trace work.** `census/round-34/c2-counter.py:157-158,177`: setup writes before strace are invisible; memfd creation is not a matched pathname syscall, and O_TMPFILE may not satisfy the listed flag alternatives. This can either admit unrelated activity or reject genuine work. Smallest correction: cover these forms and trace setup, or add explicit limits plus test cases.
3. **N4 equality is not load stability.** Preregistration C2 N4 and counter anchor behavior: two equal flaky runs at low sampled load may pass; a single load sample does not characterize load during runs. Smallest correction: require per-run load-qualified repeated pairs, or describe the observed property only as equality.
4. **N3 checks committed pin, not run-time non-modification.** `c2-counter.py:195-198,230-233`: both N3 and G6 hash the committed blob; neither compares the checked-out fixture bytes before versus after execution. Smallest correction: hash the fixture in the run clone on both sides of the run.
5. **J1 does not defeat invocation-aware junk.** `tests/fixtures/r34-sandbox-junk.py:76-94,117-132`: control injects fixed echo/printf stubs; it does not test a malicious tool that distinguishes fixture invocation via `/proc/self/cmdline`. Smallest correction: add such a behavioral mutation without changing frozen J1.

## Attack log
This item is an attack. The five findings above are source-grounded counterexamples; they are not reported as reproduced in scratch. No frozen predicate or artifact was changed.

## Deliveries
- `.ufo/waves/round-34/w1/deliver-c2-leg-attacks.txt`