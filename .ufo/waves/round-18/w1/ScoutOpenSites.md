STATUS: DONE — static open-site inventory of the C1 path at b576341: 25 repository-controlled open sites in `census_one`, 23 blockable by a FIFO swap, 2 stat/opendir-only; the one-site `info/attributes` repro is representative, not exhaustive.

# Scope and method

- Target: `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh` at `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`.
- Lane HEAD is exactly that rev and the file is undrifted, so reads of the working-tree file are reads at REV:
  - `git -C <lane> rev-parse HEAD` → `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`
  - `git -C <lane> diff --stat b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- tools/souji-census.sh` → no output, rc 0
  - `git -C <lane> show b576341…:tools/souji-census.sh | wc -l` → `2072`
- Reads/greps only over that one file; the census was **not** run (forbidden); no writes outside this report.
- Blocking semantics are POSIX/coreutils facts, not a run: `open(2)` O_RDONLY on a FIFO with no writer blocks; `test -f`/`[ -f ]` is false for a FIFO; `[ -e ]` is true. Marked `[INFERENCE]` where git's internal open set is involved.
- No tool installs; pacman untouched.

# Call graph (census_one path)

`emit_census :1402-1403` (`row=$(census_one "$repo")`, serial command substitution, no timeout) →
`census_one :1261` → `guard_path :1263`; `guard_git_surface :1264`
→ `guard_git_links :913/:931/:955/:973`, `guard_git_files :914/:932/:956/:974` (`stat :555`), `guard_git_config :915/:933/:957/:975` → `scan_config_file :688` (+ `guard_config_file_kind :667`, `guard_wt_config :776`), `guard_alternates_file :937/:979`, `guard_worktree_registrations :938/:980` → `gitfile_admin :818`
→ `git rev-parse :1280` → `count_worktrees :1000` → `count_unpushed :1006,:1010,:1014` → `count_dirty :1122` (`status_info_file :1027`, `guard_bound_filters :1069,:1085-1091`) → `scratch_bytes :1144` → `worktree_extra_flags :1253,:1244,:1249` (recursive `guard_git_surface`+`count_dirty` per linked worktree) → `newest_mtime :1162`.

# Open-site inventory

`GGS` = the once-per-gitdir `guard_git_surface` pass; `stat :555` = `guard_git_files`' single `stat -L -c '%F %h'` over the nine fixed names (`config HEAD index packed-refs commondir info/exclude info/attributes objects/info/alternates`, `:548`). "Blockable" = a swap between that guard and this open (or a create after it) leaves a FIFO that `open(2)` waits on forever.

