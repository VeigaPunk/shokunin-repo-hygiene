## Status

REPRODUCED DEFECT remains credible; the reproduced E18 wildcard row is not rejected by another frozen C1 clause. The reproduction is reported by W1, not rerun by this reviewer. Since the measured exit was 0 (same as E18's original frozen exit), a nonzero-exit bypass is a source-level inference rather than a directly demonstrated consequence of that run.

## Evidence

- Frozen revision `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`: `census/round-34/preregistration.txt:47-53` says AGREE requires equality to the stated exit and restatements carry an exit; it does not expressly authorize `*`.
- Frozen counter at that revision: `census/round-34/c1-counter.py:259-261` accepts `*`; `:305` makes wildcard `exit_ok` unconditional.
- `census/round-34/c1-items.tsv:62` specifies E18 exit 0 and argv.
- W1 `deliver-c1-attacks.txt:7-17` records attack commit `58166e2ef1f0a88441f02cad5f875c9b962ffd04` and output `ITEM E18 AGREE restated rc=0 expect_exit=* ...`. Its actual observed rc=0, matching E18's frozen expected exit. W1 `deliver-c1-E18.md:27-35,85-101` records the stale value `ids=5/5` versus run value `ids=7/7`, with exit 0.
- Frozen junk controls (`preregistration.txt:64-66`) exercise emitter, RESULTS:0, and foreign argv, not wildcard exit; A5 (`:166-169`) documents only those three forged rows being rejected.

## Findings

- Wildcard exit is accepted and no subsequent judge check compares measured rc with the original exit (`c1-counter.py:301-315`). The attack therefore defeats exit binding in the restatement row; its execution condition is not blocked by another frozen clause. A possible benign interpretation is that the wildcard is just a placeholder; however the judge treats it as success, and the E18 evidence supplies concrete exit 0, so no placeholder is needed here.
- The W1 run alone does not show a nonzero runtime accepted: E18 returned 0. The nonzero consequence is source-level inference from `:305`, clearly distinguished from W1's reproduced acceptance.
- Impacted axis: C1 calibration / measurement integrity.
- Smallest safe correction: reject wildcard in restatement exits and require a concrete exit equal to measured rc; leave frozen target/items/predicates unchanged.

## Attack log

Read-only inspection of preregistration, frozen item, counter source, W1 E18 report and attack report. No execution run during this review. W1's reported reproduction command/output are at `w1/deliver-c1-attacks.txt:11-17`; no independent reproduction is claimed.

## Deliveries

- `.ufo/waves/round-34/w2/AttackC1WildcardExit.md`
- `.ufo/waves/round-34/w2/SwarmCritic32.md`
