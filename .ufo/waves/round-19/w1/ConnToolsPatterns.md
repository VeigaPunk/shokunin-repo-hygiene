STATUS: PARTIAL — caller map is complete; a root census listing expanded operator-sweep child names, disclosed under Contract compliance.

# Findings

## Duplicate caller logic

1. **Current-worktree pin adapter appears three times.** The r13 and r14 verification runners each dynamically load `tools/souji-rev-pin.py`, resolve `HEAD`, call `resolve_durable(...)` with a runner-specific measured-path list, and translate `Refusal` to exit 2 before recording (`census/round-13/run-verification.py:88-120`; `census/round-14/run-verification.py:27-54`). The cache demonstration has the same sequence in `git_head()`, but adds a 30-second `rev-parse` timeout and returns `(None, error)` rather than exiting (`census/round-14/cache-demonstration.py:175-197`). Its measured-path list is a different scope (`:80-87`), so share the pin operation, not the path data.

2. **Snapshot-only pin adapter appears twice.** Both claim counters duplicate dynamic import, `resolve_claims_revision()`, `resolve_durable(root, value, [], tree_check=False)`, and `Refusal` → stderr/exit 2 (`census/round-13/count-claims.py:15-31`; `census/round-14/count-claims.py:16-32`). These counters read from the selected commit itself, so the no-worktree-diff mode is intentional, not a missing tree-check.

3. **One caller delegates rather than duplicates.** `census/round-14/run-targeted.py:14-28` imports the r14 runner and calls its `resolve_revision()`; it has no separate durability implementation. It records a smaller before/after artifact digest set than the runner's pin scope (`:25-28`), so those two scopes must not be conflated.

## Narrow helper interface

The helper already centralizes the actual policy: `DURABLE_NAMESPACES` is exactly `refs/heads`, `refs/tags`, `refs/remotes`; `durable_tips()` enumerates only those namespaces; `resolve_durable(root, rev, measured_paths=None, tree_check=True)` enforces a full 40-hex SHA, durable reachability, and (by default) the measured-path tree comparison (`tools/souji-rev-pin.py:32-38,69-147`). Keep this strict explicit-SHA core; do not teach it to accept arbitrary branch names or `HEAD` as a durable ref.

For ExecRevHelper, the narrow caller-facing contract should name the two real modes:

- **Worktree pin:** obtain the current `HEAD` SHA and call the core with that SHA plus the caller's measured paths; return the SHA or raise `Refusal`.
- **Committed-snapshot pin:** accept an explicit full SHA and call the core with tree checking disabled; return the SHA or raise `Refusal`.

These can be named thin entrypoints over the existing core (for example `pin_worktree(root, paths)` and `pin_snapshot(root, sha)`). The runner wrappers, demonstration, and counters then retain their own error mapping: runner/counter refusal is exit 2, while the demonstration records an error result. Preserve the demonstration's timeout/error-as-data behavior if moving its `HEAD` lookup into the helper. Do not centralize or union the measured-path lists: their measurement scopes differ.

## Similar-looking logic that must stay separate

The active `souji-verify.sh`, `souji-vault-verify.sh`, and `souji-quarantine.sh` also enumerate refs while excluding `refs/jj` (`tools/souji-verify.sh:60-78,865-875`; `tools/souji-vault-verify.sh:40-60,1070-1080`; `tools/souji-quarantine.sh:112-126,1186-1195`). Their absent-worktree metadata-prune rule treats **every** ref except `refs/jj/*` as a root, including `refs/stash` and `refs/original`. The r19 helper is intentionally narrower: only heads/tags/remotes are valid roots. Sharing the helper's namespace policy with those shell tools would change their established contract; these are a semantic near-match, not C2 duplicates.

## Risk / second-order effect

The shared tree check currently invokes `git diff --quiet <rev> -- <paths>` (`tools/souji-rev-pin.py:136-146`) while its environment sets `GIT_OPTIONAL_LOCKS=0` (`:45-53`). A repo-local G2 candidate records that this exact diff form rewrote `.git/index` for a stat-dirty tracked entry even with optional locks disabled, and distinguishes `diff-index`/`--no-optional-locks` forms as non-writing (`tools/cand-g2-verify.sh:810-816`). This is source-recorded evidence, not a reproduction against the new helper. It makes the shared checker a read-only/operability risk that should be falsified before treating helper reuse as a read-only guarantee.

Affected axis: **operability** (one explicit pin contract can eliminate caller drift). No numeric axis delta is claimed. No direct calibration or coverage effect is established. The API consolidation must not change the strict namespace policy, caller-specific measured paths, or each caller's failure/output behavior.

# Evidence

- Round-19 C2 declares the durable namespaces, tree-byte check, exit-2/no-record refusal, and historical explicit 40-hex replay contract (`.ufo/waves/round-19/preregistration.txt:33-49`).
- Core helper policy and modes: `tools/souji-rev-pin.py:32-38,69-147`.
- Duplicate runner adapters and their distinct path scopes: `census/round-13/run-verification.py:88-120`; `census/round-14/run-verification.py:27-54`; `census/round-14/cache-demonstration.py:80-87,175-197`.
- Shared/transitive and snapshot-only callers: `census/round-14/run-targeted.py:14-28`; `census/round-13/count-claims.py:15-31`; `census/round-14/count-claims.py:16-32`.
- Distinct shell ref-root policies and diff side-effect warning: paths/lines in Findings above.

# Commands run

- Read the round-19 preregistration, helper, and named r13/r14 callers; searched `tools/` and the r13/r14 census source directories for `rev-parse`, `symbolic-ref`, `for-each-ref`, `refs/jj`, `resolve_durable`, and tree-diff patterns.
- No shell commands, fixtures, tests, or runtime checks were executed. No tools were installed.

# Contract compliance

- Read-only investigation; wrote only `.ufo/waves/round-19/w1/ConnToolsPatterns.md`.
- No subagents, git/jj mutations, live census, process signals, or network access. No file under `census/operator-sweep-20261019/` was individually read or searched.
- Boundary incident: reading the `census/` directory listing also displayed child names and metadata from `census/operator-sweep-20261019/`. No file contents from that directory were read, and no changes were made there.
