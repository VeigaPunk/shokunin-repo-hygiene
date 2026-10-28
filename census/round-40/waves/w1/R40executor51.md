# R40executor51 — C3 coverage falsification attempt

- Seat: executor (leaf; no dispatch)
- Explicit distinct edge: **duplicate TOTAL row parser/cardinality handling**. This is distinct from invalid UTF-8 (R40executor63) and from `--skip-unrecorded` / ordinary TOTAL coverage.
- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Frozen contract read first: `census/round-40/preregistration.txt:10-11`.
- Verdict: **bounded measurement plan only; no r40 candidate artifacts available in the census path, so no falsifier or pass established.**
- Tool installs/upgrades: none; pacman untouched.

## Evidence pointers

1. Frozen C3 requirement is `census/round-40/preregistration.txt:10-11`: behavioral cases for duplicate/multiple TOTAL rows, `--skip-unrecorded`, and invalid UTF-8; pristine candidate passes, candidate mutants killed, r39 base mutants survive, and fixture provides its own failure summary.
2. Committed r39 `census/round-39/records/c3-after.txt:3-8` records M11–M14 all killed, `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7`; these are not r40 TOTAL-multiplicity mutants.
3. `census/round-39/waves/w1/W1RevC3Fixture.md:29-38` enumerates r39 mutants M1–M8 and their targets. No duplicate-TOTAL cardinality target is listed. Its lines 156-173 document M7 zero-row audit survival; relevant as a separate coverage-control gap, not evidence of an r40 defect.
4. `census/round-39/waves/w1/W1RevC3Fixture.md:101-103` reports the eight r39 cases as independently discriminating their assigned defects; this does not establish duplicate-TOTAL coverage in r40.
5. Directory listing of `census/round-40/` returned only `preregistration.txt`; no counter, candidate fixture, mutant source, or receipt was present to inspect or run.

## Bounded measurement plan

At a named candidate revision, compare the fixture's behavior for (a) exactly one TOTAL row, (b) two identical TOTAL rows, and (c) two conflicting TOTAL rows, using otherwise identical valid record bytes. Preserve the intended output/refusal contract as defined by the tool; do not assume whether duplicates should be accepted or rejected. Run each case alone against pristine candidate and the declared single-defect duplicate/multiple-TOTAL mutant, then run the r39 base fixture/mutants as the frozen control arm. Retain each command, stdout/stderr, exit code, named case result, and fixture `SUMMARY`. A convincing kill requires the named duplicate/multiplicity case itself to fail the mutant with the fixture's expected nonzero failure summary, while pristine passes; unrelated failures or traceback-only failures do not count. Verify the base mutant survives using the declared base fixture/arm rather than infer survival from r39 receipts.

This separates duplicate cardinality from ordering (TOTAL-before-rows), comments-only records, aggregate-value mismatch, and the independent UTF-8/skip-unrecorded branches. If the intended semantics for duplicate identical TOTAL rows are not explicit in candidate source/docs, report that prerequisite rather than selecting semantics by assumption.

## Commands and observed outputs

- Read `/home/vgpnk/.omp/agent/RULES.md` — tooling rules read; no install/update.
- Read `skill://godspeed` — skill instructions read.
- Read `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt` — frozen C3 predicate at lines 10–11.
- Listed `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39` — records and prior wave evidence found.
- Read `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/records/c3-after.txt` — exact receipt cited above.
- Read `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/waves/w1/W1RevC3Fixture.md` — prior fixture and mutant matrix cited above.
- Listed `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40` — output: `preregistration.txt` only.
- No shell command, fixture, scratch directory, counter, build, lint, test, or formatter was run.

## Limits

No r40 counter/candidate fixture/mutants/receipt were available in the inspected `census/round-40/` directory. Thus candidate duplicate-TOTAL behavior, pristine pass, mutant kill, r39 base survival, and fixture failure-summary behavior are **unrun / unverified, not pass**. No concrete falsifier is established. Read-only investigation; only this assigned report is written; no production files or frozen claims changed.
