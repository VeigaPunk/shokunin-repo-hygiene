author: SoujiR15.GitEnvironment (sentinel, leaf)

# Round 15 · w1 · GitEnvironment: inherited `GIT_*` sanitation and global/system config suppression

Axes: operability and calibration. **I reviewed source only.** I read the committed census at r14 after-hash `69c1604`. The lane HEAD at review time was `cc21683`. The working-tree census sha256 `fcff8b05…69aee9` equals the recorded r14 changed tool, so ConfigRepair had not yet modified it and no r15 fixture existed. Fixture `r14-census-boundary.py` sha256 is `e6a984b1…d14b2`. I also read baseline `a31642d` via `git show`/`git diff`, the installed git 2.55.0 man pages (`git.1.gz`, `git-config.1.gz`, `gitignore.5.gz`, decompressed in Python), and upstream `git.c`/`setup.c` at tag v2.55.0 (raw.githubusercontent.com, accessed 2026-10-20). Findings about the repair are **design-only**: they state the acceptance the repair must meet. I ran no tests and no probes.

## Verified good (keep these)

- `souji-census.sh:119` `compgen -v GIT_` → `unset`. This clears every inherited `GIT_*` shell/env variable, including `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_COUNT/KEY_n/VALUE_n`, `GIT_DIR`-family, `GIT_EXEC_PATH` and `GIT_CEILING_DIRECTORIES`. It is strictly broader than baseline `a31642d:71`, which unset only 4 names.
- `:121-123` re-exports `GIT_OPTIONAL_LOCKS=0`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_SYSTEM=/dev/null`, `GIT_CONFIG_NOSYSTEM=1` and `GIT_TERMINAL_PROMPT=0` *after* the clear, so an inherited hostile `GIT_CONFIG_GLOBAL=<file>` is overwritten.
  - git.1 :1902-1910: "if `GIT_CONFIG_GLOBAL` is set, neither `$HOME/.gitconfig` nor `$XDG_CONFIG_HOME/git/config` will be read".
  - Setting both SYSTEM=/dev/null and NOSYSTEM=1 is redundant but harmless.
- `guard_git_config:500,511` uses `--file "$cfg" --no-includes`. With `--file`, includes default off (S043), and global/command scopes are empty after `:119-123`.

## Findings

### GE-1 · MEDIUM · calibration: the r14 fixture cannot detect the tool's own global/system suppression
- **Evidence:** `r14-census-boundary.py:144-146` and `:370-372` export `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_SYSTEM=/dev/null` and `GIT_CONFIG_NOSYSTEM=1` into **every** tool run, both baseline and changed. No case removes or poisons them. The fixture never sets `XDG_CONFIG_HOME` or `GIT_CONFIG_PARAMETERS` (`GIT_ENV` tuple `:62-70`; `case_06` extra env `:602-609` covers only `GIT_DIR`/`COMMON`/`OBJECT`/`ALTERNATE`/`GIT_CONFIG_COUNT`).
- **Exploit/impact:** delete `:122-123` from the tool and all 12 R14C2 cases still pass. The header claim at `:92` ("Global/system git config … cleared") has no discriminating evidence. FixtureCounts' proposed F15 ("poisoned HOME/.gitconfig") is **vacuous** if it reuses `run_tool`'s env, because the harness already neutralises the poison.
- **Acceptance (L1):** F15-class cases build the tool env **without** the three `GIT_CONFIG_*` suppressors and inject poison:
  - (a) `GIT_CONFIG_GLOBAL=<synthetic file>` with `core.worktree=<synthetic store>`;
  - (b) synthetic `HOME/.gitconfig` plus `XDG_CONFIG_HOME/git/config` with the same key;
  - (c) `GIT_CONFIG_PARAMETERS="'core.worktree'='<store>'"`;
  - (d) `GIT_CONFIG_SYSTEM=<poisoned file>`.

  Pass criteria:
  - Zero store `openat`/`getdents64` on the changed tool, plus an unchanged positive row.
  - Paired red: baseline `a31642d` (which honours all of these) must go red on at least (a), (b) and (c).
  - Mutant red: the changed tool with `:122` removed must go red on (a) and (b).

### GE-2 · MEDIUM · operability (design constraint for ConfigRepair): XDG default ignore/attributes files bypass `GIT_CONFIG_GLOBAL`
- **Evidence:** gitignore(5) :132: the `core.excludesFile` "default value is $XDG_CONFIG_HOME/git/ignore … $HOME/.config/git/ignore is used instead". `GIT_CONFIG_GLOBAL` stops only the *config* files (git.1 :1908). The only neutraliser is the per-call `-c core.excludesFile=/dev/null -c core.attributesFile=/dev/null` on `count_dirty:710-712`. The protected-root set (`:215-267`) does not include `XDG_CONFIG_HOME`.
- **Exploit path:** suppose the repair treats the local `core.excludesFile`/`core.attributesFile` keys value-aware by dropping the `-c` overrides. A synthetic or poisoned `XDG_CONFIG_HOME=<store>` (or `$HOME/.config/git/ignore` symlinked into the store) then makes `git status` open a store file. No guard runs before it.
- **Smallest remediation:** keep both `-c …=/dev/null` on **every** status-class call, irrespective of local-key handling. This is effect-aware and agrees with ExcludesSafe R1-R3 and SimplifyConfig A.
- **Acceptance:** case `XDG_CONFIG_HOME=<synthetic store>` containing `git/ignore` and `git/attributes` gives zero store opens and an unchanged row. Mutant red: the override removed.

### GE-3 · MEDIUM · operability: `GIT_NO_LAZY_FETCH` is stripped and never re-exported
- **Evidence:** `:119` unsets a caller-supplied `GIT_NO_LAZY_FETCH=1`, and `:121-123` do not restore it. git.1 :2122: "tells Git not to lazily fetch missing objects from the promisor remote on demand". This is independently confirmed by PromisorSafe F (census unmitigated) and the probe precedent at `souji-repo-structure.sh:151`.
- **Impact:** a cautious operator's protection is removed. Exporting the variable converts a would-be fetch (network, credential helper, pack write) into a git error. `count_dirty` then prints `unverifiable` (`:716-718`) and `census_one` keeps the row (`:859-861` gives an `error` row). That outcome is per-row, so the repair can drop value-blind promisor refusal without aborting the whole fleet. This directly serves "preserve mixed fleets".
- **Remediation:** add `GIT_NO_LAZY_FETCH=1` to the `:121` export line.
- **Acceptance:** a `blob:none`/`tree:0` `file://` clone row is `unverifiable`/`error`, not clean; no `fetch` execve appears in the trace; unaffected peers stay byte-identical.

