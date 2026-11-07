## Status
STATUS: PASS — prose review only; no lane or fleet artifacts changed.

## Evidence
- Read frozen contract: `souji-shokunin/.ufo/waves/round-27/preregistration.txt:5-9` (base `e78ac7c4837b81b634db4a927605a751a7f006ba`): “Before: `findings=2` at e78ac7c. After: `findings=0` at the landing tip.”
- Compared draft `souji-shokunin/.ufo/waves/round-27/w1/round-27.md:3-6,26-62` with r25 lesson skeleton `souji-shokunin/.ufo/waves/round-25/w1/lesson-skeleton.md:107-124` and r26 distillation `souji-shokunin/.ufo/waves/round-26/w1/distill-findings.md:1-10`.
- Revision context: current round draft is a wave artifact; r25 example identifies its base and distinguishes draft from claim data. No counters were run; no outcome inferred.

## Findings
1. Placeholder noise in the r27 draft: the opening disclaimer (lines 3–6) and placeholders at lines 26–31, 35–36, 42, 46–47, 62 are scaffolding, not lesson prose. Remove them at integration; replace only with measured facts. The “empty template” at line 62 duplicates the explicit placeholder and should not ship.
2. Duplicate boilerplate: Gate candidates already restate C1–C3 from the frozen preregistration (lines 10–24), while the opening disclaimer repeats that values are placeholders. Keep a compact claim summary once; put the measured work and evidence in the sections below it. Avoid repeating the same target/counter in Work performed and Trend verdicts.
3. Unsupported as currently drafted: `round-27.md:37-38` says C3 now covers the handoff misread, but the draft itself supplies no fixture case/result demonstrating that; prereg C3 names four checks and does not name this handoff behavior. Also `:51-58` attributes the fix to C3 and cites the fleet watchdog outside lane scope. Do not assert causal coverage unless a lane-owned source and executed evidence establish it. The required quote/location form for source claims must use opened bytes and a <=25-word quote; fleet watchdog is also outside this seat’s write boundary.
4. Trend verdicts: none are present in the r27 draft. Do not copy r25’s provisional trend verdicts as boilerplate. Each verdict needs the axis definition, measured evidence, a bounded conclusion and falsifier; otherwise mark it unassessed rather than imply improvement.

## Tightened skeleton

### Work performed
- **C1 — calibration:** [change actually landed; exact path/revision]. Evidence: [frozen counter command; base and tip outputs; receipt path]. Result: [findings before → after]. [State exemption scope and any residual only if evidenced.]
- **C2 — coverage:** [entries and registry rows actually admitted]. Evidence: [source anchors/access dates, gate-check output, registry/ground-count commands, sources-census result and receipts]. Result: [measured before → after values].
- **C3 — operability:** [gate and fixture actually landed]. Evidence: [fixture command/output, including case count and false-green control result; receipt path]. Result: [exit status and named checks].

### Trend verdicts
- **Calibration:** [improved / unchanged / harmed / unassessed]. Evidence: [C1 measured result and relevant counter/receipt]. Bound: [what this measurement does and does not establish]. Falsifier: [frozen kill condition or observed contrary evidence].
- **Coverage:** [improved / unchanged / harmed / unassessed]. Evidence: [C2 grounded-entry and registry results plus gate/census evidence]. Bound: [newly grounded scope; avoid equating added rows with broader capability absent evidence]. Falsifier: [frozen kill condition or contradictory source/gate result].
- **Operability:** [improved / unchanged / harmed / unassessed]. Evidence: [C3 executed cases/control and receipt]. Bound: [checks exercised; do not claim general readiness beyond them]. Falsifier: [any failed case or false-green accepted, per frozen rule].

## Attack log
- **ATTACK — unsupported C3 causal claim:** the draft says the handoff-readiness check covers R27-M1, but the frozen C3 description lists branch-tip, report-heading, worktree-leftover, and prereg-presence checks only. Either provide executed, lane-owned evidence tying a named case to the handoff failure, or remove the claim; do not change the frozen predicate.