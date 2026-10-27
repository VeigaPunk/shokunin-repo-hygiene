## Status

INFERENCE CONFIRMED FROM FROZEN SOURCE AND COMMITTED W1 REPRODUCTION; no new fixture execution performed. The alleged G5 defect is real for the preregistered whole-set/per-commit guarantee. The later amendment/re-pin does not remove it. No counter-evidence establishes an exception for the mixed freeze/amendment commits.

## Evidence

- Frozen preregistration at revision `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`: `census/round-34/preregistration.txt:68-71` defines C1 touched scope; `:90-100` defines C2 guard G5 as “per-commit disjointness of the C1 and C2 file sets (no commit touches both namespaces)”; `:104-113` gives target, re-pin context and C2 scope; `:117-118` says G5 guards commit-level disjointness.
- Frozen guard source `census/round-34/c2-counter.py:220-229` at `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`: iterates every commit in `base..rev`, but tests only `c1 = {SCORECARD.md, SKILL.md}` against `c2 = {c2-legs.tsv, c2-counter.py}`. It does not enumerate the C1-owned counter/items/fixture files that the preregistration lists in C1 scope.
- Read-only source/revision inspection confirmed the actual base-to-list-revision range is three commits. `2b591924f607940febbb99f922cc9bb090508eb6` touches both `census/round-34/c1-counter.py`, `c1-items.tsv`, `tests/fixtures/r34-c1-junk.py` and C2's `c2-counter.py`, `c2-legs.tsv`, `tests/fixtures/r34-sandbox-junk.py`. `73f029ede48866cee87e49e8d096b6789e6aa1a4` touches C1's `tests/fixtures/r34-c1-junk.py` and C2's `c2-counter.py`. `2b0171e2071fdc9c16a69bed12b0d040e574d8c8` touches only `c2-counter.py`.
- W1 committed evidence: `.ufo/waves/round-34/w1/deliver-c2-j1guards.txt:315-361` transcribes the G5 implementation, commit-path enumeration, and classification of the first two commits as mixed under the preregistered namespaces. `:363-381` records three scratch-clone counterexamples, each with `LEG G5 PASS overlap commits=` despite a commit touching C1- and C2-owned paths. The relevant corroborating report is `.ufo/waves/round-34/w1/SwarmConnector30.md:8-19`; its `:15,19` explicitly identifies the omitted C1 paths and mixed freeze commit.
- Amendment A6 at `census/round-34/preregistration.txt:170-178` says the C2 counter repair landed at `2b0171e...` and later C2 readings use that list revision. The inspected re-pin commit changes only `c2-counter.py`; it does not amend G5's path sets. The earlier amendment commit `73f029e...` itself remains in the base-to-repin ancestry and is mixed by the declared namespaces.

## Findings

1. **HIGH — G5 does not provide its declared whole-set guarantee.** Its narrow hard-coded path sets fail to detect the mixed freeze commit `2b591924...` and the mixed repair/amendment commit `73f029e...`; both are in the range the guard enumerates. Thus, even if G5 returns PASS for the actual frozen range, that result means only “no commit intersected these two narrow subsets,” not “no commit touched both claim namespaces.” The committed W1 scratch reproductions additionally exercise the same omission with three deliberately mixed commits and record false-green PASS outputs.
2. **No benign alternate explanation in the frozen contract.** The guard explicitly scans `base..rev`; the preregistration says no commit may touch both namespaces and does not exclude initial freeze or amendment commits. The fact that those commits construct or repair the measurement apparatus may explain why they are mixed, but cannot make G5's broader guarantee true. Separate later claim landing commits can avoid future overlap, but do not retrospectively establish the required range-wide property.
3. **Amendment/re-pin is not a repair.** At the frozen list revision G5 still has the same narrow sets. The C2 counter re-pin changes implementation details elsewhere and preserves the mixed ancestors; there is no relevant frozen clause narrowing G5 to doc-only C1 paths or exempting setup commits. The concern is not caused by the re-pin measurement itself.

## Attack log

- Read the W1 G5 delivery and cross-claim report before assessing the guard; checked the exact preregistration, guard lines, re-pin amendment clause, and paths of the three commits in the pinned base-to-list-revision ancestry.
- Adversarial check: tested the strongest benign interpretation available from the preregistration—that G5 only needs to police separate claim landings, not apparatus construction. Rejected: `preregistration.txt:99` specifies “per-commit” and “no commit touches both namespaces,” while the guard checks every commit in `base..rev`; there is no setup-commit exemption. The W1 report's separate-landing suggestion is a possible future mitigation, not a defense of this frozen contract.
- Did not re-run the counter or recreate fixtures; reproduction claims above are attributed to committed W1 evidence, not represented as my execution. No mutation or fixture run performed.

## Deliveries

- `.ufo/waves/round-34/w2/AttackC2G5Disjointness.md` — this target-specific report.
- `.ufo/waves/round-34/w2/SwarmReviewer31.md` — scoped seat summary.
