# R40executor39 — C3 coverage claim attack

## Axis and distinct edge case

**Coverage. Named edge case: duplicate `TOTAL` multiplicity (two individually valid TOTAL rows), rather than a single malformed TOTAL count/order.** The frozen C3 claim explicitly calls out duplicate/multiple TOTAL rows, `--skip-unrecorded`, and invalid UTF-8 record bytes, but prior committed r39 C3 evidence exercised TOTAL-before-rows, TOTAL-only, and TOTAL consistency—not the multiple-TOTAL condition. This is a coverage-specific distinction: acceptance of one reordered or empty TOTAL does not establish behavior when a second summary row appears.

## Evidence pointers

- Frozen predicate and required matrix: `census/round-40/preregistration.txt:12-14` (C3) requires all three new branch cases, pristine candidate pass, candidate mutants killed, and r39 baseline mutants survive.
- Committed r39 fixture evidence: `census/round-39/waves/w1/W1ExecC3Fixture.md:127-140` measures a single `TOTAL` before rows and says it is accepted while still validated; `:186-201` measures a TOTAL-only record as empty; `:240-251` validates a bad-count TOTAL-first control. These are useful nearby controls but do not add a duplicate `TOTAL` row.
- Committed mutation evidence: `census/round-39/waves/w1/W1MutC3.md:44-95` documents M11–M14, all mutations to whitespace/CRLF/outside-root/indented-comment handling, and candidate result `killed=4 survived=0 pristine=ok`; none targets TOTAL multiplicity. The current r40 predicate requires declared single-defect mutants for the newly added branches, which is not demonstrated by these old mutants.
- Baseline evidence: `census/round-39/waves/w1/W1ExecC3Baseline.md:12-39` reports r38 fixture control with M11–M14 all surviving (`killed=0 survived=4 pristine=ok`, rc 1). This establishes survival only for those four mutations, not for any r40-specific TOTAL/skip/UTF-8 mutants.

## Commands and retained evidence

No new commands were run and no fixture was created. Evidence above is from the committed reports at the exact line ranges cited. No installs, git/jj/index mutations, tests, or checks were performed. No scratch was created.

## Verdict

**Bounded falsifier of treating the r39 evidence as sufficient; r40 claim remains unmeasured.** The committed r39 fixture's TOTAL cases do not cover duplicate TOTAL rows, and its four mutation targets do not cover the three r40 branch families. Thus r39 evidence cannot substantiate r40's exact new-coverage predicate. This is not a claim that the r40 fixture fails: the r40 counter/fixture and post-data result are not present in the committed evidence inspected, so pristine behavior, candidate kills, `--skip-unrecorded`, invalid UTF-8 behavior, and base-mutant survival remain unobserved.

## Bounded measurement plan

Against explicit r40 base and candidate revisions, run the candidate fixture with (1) pristine tool and all declared single-defect mutants, and (2) identical mutants against the r39 base fixture. For the distinct probe, construct a valid record with two `TOTAL` rows whose individual values agree with the REPO rows; compare against a single-TOTAL valid control to isolate multiplicity. Require the duplicate arm to distinguish the intended behavior (per the candidate contract), the fixture's own failure summary to record the mutant failure, and preserve exact stdout/exit status. Independently retain explicit arms for `--skip-unrecorded` and invalid UTF-8 bytes (feed bytes, not a text-decoded replacement); verify pristine pass, every candidate mutant killed, and every base mutant survives. Pin source/tool/fixture hashes and revisions. Use only explicit scratch paths and clean them before reporting.

## Scope and housekeeping

Only this assigned report was written. Risk: no direct r40 after-state evidence was available to measure. Blocker: the candidate fixture, its declared mutant definitions, and counter receipt/results are not in the inspected committed artifact set; once available, the plan is executable without changing the frozen claim. No installs were needed.
