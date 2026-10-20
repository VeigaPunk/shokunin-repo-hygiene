# DirtyFidelity — round 15 w1 critic (operability, calibration)

Status: **design-only against r15**. At review time `tools/souji-census.sh` was unmodified from `cc21683` (`git status` showed no `M` on tools/tests). `tests/fixtures/r15-census-config.py` was absent. The findings below attack the planned repair ("existing status neutralizations count", ConfigRepair prompt) and the r14 tool bytes it starts from. Source inspection plus installed git 2.55.0 man pages only. No tests, fixtures or git status probes on synthetic repos. Every Git-behaviour claim not quoted from docs is marked [INFERENCE].

## Axes
- operability: benign-config repos keep producing the *same row values*, not just exit 0.
- calibration: a preservation claim must have an oracle that can fail when counts drift.

## Definitions (proposed acceptance vocabulary)
- **Exit-only preservation** (insufficient): baseline r14 exits 2 on a benign config and the repair exits 0 with a header and a row. This proves the refusal is gone. It does not prove the old support is back.
- **Meaningful preservation** (required for "no harm"): for each benign control, the repaired row equals a *literal, independently derived* expected row on all 7 columns. `mtime_iso` is pinned by `touch -d`. The expected row must equal the output of the last supported tool, `a31642d` (pre-r14), run on the same synthetic fixture. Each control must also be **effect-sensitive**: it contains a path whose classification depends on the very key under test. So a mutation that neutralizes the key (e.g. `-c key=/dev/null`) must change `dirty` or `verdict_flags` and turn the case red. A control where the key changes no count cannot distinguish "honored" from "neutralized". It is vacuous.

## Findings

### DF-1 HIGH — "neutralized by override" turns refusal into silent count change (excludesFile, attributesFile)
- Evidence:
  - `count_dirty` at `tools/souji-census.sh:710-712` forces `-c core.excludesFile=/dev/null -c core.attributesFile=/dev/null`.
  - Command-line `-c` beats repo-local config: git-config(1) SCOPES `:783` names *command* among protected scopes. That `-c` wins over local is [INFERENCE] from standard precedence.
  - Baseline `a31642d` `count_dirty:131` runs plain `status --porcelain` with no overrides.
  - The guard at `:505` refuses `core.excludesfile` and `core.attributesfile` by key. That is the only reason r14 never reports these repos with a changed count.
- Counterexample 1 (robust, false-dirty). Repo-local `core.excludesFile=<in-repo file>` lists `build/`. `build/` exists, holds only untracked files, and no other ignore source matches it.
  - `a31642d`: dirty=0, `clean`.
  - r14: exit 2.
  - r15 if the key is simply un-banned: `?? build/` → dirty=1, flags `dirty`. `--compare` against a pre-r14 census then exits 3.
  - gitignore(5) `:328`: "Patterns in the exclude file are used in addition to those in $GIT_COMMON_DIR/info/exclude". git-status(1) `:207`: a directory whose contents are all ignored "is not shown".
- Counterexample 2 (false-dirty, needs only a stat change). Repo-local `core.attributesFile` with `*.txt text eol=crlf`. The worktree holds CRLF from checkout and the blob holds LF. The file is touched only: same size, new mtime.
  - Honored: CRLF→LF on rehash, so clean.
  - Overridden: raw CRLF ≠ blob, so ` M` (dirty=1).
  - gitattributes(5) `:134-150`: `text` normalizes line endings to LF in the index on checkin.
  - [INFERENCE] The rehash happens only when stat changes but size does not. A size change short-circuits to modified in both versions, so a control that edits bytes is vacuous for attributes.
- A data-level false-clean via attributes (`-text`/`ident`/`working-tree-encoding` against `core.autocrlf`) needs a same-size change or zero index size. It is [INFERENCE] and convoluted, so it is not claimed here.
- Impacted axes: operability (harmed versus `a31642d`), calibration (an exit-0 oracle would mislabel this as repaired).
- Smallest safe correction:
  - For path-valued keys (`core.excludesFile`, `core.attributesFile`), resolve the effective value with Git's own semantics: last value wins, `~` from the synthetic HOME, relative paths anchored per RelativePaths.
  - Pass the resolved value through `guard_target`, then hand it to status as `-c key=<resolved>`.
  - Fall back to refusal (not `/dev/null`) when the path is protected, so the protected case stays visible.
  - Keep `/dev/null` only for keys with no count effect.
- Count-neutral keys: `core.hooksPath`, since status under `--no-optional-locks`/`GIT_OPTIONAL_LOCKS=0` writes no index and runs no hook [INFERENCE; HooksNeutral owns this]. Also `core.fsmonitor=false`, which only removes a cache [INFERENCE]. These two are the keys where un-banning plus override is real preservation.

### DF-2 HIGH — r14 already changed counts for repos with no refused key; no fixture can see it
`git diff a31642d cc21683 -- tools/souji-census.sh` adds three count-affecting changes that apply to every repo, configured or not:

| r14 change (current line) | a31642d | Effect on `dirty` | Direction |
|---|---|---|---|
| `--ignore-submodules=all` (`:712`) | absent (`:131`) | git-status(1) `:174-178`: `all` will "hide all changes to submodules", including gitlink commit moves | **false-clean** for superprojects with moved or dirty submodules |
| `-c core.excludesFile=/dev/null` (`:711`) | default `$XDG_CONFIG_HOME/git/ignore` honored (gitignore(5) `:132`) | user-global ignores lost; ignored paths become `??` | false-dirty |
| `-c core.attributesFile=/dev/null` (`:712`) | default `$XDG_CONFIG_HOME/git/attributes` honored (gitattributes(5) `:113`) | as in DF-1 counterexample 2 | false-dirty; [INFERENCE] rare false-clean |
| `GIT_CONFIG_GLOBAL=/dev/null` (`:122`) | real global config read | global `core.excludesFile`, `status.showUntrackedFiles`, `core.autocrlf`, `diff.ignoreSubmodules` lost (git(1) `:1902-1915`) | both directions |

