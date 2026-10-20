# IncludeEscape — round 15 w1 (sentinel, source inspection)

Scope: can an include path or include condition make git reach the synthetic protected namespace before the census path guard runs? Covers recursion, symlinks, and hardlinks.
Axes: operability, calibration.

## Status: design-only against the repair

The repair has not landed. `tools/souji-census.sh` is unchanged from HEAD: mtime 04:56:30, 55730 B, and `git diff --stat` is empty when checked at write time. The code reviewed below is the round-14 key-only guard at `tools/souji-census.sh:493-522`. Every finding about the repair states the acceptance it must meet.

Primary sources: git v2.55.0 (the installed version, `git 2.55.0-1`), fetched from raw.githubusercontent.com/git/git/v2.55.0 into /var/tmp and deleted afterwards:
- `config.c:135-190` `handle_path_include`, `MAX_INCLUDE_DEPTH 10`
- `config.c:199-295` condition patterns and `include_by_gitdir`
- `config.c:297-414` `onbranch` and `hasconfig`
- `config.c:416-448` `git_config_include`
- `config.c:1307-1327` `git_config_pathname`
- `config.c:1563-1600` repo and worktree config load
- `path.c:698-737` `interpolate_path`
- `exec-cmd.c:290-299` `system_path`
- `setup.c:859-869` `read_repository_format`

I also read the installed `git-config(1)` man page.

## Current guard (round 14): no escape, but over-refusal

Any key matching `*include.*|*includeif.*` is refused before the first git call that loads config with includes. `guard_git_config` runs at `:613/:628/:650/:665/:581`, and all of them sit inside `guard_git_surface`. That function runs before `rev-parse` (`census_one:847` → `:859`) and before the worktree `count_dirty` (`:831` → `:832`). The value reads at `:500` and `:511` use `--no-includes`.

So the round-14 tool has no include escape. The cost is operability:
- **R0 (low, operability).** The case is a substring match over the newline-joined key list. It also refuses unrelated keys such as `remote.include.url`, `branch.include.merge`, and `foo.includeif.bar` (`:505`). This is already noted in round-14 BoundaryReviewRoot F-D.

## Findings that bind the repair

### I1 HIGH — recursive closure; relative base must match git byte-for-byte
**Exploit path.** `.git/config` contains `include.path=shared.inc`, which is benign and inside the gitdir. `shared.inc` contains `include.path=/S/home/.omp/agent/auth.json`. A guard that checks only the top-level values passes. `git rev-parse` then calls `access_or_die(path, R_OK, 0)` (`config.c:177`) and opens the store file (`:183`).

**Evidence.** `git_config_include` recurses through every included file (`config.c:183` passes `git_config_include` as the callback). This was observed in round 14 at `w1/BoundaryAttack.md:41` (E6: `openat(... auth.json, O_RDONLY)`).

**Base rule.** A relative include is `dirname(kvi->filename)` string-concatenated with the value (`config.c:170-174`). The base is the literal path string git opened, not its realpath. The kernel then resolves the result physically.

Consider a guard that canonicalises an included file first and takes the dirname of the canonical result. When `shared.inc` is a symlink, that guard computes a different base for the nested include than git does. The guard checks one path while git opens another.

**Smallest remediation.**
1. Run a worklist from each guarded config: `--no-includes` value read, `--null`.
2. Interpolate the path as git does (see I3).
3. If the result is relative, prefix the unresolved dirname of the including file's literal path string.
4. Resolve with `guard_target` (physical walk, protected check per component, 40 hops; `:337-411`). Do not use `guard_path`: it refuses `..`, and `../shared.inc` is a legitimate include.
5. Check the file type (see I5), then queue the file's own include values. Carry the literal joined string, not the resolved path, as the next base.
6. Bound the depth at 10. Git itself dies above 10 (`config.c:178`), so refusing depth > 10 costs nothing. Cycles end at the bound.

**Acceptance.** These cases exit 2 with zero store access: nested include at depth 2 and depth 10; include through a symlinked include directory, then a relative `../`; cycle A→B→A. Depth-1 and depth-3 benign relative includes produce identical rows.

### I2 HIGH — never skip a disabled includeIf; `hasconfig` opens every hasconfig include
**Exploit path 1.** Config holds `[includeIf "hasconfig:remote.*.url:https://nomatch/**"] path=/S/.omp/agent/x`. The condition looks false. But the first time git evaluates any `hasconfig` condition, `populate_remote_urls` rereads the whole config with `unconditional_remote_url = 1` (`config.c:340-351`). During that scan, `include_by_remote_url` returns 1 for every hasconfig condition (`:388-389`). Every hasconfig `path` is therefore opened, matching or not.

