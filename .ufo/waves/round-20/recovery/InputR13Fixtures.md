# InputR13Fixtures — scoped operability finding

**STATUS: OPEN.** `tools/souji-rev-pin.py:156-164` walks selected directories with `os.walk(..., followlinks=False)` but supplies no `onerror` handler. Python documents that `os.walk` ignores `scandir()` errors by default ([Python `os.walk` docs, lines 3703-3735](https://docs.python.org/3/library/os.html#os.walk)). If an unreadable nested directory contains a new untracked regular leaf, traversal can silently omit it; because the leaf is absent from both the Git tree’s expected mapping and the incomplete actual mapping, `input_snapshot` can return equality instead of refusal. This breaks the required exact added-leaf check and can let the r13 runner reach its record write with an incomplete snapshot. This is a source-derived counterexample, **not executed**.

## Observed revision and working bytes

Observed `HEAD`: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (the preregistered baseline). All six permitted source files were marked modified in the worktree at observation; these SHA-256 values identify the working bytes read, not the baseline blobs:

| Path | Working SHA-256 |
|---|---|
| `tools/souji-seat-audit.py` | `8f7b16473755215f4f90a85e3c1a9da2e31d47614919fd631866ddf01c31e2c9` |
| `tools/souji-rev-pin.py` | `0b9018e52553d6517b8f805f07163b6a4093d6e842fa79314876084d7b64f756` |
| `census/round-13/run-verification.py` | `a10d66ca6728f641fb4144c7fcfb2996ff1940fd7c6e2f69e30230073a9116e8` |
| `census/round-14/run-verification.py` | `45e6896c9b24e45c58a49efed38c0f09e642f0779c60dacf3bd1ab487e9b3502` |
| `census/round-14/run-targeted.py` | `2d8c61809a0cb99a4f975f9e0e290bf30ef8cd4f4d7267a6569f759da5df6895` |
| `census/round-14/cache-demonstration.py` | `3ad63d5b927fedc3aee70c2b2a13c91ad9c83d7bba9c71c5d85844507ef4213b` |

## Source facts and scope

- r13 declares `tests/fixtures/r13-cert-frozen`, `corpus/knowledge`, and `census/round-13/replay-fragments` as measured paths, along with `tools/souji-rev-pin.py` and `tools/souji-round9-selftest.sh` (`census/round-13/run-verification.py:92-115`). It resolves the helper and snapshots those inputs at start (`:121-141`).
- The runner’s executed selftests are named at `census/round-13/run-verification.py:465-466`; its `dependency_map` also includes the named shell helper for each `*-selftest` result (`:144-156`). The frozen-fixture command is at `:455-456`. Source/admission values read from `corpus/SOURCES.md` and `corpus/knowledge` are also in the measured set (`:479-492`).
- The runner takes a final `input_snapshot`, compares it to the starting map, and refuses before opening the output if they differ (`census/round-13/run-verification.py:493-512`). The map is written as `input_sha256` (`:497-502`).
- `input_snapshot` hashes committed regular blobs and working regular non-symlink leaves, and compares exact mappings (`tools/souji-rev-pin.py:115-174`). However, directory enumeration at `:156-164` silently tolerates `os.walk` traversal errors under its default `onerror=None`; its outer `except OSError` (`:165-166`) cannot catch errors that `os.walk` suppresses.
- Its selftest creates only ordinary top-level files (`tools/souji-rev-pin.py:272-278`); it has no directory-enumeration or traversal-error case. r14 uses the same helper and includes its frozen directory and targeted wrapper in the full-run measured set (`census/round-14/run-verification.py:32-45`), so the traversal gap also affects those selected directories. The targeted runner includes its prior evidence before resolving and performs the final checked snapshot before output (`census/round-14/run-targeted.py:22-25,44-59`).

**Concrete oracle change:** in an isolated synthetic repository, snapshot a selected fixture directory, then add `fixture/unreadable/new.bin` under a nested directory whose `scandir` raises `PermissionError` (or simulate that error in the test). Require the second snapshot to refuse and the caller’s output path to remain absent. This specifically distinguishes complete directory closure from a silently partial walk. Make traversal errors fatal, e.g. supply an `onerror` callback that raises/propagates the error into `Refusal`.

## Limits and remaining unknowns

This review is static source analysis only; no runner, fixture, selftest, build, or target code was executed. I found no omitted r13 helper/frozen-directory entry in the permitted caller sources, but that does not prove runtime closure. The actual `source` statement inside `tools/souji-round9-selftest.sh` was not inspected because that file was outside the allowed read set, so the helper relationship is verified only as declared/referenced by the caller. The `lsp` device was unavailable (`read xd://lsp` returned “No such tool”); regex/source reads are literal fallback evidence, not semantic LSP proof. No tools were installed or updated.