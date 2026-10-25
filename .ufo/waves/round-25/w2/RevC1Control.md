# RevC1Control — extended fixture do-nothing controls

STATUS: PARTIAL

## Evidence

- Amendment 3 lines 5–16 adds k5, k6, k7 and explicitly fixes target at `cases=16 pass=16`; lines 10–12 define the informative veto-less control. The earlier 15-case result in `w1/MutCoverageAgreement-2.md:4,7–10` is the count before its account of the final k7 case; amendment 3 is explicitly append-only and “No frozen predicate, target, kill rule or r24 case changes” (`preregistration-amendment-3.txt:31`). Thus 15→16 is an allowed frozen-set extension, not a frozen-set violation.
- Fixture builds k1/k2 with divergent HEAD outcomes at `tests/fixtures/r25-coverage-agreement.py:329–349`, k5/k6 at lines 368–387, and the embedded k7 veto-less control at lines 389–409. Score assertions include kill fields/rows and exit status at lines 435–470; final total/predicate is at lines 514–525.
- `python3 -B tests/fixtures/r25-coverage-agreement.py --tool /var/tmp/souji-r25-RevC1Control/old-tool.py` used the actual `a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe:tools/souji-coverage-agreement.py` bytes. Result: cases=16, pass=9, k1–k7 all fail because old tool refuses `--base-rev` (exit 2/no counts); control=FALSE-GREEN-REJECTED. Fixture command exits 1, expected for this red arm.
- Skip-kill mutant accepted `--base-rev` but replaced base enumeration with an empty set. Result cases=16, pass=9; k1,k2,k5 failed with no KILL-RULE and `kill_tested=0`; k3,k4,k6,k7 failed the required tested count; FALSE-GREEN-REJECTED. Its generated mutant is in scratch only.
- No-base-tree mutant likewise replaced base enumeration with an empty set (and retained rev-side computation). Result cases=16, pass=9; k1/k2/k5 failed to emit violations and all kill cases failed expected `kill_tested=1`; FALSE-GREEN-REJECTED.
- Mutation report `w1/MutCoverageAgreement-2.md:4,8–10` records pristine 16/16, old-tool fail k1–k7, and rejection of always-zero/veto-less controls; lines 54–60 disclose nine survivors, including K13 bad-base-rev validation. This attack independently reproduces the relevant control outcomes, not the whole mutation campaign.

## Findings

1. The extended fixture rejects all three requested broken tools. The old a6d2d15 tool fails k1–k7; skip-kill and no-base-tree mutants each score 9/16 and fail the base-grounded cases.
2. The 15-case W1 wording/count is superseded by the pre-measurement append-only amendment’s 16-case set. This is not a frozen-set violation; the final mutation report accurately names the 16-case set. No claim predicate was narrowed.

## Attack log

- Isolated all probe artifacts in `/var/tmp/souji-r25-RevC1Control/`; fixture creates/removes its own synthetic `/var/tmp` repositories. No lane production files modified.
- Exact fixture invocations used `python3 -B .../tests/fixtures/r25-coverage-agreement.py --tool <mutant path>`; nonzero exits (1) are expected because the fixture asserts the candidate must pass every case, while these are red-arm mutants.
- Scratch contains extracted/mutated test tool copies only; no package/tool installation.
