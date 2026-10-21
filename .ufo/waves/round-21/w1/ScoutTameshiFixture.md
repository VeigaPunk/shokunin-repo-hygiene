# Souji R21 fixture-craft findings

## Criteria from tameshi-shokunin

- **Falsifiable, sourced claims; keep evidence classes distinct.** The admission bar requires each claim to be falsifiable or marked as opinion, source-anchored, and separated into observation, inference, and unknown (`tameshi-shokunin/corpus/QUALITY.md:3-8`; `tameshi-shokunin/SKILL.md:19-23`). Predictions are preregistered with their executed outcomes; a miss stays visible as an erratum (`corpus/QUALITY.md:15-17`).
- **Independent replay, against pinned state.** The shared verifier shape calls for at least two independent lanes (`tameshi-shokunin/SKILL.md:40-41`); the verifier is a named non-author replaying committed/retained state, with committed hashes re-pinned and instrumented runs in disjoint scratch (`SKILL.md:86-88`). An author’s statement that a test “should pass” is not replay evidence.
- **Demonstrate that a fixture can catch its target.** A green count or branch-reach check is only nominal: load-bearing coverage makes the targeted case fail when the mechanism is disabled or attacked; reaching each arm alone is not enough (`SKILL.md:96-107`). QUALITY requires one fixture per weaker rule being excluded, and an undetected mutant to be reported rather than hidden (`corpus/QUALITY.md:116-123`). The concrete guard-coverage bar is that removing the guard makes its owning selftest exit nonzero (`corpus/QUALITY.md:176-189`). A miss must be adjudicated with a discriminator, not retrofitted away (`SKILL.md:114-117`).
- **Re-run recipes, not prose; keep synthetic checks hermetic.** An audit lane re-executes recipes against retained outputs and committed revision (`SKILL.md:78-88`); hermetic fixtures avoid live-path reads (`SKILL.md:68-74`). Secrets are shape-only, never content-read (`SKILL.md:19-23`). A verification that ran must land its report in the same round, or remain named debt (`corpus/QUALITY.md:21-23`).

## Application to the frozen r21 preregistration

**C1 base-discriminating oracle — meets the design bar.** It requires the measured after-set to equal an independent per-call oracle, labelled by non-implementing seats, with exact precision and recall; every positive synthetic fixture must distinguish the base tool (`souji-shokunin/.ufo/waves/round-21/preregistration.txt:12-13`). This is a particularly strong match for independence and shown-able-to-fail. The oracle labels and fixture results are still planned measurements, not observed evidence here.

**C2 replay matrix — strong falsifiable design; replay evidence remains pending.** The three source scenarios (different-HEAD scratch clone, bare mirror, lane root) have a predicted red-before/green-after result, exact `18/18` and cross-scenario summary conditions, and a source-unchanged guard (`preregistration.txt:15-19`). That is materially stronger than asserting replayability in prose. Two details are not explicit: the contract says “a non-author” but does not name the verifier, and it requires identical per-step summaries across scenarios without naming a retained, independent expected-summary receipt/oracle. **[INFERENCE]** Cross-scenario equality alone could allow three consistently wrong summaries; the executed replay should identify the pinned reference used for each step. No replay was run for this scout report.

**C3 reason-field canary — safe and behaviorally discriminating by design.** The scope forbids live `/proc` and real credentials; inputs are fabricated canaries, and the public reason-only path is explicitly `/proc`-free (`preregistration.txt:21-24`). Its measurement predicts canary leakage from the exact base-function bodies and zero leakage after, while separately asserting the 160-byte bound and byte-exact nonsecret controls (`preregistration.txt:25`). This gives a concrete counterexample for the old behavior and specific post-change expectations, consistent with the mutation bar. **[INFERENCE]** Unlike C1, the text does not explicitly say the expected per-case reason bytes are authored independently of the implementation; the named output requirements at lines 23-25 constrain them, but the eventual fixture/receipt should make those expected values inspectable. No canary fixture was run for this scout report.

## Overall assessment and unknowns

The preregistration is a credible, falsifiable fixture plan: C1 explicitly supplies an independent oracle and base discriminator; C2 supplies a meaningful replay matrix and before/after counterfactual; C3 uses synthetic-only canaries with explicit leakage, length, and preservation checks. This is a design assessment, not a pass verdict: the preregistration contains expected outcomes, not executed outcomes. The committed fixture implementations, independent oracle bytes/identity, named C2 verifier, retained per-step reference summaries, actual case-failure labels, and final replay receipts were not inspected or exercised here. Under QUALITY:6 and QUALITY:8, those outcomes must be retained in-round; expectations alone cannot be cited as passes (`corpus/QUALITY.md:15-17,21-23`).

## Sources checked

- `git -C /home/vgpnk/Projects/shokunin/tameshi-shokunin show HEAD:SKILL.md`
- `git -C /home/vgpnk/Projects/shokunin/tameshi-shokunin show HEAD:corpus/QUALITY.md`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-21/preregistration.txt`

No fixtures, tests, or target code were executed.