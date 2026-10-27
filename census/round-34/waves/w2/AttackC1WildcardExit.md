## Status

REPRODUCED DEFECT remains credible; no other frozen C1 clause rejects the wildcard exit. W1's interpretation has a specification tension: the restatement contract says the row carries the original exit, but the counter explicitly permits `*`. This makes the acceptance a concrete contract/implementation mismatch, not an unreachable attack. The source/report review does not independently rerun W1's scratch commit.

## Evidence

- Frozen preregistration revision: `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`. `census/round-34/preregistration.txt:47-53` defines AGREE by run exit equaling stated exit, then says a restatement carries the original line, exit, and other fields. It does not explicitly authorize wildcard in the restated exit cell.
- Frozen judge source at that revision: `census/round-34/c1-counter.py:259-261` accepts either signed integer or `*`; `:305` sets `exit_ok = exit_ == "*" or rc == int(exit_)`. This is an unconditional escape from exit equality for restatements.
- `census/round-34/c1-items.tsv:62` pins E18 original exit `0`, statement `selftest=PASS ids=5/5`, and argv `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh`.
- W1 `w1/deliver-c1-attacks.txt:7-17` records the forged E18 `*` row, commit `58166e2ef1f0a88441f02cad5f875c9b962ffd04`, command, and output: `ITEM E18 AGREE restated rc=0 expect_exit=* ...`; it reports the measured run happened to exit 0, so that run demonstrates the wildcard was accepted but does not itself demonstrate a nonzero runtime being incorrectly accepted.
- W1's original E18 evidence (`w1/deliver-c1-E18.md:27-35, 85-101`) establishes the mismatch is value drift: expected old `ids=5/5`, observed `ids=7/7`, both with rc 0. Therefore a benign explanation that the wildcard is needed to account for this actual E18 execution is not supported by the recorded evidence; the concrete exit is 0.

## Findings

- **Finding — wildcard exit can waive a frozen measurement condition.** The W1 survivor's structure passes row validation, cause checks, and the observed E18 statement check; no later frozen clause tests the observed `rc` against the original concrete exit when the restated cell is `*` (`c1-counter.py:301-315`). The frozen junk-control list at preregistration `:64-66` covers emitter, vacuous RESULTS, and foreign argv, but not wildcard exit. The A5 addendum at `:166-169` says those three forged rows were rejected; it does not extend rejection to this attack.
- **Counter-evidence / limitation.** The W1 reproduced command returned rc=0, exactly the original expected exit, so only acceptance of a vacuous field is directly evidenced there. Claim that a nonzero command exit would survive is source-level inference from `:305`, not a reported execution. Also, preregistration's phrase “carrying ... exit” could be read as requiring exact original exit; under that reading the counter is defective regardless of whether a nonzero exploit run is shown.
- **Impacted axis:** C1 calibration / measurement integrity (reported exit no longer binds the observed execution).
- **Smallest safe correction:** in the counter, require a restatement exit to be a concrete integer and compare measured rc to it; reject `*` for restatements. Do not alter frozen items or predicates.

## Attack log

- Read W1's E18 delivery, counter-attack report, frozen preregistration, item row, and source lines; no lane file was edited and no fixture/counter reproduction was run in this review.
- W1's exact reproduction command/output are quoted in `w1/deliver-c1-attacks.txt:11-17`; reproduced result as recorded, not independently executed here.
- Source inference: after a valid restatement row passes cause validation, `judge()` runs the row's argv at measured rev (`c1-counter.py:301-305`) and treats `*` as success independent of rc. No second frozen clause in the examined judge path restores equality.

## Deliveries

- `.ufo/waves/round-34/w2/AttackC1WildcardExit.md`