**Exploit path 2.** `gitdir:` uses the realpath of the current gitdir (`config.c:254`, retried with the absolute path at `:277-289`). For a linked worktree, that gitdir is the worktree admin dir, not the main gitdir (man page: "the final location where the .git directory is"). `onbranch:` uses each worktree's HEAD (`:308-320`). Status runs per worktree (`:831-832`). A guard that evaluates the condition once against the main repo misjudges the shared config read from each linked worktree.

**Safe direction.**
- Unknown conditionals are false (`config.c:412-413`).
- An `includeIf` without a subsection is ignored (`:436-437`, `cond` must be non-null).
- Only key `path` includes (`:438`).

**Smallest remediation.** Boundary-check every `includeif.<cond>.path` unconditionally, including unknown conditions. Never evaluate conditions for the safety decision. A disabled condition pointing at a benign path still produces a row; only protected or unreadable targets refuse. This keeps harmless disabled conditions green, which IncludeCycle and IncludeIfSafe also want.

**Acceptance.** Exit 2 with no store access for:
- non-matching `hasconfig` → store, plus a matching hasconfig elsewhere in the closure
- `gitdir:` that matches only the linked-worktree admin path → store
- `onbranch:` for the linked worktree's branch → store

A non-matching `gitdir:`/`onbranch:` to a benign file stays green.

### I3 HIGH — value interpolation must be git's, not a reimplementation of `:(optional)`
`include.path` uses `interpolate_path` (`config.c:153`), not `git_config_pathname`. So `:(optional)` is NOT stripped for includes; the strip exists only at `config.c:1316`. `:(optional)/S/.omp/agent/x` is therefore a relative path `<cfgdir>/:(optional)/S/...`.

A guard that strips `:(optional)` checks one path and git opens another. Today that is a harmless miss, but it is wrong in both directions.

Expansions that git does perform (`path.c:706-733`):
- `%(prefix)/rest` becomes `system_path(rest)`. If `rest` is absolute, it is returned verbatim (`exec-cmd.c:294-295`). So `%(prefix)//S/.omp/agent/x` means `/S/.omp/agent/x`, and `%(prefix)/../../S/...` climbs out of the prefix.
- `~/` uses `$HOME` (not realpath, `real_home=0`). If HOME is unset, the result is NULL and becomes an error at `config.c:154-155`.
- `~user/` uses `getpwnam`.

`HOME` is inherited because only `GIT_*` is scrubbed (`:119`).

**Smallest remediation.**
- Expand `~/` with the same `$HOME` git will see. Refuse when HOME is unset.
- Refuse `~user/`, `%(prefix)/` and any value starting `:(`. They are rare in benign repo config, and `RUNTIME_PREFIX` is unknown from source.
- Refuse empty values: they resolve to the config's own directory, an EISDIR read.
- Refuse values containing NUL, newline, CR or tab.
- Enumerate with `git config --file F --no-includes --null --list` and split on NUL. A `--name-only` plus `--get` pair is not enough: the include key may be repeated, and subsections may contain spaces and dots.

**Acceptance.** These exit 2 with no store access: `~/` and `%(prefix)//` → store; `%(prefix)/../..` → store; HOME unset with `~/x`; `:(optional)` prefix; two `include.path` values where only the second is protected. `~/benign.inc` under synthetic HOME stays green.

### I4 HIGH — effective-config divergence: unsafe keys can arrive through a benign include
Today every unsafe-key check reads only the top file with `--no-includes` (`:500`, `:511`). Once includes are admitted, a benign `shared.inc` can define keys that no check sees:
- `filter.x.clean`: status runs clean filters, and there is no `-c` override for filters (`:710-712`). Round 14 showed `LEAK via clean filter`, which `core.fsmonitor=false` does not stop (`BoundaryAttack.md:131`).
- `core.alternateRefsCommand`, `remote.*.promisor`, `extensions.*`.

**Partial mitigation (the second half is [INFERENCE]).**
- `extensions.*` and the setup-time `core.worktree` come from `read_repository_format`, which calls plain `git_config_from_file` (`setup.c:863`) and does not follow includes.
- `-c core.hooksPath/excludesFile/attributesFile/fsmonitor` overrides on status win over file values.
- [INFERENCE] Whether a later include-aware `core.worktree` read (`setup.c:595`, `check_repository_format_gently`) can override setup is unverified. Treat it as reachable.