### GE-4 · LOW-MEDIUM · calibration: the `guard_git_config` read depends on an unguarded cwd
- **Evidence:** `:500` and `:511` run bare `git config --file …` with no `-C`. `git.c@v2.55.0:559` registers `config` as `RUN_SETUP_GENTLY`, so git runs discovery from the **caller's cwd**. `setup.c:1600-1683` loops over `<dir>/.git` stat, `is_git_directory`, and then reads that repo's format config. git.1 :1611 says `GIT_CEILING_DIRECTORIES` "will not exclude the current working directory".
- **Exploit path:** an operator invokes the census from a cwd under the protected store (or under a repo whose discovery walks store-ancestor `.git` candidates). Every `guard_git_config` call then stats or reads store-side paths. The "before any git … read" claim at `:73-74` covers `--root`/`--compare` only, not cwd. **[INFERENCE]** about realistic incidence; I did not inspect the real store.
- **Smallest remediation:** `git -C / config --file "$cfg" --no-includes …`. `$cfg` is already absolute from `guard_target`.
- **Acceptance:** run the tool with cwd = synthetic store; strace shows zero store `stat`/`openat` (the r14 oracle `open|openat|getdents64` must add `stat|newfstatat|access` for this case).

### GE-5 · MEDIUM · operability (benign-config contraction, not disclosed): global `safe.directory` is lost
- **Evidence:** `setup.c:1431` resolves ownership exceptions only via `git_protected_config`. git-config(1) :783 defines protected scopes as system, global and command, and :10880/10898 say `safe.directory` "is only respected in protected configuration". `:122-123` empties system and global scope, so a foreign-uid repo the operator marked safe (baseline `a31642d:71-73` honoured it) now fails `rev-parse --is-inside-work-tree` and becomes an `error` row (`:859-861`).
- **Impact:** this is a row-level, not a fleet-level, harm, and it is a benign-configuration contraction under the no-trade rule. **[INFERENCE]** about incidence: zero on a single-uid fleet, but unverified.
- **Remediation:** keep global config disabled; SiblingOverlap says operator config must not be read. Then either:
  1. disclose this as an explicit residual requiring operator scope adjudication; or
  2. add an opt-in `--safe-directory PATH` that is forwarded as `-c safe.directory=PATH` (command scope is protected), boundary-checked with `guard_target`.
