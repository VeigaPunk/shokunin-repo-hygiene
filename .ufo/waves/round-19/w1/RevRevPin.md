STATUS: DONE — Static C2 review complete; six integrity/operability defects remain, while evidence-record writes are preflighted.

# Findings

1. **P1 — Durable-root enumeration rejects valid r17 roots.** `tools/souji-rev-pin.py:32-33,69-75` enumerates only `refs/heads`, `refs/tags`, and `refs/remotes`. The admitted rule is every ref except `refs/jj/*`, explicitly retaining `refs/stash` and `refs/original` (`corpus/knowledge/jj-colocation-receipts.md:35,101`). The round-17 spotcheck rejects the heads/tags/remotes-only rule and identifies `refs/stash` as a durable root (`corpus/lessons/round-17-verifier-spotcheck.md:135`). A commit reachable only through stash/original (or another non-`refs/jj` ref) is therefore refused, contrary to the canonical rule. The helper’s corresponding refusal message also overstates the allowed namespaces (`tools/souji-rev-pin.py:115,123-125`).

2. **P1 — r13’s measured-path list omits most of the frozen fixture it executes.** `census/round-13/run-verification.py:92-105` lists only `tests/fixtures/r13-cert-frozen/expected.json` from that snapshot, while the runner passes the entire directory to `souji-cert-evidence.py --frozen` (`:433`). The frozen validator verifies and reads the manifest, fragments, installed artifacts, and evidence (`tools/souji-cert-evidence.py:110-130`); `expected.json` names hashes for those files (`tests/fixtures/r13-cert-frozen/expected.json:4-11`) and `manifest.json` names both fragments (`tests/fixtures/r13-cert-frozen/manifest.json:1-5`). Changes to those tracked inputs are thus outside the helper’s diff pathspec and can be measured while the stamped revision remains accepted. This is a concrete false pin in `census/round-13/run-verification.py`.

3. **P1 — r14 targeted runner is not among the paths its shared resolver checks.** `census/round-14/run-targeted.py:15-23` imports `run-verification.py` and calls its `resolve_revision()`. That resolver passes the module-level `MEASURED_PATHS` (`census/round-14/run-verification.py:30-39,42-50`), which includes the full runner but not `census/round-14/run-targeted.py`. The targeted runner then stamps that revision into its new record (`run-targeted.py:45-53`). A dirty tracked `run-targeted.py` can therefore produce a record stamped with a revision that does not contain the executable that produced it; its before/after hash list also omits itself (`:25-28,43-49`).

4. **P1 — Helper Git subprocesses can validate a different repository/worktree than `root`.** `_env()` copies the complete process environment and only overrides four variables (`tools/souji-rev-pin.py:45-53`); `_git()` then runs `git -C root` with that environment (`:56-60`). Inherited repository-override variables such as `GIT_DIR`/`GIT_WORK_TREE` are not cleared, so Git can resolve refs and compare bytes against another repository/worktree. This can make the helper accept a revision based on external refs and clean external paths instead of the supplied lane. **[INFERENCE]** This environment-redirection case was reviewed statically, not executed. The fixture strips all `GIT_*` variables before its cases (`tests/fixtures/r19-rev-pin.py:29-36`), so it does not falsify the issue.

5. **P2 — r14 refusal handler raises `NameError` instead of returning the specified exit 2.** `census/round-14/run-verification.py:3-21` does not import `sys`, but its `except module.Refusal` handler evaluates `sys.stderr` at `:50-54`. On a helper refusal that expression raises `NameError` before the intended `SystemExit(2)`. `run-targeted.py:15-23` reuses the same handler through `module.resolve_revision()`. Both preflights remain before record writes, but the failure path is not the promised exit-2 refusal/diagnostic.

