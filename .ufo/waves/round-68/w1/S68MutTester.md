# S68MutTester: scoped findings (round 68)

Full evidence: `.ufo/waves/round-68/w1/S68MutTester/mutation-report.md`.

Baseline: the unmodified scratch copy of the frozen counter (sha256 ab3ac5c7…, selftest 8/8) reproduces the C1 target and the C2 after-arm: `SUMMARY matrix=42 base_forgeries=2 base_honest=11 new_forgeries=0 new_honest=11 class_mismatches=0 regress=PASS`, `EXIT=0`, flips 0.

| Mutant | C1 noticed | C2 noticed | Note |
|---|---|---|---|
| a remove W5 cwd rule | no | no | W5 cwd is inert (refusal before any git call) |
| b remove W4 mode_change | yes (exit 1) | yes (exit-nonzero clause) | W4 refusal depends on the mode change, not the relative poison |
| c remove GIT_COMMON_DIR from scrub | no (clean shell) | yes (ambient exit 2, flips 46) | C1 is blind to the scrub |
| d W6 accept -> refuse | yes (exit 1) | yes (exit-nonzero clause) | W6 only |

Named limits: (1) W5's cwd branch is unobservable; (2) C1 cannot see the scrub; (3) W4 does not isolate the relative-poison route; (4) C2's kill clause fires on correctness failures as well as operability.

Lane, frozen census files and sibling repos were not modified. No tools installed.
