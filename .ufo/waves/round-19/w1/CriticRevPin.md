STATUS: DONE — C2 has a real path-coverage gap; the hash friction is bounded, and untracked outputs do not trigger the measured-path check.

# Findings

- **Strongest objection — `run-targeted.py` is not itself bound to its stamped revision.** The r14 targeted runner imports `run-verification.py`, calls that module's `resolve_revision()`, then writes the returned revision into its record (`census/round-14/run-targeted.py:14-28,45-53`). The resolver's `MEASURED_PATHS` includes `run-verification.py` but omits `run-targeted.py` (`census/round-14/run-verification.py:27-39`); the targeted runner's before/after digest list also omits itself (`run-targeted.py:25-29,43-53`). **[INFERENCE — static counterexample, not executed]** If the tracked targeted runner changes while those listed paths remain equal to HEAD, the helper can accept HEAD while the changed orchestrator chooses/runs checks and stamps that older revision. The fixture checks that `run-targeted.py` calls `module.resolve_revision()` but does not check that its own path is in the measured list (`tests/fixtures/r19-rev-pin.py:56-59`). This is a false-provenance hole in the core C2 promise, more serious than the convenience cost.

- **The HEAD/branch objection is real but narrow.** Both count-claims scripts default to `HEAD` (`census/round-13/count-claims.py:10-11`; `census/round-14/count-claims.py:11-12`), while the shared resolver requires a full 40-hex ID and rejects symbolic refs (`tools/souji-rev-pin.py:96-103`). The existing C2 smoke record shows the default invocations exiting 2 and a full-hash invocation succeeding (`census/round-19/c2-smoke.txt:30-40`). This does make an ad-hoc count rerun less convenient. By contrast, the r13/r14 verification runners obtain a full ID from `git rev-parse HEAD` internally before resolving it (`census/round-13/run-verification.py:108-120`; `census/round-14/run-verification.py:42-54`), so a normal branch invocation does not require the user to supply a hash.

- **Historical replay is sufficient for committed history, with a boundary.** The count scripts read the data from the selected commit (`count-claims.py:31-45` in r13; `count-claims.py:32-44` in r14), and use `tree_check=False`; therefore a historical full hash avoids dependence on current worktree bytes. It is sufficient when that commit remains reachable from `refs/heads`, `refs/tags`, or `refs/remotes`. It is not a promise to replay arbitrary orphaned objects or commits reachable only through `refs/jj` (`tools/souji-rev-pin.py:113-128`).

- **Untracked generated outputs do not make a clean post-commit measurement fail this check.** The helper diffs only the explicitly supplied path list (`tools/souji-rev-pin.py:130-147`); r13's new output is supplied separately and written after revision resolution (`census/round-13/run-verification.py:378-407,418-420,470-483`), and r14 writes its `verification.json` after resolving and running checks (`census/round-14/run-verification.py:82-89,115-123`). Those output paths are not in the respective measured-path lists. The r14 demo also explicitly scopes its synthetic dependency bytes to `/var/tmp` rather than claiming they are in the commit (`census/round-14/cache-demonstration.py:76-87`). This does not bind untracked *inputs* omitted from a measured-path list. Separately, r14's fixed target refuses an already-existing `verification.json` (`run-verification.py:82-85`); that is an output/overwrite restriction, not a refusal caused by the measured-byte comparison.

- **Axes:** Operability is harmed modestly by the count-claims default/branch-name friction, and materially by the uncovered `run-targeted.py` false-stamp case until fixed. No calibration or coverage impact is evidenced by this review. The full-hash route preserves reliable replay for retained commits but does not erase these operability costs.

- **Smallest safe correction:** Add `census/round-14/run-targeted.py` to the revision-checked measured paths and assert that inclusion in the fixture; do not relax the full-ID/durable-ref rules. The claim's minimum disclosure should state that count-claims requires an explicit full 40-hex ID reachable from a durable ref, and that tree matching covers only the enumerated tracked paths (not arbitrary untracked inputs or external environment). A convenience invocation can resolve the hash first, e.g. `REV=$(git rev-parse --verify HEAD); python3 census/round-14/count-claims.py "$REV"`.

# Evidence

- Read the r19 preregistration's C2 scope and accepted replay route: `.ufo/waves/round-19/preregistration.txt:33-49`.
- Reviewed worktree source and helper: `tools/souji-rev-pin.py:86-147`; `census/round-13/run-verification.py:88-120,378-420,470-484`; `census/round-14/run-verification.py:27-54,81-123`; `census/round-14/run-targeted.py:14-53`; both `count-claims.py` files; `census/round-14/cache-demonstration.py:76-87`; `tests/fixtures/r19-rev-pin.py:47-68`.
- The smoke file is cited as a recorded local artifact, not as a check rerun by this seat. Its r13 runner refusal says tracked measured paths differ from the named revision (`census/round-19/c2-smoke.txt:42-45`); it is not evidence that an untracked generated output blocks the helper.

# Commands run

None. No tests, executables, shell commands, git commands, or jj commands were run; review used read/search operations only.

# Contract compliance

Wrote only this requested report. No subagents, mutations, installs, network access, or scratch files were used. No protected operator-sweep contents were opened.