6. **P2 — Helper does not verify that supplied measured paths are tracked.** `resolve_durable()` only requires a nonempty list, normalizes each name, and passes the list to `git diff` (`tools/souji-rev-pin.py:110-111,130-147`); it never checks that each name exists in the selected tree/index. An untracked-only or misspelled path can therefore produce a clean diff and allow the revision to pass without comparing the claimed bytes. The fixture covers empty paths and path escape, but not this case (`tests/fixtures/r19-rev-pin.py:164-174,255-264`).


# Assessment

- **Historical 40-hex revisions:** The helper accepts a full commit id only after commit resolution and reachability checks (`tools/souji-rev-pin.py:99-128`); with `tree_check=True`, it compares the supplied tracked paths against the working tree and returns the id only on a clean diff (`:130-147`). Its selftest and fixture source include durable-clean and historical no-tree-check acceptance cases (`:199-203,274-287`; `tests/fixtures/r19-rev-pin.py:164-174`). This is a source review; I did not execute those cases. Acceptance is conditional on the currently enumerated ref namespaces, so the stash/original case above is the exception.
- **Refusal/write ordering:** For evidence records, the preflight precedes writes: r13 calls `resolve_revision()` at the start of `execute()` (`census/round-13/run-verification.py:418-425`) and opens the new output exclusively later (`:482-483`); r14 checks for an existing target, resolves, then writes (`census/round-14/run-verification.py:81-89,115-123`); targeted does the same (`census/round-14/run-targeted.py:19-28,45-53`). The cache demonstration checks the revision before creating its `/var/tmp` output tree (`census/round-14/cache-demonstration.py:1127-1141`). The two count consumers validate before printing their results and do not write evidence files (`census/round-13/count-claims.py:25-45`; `census/round-14/count-claims.py:26-44`).
- **Historical records:** No patched caller source writes an existing historical evidence record. r13 rejects an existing/historical output path and uses exclusive create (`census/round-13/run-verification.py:341-354,482-483`); r14 full and targeted runners refuse an existing output (`census/round-14/run-verification.py:81-85`; `run-targeted.py:19-23`). The counters read the selected revision and print JSON; the cache demonstration uses scratch records and describes historical outputs as read-only (`census/round-14/cache-demonstration.py:7-8,1127-1141`). No runtime execution was performed, so this is a static conclusion.

# Residual risk and verification gaps

- `lsp` is not mounted in the available tool set: reading `xd://lsp` returned “No such tool”. References, definition, and diagnostics requests were therefore unavailable. Source reads and the scoped read-only diff ground this review; grep was used only to locate source lines, not as semantic proof.
- No helper/caller fixture, build, lint, or runtime was run. The conclusions above are static unless explicitly marked `[INFERENCE]`.

# Evidence

- Reviewed worktree bytes against base `3ab2c81` for the helper and all patched C2 callers: `tools/souji-rev-pin.py`, `census/round-13/run-verification.py`, `census/round-13/count-claims.py`, `census/round-14/run-verification.py`, `census/round-14/run-targeted.py`, `census/round-14/cache-demonstration.py`, and `census/round-14/count-claims.py`.
- Reviewed the new fixture source `tests/fixtures/r19-rev-pin.py`, the r13 frozen fixture manifest/expected file, r17’s canonical ref-root rule, and the round-17 verifier spotcheck.

# Commands run

- `git status --short` (read-only).
- `git diff 3ab2c81 -- tools/souji-rev-pin.py census/round-13/run-verification.py census/round-14/run-verification.py census/round-14/run-targeted.py census/round-14/cache-demonstration.py census/round-13/count-claims.py census/round-14/count-claims.py` (read-only).
- `git diff 3ab2c81 -- tests/fixtures/r19-rev-pin.py` (read-only).
- Static file reads, scoped glob, and source-location searches. No tests or other executables were run.

# Contract compliance

- Read `skill://godspeed` and `/home/vgpnk/.omp/agent/RULES.md` first. No tools were installed or updated.
- Wrote only this assigned report. No source, fixture, historical record, or other lane file was edited; no git/jj mutation, network access, signal, or subagent dispatch occurred.
- This is an advisory reviewer finding, not an admission or integration decision.