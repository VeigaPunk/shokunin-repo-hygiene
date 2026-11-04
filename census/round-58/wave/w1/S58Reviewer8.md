# S58Reviewer8 — bounded C2 adversarial review

## Findings by severity

No actionable defect found against the frozen five-refusal/three-preserved-receipt predicate. This is a review recommendation only, not admission or integration authority.

Reviewed authoritative implementation: `.ufo/waves/round-58/w1/S58Executor3/c2-gate.py`, final SHA256 `7c35d3ea22f75303cd593026119f30de862b439a51a5375afe2ecfc12a433ed0`. L1 SoujiR58 explicitly resolved executor01 to S58Executor3; no competing implementation was scored. Frozen r57 control SHA256 `174d7b8a3c105875f1757f9137f26ed54e38ac11c963a134015bce8a9dd16ec2`. Initial proposal digest `dfd90d9da263d0bdc28d118bbc75f355c41432034854a2de3b3ab7749cbc3bdf` was superseded by owner-authorized fixture cleanup changes; its receipts remain separately retained.

Axes: refusal correctness; honest-receipt preservation; bounded claim fidelity.

## Observed behavioral probes

Each cell is the actual CLI EXIT/finding identifier; complete command, stdout, stderr, and EXIT are retained in `S58Reviewer8/before-expanded.json` and initial `S58Reviewer8/after.json`. All 17 invocations were repeated on final revised bytes in `S58Reviewer8/after-revised.json`; same outcomes, fresh fixture commit identity.

| Case | Frozen r57 | Proposed gate |
|---|---|---|
| Honest relative regular file | 0 / none | 0 / none |
| Absolute path (even pointing inside root) | 0 / none | 1 / RECEIPT-PATH-UNCONFINED |
| ../ outside root | 0 / none | 1 / RECEIPT-PATH-UNCONFINED |
| receipts/../receipts/ok (normalizes inside) | 0 / none | 1 / RECEIPT-PATH-UNCONFINED |
| ./receipts/ok | 0 / none | 0 / none |
| Intermediate symlink escaping root | 0 / none | 1 / RECEIPT-PATH-UNCONFINED |
| Intermediate symlink staying inside root | 0 / none | 0 / none |
| Final symlink | 1 / RECEIPT-SYMLINK | 1 / RECEIPT-SYMLINK |
| FIFO (no writer) | 1 / RECEIPT-MISSING | 1 / RECEIPT-MISSING |
| Conflicting standalone headers, valid first | 0 / none | 1 / RECEIPT-REV-CONFLICT |
| Conflicting standalone headers, absent first | 1 / RECEIPT-REV-ABSENT | 1 / RECEIPT-REV-CONFLICT |
| Identical duplicate headers | 0 / none | 0 / none |
| Annotated tag OBJECT OID | 0 / none | 1 / RECEIPT-REV-ABSENT |
| Commit reachable only through annotated tag | 0 / none | 0 / none |
| Commit reachable only from refs/jj/keep | 1 / RECEIPT-REV-KEEP-ONLY | 1 / RECEIPT-REV-KEEP-ONLY |
| Commit reachable only from refs/remotes | 0 / none | 0 / none |
| Exact r57 after.tsv, three real receipts | 0 / receipts=3 findings=0 | 0 / receipts=3 findings=0 |

The unchanged control does not reach the target. `fixture-types.json` independently records `cat-file -t` returning `tag`, peeling to the distinct tag-only commit, and the complete small fixture ref inventory. No case timed out.

## Actual diff and changed contracts

`S58Reviewer8/actual-diff-revised.txt` retains the final actual unified diff and expected diff EXIT=1; `actual-diff.txt` retains initial bytes. The operational caller chain remains CLI `main` → `run_manifest` → `check_receipt`; production receipt recorder emits standalone `rev=` before command output (`census/round-57/record-receipt.sh:27-32`).

