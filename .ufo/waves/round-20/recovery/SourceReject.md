# S090 — source rejection reopen

**Decision: keep rejected; no source-based flip. Confidence: high for the bounded source question.** Axes: calibration (source fact vs lane authority), freshness (current public page), and discernment (actual round-20 reject vs historical S032).

## Observed evidence

- At the observed `HEAD` `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (the preregistered baseline), `corpus/SOURCES.md:110` records S090 as rejected, scoped to “history rewrite as Souji cleanup authority,” explicitly not as a replacement-tool endorsement. The observed file SHA-256 was `199c06c9a57e692d010bda0578ae9f8a47bbe6fe2ef34bdbc802996e3b95a500`. `corpus/lessons/round-20.md:30` quotes the top-level WARNING exactly: “its use is not recommended.” That five-word substring appears in the reopened official page's `## WARNING`; the page says the filter-branch safety/performance issues cannot be backward-compatibly fixed, recommends an alternative such as `git filter-repo`, and gives precautions if filter-branch is still needed. The page identifies 2.44.0 as its last update and says 2.44.1–2.56.0 have no changes.
- This supports the narrow fact that Git does not recommend **git-filter-branch**. It does not say all history rewriting is forbidden, nor does the alternative-tool sentence grant Souji authority to rewrite history.
- The separate local authority is `PROVINCE.md:32-35`: “Git history rewrite in any repo” is operator-owned. Its observed SHA-256 was `a545e8e79ecb07304519f6fcad410b7c2ae89521aea235c64eaeff6919f936d5`.
- `corpus/SOURCES.md:138-140` records five pages screened, four documentary admissions and S090 as the cleanup-authority rejection; the subsequent S094 makes the combined search six pages/five admissions/one rejection. The preregistration's residual duties at `.ufo/waves/round-20/preregistration.txt:4` require a real current-round admit and reject. This is not a relabeling of historical S032: the round-19 spotcheck says S032 was a standing historical reject and that round 19 had no explicit current-round reject catalogue (`corpus/lessons/round-19-verifier-spotcheck.md:127-129`).

## Adversarial calibration

Keep S090 rejected **as a source for Souji cleanup authority**. The source excerpt correctly supports the tool-specific nonrecommendation; `PROVINCE.md`, not Git's warning, supplies the operator-ownership rule. A separately scoped operator-owned history task could change who owns that task, but would not make the Git page a Souji cleanup receipt. The bounded evidence contains no such operator scope, so I cannot assess whether that flip condition is met in a particular task.

**One concrete oracle addition:** use the page's own “Please use an alternative history filtering tool such as git filter-repo” sentence as a counterexample. Require the oracle to keep a candidate rejected when it tries to use that recommendation as a grant of Souji cleanup authority, while also forbidding the opposite overreach—treating S090 as a blanket ban on separately operator-owned history work. Flip only on explicit operator scope/ownership evidence, and never count that work as a Souji cleanup receipt. This separates the source's recommendation from local authority instead of scoring a keyword match on “not recommended.”

## Scope and limits

This was a source-only reopen; no target code was executed and no tools were installed. Observed relevant bytes: `corpus/lessons/round-20.md` SHA-256 `b69815a46b1ef6f5abaf31c86ce0108d50fd9bf854d4562b8cc447a90e90a7e0`. No claim is made about an operator authorization not included in the bounded evidence, or about page changes after the stated 2.56.0 coverage.