STATUS: DONE — mapped the six current committed r13/r14 sites, their base behavior, test caller, outputs, and measured-byte scopes.

# Findings

## Revision helper and call graph

The current committed bytes are at lane `HEAD` `4f0d500` (the relevant paths were read from the worktree); the cited pre-r19 behavior was separately read from base `3ab2c81` with read-only `git show`.

`tools/souji-rev-pin.py:41-155` provides the shared API: `resolve_durable(root, rev, measured_paths, tree_check=True) -> full 40-hex commit` or raises `Refusal`. It requires a full lowercase commit id, verifies it resolves to itself, requires reachability from `refs/heads`, `refs/tags`, or `refs/remotes` (peeled tags included; not `refs/jj`), and, with the default tree check, requires a nonempty repo-relative path list and `git diff --quiet <rev> -- <paths>` to match the worktree. `tree_check=False` skips only the path/tree comparison and is used by consumers that read exclusively from the selected commit. Its CLI is `--root` (default `.`), `--rev`, repeatable `--path`, `--no-tree-check`, and `--selftest`; usage/refusal exits 2, successful resolution prints the id (`tools/souji-rev-pin.py:296-324`).

Call graph of the current producers:

- `census/round-13/run-verification.py:418-421` → `resolve_revision():108-120` → `git rev-parse HEAD` → imported helper `resolve_durable(..., MEASURED_PATHS)` → `run()` stamps each fresh result and `execute()` stamps the top-level record (`:274`, `:471-483`).
- `census/round-13/count-claims.py:15-31` → imported helper with `tree_check=False` → `git ls-tree`/`git show` at the returned commit → JSON on stdout (`:32-45`).
- `census/round-14/run-verification.py:82-87` → its `resolve_revision():43-55` → helper with its `MEASURED_PATHS`; result rows and the top-level record receive that revision (`:78`, `:116-123`). Its command list also runs the r14 cache demonstration and invokes the r13 runner with no arguments expecting its exit-2 default refusal (`:101-102`).
- `census/round-14/run-targeted.py:15-23,42-53` imports the r14 runner module and reuses `module.resolve_revision()`, `module.run()`, `module.sha()`, `module.ENV`, and `module.BASE`; it does not implement a second resolver.
- `census/round-14/cache-demonstration.py:1094-1150` → `git_head():175-197` → helper with `DEMO_MEASURED_PATHS`; producer executions re-resolve the harness revision and record it in their result (`:439-500`). It invokes the cache gate as a subprocess; temporary results and records live below its unique `/var/tmp` directory (`:388-395,500-573`).
- `census/round-14/count-claims.py:16-32` → imported helper with `tree_check=False` → complete tree listing and commit-pinned `git show` reads → JSON on stdout (`:33-43`).
- The only tests/ text match for these runner/count-claims/helper names is `tests/fixtures/r19-rev-pin.py`. Its CLI is `--tool` and `--tool-dir`; it invokes the helper CLI in a fresh `/var/tmp` sandbox for behavioral cases, then statically reads five consumer files for wiring (`:47-67,110-131,164-190`). It does **not** execute the listed runners or count-claims scripts. Its wiring table omits `census/round-14/cache-demonstration.py`, so that site has no static wiring assertion in this fixture. The fixture writes no fixed result file and removes its scratch tree (`:143-146,220-228`).

## Site-by-site surface and byte scope

1. **r13 verification runner — `census/round-13/run-verification.py`** (`:88-120,315-387,418-483`)
   - CLI: `--round N` and `--output census/round-N/<new>.json` are required; optional `--retry-failed` and `--previous PATH` (default `census/round-13/verification.json`). Missing required arguments refuse with exit 2. Output must be new, lane-contained, in that round directory, `.json`, and outside protected/operator-sweep paths; symlinks, existing files, invalid parents, historical output, and closed rounds are refused. Final creation uses `output.open("x")`, so an existing/racing file is not overwritten (exit 2 on `FileExistsError`).
   - Output: caller-selected `--output`; the prior evidence file is read-only.
   - Revision/tree-check paths (`MEASURED_PATHS`, exactly 12): `tools/souji-verify.sh`; `tools/souji-vault-verify.sh`; `tools/souji-quarantine.sh`; `tools/souji-census.sh`; `tools/souji-cert-evidence.py`; `tools/souji-repo-structure.sh`; `tools/souji-evidence-cache.py`; `tests/fixtures/r13-cert-evidence.py`; `tests/fixtures/r13-repo-structure.sh`; `tests/fixtures/r13-quarantine-bounds.sh`; `tests/fixtures/r13-cert-frozen/expected.json`; `census/round-13/run-verification.py` (`:92-105`).
   - Other path-byte claims: top-level `installed_sha256` is the seven `tools/` paths above (`:422-431,470-474`). Each result also has a dynamic `dependencies` digest map: runner plus existing lane paths named by that result's command (recursively enumerating a named directory); external paths are excluded (`:123-161,264-275`). Thus the fixed helper scope and per-result digest scope are distinct.
   - Base contrast: at `3ab2c81`, `execute()` directly assigned `revision = git("rev-parse", "HEAD")` (base `census/round-13/run-verification.py:384`); no helper/tree/ref check.