* Final proposal lines 91-116 reject lexical absolute/.. and resolved outside-root paths; lines 143-152 perform confinement before content read and retain final-symlink/nonregular-file refusal. Static FIFOs are not opened.
* `durable_kind` requires exact object type `commit`, retaining heads/tags/remotes ancestry and keep-only classification. The tag-only commit positive leg prevents mistaking tag-object rejection for blanket tag rejection.
* Lines 153-161 collect distinct standalone revision headers, refusing either conflicting order and preserving identical duplicates. Standalone headers take precedence over body `SUMMARY rev=` fields; the documented legacy scan applies only without standalone headers. This is not execution authentication.
* Lines 369-430 statically compare per-case rc and complete ordered canonicalized findings, and require exact expected-case identity. Canonicalization replaces work-prefix and hex runs; it is not byte-exact OID validation. Final `run_selftest` lines 358-366 creates a unique temporary fixture and removes only that created root in finally. I did not rerun the gate selftest; its execution/idempotence belongs to the implementation/acceptance owners.
* `run_manifest` retains malformed/unreadable-manifest rc2 handling. Receipt filesystem races and read failures remain outside this static-case result.

LSP device was unavailable: `read xd://lsp` returned “No such tool”. References/definition/diagnostics therefore could not run. Caller/definition review used source inspection and literal fallback search, not semantic absence proof. No other runtime was invoked. Resume continuity, same-identity rerouting, and saturation are not contracts changed by this receipt gate and were not claimed or tested.

## Residual risk and verification gaps

* Static confinement uses separate path checks and `read_bytes` (lines 91-116, 147-152), not an atomic descriptor-based open: concurrent replacement could race it. No adversarial race probe was assigned/run; no universal privacy/confinement assertion follows.
* Allowed internal parent symlinks and lexical `./` normalization remain intentional. Lexical `..` is rejected even when normalization would stay inside. FIFO refusal is reported as MISSING, not a newly claimed type-specific diagnostic.
* Header precedence intentionally ignores body revision tokens when standalone headers exist. No universal receipt parser or execution-authentication claim is supported.
* No Markdown repair, C1 scoring, builds, lint, formatters, network, installs, service/config changes, commits, pushes, or production/history edits performed. Canonical independent acceptance and gate selftest/idempotence were not run by this seat; only the assigned adversarial CLI probes above were exercised.

## Evidence and cleanup

Evidence directory: `.ufo/waves/round-58/w1/S58Reviewer8/`: `probe.py`, initial `before.json`, expanded same-fixture `before-expanded.json`, initial `after.json`, final `after-revised.json`, `fixture-types.json`, initial `actual-diff.txt`, final `actual-diff-revised.txt`. Scratch fixture Git CLI mutations were explicit `-C` init/config/add/commit only; toplevel asserted before config/add/commit. Deterministic loose objects/refs were written directly only in own asserted fixture, never via tag/update-ref/reset. All raw evidence was copied before deleting own scratch. Tools installed/updated: none.

Self-evaluation: accuracy 4 (raw command receipts; no atomic-race evidence), completeness 4 (all assigned adversarial families exercised; selftest execution left to owners), clarity 4 (case matrix and line citations; canonicalization caveat matters), actionability 4 (exact implementation digest and reproducible driver; scratch deliberately removed), conciseness 4 (raw logs separated from report). Average 4.0; strongest improvement would be owner verification of frozen acceptance/selftest on this exact digest, not broadening the claim. Would the user agree: bounded evidence and explicit unrun legs are provided.

## Final owner-authorized simplification addendum

This addendum supersedes the implementation digest labeled final above. Latest reviewed SHA256: `56f2a31163035726f1190db3e6b827fc121602377e187d16a54a6ae8f15af543`. The owner removed emit-expected/overwrite CLI behavior and added malformed expected-rc handling. All 16 assigned adversarial fixture cases plus the three-receipt manifest were rerun on these exact bytes, with unchanged outcomes, no timeout, and no actionable bounded-predicate finding. Raw final commands/output/EXIT: `S58Reviewer8/after-final.json`; actual final diff: `S58Reviewer8/actual-diff-final.txt`. Prior evidence is retained, not overwritten. Selftest/idempotence/malformed-expected execution remains unrun by this reviewer. Own scratch was again removed after copying receipts.

Report: .ufo/waves/round-58/w1/S58Reviewer8.md
