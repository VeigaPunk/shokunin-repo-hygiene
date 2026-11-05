# S67ReviewerDesign — design.md (frozen C1 design attack, attack lines 1-5)

Full evidence trail lives in `report.md`; this file states the design verdicts in claim order so the L1 can
lift them directly into the round report. Scope: preregistration-attempt4 C1 surface. Every probe below ran in
seat scratch on host git 2.56.0 and the scratch is gone; artifacts cited are the committed control receipts and
the copied selftest log.

## Design verdict per attack line

1. **W1 semantics — sound.** The mode-change (755→644 on seeded `tools/instr.sh`) is really hidden by the
   redirected common dir (config copy carrying `core.fileMode=false`) on this host: plain status shows
   ` M tools/instr.sh`, redirected status is clean, base writer accepts (matching the committed control row and
   probe P1), and the same run unredirected refuses `lane worktree is dirty` (99-byte stderr with zero COMMONDIR
   tokens). The counter's judge separates the two refusal reasons via expected_class substring matching, so a
   candidate refusing-by-dirty on W1 scores class_mismatches>0 — the row has real kill power in both directions.
2. **W3 resolution — sound, and the design pins the right trap.** `rev-parse --git-common-dir` prints `.git`
   RELATIVE on this host, and while GIT_COMMON_DIR is set it echoes the caller's value verbatim. So an
   implementation that fails either (a) scrubbing the variable from its resolution call or (b) realpathing the
   relative output fails W3 (new_honest=5) or — worse — vacuously accepts W1/W2. The frozen matrix exercises
   exactly this dual requirement; the candidate satisfies it (report.md byte review, item 3; relative-form
   acceptance additionally covered by candidate selftest case_35).
3. **Docstring vs control — clean (M6 class does not recur).** All 31 rows of the docstring's base-behavior
   paragraph match the committed do-nothing control; the only nit is the SY3 labeling nit (report.md LOW-3).
4. **Receipt grammar — bound correctly.** The r67 measured-rev fix (`rev=<measured>`, --rev in the candidate arm,
   --base-rev in the do-nothing arm) revises exactly the r66 routed defect 5: synthetic freeze-check --chronology
   re-derivation shows the descendant-bound After receipt passes and base-bound or freeze-bound receipts trip
   `RECEIPT-MEASURED-BEFORE-FREEZE`; the real-lane read-only check at the freeze rev reports only the expected
   pre-landing `AFTER-MISSING` for C1 (C2 declares no After line, per the prereg's separability rule).
5. **Named limits — no hidden trades found.** L2's relative-value rule matches git's observed cwd-based
   resolution; the empty-value refusal is honest (git treats empty as a bogus path and dies rc 128 — the base
   writer wraps that into a confusing `rev is not a commit object` failure, so the candidate's clean refusal is
   an error-class improvement, not a Q22 trade); L1/L3/L4/L5/L6 carried verbatim; no L1-L6 item hides an
   undeclared trade found by this seat.

## Design-level findings (severity-exact; evidence in report.md)

- **MEDIUM-1**: the predicate's "every git call scrubs the variable" clause is behaviorally unbound by the
  frozen matrix (match arms are observationally identical; mismatch arms refuse before any git call). Same
  redundant-pin family as r66 K3/K4; route through the S67MutKill defence-in-depth decision.
- **MEDIUM-2**: the frozen counter's `clean_env` does not scrub a caller-set `GIT_COMMON_DIR`, so a stale
  operator export leaks into both slots of every row. Cannot flip the target to a false PASS (error verdicts
  move counts away from PASS); disclose as a named limit (frozen bytes, r66 M-class disclose-not-amend precedent).
- **LOW-3**: SY3 labeled r60-r65 machinery in the docstring vs r66 in CASE_SPECS comments — wording only.
