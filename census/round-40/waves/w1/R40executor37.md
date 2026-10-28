# R40executor37 — C1 calibration attack

- Axis: calibration.
- Distinct edge: **resolvable but semantically misbound evidence pointer**. This is separate from the r39 token-only forgery: even if r40 requires a revision-resolving pointer on each item line, existence/resolution alone does not establish that the cited receipt belongs to that item or contains its claimed result.
- Verdict: **bounded attack; r40 candidate not yet available in committed census artifacts, so no r40 behavior is claimed as measured.** The frozen target is testable; the evidence below falsifies the sufficiency of token/pointer-shape checks unless the measurement verifies pointer-to-item/value binding.

## Evidence

1. `census/round-40/preregistration.txt` (read first), C1: requires an evidence-bound line and strict-descendant `commit` vs `receipt_rev`; explicitly says forged token-only line stays OPEN. It does not spell out in the predicate that a resolvable pointer must lead to a receipt proving the *same item’s* expected value.
2. `corpus/lessons/round-39-verifier-spotcheck.md:44-52`: the six r39 register rows all had `commit` strict descendants of `receipt_rev`, but the reviewer found all six `commit` fields named one distinct hash (`a8e6d75…`). This is direct evidence that strict-descendant relation is not itself evidence identity/binding.
3. `corpus/lessons/round-39.md:103-115`: disclosed limits include that an item only binds an anchored line to token presence, a token-only line can satisfy it, and `commit_distinct>=2` does not prove any row’s revision is right.
4. `census/round-39/waves/w1/W1RevC1Forge.md:114-175, 250-290`: fixture attack recorded two bare correction lines without a receipt/path/revision, closing both forged items (rc 0 with clean register); it further explains the item and register arms are disjoint. This is the prior forgery mechanism; my distinct extension is a *valid/resolving but wrong-item/wrong-value receipt pointer*, not a token-only line.
5. `census/round-39/c1-counter.py:19-23,136-163` (grep result): r39 register path parses row count and `commit != receipt_rev`, then runs the citation reconciler; this identifies the existing pattern to test against without asserting r40 implementation details.

## Bounded measurement plan / falsifier

Once the candidate r40 counter and fixture/receipt bytes are committed, make two otherwise-identical item lines in a disposable fixture: (A) cite an existing resolvable receipt/revision carrying the expected token for that item; (B) cite a different, equally resolvable receipt/revision carrying the same generic token but no evidence for that item (or a receipt for another item). Keep anchor and required tokens identical; use a strict-descendant commit for both rows, and include controls for equal and backwards commits. Run the exact frozen r40 invocation at the candidate landing revision and compare item-level closure and register mismatches. The claim is falsified if B closes, or if equal/backwards commit passes. Also run the declared token-only forged line; it must stay OPEN. Preserve outputs and exact revisions in the lane-owned receipt.

This isolates binding semantics from revision resolvability and from the already-known token-only attack. A mere `git cat-file` check or substring check cannot distinguish A from B. Do not infer a pass from a planned/unrun probe.

## Commands and outputs actually run

- Read `RULES.md`, `census/round-40/preregistration.txt`, `skill://godspeed`, `corpus/lessons/round-39-verifier-spotcheck.md`, `corpus/lessons/round-39.md`, `.ufo/waves/round-40/w1-spec.json`, and located r39 C1 artifacts with `glob`/`grep`/`read` tools.
- No shell commands, candidate counter execution, fixture construction, git mutation, or tests were run. No installs.
- Result: evidence-backed attack boundary and bounded probe only; candidate behavior remains unmeasured.
