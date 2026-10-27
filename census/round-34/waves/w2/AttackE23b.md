## Status

**Confirmed real as a frozen-contract reachability defect; not a measurement artifact.** The W1 execution receipts show E23b mismatches at base. Independent source/history inspection confirms no route allowed by the frozen cause rules can restate it. This seat did not rerun the counter or execute a fixture; runtime readings below are explicitly W1's committed evidence, not a reproduction by this reviewer.

## Evidence

- Frozen list `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`, `census/round-34/c1-items.tsv:68`: E23b is bound to `SCORECARD.md:304`, expected exit `0`, predicate `lost=0 fidelity=0 floor_violations=0 tool_unchanged=0`, sole file `census/round-29/c2-counter-v2.py`, argv uses `--rev {REV}` and base-rev `691dd29211c53d0ef94fa072394cb9c8a69fe92e`.
- Base do-nothing receipt `census/round-34/records/controls-c1-do-nothing.txt:52` records `rc=1`, `expect_exit=0`, predicate holds, and `uncovered=1`; W1's corresponding run is in `.ufo/waves/round-34/w1/deliver-c1-E23b.md:5-16`.
- Frozen semantics: `census/round-34/preregistration.txt:48-57` requires an executed cause: either value drift (original holds at parent, fails at cause, cause touches an item file) or argv correction (cause wrote the row line and original row argv already fails at cause). The row-writing condition checks the frozen original argv, irrespective of the proposed corrected argv: `census/round-34/c1-counter.py:282-300`. A corrected argv must name an item file (`:263-268`); the restated statement must be the run's exact last digit-bearing line (`:269-272, 301-313`).
- Independent read-only history checks: `git blame -L 304,304 2b0171e... -- SCORECARD.md` attributes the row line to `de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b`; `git log --follow ... -- census/round-29/c2-counter-v2.py` returns only `8aaacf518d0dc9292d5258abf7d74bdaea1b76e7`. W1 additionally reports the line absent in the writer's parent and the sole-file history at `.ufo/waves/round-34/w1/deliver-c1-E23b.md:22-28`.
- The counter's exit condition includes `uncovered=0` (`census/round-29/c2-counter-v2.py:14-16`), explaining why the base receipt exits 1 although E23b's narrower predicate holds.
- Q76: the base control is un-restated, and W1's prior-correction check found no binding row; the related references concern a different SCORECARD line or the enumeration source (`.ufo/waves/round-34/w1/deliver-c1-E23b.md:18-20`; corroborating details in `deliver-c1-E23a.md:17-28`). No Q76 escape is evidenced.

## Findings

1. **No honest value-drift route.** The reported drift onset is `af7fd250c8a862130f88b8f77ad29debf343e54d`; W1 says its only changed path is `census/round-33/waves/w1-results.json`, not E23b's sole item file. Thus `same` fails the cause-file test. The only commit in the item's tool history is its creation, `8aaacf51…`; W1 reports the original command fails at both its parent (script absent) and the cause, not the required True/False transition. See W1 `deliver-c1-E23b.md:34-51`.
2. **No honest argv-correction route.** The unique row-line writer is `de874ee8…`. W1's execution table says the original `{REV}` command at that cause exits 0 and its predicate holds (`deliver-c1-E23b.md:38-39`); the frozen counter therefore rejects every corrected argv at this cause as `BAD-CAUSE(the row's own argv held at the cause)` (`c1-counter.py:299-300`). Pinning the corrected argv to the historical green measurement `b8620071…` produces a valid-looking last-line statement, but does not cure that failed cause precondition; W1's attempted row and rejection are at `deliver-c1-E23b.md:57-67`. Pinning to a red historical revision likewise cannot satisfy the cause check, which evaluates the *original* argv at the row writer.
3. **Exit/statement adjustment is not a bypass.** Setting exit to the observed base rc or quoting the base summary could make a row's measured output match, but with `same` it still needs an item-file cause and a True/False drift; with corrected argv it still needs the row writer and original argv failure there. The exact statement requirement and Q76 do not waive either cause predicate.

**Conclusion:** the W1 blockage reasoning survives this adversarial check. E23b is unreachable under the frozen rules; no benign alternative route was found. The W1 route-C rejection is supported by its committed counter output, but not independently rerun by this seat.

## Attack log

- Read frozen preregistration, item list, counter implementation, C2-v2 tool, base do-nothing receipt, and W1 E23a/E23b reports.
- Read-only commands executed from the lane:
  - `git blame -L 304,304 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 -- SCORECARD.md` → line 304 attributed to `de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b`.
  - `git log --follow --format='%H %s' 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 -- census/round-29/c2-counter-v2.py` → only `8aaacf518d0dc9292d5258abf7d74bdaea1b76e7`.
  - `git diff-tree --no-commit-id --name-only -r de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b` → includes `SCORECARD.md` and many unrelated round-29 paths; no `census/round-29/c2-counter-v2.py`.
- No counter, fixture, build, or test was run; no scratch created and no lane files modified. No LSP device was available in the provided tool inventory; conclusions use the frozen source and read-only git history, not grep as semantic proof.

## Deliveries

- `.ufo/waves/round-34/w2/AttackE23b.md` (this report)
- `.ufo/waves/round-34/w2/SwarmReviewer18.md` (same scoped report, per seat delivery instruction)
