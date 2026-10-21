# Souji round 20 — deleted owned input review

## Axes and evidence boundary

Axes reviewed: (1) a missing owned input refuses before producing a record, (2) the input receipt covers every required input, and (3) a mid-run deletion is caught by the final snapshot check.

Source-only review; no target code, tests, builds, linters, or formatters were run. No `lsp` device/server is available in the mounted tool inventory, so status/references/definition/diagnostics could not be requested. Literal grep was used only to locate source anchors; the findings below are based on bounded source reads, not grep as semantic proof.

Observed revision: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (the stated baseline). The initial working-byte inventory showed all six inspected production files modified and recorded these SHA-256 values:

- `tools/souji-seat-audit.py` — `9ac0c6e08aad430e964a6ced088409e300e93705ea048be09af1479bdb26eabd`
- `tools/souji-rev-pin.py` — `d49efa4e0ee4e9c275e2866dd7b6a20b201a4ac12d2225ca9a0772cfae6578c9`
- `census/round-13/run-verification.py` — `a10d66ca6728f641fb4144c7fcfb2996ff1940fd7c6e2f69e30230073a9116e8`
- `census/round-14/run-verification.py` — `45e6896c9b24e45c58a49efed38c0f09e642f0779c60dacf3bd1ab487e9b3502`
- `census/round-14/run-targeted.py` — `2d8c61809a0cb99a4f975f9e0e290bf30ef8cd4f4d7267a6569f759da5df6895`
- `census/round-14/cache-demonstration.py` — `3ad63d5b927fedc3aee70c2b2a13c91ad9c83d7bba9c71c5d85844507ef4213b`

These are the observed working-tree digests, not claims that the working tree equals HEAD. Per the no-wait/no-recheck boundary, I did not poll or re-hash after inspection.

## Finding

### High — a deleted required seat transcript can still produce a successful audit receipt

`tools/souji-seat-audit.py:361-366` treats a spec item with no `<SeatName>.txt` as a `missing_transcripts` entry and continues instead of refusing. `:387-398` only rejects if that missing transcript appears during the run; it then hashes only bytes actually consumed and returns the result. In the CLI, `:569-582` writes the JSON receipt after `run()` returns, and `:589-591` chooses the exit status from major violations alone—not from `missing_transcripts`. Therefore, with a fresh JSON destination and no major violations, deleting a transcript required by the spec can yield a receipt with that seat omitted and exit 0. The absent transcript has no digest in `input_sha256`. This contradicts the round-20 C1 preregistration that receipts bind the actual transcript bytes, and the assigned deleted-owned-input refusal criterion. This is a static control-flow finding, not a fresh runtime observation.

**Concrete oracle change:** in the audit caller fixture, define one required seat and its transcript, then delete that transcript while keeping the spec (and any manifest) intact. Invoke the CLI with a new JSON output path and assert exit 2/refusal and that the output path remains absent. This specifically distinguishes fail-closed behavior from a partial receipt that merely lists a missing seat.

## C2 deletion path review

Static source inspection did not find the same missing-leaf acceptance in the shared revision-pin path: `tools/souji-rev-pin.py:131-178` checks real regular non-symlink leaves, wraps filesystem errors as `Refusal`, and compares the actual map against committed expected leaves, including missing entries. The r13 runner catches initial `Refusal` before a record (`census/round-13/run-verification.py:121-141`) and rechecks before opening its output (`:493-512`). The r14 runner similarly refuses during initial resolution (`census/round-14/run-verification.py:51-67`) and checks again before its exclusive output open (`:150-164`); `run-targeted.py:20-25,44-59` uses that resolver and recheck before its output open. The cache demonstration catches binding refusal in `git_head` (`cache-demonstration.py:194-207`) and returns a blocked stdout payload rather than writing an external result; its final binding refusal also returns before successful payload emission (`:1210-1218`). These are source-order observations only, not execution evidence.

## Residual risk and verification gaps

No deletion oracle was executed under this read-only assignment, so race timing and actual CLI exit/output behavior remain unverified. The concrete actionable defect is the audit path's deliberate missing-transcript continuation; the C2 refusal ordering appears correctly placed in source but still needs the preregistered caller-level deleted-input/no-record oracle at the measured revision. This is author-side review evidence, not independent closure or admission.