- Why r14 missed it:
  - `R14C2-07/08/09/12` (`r14-census-boundary.py:591-626`) run both tools with `GIT_CONFIG_GLOBAL=/dev/null` in the environment (`:370`), so the baseline is pre-sanitized. The tool under test is always the same version.
  - `positive_problems` (`:505-541`) checks a clean repo only (dirty=0, `clean`).
  - No fixture or selftest contains a submodule, an excludes or attributes file, or autocrlf. A grep of the census selftest and the r14 fixture found none.
- Tradeoff, not a plain defect. `R14C2-09` home-store (`:612`, HOME=store) is a verified namespace gain, and it depends on git *not* reading `$HOME/.config/git/{ignore,attributes,config}` or `~/.gitconfig` inside a protected HOME. Restoring the XDG defaults is fixable: guard the resolved path and pass it only when not protected. Restoring global config needs guarding or reading `~/.gitconfig` (it can hold auth settings). That is an operator scope decision.
- Submodule false-clean is fixable: guard submodule gitfiles (the `guard_git_pointer` pattern at `:546`) and drop `=all`. Otherwise disclose it as an unrepaired r14 contraction.
- Smallest safe correction: r15 must either (a) restore each row with paired controls, or (b) list each row explicitly as an unrepaired r14 contraction routed to operator or canonical adjudication. The C1 claim then stays "repository-local config". It must not be stated as "benign configurations preserved".
- Impacted axes: operability, calibration.

### DF-3 MEDIUM — baseline choice can make preservation unfalsifiable
- RoundRunner uses baseline `cc21683`, which is r14 itself. For benign controls r14 exits 2, so "red→green" proves only exit-only preservation.
- The harm the closure judged (`round-14-verifier-spotcheck.md`, C2 no-harm) was measured relative to `a31642d`.
- Correction: the r15 config fixture's benign controls must use literal expected rows. The runner should also execute those controls against an extracted `a31642d` tool in a synthetic HOME and /var/tmp, and require equal rows. Namespace cases do not run against `a31642d`.
- The C2 admission checker must reject evidence where:
  - a benign control asserts only `rc==0` or a header;
  - expected `dirty` or `verdict_flags` are missing;
  - the control has no effect-sensitive path.

### DF-4 LOW — new "safe" overrides must not be added without paired controls
Each of these flags would silently change counts versus local config that `a31642d` honored:
- `--untracked-files=normal|no|all` (local `status.showUntrackedFiles`);
- `-c core.autocrlf=…`;
- `-c filter.<d>.clean=` (neutralizing a clean filter, e.g. LFS or nbstripout). [INFERENCE] This gives false-dirty, and with `filter.<d>.required=true` it gives `unverifiable`.

Rule: any new override in `count_dirty` or `worktree_extra_flags` (`:832` reuses `count_dirty` for `wt-dirty`) needs a paired control proving the count is unchanged, or explicit disclosure.

## Required acceptance (for L1; unrun)
Use synthetic HOME under /var/tmp. For each case, assert the exact 7-column row and `rc`. Run each case on `a31642d` (benign only), `cc21683` and the installed tool.
1. `excl-local`: local `core.excludesFile` that wholly ignores one untracked dir. Expect dirty=0/`clean` on a31642d and the repaired tool; exit 2 on cc21683. Mutation: add `/dev/null` override → red.
2. `excl-xdg`: synthetic `$HOME/.config/git/ignore` with the same effect and no local key. Expect a31642d=repaired, or a disclosed contraction.
3. `attr-local`: local `core.attributesFile` with `*.txt text eol=crlf`, CRLF worktree, LF blob, `touch` only. Expect dirty=0 preserved.
4. `hooks-any`: local `core.hooksPath=<benign dir>` and `=/dev/null`. Expect identical rows on a31642d and the repaired tool.
5. `submodule-moved`: superproject whose gitlink moved. Expect a31642d dirty≥1, or a disclosed r14 false-clean.
6. `excl-protected`: `core.excludesFile` pointing into the synthetic store. Expect refusal, with no store access (strace oracle as in `r14-census-boundary.py:420-470`).
7. A mixed fleet containing 1–3 next to a clean peer. Every peer row is present and exact.

## Process disclosure (boundary reminder received mid-review)
These calls predate L1's no-query reminder and were not repeated afterwards:
- `grep pattern="untracked|ignored|dirty" path=/home/vgpnk/Projects/shokunin/souji-shokunin`: a whole-lane-root search. The operator sweep is untracked, not gitignored, so it may have been scanned. Matches shown came only from `.ufo/` and `w1/` files. No sweep content was displayed or used.
- `git status --porcelain | grep -v operator-sweep` (twice) and `ls census/`. These list or collapse untracked directories, including the sweep path name. No contents were read.
- Also run: `git log`, `git show <rev>:tools/souji-census.sh`, `git diff a31642d cc21683 -- tools/souji-census.sh`, `git --version`, and `zcat` plus `sha256sum` of installed man pages:

| Man page | sha256 prefix |
|---|---|
| gitignore.5 | `d2dd9ca5…` |
| gitattributes.5 | `6b0a4d4c…` |
| git.1 | `8b58cbf7…` |
| git-status.1 | `4aefb916…` |
| git-config.1 | `f75fbd7d…` |

No tests, fixtures, synthetic repos or empirical git behaviour probes were run. No credential, auth or `~/.gitconfig` files were read. Tool installs/updates: none.
