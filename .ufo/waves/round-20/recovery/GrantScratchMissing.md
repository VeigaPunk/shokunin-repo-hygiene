# GrantScratchMissing — calibration

**Observed bytes:** `tools/souji-seat-audit.py` reader snapshot `1A5C` (the same snapshot tag on each bounded range below); preregistration names baseline `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. This is a source-only review of the observed snapshot, not a fresh execution or an independent commit check. No target code was run.

**Impacted axis: calibration (C1) only.**

## Finding

No source counterexample was found to the rule that an undeclared scratch root grants no `/var/tmp` writes. At `tools/souji-seat-audit.py:138-151`, `scratch_path()` searches only explicit `SCRATCH:`, `Workdir:`, or `Scratch root:` lines in the item prompt or context, accepts only a seat-specific `souji-r<N>[w<N>]-<seat>` root, and otherwise returns `""`. `run()` passes that result to the auditor at `:368-371`; it does not derive scratch from the wave field. With empty scratch, `target_verdict()` allows an absolute target only when it is under a nonempty scratch root or exactly in the report/owned/delivery allowlist (`:251-255`), so an unowned `/var/tmp` target is `V-WRITE-SCOPE`.

The remaining gap is calibration evidence: the existing no-scratch case at `:469` invokes `audit_seat()` directly for `/var/tmp/misc/out.txt`. The `run()` wiring case at `:529-544` covers two *explicitly declared* roots and a cross-seat write, but does not establish that a wave/slot label alone cannot grant scratch. The prior lesson records the old slot-spelling defect at `corpus/lessons/round-19-verifier-spotcheck.md:68`; that historical observation is not evidence of a current failure. The observed regex now admits `w<N>` only as part of an explicit, seat-specific root.

**Counterexample to oracle coverage (not an observed product failure):** feed `run()` a spec whose wave/context mentions `souji-r20w2-` but contains no scratch declaration, item `A` has no scratch directive, and `A.txt` writes both `/var/tmp/souji-r20w2-A/out.txt` and `/var/tmp/unrelated/out.txt`. The correct result is two major `V-WRITE-SCOPE` findings. A broad `/var/tmp` default or wave-name inference would incorrectly clear one or both. This case is absent from the run-level checks above; static inspection predicts the observed code rejects both, but this has not been executed.

**Smallest safe correction:** add that single no-declaration `run()` oracle case and assert both targets are major `V-WRITE-SCOPE`; keep any positive slot-qualified case separately tied to an explicit item/context declaration and keep the sibling-slot refusal. This converts the current static inference into falsifiable caller-level coverage without changing the scope policy.

**STATUS: OPEN** — no implementation defect is evidenced in the observed source, but the requested no-declaration behavior is not directly covered through `run()`; the proposed caller-level oracle remains unexecuted.