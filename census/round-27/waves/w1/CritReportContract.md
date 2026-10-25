# CritReportContract — round-27 w1 planned-report attack (marker/gap risk)

## Status

STATUS: PARTIAL — 4/6 checklist items pass on the current plan; item 5 (wave shape/seat counts/roles/dead seats/planner-seat mapping) is unplanned, and item 2 (bullet-to-pointer backing) has no enforcement against `[PENDING]` residue at filing. Both are fixable before filing; corrections below.

## Evidence

- Plan source: `w1-spec.json` item ScribeReport (`.ufo/waves/round-27/w1-spec.json:383-386`): "Assemble the full round report draft ... with sections in order: Work performed (naming claims C1/C2/C3 and target axes), Landed changes, Before→after measurements, Sources & frontier, Trend verdicts, SHONEN (4 box lines with `[~]`/`[ ]` + pointers), Stale-lane, installs. ... use `[PENDING:<what>]` only where the L1's integration values are required."
- Contract: `templates/round-prompt.md:101-125` — required sections in order, "each carrying an evidence pointer (path:line, command output, or commit hash)", "Sources & frontier ... This is a conformance item", "Trend verdicts — one verdict each for expansion, quality, and discernment", "SHONEN — one line per box", marker rule "placeholder text ... counts as the round failed".
- `PROTOCOL.md:100-101` (five child-lane items incl. "commit-before-report ordering", "commit-hash citation rule"); `PROTOCOL.md:117-121`: "A lane report lands last — written only after the lane's child-repo work is committed, and it must cite that commit's hash" and "not an ancestor of HEAD at closure is a conformance defect".
- Watchdog `report_of` validates heading + `MIN_REPORT_BYTES=400` only (`scripts/shokunin-watchdog.sh:54,140-164`); it does not check placeholders, pointers, or Trend verdicts.
- Wave artifacts: `w1/wave-note.md:9-11` "Spawn count: 79 (spawn=79, resume=0, total=79)" and role histogram (connector 3, scout 11, executor 25, reviewer 12, critic 10, mutation-tester 6, simplifier 3, revenger 1, scribe 8); `w1/swarm-registry.json` has 79 `"role"` members; `w1-spec.json` has 79 items. Note: SimplWaveSpec's prompt still says "Review the 80-item wave spec" (`w1-spec.json:345`) — stale count.
- Model: `.ufo/reports/round-26/souji.md:12` ("**Round shape / swarm:** w1 spec 87 seats (role mix per `w1-spec.json`)"), `:34` (lane pushed, "This fleet report is the final commit and is pushed separately"), `:65` ("Stale-lane: mission progressing ..."). Prior souji reports all record "L1 holds the canonical planner seat" (round-13/14/15).
- SHONEN.md has four boxes (`SHONEN.md:5,7,9,11`).

## Findings

1. **Item 5 FAIL — wave shape/seat counts/roles/dead seats/planner-seat mapping unplanned.** ScribeReport's skeleton (w1-spec.json:385) names no wave-shape section/bullet; no seat is tasked to add it. The material exists (`wave-note.md`, `swarm-registry.json`, `w1-validate.out`), but nothing plans its inclusion. Prior r13–r26 souji reports all carry it; omission would break the lane's own convention. Risk: a 79-seat wave reported with no size/role/dead-seat/planner line.
2. **Item 2 PARTIAL — pointer backing planned but unenforced.** The template and r26 model require pointer-per-bullet, yet the scribe prompt permits `[PENDING:<what>]` and nothing checks they are gone at filing (watchdog checks heading+bytes only). Left-in placeholders = "placeholder text" → round failed under the marker rule. Also: any cited hash must exist and be an ancestor of HEAD at closure (PROTOCOL:119-121); no planned check.
3. **Item 1 PASS — sections planned.** All contract sections appear in order in the scribe prompt, including both conformance items (Sources & frontier, Trend verdicts). Ensure the Sources & frontier block carries rows before→after with counting command, tiers added, touched old→new, and frontier rows advanced (r26 model), not just census rc.
4. **Item 3 PASS — SHONEN heading rule planned.** 4 box lines with `[~]`/`[ ]` + pointers matches SHONEN.md's four boxes; C3 gate enforces exactly one `^## SHONEN` heading; no `[x]` without a named non-author verifier (none this round, as r26).
5. **Item 4 PASS with sequencing caveat — timing.** C3 pre-report gate enforces tip==ls-remote and clean lane worktree, i.e. push-before-report mechanically; PROTOCOL:117 mandates report-last + cited tip being HEAD's ancestor. Caveat: the gate runs before the fleet report is committed; the L1 must run it as the last lane-side step, write the fleet report citing that same rev, then fleet-commit+push (round-prompt:133-134), and make no further lane commits afterward.
6. **Item 6 PASS — Stale-lane line planned.** ScribeReport lists Stale-lane as a section. It must state the true mission state (attempt 2 progressing via lane commits; no other open mission; never silent/failed) per protocol and r26 style.
7. **Count hazard.** The plan's own SimplWaveSpec prompt says "80-item", but the artifacts say 79 (spec items, registry members, spawn). The report must take counts from `w1-spec.json`/`w1-validate.out`/`swarm-registry.json`, never from memory or earlier prose; record any dead seats (provider failures) by name like r14/r15 kama precedent.

## Attack log

- Attack (primary): the planned report has no home for the wave-shape/seat/planner record — a conformance-by-convention item — despite validating artifacts being ready. Smallest safe correction: add to the report skeleton a "Round shape / swarm" bullet in Work performed, sourced from `wave-note.md:3-11` + registry counts, plus a dead-seats line to be filled before filing.
- Attack (secondary): `[PENDING:<what>]` residue would fail the marker rule undetected (watchdog cannot see it). Smallest safe correction: add a pre-filing check — zero `[PENDING]`/placeholder tokens; every Landed-changes row maps to a LOG entry + commit; every cited hash passes `git merge-base --is-ancestor`; measurement rows carry command + measured commit.
- Attack (tertiary): sequencing — after the C3 gate passes, nothing may touch the lane; report must cite the gate-verified tip and be committed/pushed on the fleet repo last.
