# SourceDiff — S093 `git diff --quiet` reopen

## Observed source state

This was a bounded, read-only source review at observed `HEAD` `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (the preregistered baseline). At the first source-byte sample, these six permitted code files were worktree-modified; their observed SHA-256 values identify the reviewed working bytes, not the baseline blobs:

| path | working-byte SHA-256 |
|---|---|
| `tools/souji-seat-audit.py` | `08a006657357e94d9153a6279c723340d7b586aa806c2355ec206253f09133c6` |
| `tools/souji-rev-pin.py` | `869d399ca1ec2868e9c794e438298a9dfd844eed76e5d477fa38b710f170e49d` |
| `census/round-13/run-verification.py` | `945cf6ecd5f4472c2556eb6f0b26e0a42193268a158cf3a0a8d776c00ef1d0cc` |
| `census/round-14/run-verification.py` | `bde95f972e09de393d32b1aa840bc2282f1677c147399ae7ed24c6558f525f73` |
| `census/round-14/run-targeted.py` | `a0c08e1252df3b7c20cab6eaecaa8222c7eed5f39ba19188eca2da031c5fd3f2` |
| `census/round-14/cache-demonstration.py` | `706200486d0938322a773116ae01377f3a56ec82443415e0d1956cd126c95bd6` |

No target code, tests, or validators were run; no tools were installed. No LSP endpoint was exposed in the available tool routes, so this is literal bounded source evidence, not semantic LSP proof.

## S093 source reopen

`corpus/SOURCES.md:113` records S093 as a narrowing of S081: `--quiet` disables output and implies `--exit-code`; status 1 means differences and 0 means no differences; complete measured-path discovery and failure classification are separate lane obligations. Its wording does not attribute a completeness guarantee to Git.

Fresh reopen: [git-diff documentation](https://git-scm.com/docs/git-diff), current page last updated in Git 2.56.0 (2026-09-28), `OPTIONS`:

- `--exit-code`: “That is, it exits with 1 if there were differences and 0 means no differences.”
- `--quiet`: “Disable all output of the program. Implies --exit-code.”
- `<path>...`: “The path parameters, when given, are used to limit the diff to the named paths (you can give directory names and get diff for all files under them).”

**Finding:** S093's exit-status/output statements match the reopened text. The path-scope statement is a direct limitation in the documentation: `--quiet` does not broaden the paths compared. **[INFERENCE]** A clean status for a supplied pathspec cannot establish that omitted dependencies or omitted path roots were clean; path-list completeness is a caller obligation, exactly as S093 narrows it. The page does not itself classify every possible command failure as 0 or 1.

## Current bounded code evidence

- `tools/souji-rev-pin.py:93-98` describes `input_snapshot` as a bounded file/directory binding and expressly says it re-enumerates untracked and ignored files. Lines 115-128 build the expected committed regular-file digest map from `git ls-tree`; lines 148-178 walk each selected directory and reject actual-vs-expected differences, including added, missing, and changed paths. Lines 181-225 show `resolve_durable(..., tree_check=True)` calls this snapshot for its supplied `measured_paths`. The implementation therefore does more than `git diff --quiet` for a directory that is actually selected; it cannot infer a dependency root the caller omitted.
- `census/round-13/run-verification.py:92-115` currently includes the helper, its own runner, `corpus/SOURCES.md`, the `corpus/knowledge` directory, and fixture/replay inputs in `MEASURED_PATHS`. Lines 137-143 bind that list (plus optional prior evidence); lines 499-502 compare a second snapshot before record construction/write (lines 503-518). The directory binding is relevant to the count loop at lines 483-497, including the knowledge-file enumeration.
- `census/round-14/run-verification.py:32-46` currently lists the helper, both runner wrappers, frozen fixture directory, source file, and prior r13 evidence. Its start/end binding is at lines 51-79 and 156-169; its command list uses the frozen directory at lines 139-152. `run-targeted.py:15-25` imports the r14 runner and adds the prior attempt to its measured paths; it binds via `resolve_revision` before its checks and performs a final checked snapshot before writing at lines 44-59.
- `census/round-14/cache-demonstration.py:80-89` has a separate `DEMO_MEASURED_PATHS` list including its own source, revision helper, the imported r13 runner, fixtures, and prior r13 result. Its helper and snapshot calls are at lines 198-207; the imported r13 module is loaded at lines 366-391 without invoking the runner suite. This is evidence of the declared bounded inputs, not proof that every possible dynamic/external input is attested.

No omission among the specifically named helper/wrapper/frozen/corpus inputs was found in the current r13/r14 runner lists. This is a static comparison of those lists and visible read/call sites; it does not prove global completeness or establish a fresh refusal receipt.

## One concrete counterexample/oracle refinement

In a temporary copy pinned to the tested revision, add an **untracked**, non-symlink `corpus/knowledge/__oracle_added__.md` whose first three lines satisfy the runner's `source:`, `verified-at:`, and `recheck:` admission-prefix check and which lacks the HELD marker. Invoke the r13 runner and require exit 2 with no result file. This specifically falsifies a path-limited `git diff --quiet`/tracked-only check: the new path is within the declared directory but absent from the committed tree. The current snapshot implementation is statically expected to detect it as an added actual leaf; that outcome was not executed or claimed here.

STATUS: OPEN — this source-only reopen validates S093's quote and its scope, but does not execute the proposed untracked-file oracle or certify all entry-point input inventories; those remain caller-level evidence obligations.

Report: .ufo/waves/round-20/recovery/SourceDiff.md
