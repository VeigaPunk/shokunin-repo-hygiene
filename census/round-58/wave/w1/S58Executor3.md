# S58Executor3 — C2 implementation delivery

Axes: bounded refusal correctness; preservation of three honest receipts; selftest discrimination; scratch safety. Sole integration authority remains SoujiR58.

## Delivered files

All paths relative to souji-shokunin:
- `.ufo/waves/round-58/w1/S58Executor3/c2-gate.py`
- `.ufo/waves/round-58/w1/S58Executor3/c2-selftest-expected.tsv`
- Evidence in the same delivery directory: `selftest.txt`, `idempotence.txt`, `idempotence-comparison.txt`, `honest.txt`.

Final gate SHA256: `56f2a31163035726f1190db3e6b827fc121602377e187d16a54a6ae8f15af543`.

Derived from census/round-57/c2-counter.py; historical bytes were not edited. Predicate commit e7f64f30324e8ddb3f2266302daa9066054cdbb3 was observed as a commit with the round-58 freeze subject.

## Behaviour

- Absolute receipt paths, paths containing `..`, and intermediate symlink escapes return RECEIPT-PATH-UNCONFINED before receipt content reads.
- Exact OID must have cat-file type commit. Tag objects return RECEIPT-REV-ABSENT; commit reachability via heads/tags/remotes remains accepted. Existing keep-only refusal retained.
- Distinct standalone rev headers return RECEIPT-REV-CONFLICT; identical duplicates allowed. Standalone headers take precedence over SUMMARY/body tokens. Without standalone headers, legacy whitespace-token grammar remains. This boundary was explicitly approved by L1: historical c1-tip.txt has a full40 header plus a short SUMMARY rev, which is body data, not a conflicting header. No prefix-equivalence exception exists among headers.
- Selftest asserts rc and complete ordered finding strings after documented normalization (fixture-root prefix and hex runs), and exact expected case identity; duplicate expected case names refuse evaluation. Hand-authored expected TSV contains 17 cases.
- Fixtures use scrubbed Git environment and explicit `git -C`; toplevel is checked before non-init fixture commands. Unique mkdtemp root is created under work and cleaned in finally, including build failures. No existing caller fixture subtree is recursively removed.

## Retained observed evidence

Each probe receipt retains COMMAND, output and EXIT.

- `selftest.txt`: 17 expected/17 actual, no extra/missing cases; every rc and full normalized findings match; always-clean control rejected (4 matches, 13 discriminated); EXIT=0.
- `idempotence.txt`: identical second selftest at the same work path; EXIT=0.
- `idempotence-comparison.txt`: retained receipts compare IDENTICAL; EXIT=0.
- `honest.txt`: frozen r57 after.tsv yields SUMMARY receipts=3 findings=0; EXIT=0.
- `malformed-rc.txt`: L1-assigned malformed expected rc probe returns CANNOT-EVALUATE without traceback; EXIT=2.

No builds, lint, formatters, production commits, pushes, installs, global config edits, or external remediation. Own scratch removed after final evidence capture. LSP tool unavailable in this session's exposed inventory; direct source inspection used instead.

## Superseded attempts and limits

Initial all-token conflict detection regressed the honest c1 receipt; a temporary prefix-equivalence experiment was rejected in favour of L1-approved header precedence before canonical delivery. Earlier relative-work fixture runs failed because an intended absolute-path fixture was relative; corrected by resolving work. Earlier shell idempotence comparison also included unequal run-label strings. `earlier-*` files retain these failed intermediate outputs (not final evidence).

Candidate dfd90d9... passed behavioural probes but Sentinel11 identified unconditional deletion of caller work/c2-fixtures. L1 authorized a safety revision; `superseded-*` receipts refer only to that older candidate. Final receipts above were rerun against final bytes. Early scratch builder invocations inherited reset/update-ref/tag commands and cwd-based git invocation from r57; these were confined to exclusive scratch but did not satisfy the strict fixture-command restriction. Final builder removes those Git mutation commands and uses explicit -C/toplevel guards. No outside-scratch mutation was performed.

Independent acceptance after-arm, adversarial review, and mutation scoring belong to L1/review seats and are not claimed here. No execution-authentication, universal parser, concurrent symlink-race resistance, Markdown repair, or universal filesystem-safety claim. Full finding comparison normalizes hashes; it does not prove exact hash values in selftest output. Symlink confinement checks are stat/realpath-based, not race-free descriptor traversal.

L1 subsequently authorized removing the unrequested emit-expected CLI and mapping malformed expected rc to CANNOT-EVALUATE. Final digest above includes both changes; `superseded-7c35-*` retains prior revision receipts, not final-byte evidence. All canonical receipts were rerun against the final digest. Expected TSV and acceptance predicate unchanged.

Self-evaluation: accuracy 4 (bounded probes pass; independent acceptance not run here); completeness 4 (delivery and assigned probes complete, parent owns integration); clarity 4 (header/body boundary documented); actionability 4 (exact artifact, digest, CLI and receipts supplied); conciseness 3 (derived gate retains verbose inherited documentation). Overall 3.8. Improvement: independently score final bytes using Executor4's acceptance driver; preserve bounded claim wording.

Report: .ufo/waves/round-58/w1/S58Executor3.md
