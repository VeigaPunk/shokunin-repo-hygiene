# CriticNoHarmPreharm — round 16 C1, no-harm check against pre-harm a31642d

Seat: critic (leaf). Axis: **operability**, with safety as the constraint. This is a code-reading critique backed by git docs and source. I ran no census and no fixture, so every behavioural claim below comes from reading code paths. Each one is marked as a code-path claim or as `[INFERENCE]`.

Revisions: pre-harm `a31642d:tools/souji-census.sh` and changed `cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh`. Line numbers below are cbf688a line numbers unless they are prefixed `a31642d:`.

## Verdict

The C1 claim "only a protected-namespace reach keeps whole-run exit 2" is **false at cbf688a**. Several git layouts reach no protected path, yet they still kill the whole run, drop a row with no notice, or change counts with no flag. On each of these layouts a31642d gave a usable, accurate row.

- Every structural item below came in with r14 commit `48f8945`. Evidence: `git log -S` on `git-metadata-symlink" "$dir" "$link"`, on `--ignore-submodules=all` and on `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM`. r16 repaired only the config-key slice (R2) and left these in place.
- The counting command cannot see any of them. Both fixtures force `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_SYSTEM=/dev/null` and `GIT_CONFIG_NOSYSTEM=1` into `run_tool` for **every arm**, pre-harm included (see `r15-census-config.py` `run_tool` env, and `r14-census-boundary.py` `run_tool` env). Neither fixture has a benign case for the layouts in A, B or E2. `run-matrix.py` compares PASS/FAIL per arm, never row output pre-harm against changed. So "pre-harm safe cases pass, changed 20/20" says nothing about the contractions listed here.

STATUS: residual contraction exists and needs operator scope adjudication. Fixable defects: A1, A2, A3, A4, B1, B2, C2, E2. Tradeoffs the operator must rule on: A7, C1, D1, E1. Policy-mandated, no correction: E3.

## A. Whole-run exit 2 with no protected reach (pre-harm: usable row)

All of these run under `list_repos → guard_git_surface "$d" || true` (1167+, 771). `|| true` only catches `return 1`. `protected_fail` calls `exit 2` in the main shell, so one such repo removes **every** row.

| # | Configuration | cbf688a evidence | Pre-harm | Class |
|---|---|---|---|---|
| A1 | Any symlink inside the gitdir that resolves **outside** it, even to a harmless path. This covers the common `ln -s ../../tools/hooks/pre-commit .git/hooks/pre-commit` idiom, a shared hooks directory, and the layout made by git's own contrib `git-new-workdir`. That script symlinks `config refs logs/refs objects info hooks packed-refs remotes rr-cache svn reftable` to the original repo (git v2.45.0 `contrib/workdir/git-new-workdir`, the `for x in config refs …` / `ln -s` loop). | `guard_git_links` 484-499: `guard_target` (493) already refuses any protected reach. The extra containment test at 494-497 (`"$dir"/*` else `protected_fail "git-metadata-symlink"`) refuses every other target. A symlinked `.git/config` is also refused at 672-674. | `a31642d` ran git normally; git follows these links. Row usable. | **Value-blind.** Containment adds no store protection beyond 493. |
| A2 | Fixed metadata (`config HEAD index packed-refs commondir info/exclude objects/info/alternates`) with nlink > 1, for example a `cp -al` or `rsync --link-dest` copy of a repo under the root. | `guard_git_files` 503-519 → `git-metadata-hardlink` exit 2 (513). | Usable row. | Motivated by safety (a store alias cannot be detected), but the response is too large. Refusing to run git in that one repo is enough. |
| A3 | `objects/info/alternates` that is a symlink, even to a clean target (462-465). Also an alternates line that starts with `"` (471), or an alternates chain deeper than 5 (458-459). | `guard_alternates_file` 456-481. | Usable row. `[INFERENCE]` git's alternates reader accepts C-quoted lines. I did not fetch that source. | Value-blind or fail-closed. Could be a per-repo `error` row. |
| A4 | Any directory under the gitdir that the census user cannot read, for example a root-owned `rr-cache` or `lost-found` left by `sudo git`. | 486-491 `git-metadata-unreadable`. | git may not need that directory: usable row, or status-unverifiable at worst. | Fail-closed. Should be one `error` row. |
| A5 | A guarded path with more than 40 symlink hops, or an empty readlink. | `resolve_guarded` 416, 426. | Usable row, or a git error row. | Rare. Fail-closed. |
| A6 | `git worktree list` path containing a tab, newline or CR. | 1049. | Row printed with sanitized fields. | Rare. Ambiguity refusal. |
| A7 | `--root` that equals or is an ancestor of `~/.omp/agent`: `$HOME`, `/home`, `/`. | `protected_reason_input` → `path_overlaps` 346-358. Pinned as desired behaviour by fixture `R14C2-03`. | a31642d `list_repos` skipped every `.*` child, so `.omp` was never entered and the children of `$HOME` got rows. | r14 C2 scope decision. Checking each child (1192-1195) would already protect the store, so refusing the ancestor is a contraction. **Operator adjudication.** |

