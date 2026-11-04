# S58Connector2 — bounded sibling-overlap scan

## Axes and scope

Declared axes: C1 calibration (lowest score 7), C2 operability (8), coverage 8 unchanged. Source: `census/round-58/preregistration.txt`, including its complete C2 line. Assignment predicate pin: `e7f64f30324e8ddb3f2266302daa9066054cdbb3` (provided identity; not independently checked by this seat).

Read-only source scan of `../kaidoku-shokunin/tools/`, `../kama-shokunin/tools/`, and `../kumitate-shokunin/scripts/` (the observed kumitate tool directory). No sibling code was executed. No production, historical counter, sibling, or fleet files were changed. This is not Markdown repair, an admission decision, or an implementation.

## Evidence and reuse candidates

| Owner / source | Observed mechanism | Reuse boundary |
|---|---|---|
| Kaidoku: `tools/round-80/receipt-provenance.py:136-142` | Rejects empty, absolute, and literal `..` path segments. | Useful lexical predicate only; not filesystem symlink confinement. Its committed-blob provenance resolver and history search at lines 123-134 answer a different ownership question: where instrument bytes were bound. Do not import history fallback into Souji receipt admission. |
| Kaidoku: `tools/round-39/mk-carriers.py:56-65` | `real_under` resolves candidate and root, checks equality or root-plus-separator prefix, then requires a file. | Useful Python canonical containment pattern, including intermediate symlink escape. It explicitly permits absolute paths inside root: copied alone, it contradicts round-58's absolute-path refusal. |
| Kama: `tools/round72-receipt-tip-binding.py:416-427` | Collects every matching header in its five-line window, lowercases hex, rejects more than one distinct revision. | Reuse the distinct-value cardinality idea for `RECEIPT-REV-CONFLICT`, not Kama's window or header grammar without checking Souji's frozen contract. Identical repeated values are not conflicts in this source. |
| Kama: same file, lines 155-159 and 430-440 | `_commit_sha` resolves `rev + '^{commit}'`; header evaluation then tests ancestry and record-only changes. | Not a raw commit-type guard: peeling can accept an annotated tag object. Kama's ancestry/record-path policy belongs to Kama, not Souji's five-case repair. |
| Kumitate: `scripts/counter-pins.mjs:120-154` | Canonicalizes base and target, checks relative escape, then requires the named object to be a regular file using `lstatSync`. | Demonstrates separating canonical confinement from file-kind admission. Its registry-local base for explicit registries must not replace Souji's receipt root. |
| Kumitate: `scripts/routed-ledger.mjs:185-214` | Separates lexical containment, symlink-chain inspection, and regular-file reading. | Rejecting every symlink is stronger than merely rejecting an escaping symlink. Do not silently widen Souji's refusal policy to all in-root links. |
| Kumitate: `scripts/ready-handoff.mjs:104-121` | Canonicalizes deepest existing ancestor for potentially nonexistent report destinations. | This owns output destination safety, not existing receipt evidence; unnecessary complexity for the bounded receipt reader. |
| Kumitate: `scripts/report-receipt-diff.mjs:190-193,295-300,547-550` | Admits regular Git-tree blob modes for receipts; commit existence and CLI revision use `^{commit}`. | Blob-mode admission is not raw revision-type validation. Its Markdown report parser and hash ancestry checks are outside scope. |

Bounded type-guard search found `cat-file -t` examples operating on `REV:PATH` blobs/trees (Kaidoku round-29/30/31/45 and Kama round72 tools), but no directly reusable raw revision `type == commit` guard in the returned matches. This is not a claim that no sibling implementation exists: broad results were paginated, then narrowed; the scan was not an exhaustive semantic audit.

## One proposed move

**Locally adapt the separation of lexical identity, canonical location, and raw object identity; do not share/import a sibling gate.**

For L1's Souji C2 integration: retain the existing receipt grammar and findings interface, use the Kaidoku lexical pattern before canonical containment, then use a root-plus-separator canonical containment check for the existing receipt. Independently collect distinct recognized revision headers before choosing one. For a single header, require the unpeeled named object's Git type to be `commit`; do not substitute sibling `^{commit}` resolution for that check.

Map the three unsafe path forms to `RECEIPT-PATH-UNCONFINED`, a tag-object revision to `RECEIPT-REV-ABSENT`, and differing recognized revision values to `RECEIPT-REV-CONFLICT`, exactly as preregistered. No new finding vocabulary, dependencies, shared package, sibling subprocess, or historical-reader edits are proposed.

Affected axes: C2 operability improves if the fixed acceptance inventory passes. C1 correction and coverage remain untouched by construction; no measured axis improvement is claimed by this scan.

## Second-order effects and risks

- Runtime: canonical containment must precede reading receipt bytes, otherwise an escaping path is still opened before refusal. This does not establish race-free execution authentication.
- Contract: resolving to a commit and naming a commit object are different predicates. Sibling peeling conflicts with the annotated-tag refusal; explicitly preserve the latter.
- Substrate: retain Souji's own root selection and Git invocation context. Sharing sibling scripts would add runtime/ownership coupling for no acceptance gain.
- Verification: header windows, absent-file precedence, repeated identical headers, and in-root symlink behavior must not drift merely because a donor tool has stronger or different policy. Their behavior is not newly specified here.

## Verification and unrun legs

Observed operations were specialized `read` and `grep` source inspection only; those tools do not supply shell EXIT receipts. No shell command, behavioral probe, selftest, build, lint, formatter, sibling runtime, installation, or Git mutation was run; no command/output/EXIT receipt is fabricated. No own scratch was created, so none requires removal.

L1 verification remains unrun here: the frozen five-case before control, independently implemented C2 acceptance (five exact refusals and three preserved r57 receipts), rc plus full findings and exact case identities, scratch idempotence, and the separately owned C1 target/deletion controls. This seat does not change any frozen inventory or counter bytes.

Self-evaluation: accuracy 4/5 (static evidence, no runtime confirmation); completeness 4/5 (bounded candidate scan, not exhaustive type-guard proof); clarity 4/5 (explicit donor-policy distinctions); actionability 4/5 (single local adaptation, acceptance still L1-owned); conciseness 4/5 (table needed to distinguish three owners). Average 4.0/5. Main limitation: source inspection cannot certify behavioral preservation.

Report: .ufo/waves/round-58/w1/S58Connector2.md