| # | site:line | opener | repo-controlled path opened | guard immediately preceding | FIFO-swap blockable |
|---|---|---|---|---|---|
| 1 | :515 `done < "$alt"` | bash redirection | `$GIT_DIR/objects/info/alternates`; recursive alternates targets | `-L` refuse :500; `[ -f ]` :504; `stat :555` only for the main gitdir | **YES** — swap after :504 or after :555; a FIFO at :504 is treated as absent and git opens it later |
| 2 | :695 `tr -d '\000' < "$cfg"` | `tr` redirection | `$GIT_DIR/config`, every `include.path`/`includeIf.*.path` target, `config.worktree` | main: `-L` :798, `[ -f ]` :803, `stat :555`; include: `guard_config_file_kind` :727; wt: :784 | **YES** — non-atomic `stat`→`open`; a FIFO at :803 reads as "no config", guard passes, git opens it later |
| 3 | :695 `cmp -s -- - "$cfg"` | `cmp` (second open of same path) | same as #2 | same as #2 | **YES** — even a swap between #2 and #3 blocks |
| 4 | :698 `git config --file "$cfg" --list -z` | git | same as #2 | same as #2 | **YES** |
| 5 | :701 `git config --file "$cfg" --list -z` (mapfile) | git | same as #2 | same as #2 | **YES** |
| 6 | :751 `git config --file "$cfg" --type=bool --get-all` | git | `$dir/config` / `config.worktree` (depth-0 only, :748) | same as #2 | **YES** |
| 7 | :820 `IFS= read -r line < "$file"` (`gitfile_admin`) | bash redirection | linked-worktree `.git` file named by `worktrees/<id>/gitdir` | caller `guard_worktree_registrations`: `-d` :854, `[ -f "$target" ]` :868; `guard_target` path-only :866 | **YES** — swap after :868 |
| 8 | :857 `IFS= read -r target < "$reg"` | bash redirection | `$GIT_DIR/worktrees/<id>/gitdir` (incl. dot-named admins) | `-d "$entry"` :854; `[ -f "$reg" ]` :856 | **YES** — FIFO at :856 skipped; `git worktree list` (:1000/:1253) opens it |
| 9 | :880 `IFS= read -r c < "$common"` | bash redirection | linked admin `commondir` | `guard_git_files "$admin"` :871; `[ -f ]` :879 | **YES** |
| 10 | :923 `IFS= read -r target < "$common"` | bash redirection | `$GIT_DIR/commondir` | `stat :555` :914; `[ -f ]` :922 | **YES** — FIFO at :922 reads as absent; every later git call opens commondir |
| 11 | :943 `IFS= read -r target < "$g"` | bash redirection | `<repo>/.git` gitfile | `[ -f "$g" ]` :942 only; `guard_git_files` never stats the `.git` file | **YES** — swap after :942, or after `list_repos` admitted the repo; a FIFO `.git` makes `-L/-d/-f` all false, GGS returns 0, `census_one :1274` still passes on `-e`, and `git rev-parse :1280` opens it |
| 12 | :965 `IFS= read -r target < "$common"` | bash redirection | `commondir` of the resolved common dir | `stat :555` :956/:974; `[ -f ]` :964 | **YES** |
| 13 | :1000 `git -C "$1" worktree list` | git | config, commondir, `worktrees/*/gitdir`, `worktrees/*/HEAD` | GGS :914-938; no per-open recheck | **YES** — `worktrees/*/HEAD` is not even in the fixed list |
| 14 | :1006 `git for-each-ref … refs/remotes` | git | `packed-refs`, `refs/**`, config | GGS; `stat :555` covers packed-refs only | **YES** |
| 15 | :1010 `git rev-list --count --branches` | git | `packed-refs`, `refs/**`, `shallow`, `info/grafts`, `objects/**` | GGS; `stat :555` covers packed-refs only | **YES** |
| 16 | :1014 `git rev-list --count --branches --not --remotes` | git | same as #15 | same as #15 | **YES** |
| 17 | :1027 `git config --get "$key"` (`status_info_file`, twice) | git | config, `config.worktree` | GGS; `guard_wt_config :784` only when the extension was seen | **YES** — extension added after scan ⇒ `config.worktree` FIFO opened unguarded |
| 18 | :1069 `git config -z --get-regexp '^filter\.…'` | git | config, `config.worktree` | GGS | **YES** |
| 19 | :1085 `git ls-files -z --cached` | git | `.git/index`, config | `stat :555` (index) | **YES** |
| 20 | :1090 `git check-attr -z --stdin filter` | git | `$GIT_DIR/info/attributes`, `core.attributesFile=$attrs`, config | `stat :555` (info/attributes); `[ ! -f ]` non-regular check :1038 for `$attrs` | **YES** — :1038 is TOCTOU; info/attributes swap after :555 is invisible |
| 21 | :1122 `git status --porcelain` | git | index, HEAD, config, packed-refs, `info/exclude`, `info/attributes`, `$at`, `$ex`, worktree contents | `stat :555`; :1038; `guard_bound_filters :1093` | **YES — L1's repro**; also the declared `wt-dirty`/`count_dirty` measurement itself |
| 22 | :1144 `du -sb -P -- "$d"` | du (fts) | `<repo>/.scratch` tree | `-L` :1139, `-e` :1140, `-d` :1141 | NO — stat/opendir only, never opens file content; **unbounded time**, not FIFO-blocking |
| 23 | :1162 `find -P .` | find | whole work tree | prune list only | NO — stat/opendir only, contents never opened; **unbounded time**, not FIFO-blocking |
| 24 | :1253 `git -C "$repo" worktree list --porcelain` | git | config, commondir, `worktrees/*/gitdir`, `worktrees/*/HEAD` | GGS run earlier; the loop's per-cpath `guard_git_surface :1244` runs only **after** this git process has already opened its metadata | **YES** |
| 25 | :1280 `git -C "$repo" rev-parse --is-inside-work-tree` | git | `<repo>/.git` (dir/file), config, commondir | GGS :906-942; `.git` dir/file checks :942 only | **YES** |

Count: 25 sites — 9 bash/coreutils file opens (rows 1-3, 7-12), 14 git invocations (rows 4-6, 13-21, 24-25), 2 du/find stat-only (rows 22-23). 23 of 25 blockable; none of the 23 has a type check atomic with its open.

# Guard classes and why every gate leaks

