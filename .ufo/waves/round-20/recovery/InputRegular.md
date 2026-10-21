# Input regularity and bounded-directory review

## Axes

- **Operability:** one open fail-closed directory-scope finding below.
- **Calibration:** not evaluated in this item.

## Observed source identity

Static inspection observed lane HEAD `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. Working-byte SHA-256 values at inspection:

- `tools/souji-rev-pin.py`: `0b9018e52553d6517b8f805f07163b6a4093d6e842fa79314876084d7b64f756`
- `census/round-13/run-verification.py`: `a10d66ca6728f641fb4144c7fcfb2996ff1940fd7c6e2f69e30230073a9116e8`
- `census/round-14/run-verification.py`: `45e6896c9b24e45c58a49efed38c0f09e642f0779c60dacf3bd1ab487e9b3502`
- `census/round-14/run-targeted.py`: `2d8c61809a0cb99a4f975f9e0e290bf30ef8cd4f4d7267a6569f759da5df6895`
- `census/round-14/cache-demonstration.py`: `3ad63d5b927fedc3aee70c2b2a13c91ad9c83d7bba9c71c5d85844507ef4213b`

These identify the inspected working bytes; this is source analysis only, not a claim that the files are committed at HEAD. No source/target code was executed, and no tests or validators were run.

## Counterexample and evidence

`tools/souji-rev-pin.py:100-112` rejects absolute paths and `.`/`..`, but its protected-census predicate applies only when `parts[0] == "census"` **and** `len(parts) > 1`. Consequently `paths=["census"]` passes validation. At `:145-159`, a selected directory is then recursively traversed by `os.walk(..., followlinks=False)`; the loop checks symlinked child directories but neither bounds the traversal nor rejects/prunes protected directory names before descent. Thus this accepted input would walk the census subtree, including `census/operator-sweep-20261019/` if present. This is a static conditional counterexample; I did not call the helper or inspect/list/traverse that protected tree.

The currently inspected caller lists are narrower: round 13 `run-verification.py:92-112`, round 14 `run-verification.py:32-46`, `run-targeted.py:22-29`, and `cache-demonstration.py:80-89` do not pass the `census` root. I observed no current caller making this broad selection; the finding is that the shared helper does not enforce the promised bounded-directory contract for its accepted inputs.

For stable paths, the leaf checks are directionally correct in source: `:133-143` checks path components for symlinks, opens with `O_NONBLOCK | O_NOFOLLOW`, and verifies `fstat` says regular before hashing; `:148-159` refuses a selected symlink or non-regular leaf, and explicitly refuses symlinked child directories. These are source observations, not fresh behavioral receipts for symlink/FIFO/device cases. No historical receipt was used as fresh execution evidence.

## Finding

**STATUS: OPEN —** `input_snapshot` accepts a broad `census` directory root and recursively walks it, so its public path validation does not keep directory scans bounded or keep traversal out of the expressly protected census subtree. This is a helper-level operability/scope defect; it is not evidence that any current runner selected that root.

Smallest safe correction: fail closed on directory roots that are not an explicitly permitted bounded set (at minimum reject `census` itself and any selected ancestor that can contain the protected subtree), and refuse a protected directory encountered before recursive descent. Add a synthetic-tree oracle where `paths=["census"]` must be refused before enumerating a nested `operator-sweep-*` fixture; do not run that oracle against the real protected tree. Keep current caller lists as bounded paths. No installation or mutation outside this report was performed.