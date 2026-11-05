# S66MutKill — findings

Full detail: `.ufo/waves/round-66/w1/S66MutKill/report.md`. Matrix: `.ufo/waves/round-66/w1/S66MutKill/kill-matrix.tsv`. Mutant bytes: `.ufo/waves/round-66/w1/S66MutKill/mutants/`.

- Candidate sha256 `a8c47d362a901c222f9582b8b96609fba39cb5e0e662d4057e724db96c1097fc`, matches CANDIDATE-READY.
- Kill rate: **4/8 (50%)**. Killed: K1, K2, K5, K8. Survived: K3, K4, K6, K7. None compile-failed.
- K0 control (base writer in new slot): `SUMMARY matrix=28 base_forgeries=8 base_honest=5 new_forgeries=8 new_honest=5 class_mismatches=8 regress=PASS`, EXIT=1. Matches the frozen do-nothing control.
- K1: `new_forgeries=0 class_mismatches=2`, EXIT=1 (E1, E2).
- K2: `new_forgeries=3 class_mismatches=3`, EXIT=1 (E4, E5, E6).
- K3: `new_forgeries=0 class_mismatches=0`, EXIT=0. **Survived.**
- K4: `new_forgeries=0 class_mismatches=0`, EXIT=0. **Survived.**
- K5: `new_forgeries=2 class_mismatches=2`, EXIT=1 (MOD2, MOD3).
- K6: `new_forgeries=0 class_mismatches=0`, EXIT=0. **Survived.**
- K7: `new_forgeries=0 class_mismatches=0`, EXIT=0. **Survived.**
- K8 (M-ENV, frozen recipe exit 0): C1 `new_forgeries=2 class_mismatches=2`, EXIT=1 (N3, P13). C2 round-66: `SUMMARY rows=5 findings=2 verdict=FAIL`, EXIT=1 (`SCOPE-OVERREACH s2`, `GOVERNED-STATEMENT-UNRESOLVED s5`; env=0). C2 round-65: `SUMMARY rows=4 findings=0 verdict=PASS`, EXIT=0 (M10 reproduced).
- Survivor finding: K3, K4, K6, K7 target pins the frozen matrix does not exercise (host/system/repo-local config, replace refs). Coverage finding under named limit L1/L2, not a contract change.
- Caveat: mutant commits used BASE SKILL.md. The s5 finding in K8 is an artefact of that. The M-ENV kill is the s2 finding from writer bytes; rerun against candidate SKILL.md before reading s5.
- Not measured: the unmutated candidate under C1 (L1's job).
- Tooling: none installed or upgraded. Scratch removed; lane untouched (read-only).