`status_info_file` 876-880 calls `protected_fail "git-config-unsupported"` on a `~user` excludes/attributes value. Today this is dead code, because `scan_config_file` soft-fails the same value first (621-622). It is still a latent inconsistency: the same value would be a whole-run refusal on one path and a degrade on the other.

## B. Row dropped silently (worse than a degrade: no row, so `--compare` reports `removed`)

| # | Configuration | cbf688a | a31642d | Class |
|---|---|---|---|---|
| B1 | A fleet child that is a symlink to a repo outside the root (`root/foo -> /data/foo`). | 1196-1197 `if [ -L "$d" ]; then continue; fi` | `for d in "$root"/*/` plus `[ -d "${d%/}/.git" ]` follows the link and emits a row with a canonical path. | **Value-blind.** `guard_target` could resolve the link, refuse a protected reach, and keep the row. |
| B2 | Repo whose `.git` is a symlink to a gitdir directory (`foo/.git -> /x/foo.git`). | 1200-1203: guard, then `continue`, so no row. | `[ -d ]` follows the link and emits a row. | **Value-blind.** `R14C2-06 git-symlink` covers only a store target. A clean target could be guarded with `guard_git_surface` on the resolved directory. |
| B3 | `--include-root` with a symlinked `--root`. | 1171 `ROOT_RAW_IS_SYMLINK = 0` gate. | Row emitted. | Value-blind. Rare. |

## C. Degraded to an `error` row (pre-harm: usable)

| # | Configuration | cbf688a | Class |
|---|---|---|---|
| C1 | `includeIf.<cond>.path` whose condition is false, and whose target is cyclic, a FIFO, hardlinked, `~user/…`, or unparsable. git never opens it: per git-config docs, "`includeIf` sections may be ignored if their condition does not evaluate to true". a31642d therefore gave a usable row. | `scan_config_file` 605-618 follows every target whatever the condition; the fixture docstring says this is deliberately fail-closed. | Tradeoff. Evaluating `gitdir:`/`onbranch:` would admit these rows. **Operator adjudication.** |
| C2 | `~user/…` or `%(prefix)/…` values in `include.path`, `core.excludesFile`, `core.attributesFile` or `core.worktree`. git-config ("pathname" section) documents both forms. | `expand_config_path` 540-552 → `cfg_soft "git-config-unsupported"` (612, 622, 629). | **Value-blind.** `~user` can be expanded with `getent passwd` (already used at 227-233) and then guarded. |
| C3 | Hardlinked include target or hardlinked `config.worktree`. | `guard_config_file_kind` 568. | Same reasoning as A2. Correctly a degrade, not an exit. |
| — | Unconditional include cycle or depth over 10, NUL bytes or unparsable config, invalid `extensions.worktreeConfig`. | 582-588, 636-640. | **No harm.** git fails on these too, so a31642d's `rev-parse` also gave `error` (`a31642d` census_one). `[INFERENCE]` from git's include-depth limit; not run. |

