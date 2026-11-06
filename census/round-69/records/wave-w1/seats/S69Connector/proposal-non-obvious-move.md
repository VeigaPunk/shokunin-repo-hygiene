# UFO-FSD Connector Proposal: Subdirectory-Rooted Index Scope (Closing D29 Limit)

## 1. Evidence
- Round 69 frozen claims freeze two named limits in `census/round-69/preregistration.txt:99-105` and `census/round-69/battery-limits.tsv`: D18 (`GIT_OPTIONAL_LOCKS=0`) and D29 (`:(top)` pathspec). Both mutants survived across all 47 matrix rows (`controls/d18-limit-battery.txt`, `controls/d29-limit-battery.txt`).
- Analysis of `tools/souji-receipt-write.py:118`:
  `_index_stages(top)` invokes `git(top, "ls-files", "-s", "-z", ":(top)")`. Because `top` is the resolved repository toplevel, the subprocess working directory is `-C top`. Therefore, `:(top)` operates from the root of the repository, making the `:(top)` magic prefix a no-op that cannot be observed or killed by any single-edit mutation in `tools/souji-receipt-write.py`.
- Analysis of `census/round-69/c1-counter.py`:
  Counter C2 establishes ambient immunity by scrubbing `HOME`, `XDG_CONFIG_HOME`, `GIT_TRACE*` in `clean_env()`, but `tools/souji-receipt-write.py:99` only scrubs `GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR` in its `git()` helper, leaving `GIT_TRACE*` unscrubbed in production executions.

## 2. Affected Axes
- **coverage** (score 8): improves by converting named limit D29 into an actively refuted mutant, moving covered protections from 12 to 13 of 14 declared items.
- **operability** (score 8): improves by aligning `tools/souji-receipt-write.py:git()` environment scrubbing with counter C2 `clean_env()`, eliminating trace stream leakage.
- **calibration** (score 7): harmed none; preserves 47-row matrix outcomes and Q131 split.

## 3. Proposed Move (Bounded for Round 70)
1. **Subdirectory-Rooted Index Invocation:**
   In `tools/souji-receipt-write.py`: change `_index_stages(top)` to `_index_stages(root, top)` and call `git(root, "ls-files", "-s", "-z", ":(top)")`. When `--root` points to a subdirectory of the worktree, `:(top)` is strictly required to observe the full repository index.
2. **Matrix Row for Subdirectory Index Concealment:**
   Add a test row to `c1-matrix.tsv` where the candidate is invoked from a subdirectory while an unmerged or concealed entry exists in a parent/sibling directory. The D29 mutant (dropping `:(top)`) will fail to observe the index entry and emit a forgery, killing D29.
3. **Plumbing Hygiene Parity:**
   In `tools/souji-receipt-write.py:git()`, add `--no-optional-locks` to the CLI argument vector (matching `mori-shokunin` and `kengaku-shokunin`) and scrub `GIT_TRACE*` variables.

## 4. Risks & Contradictions
- Low risk: Calling `git(root, ...)` requires that `root` is a directory within the repository worktree, which is already validated by `_toplevel(root)` at line 281.
- Contradiction avoided: Does not weaken or modify frozen round 69 code or contracts.

## 5. Verification
- Under the subdirectory matrix row, D29 mutant produces `outcome=forgery`, verified by `python3 -B census/round-69/c1-counter.py`.
- `declared-coverage.tsv` updates D29 disposition from `limit` to `mutant`, achieving `covered=13 limits=1`.
