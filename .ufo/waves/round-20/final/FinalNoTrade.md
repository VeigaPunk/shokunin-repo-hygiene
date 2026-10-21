# FinalNoTrade — bounded pinned-build review

**Disposition:** reasoned scoped agreement; no new supported-domain contraction is established by the named evidence reviewed. This is not an axis score, test result, author-side admission, or claim that the implementation is runtime-proven.

## Axes

- **Calibration:** exact, item-local grant semantics (Q39/Q44; C1).
- **Operability:** full-ID cutover and the producer-specific measured-input boundary (Q40/Q41; C2).
- Coverage is not implicated by this slice.

## Adversarial case: do not turn an irrelevant directory into a global prerequisite

`InputAdded.md` (“Finding” and “Concrete counterexample / oracle change”) proposes that every r14 runner, targeted wrapper, and cache demonstration refuse when an ignored, untracked, admitted-format file is added under `corpus/knowledge/`. That is a useful falsifier **only if that caller actually reads the working-tree knowledge entry or derives a reported field from it**. Otherwise, adding that directory to every caller's measured set would make an unrelated knowledge-file addition cause exit 2/no record: a new fail-closed operability contraction, not better binding.

The same-baseline/pinned documents explicitly distinguish these consumers. `corpus/lessons/round-20.md`, “Additional source and residual dispositions” (`InputAdded`), says the r14/targeted callers do not count or read knowledge entries, while r13's source/admission fields do bind the knowledge directory and r14 binds the frozen/SOURCES inputs it uses. `corpus/README.md`, “Round 20 — current replay contract” and “Current full-ID counter commands,” separately says historical count commands read committed bytes, not the current corpus. Thus the report's untracked-working-tree mutation does not, on this evidence, demonstrate a change in an r14 output; it cannot justify widening all r14 input sets. `InputAdded.md` records the *baseline* `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`, so its source observation alone is not evidence against changed build `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`.

**Boundary:** this is a documentary distinction, not an independently re-derived call graph or executed oracle. If a changed-build producer is shown to read/count the current knowledge directory for a field it records, the narrow safe correction is to bind that actual dependency at that producer and add that caller-specific before/after case—not to add `corpus/knowledge/` to every r14 consumer. Retain the r13 directory binding where its reported fields depend on it.

## Preservation check

- Q39/Q44 and `SKILL.md`, “Round 20 repair contract,” define exact per-item requested delivery artifacts, exact `OWN ONLY` paths, and explicitly granted own-slot scratch; directive parsing is limited to standalone positive directives, and the calibration is limited to parsed write/edit/ast_edit targets. This preserves the declared positive grant shapes while removing the former suffix-wide inference. The reviewed records do not establish an exercised positive-grant pass, so I make no runtime claim.
- Q41 and `corpus/README.md`'s current replacement index retain the full-ID/durable-ref rule and supply the five current full IDs (two r13, two r14, one r19 counter examples). The README labels these as current replacements, leaves historical bytes unchanged, and distinguishes committed-data counters from working-tree producers. I found no evidence in this bounded material that the safety guard was relaxed or that a current executable README example still requires a short ID.
- Q40 requires actual caller inputs, not blanket corpus inclusion. The `InputAdded` proposal is not a demonstrated contraction in the revised call boundary absent evidence that those r14 fields consume this directory; applying it indiscriminately would itself shrink the supported domain.

## Finding, impact, correction

No current changed-build defect is established by this bounded attack. The strongest counterexample is against the *overbroad fix* proposed by `InputAdded`: a non-consumed ignored knowledge file should not invalidate every r14 measurement. Impact if adopted: **operability harmed**; calibration would also be misstated if such a refusal were counted as input-binding success. Smallest safe correction: preserve per-caller dependencies and full IDs; require a concrete consumed-field dependency before extending a caller's input set. Do not claim this agreement as evidence that the unexecuted exact-grant or caller-level oracles pass.

**Evidence boundary:** named files were read from commit `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1` with `git show`; `InputAdded.md` is treated only as the baseline attack statement it identifies. No target code, tests, builds, linters, smokes, or runtime probes were run.