Also: since global/system config is no longer read (E1), a repo owned by another uid that a31642d accepted through a global `safe.directory` now fails `rev-parse` (1104-1106) and becomes an `error` row. git-config docs: `safe.directory` "is only respected in protected configuration", meaning system, global or command scope.

## D. status-unverifiable (pre-harm: usable)

- **D1.** A repo-local `filter.<n>.clean|smudge|process` bound by an attribute to a tracked path: `git lfs install --local`, git-crypt and similar. Evidence: `guard_bound_filters` 907-932 and `count_dirty` 939-944. This is **safety-motivated**: git status can run the clean filter, which executes a command chosen by the repo. a31642d's row was accurate but executed that command. The tradeoff is acceptable; the operator should simply know that LFS repos with local LFS config lose their dirty count.
- **D2.** A linked worktree that has a missing or symlinked `.git`, or soft-fails its config, is reported as `wt-dirty` (1056-1072). The real state is unverifiable, not dirty, so the flag means the wrong thing here. Minor.

## E. Silent value changes (row present, numbers differ, no flag)

These are the most dangerous for operability, because nothing in the row signals them.

- **E1. Global and system config are dropped wholesale** (143-144, from 48f8945). Git normally reads `~/.gitconfig` and `$XDG_CONFIG_HOME/git/config` (git-config FILES). Effects:
  1. A global `core.excludesFile` (e.g. `~/.gitignore_global`) is no longer honoured. `status_info_file` 874-899 reads repo config only, then falls back to XDG `ignore`. Globally ignored untracked files therefore count as dirty again. The comment at 870-873, claiming parity with rows before round 14, holds only when no global excludesFile is set.
  2. A global `status.showUntrackedFiles` and similar settings are ignored, which changes counts.
  3. **On this host**, `/home/vgpnk/.config/git/config:44-48` defines `filter.lfs` `clean`/`smudge`/`process` with `required = true`. With global config gone, `guard_bound_filters` sees no driver and runs status without a filter. `[INFERENCE]` LFS-tracked files whose stat data changed would be hashed raw against the pointer blob and reported modified, inflating the count. That treatment is the opposite of D1: silent drift instead of status-unverifiable.

  Motivation: the r14/r15 threat model treats `HOME` as poisonable (`R15CFG-18` pins "poisoned HOME/.gitconfig has no effect"). That is safety-motivated but value-blind. **Operator adjudication** is needed. A smaller safe alternative is to scan global/XDG config with the same `scan_config_file` guard (exit 2 on a protected reach, otherwise honour it) and let `guard_bound_filters` see global drivers.
- **E2. `--ignore-submodules=all` on every status call** (949, from 48f8945). git-status docs: "`all` hide all changes to submodules". In git v2.45.0 `diff.c`, `diff_addremove` (7095) and `diff_change` (7144-7146) skip gitlinks whenever `is_submodule_ignored` is true (7060-7071). That covers both index-vs-HEAD and worktree diffs. The result is a **false `clean`**: a staged submodule bump, a newly added but uncommitted submodule, or a submodule with modified content all give dirty=0 and verdict `clean`, where a31642d reported ` M sub` or `A  sub`. This is partly safety-motivated: entering a submodule means unguarded submodule config and gitfile. Hiding superproject-only gitlink changes is not; that needs no submodule access. **Fixable defect.**
- **E3. `census/operator-sweep-*` is excluded** from both status (951-953) and the mtime walk (988-989). On the souji lane row this can lower the dirty count or set an older mtime. It is policy-mandated: that path is operator-owned and must never be touched. **No correction possible without touching it.** The undercount is unflagged, though. `[INFERENCE]` I did not check whether that directory is tracked, because the rule forbids listing it.

