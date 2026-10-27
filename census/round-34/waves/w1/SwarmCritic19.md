## Status
STATUS: PARTIAL — do-nothing reproduction completed; found a frozen C1 dedup violation. No frozen bytes changed.

## Evidence
- Ran the frozen C1 counter at base `9c76c7222a8abff027af42e37f0d160d52526bba`, list-rev `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`: `SUMMARY items=60 agree=35 mismatches=25 restated=0`, rc 1. Full item output and load evidence are copied into `deliver-q76-honoring.txt`.
- Compared `c1-items.tsv` and `c1-counter.py` at attempt-1 freeze `2b591924f607940febbb99f922cc9bb090508eb6` vs re-pin `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`: empty diff.
- Checked exact `(argv, predicate)` uniqueness in the frozen TSV: 60 rows, 59 distinct pairs; G20/E09b is duplicated.
- Searched base SCORECARD/SKILL correction and supersession text, then checked correction anchors against the mismatch rows. No existing R30/L/N/K correction binds any mismatching item cell; detailed list and distinction are in the delivery file.

## Findings
1. **ATTACK — duplicate frozen pair.** `census/round-34/c1-items.tsv`, G20 and E09b: identical argv `bash tests/fixtures/r27-pre-report-gate.sh` and statement `cases=4 pass=4 control=FALSE-GREEN-REJECTED`. Both AGREE at base, so one measurement is counted twice. This violates the header's one-item-per-pair rule, can inflate the target denominator, and is not a do-nothing artifact. Do not mutate the frozen set; smallest safe future correction is uniqueness validation and a single merged identity for the pair.
2. **No Q76 false-positive found.** The 25 reproduced mismatches are not already corrected at their own cells by the base's R30, R31 L, R32 N, or R33 K rows. For example, K04 at `SCORECARD.md:502` is for `SCORECARD.md:155`, while E18 is the separate `SCORECARD.md:71` cell; overlapping command text does not make that an already-binding correction.
3. **Inverse-hole check bounded.** The named exclusions that are exact R33 K-pair duplicates are covered by their corresponding K rows. E08b's cited value is a revision-bound count (4 at 6cb22dc); E14's `cases=8` is explicitly superseded by E12's current `cases=12` entry in the prior enumeration. I found no evidenced stale, uncorrected excluded cell. Excluded rows were not counter-executed as separate items, so this is not a claim that every excluded command was independently run.

## Attack log
- C1 uniqueness rule counterexample: G20/E09b duplicate `(argv, statement)` pair; frozen pair count is 59 for 60 items. Reproduced using the exact list-rev counter invocation above.

## Deliveries
- `.ufo/waves/round-34/w1/deliver-q76-honoring.txt`
- `.ufo/waves/round-34/w1/SwarmCritic19.md`