2. **r13 claim counter — `census/round-13/count-claims.py`** (`:11-45`)
   - CLI: one optional positional revision; the code defaults to the string `HEAD` when the argument count is not exactly one. The current helper rejects that default, branch names, and abbreviated ids; a full durable 40-hex id is required in practice. Refusal prints to stderr and exits 2.
   - Output: one JSON object on stdout, no output file and therefore no file-overwrite case.
   - Byte scope: it lists the selected commit's paths under `tools/`, `corpus/knowledge/`, and `corpus/SOURCES.md` (`:32`); it reads every `corpus/knowledge/*.md` from that commit and reads `corpus/SOURCES.md` from that commit (`:34-45`). The reported tools/F2 flags are tree-path existence bits, not reads of tool contents. It does not compare the worktree (`tree_check=False`, `:26`).
   - Base contrast: at `3ab2c81`, it defaulted to `HEAD` and ran `git rev-parse <revision>` (`base census/round-13/count-claims.py:11-16`).

3. **r14 full verification runner — `census/round-14/run-verification.py`** (`:31-55,82-123`)
   - CLI: none; `main()` takes no arguments.
   - Output: fixed `census/round-14/verification.json`. It raises `RuntimeError` if the file exists (`:83-85`), then writes with `Path.write_text()` (`:123`). The pre-check refuses an already-existing output, but creation is not exclusive/atomic, so an intervening file could be truncated.
   - Revision/tree-check paths (exactly 8): `tools/souji-evidence-cache.py`; `tools/souji-census.sh`; `tests/fixtures/r14-evidence-cache.py`; `tests/fixtures/r14-census-boundary.py`; `census/round-14/cache-demonstration.py`; `census/round-14/check-timeout-anchor.py`; `census/round-14/run-verification.py`; `census/round-13/run-verification.py` (`:31-40`).
   - Other path-byte claims: `installed_sha256` hashes six worktree paths—the first four above, plus `cache-demonstration.py` and `census/round-13/run-verification.py` (`:87-96,116-120`). It also hashes `census/round-13/verification.json` before/after and records a digest of the baseline `tools/souji-census.sh` extracted from `BASE` (`:90-99,108-121`). **Gap:** the command list executes `tools/souji-evidence-cache.py --frozen tests/fixtures/r14-cache-frozen`, but that frozen fixture path is absent from both `MEASURED_PATHS` and the six-entry `installed_sha256` set (`:31-40,96-103`).
   - Base contrast: at `3ab2c81: census/round-14/run-verification.py:48-60`, the existing-output check preceded `revision = git("rev-parse", "HEAD")`; it stamped that raw value.

4. **r14 targeted runner — `census/round-14/run-targeted.py`** (`:15-53`)
   - CLI: none.
   - Output: same fixed `census/round-14/verification.json`; existing target raises `RuntimeError` (`:20-22`), then `write_text()` writes it (`:53`). As with the full runner, refusal is a pre-check, not exclusive creation.
   - Revision/tree-check set: it calls the r14 module's `resolve_revision()`, so it inherits the eight `MEASURED_PATHS` in item 3. **Gap:** that list includes `census/round-14/run-verification.py` but not `census/round-14/run-targeted.py` itself; the script stamping the revision is not among its own tree-checked paths (`:15,23`; compare module list `run-verification.py:31-40`).
   - Other path-byte claims: its `installed_sha256` is the same six paths as the full runner (`:25-29,43,47`); it also hashes prior `census/round-14/verification-attempt-1.json` and `census/round-13/verification.json` (`:24,43-50`). The baseline census tool is extracted to `/var/tmp` for the fixture but no baseline digest is put in this record (`:29-40,45-52`).
   - Base contrast: at `3ab2c81:census/round-14/run-targeted.py:17-29`, it directly used `module.git("rev-parse", "HEAD")` after its overwrite check.

