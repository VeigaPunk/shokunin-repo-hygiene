# InputR14Frozen — operability review

## Observed bytes and scope

Observed repository revision: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. The six bounded production files were modified in the worktree at inspection. Relevant captured working-byte SHA-256 values:

- `tools/souji-rev-pin.py`: `0b9018e52553d6517b8f805f07163b6a4093d6e842fa79314876084d7b64f756`
- `census/round-14/run-verification.py`: `45e6896c9b24e45c58a49efed38c0f09e642f0779c60dacf3bd1ab487e9b3502`
- `census/round-14/run-targeted.py`: `2d8c61809a0cb99a4f975f9e0e290bf30ef8cd4f4d7267a6569f759da5df6895`
- `census/round-14/cache-demonstration.py`: `3ad63d5b927fedc3aee70c2b2a13c91ad9c83d7bba9c71c5d85844507ef4213b`

Static source review only; no runner, test, or target code was executed. The LSP device is unavailable (`xd://lsp` returned “No such tool”), so no LSP references/definitions/diagnostics were available. I did not read the frozen fixture files themselves, outside the bounded source list.

## Frozen input binding

The inspected wiring is substantive rather than a marker-only declaration for the frozen fixture subtree: `census/round-14/run-verification.py:32-46` includes the entire `tests/fixtures/r14-cache-frozen` directory, along with the revision helper and runner/wrapper sources. `tools/souji-rev-pin.py:93-178` enumerates committed blobs and actual leaves recursively, rejects nonregular/symlink inputs, and refuses unequal expected/actual maps. The r14 runner snapshots at revision resolution and rechecks against that initial map before writing (`census/round-14/run-verification.py:51-73,150-164`). `run-targeted.py:20-25` adds the prior record to `MEASURED_PATHS` before resolving the revision. These source paths support the claim that a changed/added/removed ordinary file beneath the frozen directory is included in the digest/refusal boundary; they are not fresh execution receipts.

## Finding — moderate, operability: malformed dirty helper misses required refusal exit

**STATUS: OPEN** — The preregistered C2 oracle requires every actual caller to reject a dirty helper with exit 2 and no output. A syntactically invalid dirty helper instead escapes as an uncaught `SyntaxError`, so these callers do not meet the specified refusal contract. In `census/round-14/run-verification.py:54-57`, the revision helper is loaded with `exec_module()` before the `try` that begins at line 60; its `__main__` handler at lines 167-172 catches only `OSError`, `ValueError`, and `RuntimeError`, not `SyntaxError`. The targeted wrapper likewise excludes `SyntaxError` in its handler (`census/round-14/run-targeted.py:62-67`); its top-level r14-runner import is also unguarded (`:16-18`). The cache demonstration loads the helper before its `Refusal` handler (`census/round-14/cache-demonstration.py:194-200`), and invokes this check at `:1137` before its later protected block (`:1150`); its entry point has no conversion of that loader error to exit 2. Thus a simple counterexample is a dirty helper containing invalid Python: loading aborts before the byte comparison, producing Python's uncaught-error exit rather than the required controlled exit 2. No evidence here claims this case was executed.

**Concrete oracle/fix:** add an invalid-helper-byte variant to the dirty-helper refusal oracle for r14, targeted, and cache-demo callers; require exit 2, no output record, and a refusal diagnostic. Catch loader/syntax/import failures at the helper-load boundary and convert them into the same pre-output refusal path. Preserve the existing full snapshot comparison.

## Verification gaps

The frozen subtree contents, actual fixture names, and caller behavior remain unverified dynamically because only the named bounded source files were in scope and all execution was prohibited. No LSP server was available. No tool was installed or updated.