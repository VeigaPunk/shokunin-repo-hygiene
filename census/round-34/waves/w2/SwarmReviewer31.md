## Status

Completed read-only adversarial review of AttackC2G5Disjointness. Finding confirmed from frozen source plus committed W1 reproduction; no new fixture execution claimed.

## Evidence

- Frozen preregistration `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`: `census/round-34/preregistration.txt:68-71,90-100,104-118` defines C1/C2 scopes and requires per-commit disjointness with no commit touching both namespaces.
- Frozen G5 implementation `census/round-34/c2-counter.py:220-229` checks only `{SCORECARD.md, SKILL.md}` versus `{c2-legs.tsv, c2-counter.py}` while enumerating `base..rev`.
- Actual range paths inspected: mixed freeze commit `2b591924f607940febbb99f922cc9bb090508eb6` includes C1 counter/items and C2 counter/legs; mixed repair commit `73f029ede48866cee87e49e8d096b6789e6aa1a4` includes C1 r34 fixture and C2 counter; re-pin `2b0171e2071fdc9c16a69bed12b0d040e574d8c8` includes only C2 counter. W1's committed reproductions report false-green results: `.ufo/waves/round-34/w1/deliver-c2-j1guards.txt:315-381`.

## Findings

**HIGH — real whole-set disjointness gap.** G5 cannot establish the stated guarantee: the mixed freeze and repair commits are inside its own enumerated range, yet its C1 set omits the relevant C1-owned files. W1 further recorded PASS for three mixed-namespace scratch commits. The A6 repair/re-pin did not fix G5 or exempt earlier mixed commits; no such exemption exists in the frozen preregistration. Separate claim-landing commits may mitigate later overlap but do not satisfy this range-wide clause. See the target-specific report for details.

## Attack log

Read W1 G5 reports first, then inspected frozen clause, guard source, re-pin amendment, and exact commit paths. Considered and rejected an apparatus-commit exception: the frozen wording says per-commit/no commit touches both and scans the full base-to-revision history. Did not execute a new counter or fixture; prior outputs are attributed to committed W1 receipts. No files outside the two assigned report paths were written.

## Deliveries

- `.ufo/waves/round-34/w2/AttackC2G5Disjointness.md`
- `.ufo/waves/round-34/w2/SwarmReviewer31.md`
