# AttackRunnerSourceStateLimits — C2 operability

**Axis:** operability

## Low — `source_unchanged` is not a whole-source integrity check

`census/round-21/run-acceptance.py:524-533` defines `source_state` as `HEAD`, bare-repository status, and `git status --porcelain --untracked-files=no`; `:617-623` compares those sampled values and emits `source_unchanged: true` on equality. The independent `replay-matrix.sh:25-31,47` adds a SHA-256 of `git for-each-ref` output, but likewise only records porcelain status with `--untracked-files=no`; that digest is of refs, not source files. `input_sha256_before/after` in the runner cover its explicit input snapshot in the temporary clone, not a digest of the source filesystem.

**Counterexample to treating the flag as whole-source proof:** an ignored or untracked file can be created, removed, or have its contents changed while the status string remains identical; a private subtree is likewise outside the sampled state. If a tracked file is already modified, changing its contents while preserving the same porcelain path/status also leaves this state equal. The runner then can report `source_unchanged: true` even though the source filesystem differs. The pinned `final-matrix.json` itself illustrates that the flag means equality, not cleanliness: S3 records tracked modifications to `SCORECARD.md` and `corpus/README.md` in both snapshots and still reports `source_unchanged: true`.

This is a limit of the evidence/label, **not evidence that the pinned runner changed its source**. Static flow in `run-acceptance.py` clones under `/var/tmp`, runs steps with the clone as `cwd`, and rejects an output inside the source repository. If `source_unchanged` is intended only to mean equality of the listed sampled Git fields, the result is consistent with that limited meaning. It does not establish a full-filesystem no-write guarantee; avoid presenting the flag or the matrix's “source repos never modified” description as that proof.

The output scope text at `run-acceptance.py:635` says “source HEAD/tree not measured.” That is imprecise: HEAD and tracked porcelain status are measured before/after (and the matrix also fingerprints refs), while the complete tree is not. A precise boundary would say that only HEAD/refs/tracked-status are compared and that untracked, ignored, and private filesystem content is not covered. The public-input/private-data wording does not itself claim those excluded files were measured.

## Residual risk and verification gaps

- No full source-tree or filesystem digest is produced; concurrent/external mutations that preserve the sampled fields are not detectable by these fields.
- No concrete source write by the fixed runner was established; assessment is static as required, with no code execution.
- No LSP device is mounted (`read xd://lsp` returned “No such tool”); `git grep` was used only to locate literal references, and conclusions above are based on the pinned `git show` source for `run-acceptance.py`, `replay-matrix.sh`, `step-inventory.json`, `tests/fixtures/r21-replay-boundaries.py`, plus the pinned matrix record.
