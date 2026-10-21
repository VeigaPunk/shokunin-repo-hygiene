# Output exclusivity review — operability

Scope: static review of r13/r14/targeted output validation, exclusive creation, and pre-output refusals; plus the r14 cache-demo binding-failure output path. No target code or runner was executed.

## Findings

### Medium — output containment can be bypassed after preflight

The output location is checked before the lengthy measurement, but not pinned or checked again when the result is created. In r13, `validate_output` checks containment and symlink components at `census/round-13/run-verification.py:356-379`; `main` calls it before `execute` at lines 422-435, and the eventual write is `output.open("x")` at lines 517-518. In r14, `output_path` checks the path and parent at `census/round-14/run-verification.py:82-99`, before the runner work at lines 126-158; it later writes through the path at lines 169-170. `run-targeted.py:21-25` uses that same early preflight, then performs its work and writes at lines 46-59.

[INFERENCE] A same-user concurrent actor can replace the validated `census/round-N` directory with a symlink to an external directory while checks are running. The final `open("x")` follows a symlink in a parent component, so the record can be created outside the lane. Exclusive mode prevents replacing an already existing final filename; it does not anchor the parent directory or preserve the earlier containment result. No such race was executed or observed.

Concrete oracle: in an isolated fixture, pause after output preflight, replace the round directory with a symlink to an external temporary directory, then resume. Require refusal and no external output. Pin a verified directory descriptor and create relative to it without following links (or otherwise make final containment and publication race-safe); a second string-path check alone retains a check-to-use window.

### Medium — a failed final write can leave a partial record despite reporting refusal

All three writers create the destination before writing the serialized record: r13 `run-verification.py:517-518`, r14 `run-verification.py:169-170`, and targeted `run-targeted.py:58-59`. Their refusal handlers catch write-time `OSError` (r13 `run-verification.py:436-443`; r14 `run-verification.py:173-178`; targeted `run-targeted.py:62-67`) but do not remove a partially created destination. For example, an I/O error after exclusive creation but during write/flush can leave a truncated JSON file; the process then reports refusal, and a subsequent attempt will reject that path as already existing. This is a source-derived failure case, not an observed disk error.

Oracle change: inject a write/flush failure after destination creation; assert exit 2 and that the destination is absent. Publish via a same-directory temporary plus an exclusive no-replace finalization, cleaning the temporary on failure.

### Low — r14 accepts non-numeric round directory names

`census/round-14/run-verification.py:87-90` checks that the second path component merely `startswith("round-")`; it does not require the `round-N` numeric form specified by the CLI contract. If `census/round-preview/` already exists and is a real directory, `--output census/round-preview/new.json` satisfies the shown shape and containment checks and can write there. `run-targeted.py` inherits this validator. This is not an escape from `census`, but it permits a record outside the expected round namespace. Use a full match such as `round-[0-9]+` (and an oracle case for `round-preview`) rather than a prefix test.

## Checks that passed statically

- r13 requires explicit `--round` and `--output` and refuses their omission before execution (`run-verification.py:417-425`); it also requires the output parent to equal the exact numeric round directory (`:352-363`).
- r13 and r14 reject a pre-existing target and use exclusive `open("x")` at their write sites, so the normal preflight/no-overwrite path is present. Targeted inherits r14's output validation and exclusive write.
- For input-binding drift, r13 compares the final snapshot before its output write (`run-verification.py:499-502`); r14 checks inputs before writing (`run-verification.py:156-170`); targeted does likewise (`run-targeted.py:44-59`). Their refusal handlers produce exit 2 for these ValueError/OSError paths and do not reach the record write.
- The cache demonstration validates through `git_head` before running the demonstration (`cache-demonstration.py:194-214`); failure emits its blocked JSON to stdout at lines 1144-1155. It has no caller-selected result-file path in `main` (`:1111-1123`), so this review found no external result-file write on that binding-refusal path.

## Evidence and verification gaps

Working-tree SHA-256 observed in the initial read batch (not a claim about a committed revision):

| Path | SHA-256 |
|---|---|
| `tools/souji-seat-audit.py` | `78d73d85ba198df6614a47b5d4d9388038da5c74407b475148713bc8958f6269` |
| `tools/souji-rev-pin.py` | `869d399ca1ec2868e9c794e438298a9dfd844eed76e5d477fa38b710f170e49d` |
| `census/round-13/run-verification.py` | `945cf6ecd5f4472c2556eb6f0b26e0a42193268a158cf3a0a8d776c00ef1d0cc` |
| `census/round-14/run-verification.py` | `bde95f972e09de393d32b1aa840bc2282f1677c147399ae7ed24c6558f525f73` |
| `census/round-14/run-targeted.py` | `a0c08e1252df3b7c20cab6eaecaa8222c7eed5f39ba19188eca2da031c5fd3f2` |
| `census/round-14/cache-demonstration.py` | `706200486d0938322a773116ae01377f3a56ec82443415e0d1956cd126c95bd6` |

The `lsp` device is unavailable in this session (`read xd://lsp` returned “No such tool”; the mounted-device inventory omitted it). No grep was used. Findings are bounded source analysis; no runtime race, write-failure, or CLI oracle was exercised.