5. **r14 cache demonstration — `census/round-14/cache-demonstration.py`** (`:76-96,175-197,388-395,439-500,572-573,1089-1199`)
   - CLI: `--gate PATH` (default installed `tools/souji-evidence-cache.py`) and `--keep` (retain the scratch tree). No other arguments.
   - Output: JSON payload to stdout via `emit()`; no lane output file (`:1089-1091`). Its `records/record.json`, phase result JSON files, and synthetic observations are under a unique `/var/tmp/souji-r14-cache-demo.*` directory; cleaned unless `--keep` (`:388-395,500-573,1101-1104,1141`). It has no fixed-path overwrite refusal; each run creates a fresh temporary directory.
   - Revision/tree-check paths (exactly 6): `tools/souji-evidence-cache.py`; `tools/souji-census.sh`; `tests/fixtures/r14-evidence-cache.py`; `tests/fixtures/r14-census-boundary.py`; `census/round-14/cache-demonstration.py`; `census/round-13/run-verification.py` (`:80-87`). Producer/result records carry the resolved harness revision; their `measured_commit_scope` explicitly excludes synthetic `/var/tmp` dependency bytes (`:479-498,527-529,993-995`).
   - Base contrast: at `3ab2c81`, `git_head()` required a 40-hex `rev-parse --verify HEAD` result but returned it without durable-ref or tree comparison (`base census/round-14/cache-demonstration.py:160-182`).

6. **r14 claim counter — `census/round-14/count-claims.py`** (`:12-43`)
   - CLI: same optional positional revision / `HEAD` default behavior as r13; current helper refuses the default, so an explicit full durable 40-hex id is needed. Refusal exits 2.
   - Output: JSON on stdout only, no output file and no overwrite case.
   - Byte scope: `git ls-tree -r` inventories the entire selected commit (`:33`); it reads `corpus/SOURCES.md` and every `corpus/knowledge/*.md` from that commit (`:34-38`). Cache-gate and fixture fields are path-existence bits from the tree listing (`:39-41`); no tool/fixture contents are read. No worktree check (`tree_check=False`, `:27`).
   - Base contrast: at `3ab2c81`, it defaulted to `HEAD` and resolved it with `git rev-parse` (`base census/round-14/count-claims.py:11-16`).

**Adjacent field hits:** a lane-wide search also found `tools/souji-evidence-cache.py:876-880` and `tools/souji-preservation-evidence.py:1140-1144`. These validate/copy a `measured_commit` supplied in an input record; neither chooses a default revision or resolves/stamps a fresh commit, so they are not additional producer sites in this map.

## Minimal shared API

The minimal cross-site API is `resolve_durable(root, rev, measured_paths, tree_check=True)` plus the `Refusal` exception (`tools/souji-rev-pin.py:41,86-155`). Tree-measuring runners supply their exact path list and use the default `tree_check=True`; commit-only counters pass `[]` and `tree_check=False`. `durable_tips()` is helper internals, not needed by consumers. Existing wrappers (`resolve_revision()` and `resolve_claims_revision()`) provide each script's local CLI/error policy; targeted r14 correctly reuses the full runner's wrapper.

# Evidence

- Current committed source read from worktree at `HEAD 4f0d500`; relevant source references are given above. Base behavior was read with `git show 3ab2c81:<path>` for each item-cited site, including the base lines named above.
- Test search found only `tests/fixtures/r19-rev-pin.py` for these script/helper names; it has five `WIRING` entries and does not include cache-demonstration (`:47-67`). The fixture exercises helper CLI behavior, not producer outputs.
- No test, runner, selftest, or fixture was executed for this scouting task; behavior beyond source-level control flow is not claimed.

# Commands run

- Read the godspeed skill and `.ufo/waves/round-19/preregistration.txt`.
- Read the named r13/r14 scripts, `tools/souji-rev-pin.py`, and `tests/fixtures/r19-rev-pin.py`; searched `census/`, `tools/`, and `tests/` for revision fields, runner names, and callers.
- Read-only `git log --oneline -4`, `git status --porcelain`, and base excerpts via `git show 3ab2c81:<path>` for the cited revision sites.
- No behavioral commands or checks were run.

# Contract compliance

- Wrote only this assigned report; no other files were changed. No subagents, git/jj mutations, network access, process signals, or scratch directories were used. The operator-owned `census/operator-sweep-20261019/` path was not opened or touched.
- No tools were installed or updated.