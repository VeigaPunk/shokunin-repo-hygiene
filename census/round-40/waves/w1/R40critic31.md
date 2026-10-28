# R40critic31 — independent C1 calibration attack

## Axes
- **Calibration** (primary): whether the C1 counter actually establishes the frozen evidence-bound / revision-bound claim.
- **Operability** (secondary): whether the evidence requirement can be applied reproducibly to the exact committed bytes.
- Coverage is not assessed by this attack.

## Verdict
**C1 has a meaningful, testable calibration predicate, but its success must not be summarized as proof that the anchored correction is factually true.** The sharp counterexample to an over-broad reading is a single line containing an anchor and all expected tokens while also asserting the stale value elsewhere: token co-occurrence can close the item unless the stale value is explicitly prohibited. The r39 spot-check already established that limitation. r40's additional `mustnot` requirement can address it, but only for stale literals represented in the item schema; it cannot verify arbitrary factual entailment. This is a bounded limitation, not a falsifier of the narrower frozen predicate (which requires resolvable evidence pointers and strict-descendant commits).

A distinct edge case for this item: **a syntactically valid but semantically irrelevant evidence pointer**. A line may contain a resolvable revision-bound path/anchor yet the cited evidence says nothing supporting the correction. The r40 claim as frozen says “resolvable, revision-bound evidence pointer,” not that the counter independently validates the cited proposition. Thus an all-closed receipt alone supports linkage/integrity, not truth. Do not credit a stronger truth-validation claim unless the receipt demonstrates source-content checking or a separately independent review.

## Evidence and exact pointers

1. Frozen claim and control: `census/round-40/preregistration.txt` (preregistration read first), C1 paragraph: requires each anchored item line to have a resolvable revision-bound pointer in addition to r39 token predicate, strict descendant of `receipt_rev`; forged token-only line must remain open; kill conditions include forged closure and backwards/equal commit.
2. Prior concrete false-green observation: `.ufo/waves/round-39/w1/W1CritC1Axis.md:181-210,253-257`. It records `D-TRUE` and `D-FALSE` both CLOSED, plus a retained-stale contradiction CLOSED, and a `mustnot` variant OPEN. Its finding explicitly limits item-arm evidence to presence rather than truth and notes all r39 item rows had `mustnot = -`.
3. Prior independent committed-bytes spot check: `corpus/lessons/round-39-verifier-spotcheck.md:36-55` reports 16/16 at `0242085`, base 16 open, and six rows whose commit was a strict descendant of receipt_rev; `:42-49` gives its re-derivation and tool command. This supports that strict-descendant is measurable, not that pointer relevance is automatically validated.
4. r39 counter pattern: `census/round-39/c1-counter.py` (selected-file source available by path; preregistration is r40’s only claim authority). The committed r39 spot-check describes the item matching behavior in `corpus/lessons/round-39-verifier-spotcheck.md:38-40`: anchor, must tokens, and absence of mustnot on one line. The frozen r40 text itself adds the evidence-pointer condition; no r40 C1 counter/receipt was inspected or claimed here.
5. Nearby distinct parser edge, not the assigned claim: `tools/souji-worktree-drift.py:147-168` decodes record bytes using UTF-8 `replace`, parses every TOTAL row by replacing `total`, and validates only the final total at `:169-178`. This may motivate C3 tests, but does not falsify C1 and is deliberately not presented as a C1 result.

## Counterexample / bounded measurement plan

Use an isolated scratch fixture with two item lines and a tiny committed evidence tree:
- `E1` cites a resolvable revision/path/anchor whose contents do support the expected correction; should close.
- `E2` carries the same valid revision/path/anchor shape but the cited contents contain unrelated text; expected-token line itself remains present. If C1 closes E2, that demonstrates the instrument checks pointer resolution/binding but not semantic relevance. This is a **bounded measurement**, not a claim that the frozen predicate requires semantic entailment.

Also pair the existing r39-style contradictory line (anchor + expected + stale literal) with an item whose stale literal is in `mustnot`; this tests the specific known false-green control. Both fixtures should use `git -C "$D"` exclusively and assert `git -C "$D" rev-parse --show-toplevel` equals `$D` before any fixture commit. Run counter on a committed base and candidate revision, record exact stdout/stderr/status and hashes, and remove scratch. No such measurement was run by this seat.

## Commands actually run and results

- `read /home/vgpnk/.omp/agent/RULES.md` — succeeded; tooling rules read.
- `read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt` — succeeded; frozen C1/C2/C3 predicates read.
- `read skill://godspeed` — succeeded.
- `read .../corpus/lessons/round-39-verifier-spotcheck.md` — first attempted wrong path `census/round-39-verifier-spotcheck.md` (not found), then correct path succeeded.
- `glob .../.ufo/waves/round-39` and `glob .../census/round-39` — confirmed committed r39 reports/artifacts and counters are present.
- `read .../.ufo/waves/round-39/w1/W1CritC1Axis.md` — succeeded; reviewed C1 false-green fixture/finding.
- `read .../census/round-39/c3-counter.py` — succeeded; reviewed C3 historical control pattern.
- `grep` on `tools/souji-worktree-drift.py` for TOTAL/UTF-8/skip branches — returned parser and branch locations.
- `read .../tools/souji-worktree-drift.py:138-180,265-330` — succeeded; inspected record decode/TOTAL and skip-related run region.
- `read .../census/round-39/c2-counter.py:1-170` — succeeded; inspected historical docstring analyzer.
- No shell commands, fixture commits, production edits, counter runs, or tests were performed. No installs or scratch directories were created.

## Impacted axis and smallest safe correction

- **Calibration:** preserve the claim as narrowly stated; report “pointer resolves and is revision-bound” separately from “correction is true.” The smallest correction is a receipt field/wording that distinguishes evidence-link integrity from factual support, with the stale-literal contradiction fixture included in the counter battery. Do not expand C1 into semantic entailment absent a defined, reproducible rule.
- **Operability:** measurement recipe above is executable and bounded; no observed r40 behavior is claimed.
- **Coverage:** no conclusion.