1. **One-shot stat** (`:555`). Nine names are stat'ed once per gitdir, at `:914/:932/:956/:974` and `:871`, then never revalidated. All later opens of those names (rows 4-6, 13-21, 25) are in a separate syscall, so a swap after the stat is invisible. This is the class L1 reproduced on `info/attributes`; it applies equally to `config`, `HEAD`, `index`, `packed-refs`, `commondir`, `info/exclude` and `objects/info/alternates`.
2. **`[ -f ]` / `[ -e ]` / `[ -d ]` gates** (`:504`, `:803`, `:856`, `:868`, `:879`, `:922`, `:942`, `:964`; `:669`, `:784`). These are not refusal gates: a FIFO fails `-f` and is silently classified "absent", so the guard returns success and a later opener blocks. Examples: `:922` commondir absent → later created FIFO → every git call opens it; `:856` registration absent → created → `worktree list` opens it; `:803` config FIFO → scan skipped → `rev-parse` opens it.
3. **`-L` symlink refusal only** (`:500`, `:779`, `:798`). Refuses symlinks, never the regular→FIFO type change.
4. **No guard at all** for git's wider metadata set. `guard_git_files :548` is a nine-name allowlist, not an open-site inventory. Documented layout implies git also opens, from the repo: `shallow`, `info/grafts`, `objects/info/commit-graph`, `objects/pack/*.idx`, loose `objects/**`, loose `refs/**`, and `worktrees/*/HEAD` [INFERENCE: git internals; the script never stats these]. A FIFO at any of them blocks `rev-list`/`for-each-ref`/`status` with zero guard passes.
5. **Create-after-guard**, beyond type-swap: a name absent at guard time (`stat :555` failure → `continue`, `:555`; `-f` false at `:504/:803/:856/:922`) can be created as a FIFO before the opener. `guard_git_files` explicitly treats a failed stat as "absent or dangling symlink", not as a refusal.
6. **`worktrees/*/HEAD`** is read by both `worktree list` invocations (rows 13, 24) and is absent from every guard; only `gitdir` and `commondir` are read/guarded at `:857`/`:880`.

Only rows 22-23 are structurally immune: `du` and `find` use `stat`/`opendir` and never `open(2)` file contents. Both remain unbounded in time (large tree), which the same per-repo bound must cover.

# Why this hangs the fleet at base

- `emit_census :1402-1403`: `for repo …; if row=$(census_one "$repo")`. The command substitution waits for `census_one` *and every child it spawned*; a block inside any row stalls the loop before later repos are emitted.
- No bound exists anywhere: `grep -nE 'timeout|setsid|killpg|kill --|process group|set -m' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh` → no output, `rc=1`. An outer `timeout 15` kills only `emit_census`/its shell, leaving git (and its FIFO open) orphaned; the healthy neighbours' rows are never printed.
- The header already concedes the mechanism at `:149-151` ("the guard and the later access are not one atomic operation") but scopes it to hardlinks; `:643` ("no git call that could read that file runs afterwards") is only true while the guarded file is unchanged between the guard and the call.

# Verdict

**C1 holds, and its repro is one of 23.** The `info/attributes` swap is the cheapest instance because the file is read by `git status` unconditionally — the per-repo `$GIT_DIR/info/attributes` is always consulted even when `-c core.attributesFile=/dev/null` is passed (gitattributes(5) precedence; `[INFERENCE: documented git behavior, not re-observed here]`) — and its only guard is the one-shot stat at `:555`. But the same swap works on `index`, `HEAD`, `packed-refs`, `config`, `commondir`, `info/exclude`, `objects/info/alternates`, and on unguarded names (`shallow`, `info/grafts`, `objects/**`, `refs/**`, `worktrees/*/HEAD`) with no race at all against a named guard.

Consequence for the fix design: no ordering or strengthening of shell guards closes this class, because `open(2)` cannot be made type-atomic with any earlier `stat`/`-f` from bash, and git's open set is not enumerable by a fixed name list. The contract's per-repo process group + watchdog in `emit_census` is the load-bearing control; guard changes can only shrink the window.

# Smallest fix

- Required (as contracted): in `emit_census :1394-1416`, run each `census_one` in its own process group (`set -m` only around that fork), stdout to a private temp file, SIGTERM the group at the bound, SIGKILL +2 s, row `<repo>\t0\t0\t0\t0\t\terror` + stderr `souji-census: repo-timeout <N>s <repo>`, other repos measured, exit 0; `--repo-timeout`/`SOUJI_CENSUS_REPO_TIMEOUT` 1..86400 default 600, invalid → usage 2.
- Optional, not sufficient (cheap reductions only): (a) make every `[ -f "$p" ]` gate refuse a present non-regular (`[ -e "$p" ] && [ ! -f "$p" ]` → soft/refusal) instead of treating it as absent; (b) add `shallow`, `info/grafts`, `objects/info/commit-graph`, `objects/pack/*.idx`, `worktrees/*/HEAD` to `:548` and re-stat at each use site. Both are still TOCTOU and neither covers loose objects/refs, so the watchdog remains the only sound bound.

# Remaining unknowns

- Exact per-version git open set for `rev-parse`/`worktree list`/`for-each-ref`/`rev-list`/`status` (documented layout used above; not observed on this host, and the lane's git version was not inspected).
- Whether `git status` opens a tracked worktree path after a regular→FIFO swap (typechange handling) — outside the metadata class and unguarded, but not part of C1's stated surface.
- `guard_bound_filters`' `wait "$pid"` at `:1093` was checked separately: bash sets `$!` for the process substitution (`bash -c 'mapfile … < <(printf x); printf "pid=[%s]" "$!"'` → `pid=[429745]`, rc 0), so it does not force `status-unverifiable`; not a finding.