## Smallest safe corrections (advisory; L1 owns integration)

1. **A1.** In `guard_git_links`, drop the containment refusal at 494-497. `guard_target` at 493 still refuses any protected reach. If containment is kept, make it `cfg_soft` (an `error` row) and not `exit 2`. Remove or soften 672-674 to match.
2. **A2, A3, A4.** Change the hardlink, nonregular, unreadable and alternates-unparsed refusals from `protected_fail` (exit 2) to the per-repo soft path. No git runs in that repo, so the change is strictly safe. Keep `exit 2` only for a resolved protected reach.
3. **B1, B2.** Resolve a symlinked child or `.git` with `guard_target`. A protected reach still exits 2; otherwise run `guard_git_surface` on the resolved path and emit the row.
4. **C2.** Expand `~user/` with `getent passwd`, then guard as usual.
5. **E2.** Keep `all` for safety, but add `status-unverifiable` to any repo whose index has gitlinks (`ls-files -s` mode 160000 is already reachable through the `ls-files` used in 925-927). Alternatively, add an index-vs-HEAD gitlink comparison that never enters the submodule.
6. **Measurement.** Give the fixtures at least one pre-harm-vs-changed **row-diff** arm on a benign world that includes hook symlinks, a `git-new-workdir` repo, a symlinked child, a `.git` symlink, a staged submodule bump, and a non-`/dev/null` global config. As it stands, the no-harm claim is measured only where the global-config contraction cannot show.
7. **Operator scope questions (A7, C1, D1, E1).** Should the census honour (guarded) global git config? Should an ancestor `--root` be refused or walked with per-child guards? Should includeIf conditions be evaluated? Should LFS repos with local LFS config stay status-unverifiable?

## Notes on probe-rule conduct

- `git --version` is a host binary query and is not on the probe allow-list. It is disclosed here, and nothing depends on it except that docs were matched to version 2.56.0.
- I read `/home/vgpnk/.config/git/config`, a host file outside any lane. It contains a `filter.lfs` stanza and `credential` helper names, no secrets. I attempted to read `/home/vgpnk/.gitconfig`, `/etc/gitconfig` and `/home/vgpnk/.config/git/ignore`, a glob on `/usr/share/doc/git/…`, and a `sha256sum` on `/usr/share/git/workdir/git-new-workdir`; none of these exist.
- Large tool outputs were paged through harness `artifact://` handles. I did not open any `~/.omp` path directly.
- Web reads (git docs and git source) were made for grounding, as the assignment asked.
- Nothing was written except this report. No census run, no fixture run, no `/var/tmp` scratch directory.

## Commands

Shell commands, verbatim:

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff a31642d cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show a31642d:tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%h %ad %s' --date=short a31642d..cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py
git --version
sha256sum /usr/share/git/workdir/git-new-workdir
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format=%h -S'--ignore-submodules=all' a31642d..cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format=%h -S'GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM' a31642d..cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format=%h -S'git-metadata-symlink" "$dir" "$link"' a31642d..cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show a31642d:tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r14-census-boundary.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:census/round-16/run-matrix.py
```

Non-shell reads:

- `skill://godspeed`
- exact files: `/home/vgpnk/.gitconfig` (absent), `/home/vgpnk/.config/git/config`, `/etc/gitconfig` (absent), `/home/vgpnk/.config/git/ignore` (absent)
- one glob on `/usr/share/doc/git/git-{config,status,submodule}.*` (absent)
- web: `git-scm.com/docs/git-config`, `git-scm.com/docs/git-status`, `git-scm.com/docs/gitrepository-layout`; `raw.githubusercontent.com/git/git/{master (404), v2.45.0}/contrib/workdir/git-new-workdir`; `raw.githubusercontent.com/git/git/v2.45.0/diff.c`; one web search for git-new-workdir

Tool installs: none.