**Smallest remediation.** Run every value-aware unsafe-key decision over the union of all guarded files in the I1 closure, after their paths pass. Run each check per file with `--no-includes`. Never use a git include-following read for the decision.

**Acceptance.** These exit 2 or are neutralised, with no execution or store access:
- `shared.inc` defines a `filter.x.clean` command, plus `* filter=x`
- `shared.inc` sets `core.worktree` → store
- `shared.inc` sets `core.alternateRefsCommand`

A `shared.inc` containing only `user.name` stays green.

### I5 MEDIUM — include target type and hardlinks
`guard_git_files` checks nlink and nonregular files only for fixed names (`:477`). An include target can be:
- A FIFO: git opens it and blocks; the tool hangs.
- A directory: the read fails, so the result is inconsistent.
- A regular file whose inode is hard-linked to a store file: the name is benign and the path guard is blind to it.

`stat -L` after `guard_target` follows the symlinks already vetted, so it is safe to run.

**Smallest remediation.** After `guard_target`, require a regular file (`-f`, not `-p/-S/-b/-c/-d`) with `nlink == 1` (`stat -L -c %h`). Otherwise refuse with exit 2: `git-config-include-nonregular` or `-hardlink`.

**Residual.** As at `:95-99`, guard and open are not atomic. A file outside the fleet can be replaced between check and git's read. Disclose this in the header; it is not fixable in bash.

**Acceptance.** FIFO include → exit 2 within the timeout. Hard-linked include with nlink 2 → exit 2.

### I6 MEDIUM — no recursive delegation before the guard
Any `git config --includes`, `--show-origin`, `git -C repo config ...`, or `git config --get` without `--file F --no-includes` resolves includes inside git before the walker runs. That reproduces I1 inside the guard itself.

**Static acceptance (L1).** Every `git config` in `tools/souji-census.sh` matches `--file .* --no-includes`. `grep -nE 'git( -C [^ ]+)? config' tools/souji-census.sh | grep -v -- '--no-includes'` must be empty. `grep -n -- '--includes\b\|--show-origin' tools/souji-census.sh` must also be empty.

### I7 LOW — config.worktree is outside the guard
When `extensions.worktreeConfig` is true, git reads `$GIT_DIR/config.worktree` (`config.c:1565,1593-1597`). That file, and its includes, are not in `guard_git_files` (`:477`) and are not passed through `guard_git_config`. Round 14 refuses the extension outright, so this is moot today.

**Acceptance if the repair admits a false or true `worktreeConfig`.** `config.worktree` gets the same symlink, nlink and regular-file checks and the I1–I4 closure, for the main gitdir and each worktree admin dir. A `config.worktree` with `include.path` → store must exit 2.

### I8 LOW — key parsing
- Section and key names are case-insensitive, and git lowercases them. `includeIf` subsections are case-preserving and may contain `.` and spaces.
- `include.path` is exact (`config.c:433`). `include.<sub>.path` is NOT an include.
- The repair should match these exact shapes on `--null` output and replace the substring case at `:505`. This also fixes R0.

**Acceptance.** `remote.include.url` and `include.foo.path` → identical rows (green). `INCLUDE.PATH` and `IncludeIf.GitDir:/x.Path` → treated as includes.

## Messages
I sent a summary of I1–I4 to SoujiR15.

## Boundary disclosure
- My first discovery call was an unscoped `grep pattern=include path=/home/vgpnk/Projects/shokunin/souji-shokunin`, with output capped at 20 files. All 20 displayed results were `.ufo/waves/*`. The search itself traversed the lane root, which could include `census/operator-sweep-*`. I did not open, quote, or rely on any operator-sweep content.
- I also ran `git status --short | grep -v operator-sweep`, which lists untracked paths.
- Both calls happened before the SoujiR15 boundary reminder. I did not repeat them.
- No tests, probes or runtime checks were run against the tool or git behaviour. The git semantics above come from primary source and the man page only.
- External fetch: `curl` of five git v2.55.0 source files into /var/tmp. They have been removed.

## Tool installs
None.

## Unrun checks (for L1)
The acceptance cases in I1–I5, I7 and I8 under the round-14 strace and mode-000 store fixture pattern, plus the I6 static greps. Run them after `tools/souji-census.sh` changes and in `tests/fixtures/r15-census-config.py`.