- **Acceptance:** a foreign-ownership case is not possible without root, so the honest acceptance is a documented residual plus the header text. Do not claim a preservation test.

### GE-6 · LOW · operability/calibration (adjacent; route to the dirty-count owner): `--ignore-submodules=all` hides dirty submodules
- **Evidence:** the r14 change at `:712`; baseline `a31642d:131` honoured default submodule status. A submodule with uncommitted work or new commits now counts 0 dirty. For a cleanup tool this is the fail-unsafe direction. It is disclosed in the header (`:34-35` area), but disclosure does not satisfy the no-trade rule (spotcheck `:7`).
- **Acceptance:** either a paired baseline/changed submodule control with equal dirty counts, or explicit operator adjudication. **[INFERENCE]** `=dirty` mode avoids child processes; this is not verified.

### GE-7 · INFO · calibration of the header wording `:92`
"Every inherited GIT_* variable … cleared" holds for accidental inheritance (hooks, `git -c` aliases, agent env). It does not hold against a caller who controls the environment:
- `BASH_ENV` runs before `:112`;
- an imported `BASH_FUNC_unset%%`/`compgen%%`/`read%%` overrides the builtins used at `:112-119` (bash non-POSIX mode resolves functions first);
- `PATH` is trusted.

That caller already owns `PATH`, so this is not a privilege boundary. Suggested wording: "assuming a non-hostile shell environment". `GIT_EXEC_PATH` clearing could break a relocated git install; this host's pacman git is unaffected **[INFERENCE]**.

## Exact acceptance summary for L1 (unrun)
1. GE-1 cases (a)-(d) on the changed tool: green with zero store access. On baseline `a31642d`: red on (a), (b), (c). Mutant (`:122` deleted): red on (a), (b).
2. GE-2 `XDG_CONFIG_HOME`-poison case: green on the changed tool. Mutant (status `-c` overrides removed): red.
3. GE-3: `grep -n 'GIT_NO_LAZY_FETCH=1' tools/souji-census.sh` ≥ 1. The partial-clone row is not clean, no fetch execve appears, and peers are unchanged.
4. GE-4: cwd-in-synthetic-store case with a stat-inclusive strace filter shows zero store hits.
5. R14C2-01..12 rerun 12/12 on the changed tool (namespace control); benign-config mixed-fleet rows byte-identical to baseline where the semantics are unchanged.

## Process disclosure (boundary violations; not repeated)
- Two early `grep` calls had `path: souji-shokunin` (whole lane root, gitignore-respecting): pattern `GIT_CONFIG|GIT_DIR|GIT_|NOSYSTEM|XDG_CONFIG|HOME` and pattern `value-blind|GitEnvironment`. `census/operator-sweep-20261019/` is untracked, not ignored, so it may have been traversed. No operator-sweep path appeared in the returned output, and none was opened, copied, edited or staged.
- `git --no-optional-locks status --porcelain` was run scoped to `tools tests .ufo/waves/round-15 census/round-15`. This was an index-read query, not the operator sweep.
- `git diff`/`git show` read committed bytes `a31642d`/`69c1604` of `tools/souji-census.sh`. A `sha256sum` of two source files was started, and its result is not used here.
- Upstream git source was fetched read-only from GitHub tag v2.55.0.
- No tests, fixtures, real HOME/auth/agent-store files or separate omp processes. Tool installs/updates: **none**.
