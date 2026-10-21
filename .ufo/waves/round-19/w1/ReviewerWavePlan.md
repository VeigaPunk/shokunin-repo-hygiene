STATUS: DONE — the 90-seat design is broadly claim-covered and has a workable role mix, but contains a scope violation, one duplicated replay seat, a C2 contract ambiguity, and a missing count-level C3 falsifier; the packed 68-seat plan is below the registered target.

# Findings

1. **HIGH — the packed plan is outside the registered Wave 1 size.** The preregistration requires 84–96 genuine seats for Wave 1 ( `.ufo/waves/round-19/preregistration.txt:72-76` ). The original 90-item `w1-spec.json` meets that range, but the active `w1b-spec.json` declares 68 items and says 22 were dropped for the process-wide job cap (`.ufo/waves/round-19/w1b-spec.json:2-6`). The note expressly says this is not a low-value judgment, so I would not call those dropped items padding. However, no amendment to the 84–96 contract appears in the preregistration. Record a disposition/waiver or otherwise resolve this mismatch; do not present 68 as meeting the declared range.

2. **HIGH — `ScoutInherited` asks for forbidden operator-owned state.** Its prompt requests the operator-sweep path state (`.ufo/waves/round-19/w1-spec.json:544-549`), while the binding contract says the operator sweep is never to be opened or touched (`.ufo/waves/round-19/w1b-spec.json:5`). Remove that subtask or require an explicit “not inspected; prohibited” result. The rest of the inherited-state check is separable and need not be dropped.

3. **MEDIUM — the C2 reviewer prompt conflicts with the preregistered durable-ref allowlist.** C2 specifies `refs/heads`, `refs/tags`, and `refs/remotes`, never `refs/jj` (`.ufo/waves/round-19/preregistration.txt:33-37`); `ExecRevHelper` repeats that allowlist (`w1-spec.json:200-205`). But `RevRevPin` asks for behavior consistent with the broader r17 rule of every ref except `refs/jj`, explicitly raising `refs/stash` and `refs/original` (`w1-spec.json:240-245`). Make the review test the preregistered allowlist (including refusal outside it), or amend the claim before measurement; otherwise the same behavior can be scored both compliant and defective.

4. **MEDIUM — the auditor path-laundering mutation is not activated by the specified fixture cases.** `MutAuditPatchPath` mutates the allow predicate to accept a `tools/` path when the transcript claims a `.patch` suffix and requires the fixture to fail (`w1-spec.json:160-165`). `ExecAuditFixture` specifies an ordinary `tools/souji-census.sh` write, but no forged `.patch`-attributed `tools/` destination (`w1-spec.json:136-141`). Add that exact adversarial transcript/path case, plus the arbitrary-lane-write case requested by `RevAuditShapes` (`w1-spec.json:144-149`), or the mutation result may be unactivated and the whitelist’s key laundering risk remains untested.

5. **MEDIUM — C3 has no count/source-validation measurement item.** C3 has meaningful content-level challenges: `ReviewerProcEntry`, `CriticProcEntry`, and `ScoutProcFixtureMap` examine its evidence and limits (`w1-spec.json:328-381`); pointer review is also assigned (`w1-spec.json:704-709`). But no item re-derives the claimed admitted-entry count change or runs the source-registry validation after the proposed entry/rows. Add an explicit falsifier for the 6→7 count and the source-census result. This is not a wholly unchallenged claim, but its first falsifier is weaker than C1/C2’s base-vs-changed fixtures.

6. **LOW — merge the duplicate replay scouts.** `ScoutCarryReplay` and `ScoutGateReplayExpect` both inspect the r17 replay runner/expected tuples and determine whether the round-18 gate leaves all five replays unchanged (`w1-spec.json:24-29,472-477`). Merge into one seat retaining both the comparison semantics and exact tuple/base-revision requirements. That removes a genuinely duplicative assignment while leaving 89 seats, still inside the registered target. I would not drop a whole role family: the 90-item role mix is varied, and the implementation, mutation, review, source, and integration tasks generally have distinct outputs.

# Evidence

- Read the complete 90-item roster and grouped its `axes` and `role` fields in `.ufo/waves/round-19/w1-spec.json:6-727`: 90 total; 53 calibration, 20 operability, 16 coverage, and 1 freshness. Role counts: 31 scouts, 12 reviewers, 11 executors, 9 scribes, 8 connectors, 6 critics, 4 mutation-testers, 4 revengers, 3 simplifiers, and 2 sentinels. The calibration-heavy allocation is consistent with calibration being the lowest axis; the single freshness task is a specific carried S038 anchor issue, not a substitute for C3 coverage.
- The plan’s main claim paths have first attacks: C1 carry has explicit positive/negative fixture cases and mutations; C1 auditor has a fixture and mutation task (with the laundering gap above); C2 has a durable-ref fixture and helper mutants. C3 has static entry/source review, but lacks the stated count/source-validation measurement.
- No same-file executor ownership collision is apparent: executor deliverables are named as distinct report-sidecar artifacts, with separate carry, auditor, rev-pin runner/helper, D2, and D5 targets. The intended helper-to-caller dependencies are explicit rather than conflicting ownership. The repeated replay analysis is the clearest seat-level duplication.

# Commands run

- Read `.ufo/waves/round-19/preregistration.txt`, `w1-spec.json`, and `w1b-spec.json`; queried the frozen JSON for item count, role/axis groupings, names, and prompts.
- Searched the frozen spec for the cited item anchors. No shell commands, tests, fixtures, build, lint, or public-document fetch were run.

# Contract compliance

- Wrote only `.ufo/waves/round-19/w1/ReviewerWavePlan.md`.
- No subagents, git/jj mutations, network access, tool installs, live census, signals, or operator-owned path reads. No scratch files were created.
- Review is advisory; the 68-seat discrepancy is reported against the preregistered target, not silently treated as a waiver.