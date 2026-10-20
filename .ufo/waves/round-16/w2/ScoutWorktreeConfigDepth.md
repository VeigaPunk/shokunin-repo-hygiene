# ScoutWorktreeConfigDepth — W2 falsify recon

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin at HEAD a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae
(`tools/souji-census.sh` sha256 64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c).
Host git 2.56.0 [OBSERVED: `git --version`]; sources read at tag v2.56.0, matched to the host.

Question: does git read `extensions.worktreeConfig` only from `$GIT_DIR/config` (repository format
check) and never from `include.path` targets or `config.worktree`?

## Verdict

- **Holds** (confidence HIGH) for the claim's substance: the extension that gates `config.worktree`
  is taken only by the repository-format read of the **common** config, and that read does not follow
  includes. `config.worktree` cannot enable itself: the format-time read of it uses a callback that
  understands only `core.bare`/`core.worktree`, and the ordinary read is gated on the flag already
  computed from the common config.
- **Wording precision:** the path is `$GIT_COMMON_DIR/config`, which equals `$GIT_DIR/config` only for
  the main worktree. For a linked worktree the format read consults the common config, not the
  worktree admin's own `config`. Census already models this (§Census mapping).
- One census comment is **overstated and fails narrowly**: `tools/souji-census.sh:694-695`
  "config.worktree … is never opened otherwise". A `git worktree list` code path opens
  `$GIT_COMMON_DIR/config.worktree` with no extension gate (§Counterexample).

## Evidence (all URLs accessed 2026-10-20)

1. https://github.com/git/git/blob/v2.56.0/setup.c#L759-L761 — format read source path:
   "`has_common = get_common_dir(&sb, gitdir); strbuf_addstr(&sb, "/config"); read_repository_format(format, sb.buf);`".
2. https://github.com/git/git/blob/v2.56.0/setup.c#L866-L872 — "`git_config_from_file(check_repo_format, path, format);`"
   (plain file read, no include-capable option object).
3. https://github.com/git/git/blob/v2.56.0/config.c#L1441-L1445 — "`git_config_from_file_with_options(fn, filename, data, CONFIG_SCOPE_UNKNOWN, NULL);`"
   (the final `NULL` is the options argument).
4. https://github.com/git/git/blob/v2.56.0/config.c#L1632-L1639 — include processing is installed only
   here: "`if (opts->respect_includes) { … fn = git_config_include; data = &inc; }`". With `opts == NULL`,
   an `include.path` key reaches the callback as an ordinary key; `check_repo_format` ignores it
   (it falls through to `read_worktree_config`, which matches only `core.bare`/`core.worktree`).
5. https://github.com/git/git/blob/v2.56.0/config.c#L1605-L1607 — the only gate on reading
   `config.worktree`: "`if (!opts->ignore_worktree && worktree_config && repo && repo->repository_format_worktree_config &&`".
   Path built as "`mkpathdup("%s/config.worktree", opts->git_dir)`" (config.c:1577).
6. https://github.com/git/git/blob/v2.56.0/setup.c#L785-L792 — format-time `config.worktree` read:
   "`if (format->worktree_config) { … git_config_from_file(read_worktree_config, sb.buf, format);`".
   `read_worktree_config` (setup.c:585-598) handles only "`core.bare`" and "`core.worktree`", so an
   `extensions.worktreeConfig` line there is inert.
7. https://github.com/git/git/blob/v2.56.0/Documentation/config/extensions.adoc#L119-L127 —
   "If enabled, then worktrees will load config settings from the `$GIT_DIR/config.worktree` file in addition to the `$GIT_COMMON_DIR/config` file."
8. https://github.com/git/git/blob/v2.56.0/Documentation/gitrepository-layout.adoc#L146-L148 —
   "This file is ignored if $GIT_COMMON_DIR is set and "$GIT_COMMON_DIR/config" will be used instead."
9. https://github.com/git/git/blob/v2.56.0/t/t2404-worktree-config.sh#L74-L79 — behavioural test:
   "`config.worktree no longer read without extension`" (after unsetting the extension, all three
   worktrees fall back to the shared value).
10. https://github.com/git/git/blob/v2.56.0/repository.c (config read is `repo_read_config`,
    config.c:2299-2323) — ordinary config reads set "`opts.respect_includes = 1;`" (config.c:2304), so
    `git config --get extensions.worktreeConfig` *does* report an include-set value even though that
    value gates nothing. This is the asymmetry to keep in mind when reading census output.

Closed additional route: no other consumer of `extensions.worktreeConfig` exists. A sweep of every
`*.c`/`*.h` at v2.56.0 for `worktree_config`/`worktreeconfig` yields only setup.c, config.c,
worktree.c, builtin/config.c, builtin/worktree.c, builtin/sparse-checkout.c — all gated on
`the_repository->repository_format_worktree_config` or `format->worktree_config`.

## Census mapping (HEAD a6ec7810)

- `souji-census.sh:664-681` — `extensions:worktreeconfig` is honoured only at `depth = 0`
  (`:669`), i.e. only in the file passed to the scan, never in an include target. **Matches git**
  (evidence 2-4). Note the census follows include targets regardless of `includeIf` condition
  (`:634-665`), an over-approximation consistent with a guard.
- `souji-census.sh:694-711` — `guard_wt_config` opens/scans `$gitdir/config.worktree` only when
  `CFG_WT_ENABLED = 1` (`:698`), restores the inherited flag after scanning (`:708-709`), and the
  caller re-asserts the parent value at `:728-731`, so a value inside `config.worktree` cannot
  change which files are scanned. **Matches git** (evidence 5-6).
- `souji-census.sh:726-731` — for a linked worktree the flag threaded into `guard_wt_config "$first"`
  comes from the **common** config guard, matching evidence 1 and 5 (git uses
  `$GIT_COMMON_DIR/config.worktree` as `$GIT_DIR/config.worktree`).
- `souji-census.sh:88-93` (header) — "through config.worktree when the common config's
  extensions.worktreeConfig is true" is accurate.
- Therefore: include-set `extensions.worktreeConfig` is correctly ignored by the census; a
  config.worktree-set value is correctly unable to enable itself.

## Counterexample to "never opened otherwise" (narrow; `:694-695` fails)

Observed code path [OBSERVED at v2.56.0], reachability [INFERENCE from the layout]:

- `git -C <row> worktree list` (census `:917` via `count_worktrees`, and `:1166`) ->
  `builtin/worktree.c:1154` `get_worktrees()` -> `worktree.c:197` `get_main_worktree()`.
- `worktree.c:126-134` sets `is_bare` with `(!worktree->is_current && is_main_worktree_bare(repo))`.
- `worktree.c:58-66` `is_current_worktree()` compares `repo_get_git_dir()` with
  `get_worktree_git_dir()`; for the main entry the latter returns **`repo_get_common_dir()`**
  (`worktree.c:229-236`). So `is_current` is false whenever `git_dir != commondir`.
- `worktree.c:95-107` `is_main_worktree_bare()` then opens
  `xstrfmt("%s/config.worktree", repo_get_common_dir(repo))` through
  `git_configset_add_file()` (`config.c:1843-1846` -> `git_config_from_file`, options `NULL`, so
  includes are not followed — but the file **is opened and parsed**) with **no extension check**.

Census row predicate requires a `.git` **directory** (`:1289-1297`); a `.git` file is guarded, not a
row. A `.git` directory may carry a `commondir` file — the census explicitly implements that layout
(`:786-800`), so it is inside the census's threat model. With `extensions.worktreeConfig` absent:

1. `guard_git_config` on `.git`, then on the common dir C: `CFG_WT_ENABLED = 0`; `guard_wt_config`
   returns at `:698` **before** the kind check at `:704`. `guard_git_files` (`:521`) does not list
   `config.worktree`. `guard_git_links` rejects symlinks under C, so a symlink is not a hole.
2. `count_worktrees` runs `git -C <row> worktree list`; `git_dir` (`<row>/.git`) != `commondir` (C),
   so `is_main_worktree_bare()` opens `C/config.worktree` unguarded.
3. Consequences:
   - `C/config.worktree` is a FIFO/device: `fopen_or_warn(..., "r")` (`config.c:1421-1428`) blocks on
     `open()` — the census hangs, the exact outcome `guard_git_files` (`:517-533`) is written to
     prevent ("refused rather than opened or waited on"). [INFERENCE: POSIX FIFO semantics]
   - `C/config.worktree` is a hardlink (nlink > 1) to a protected file: its content is read at
     `git_configset_add_file` time — a protected-content reach the r14 guards refuse for `config`
     and other fixed metadata. [OBSERVED that the file is opened; INFERENCE about content]
   - `include.path` *inside* that file is NOT followed by this call (`opts == NULL`), so a protected
     include target is not reached through this path; only the file's own bytes are.

Scope: requires the `.git`-directory + `commondir` layout and an unenabled `config.worktree`. Normal
repos (`git_dir == commondir`) never take this branch; census never runs `git worktree list` from a
linked worktree, so the common `is_current == false` case (running inside a linked worktree) is not
reachable by census itself.

## Smallest fix

Hoist the kind check above the enabled gate in `guard_wt_config` (`souji-census.sh:696-704`):

```bash
  local dir=$1 wtc="$1/config.worktree"
  if [ -L "$wtc" ]; then protected_fail "git-metadata-symlink" "$dir" "$wtc"; fi
  [ -e "$wtc" ] || return 0
  guard_config_file_kind "$wtc" || return 1      # moved above the gate: non-regular/hardlink -> soft
  [ "$CFG_WT_ENABLED" = 1 ] || return 0          # content scan stays gated
```

This keeps the documented soft outcome (`error` row, no git command in that repository) rather than
the whole-run refusal that adding `config.worktree` to `guard_git_files` (`:521`) would create, and
it closes both the FIFO hang and the hardlink read. Cost: a normal-layout repo with a stray
non-regular `config.worktree` and no extension degrades from a normal row to an `error` row — a
conservative outcome consistent with the census's fail-closed posture.

## Remaining unknowns

- No upstream test asserts that an *include-set* `extensions.worktreeConfig` is ignored; the
  conclusion rests on the code path (`opts == NULL` at `config.c:1441-1445`). HIGH confidence, not
  test-encoded.
- Whether git accepts a `.git`-directory + `.git/commondir` layout was not exercised (no
  ALLOWED-EXEC for repo experiments); it is [INFERENCE] from `get_common_dir` reading
  `$GIT_DIR/commondir`, and the census already guards the layout.
- FIFO blocking was not empirically observed here (POSIX semantics only).

## Commands

File reads used the `read` tool (not shell) on `tools/souji-census.sh:555-760` and `:85-130`.
Shell commands, verbatim:

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && sha256sum tools/souji-census.sh && grep -n "worktreeConfig\|GIT_DIR\|include.path\|config.worktree\|extensions\." tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "git\b" tools/souji-census.sh | head -80
git --version; cd /var/tmp && mkdir -p souji-r16-ScoutWorktreeConfigDepth && cd souji-r16-ScoutWorktreeConfigDepth && curl -sSL -o setup.c https://raw.githubusercontent.com/git/git/v2.51.0/setup.c && curl -sSL -o config.c https://raw.githubusercontent.com/git/git/v2.51.0/config.c && wc -l setup.c config.c && grep -n "read_repository_format\|check_repo_format\|worktree_config\|git_config_from_file" setup.c | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '815,900p' tools/souji-census.sh
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && for f in setup.c config.c; do curl -sSL -o 256-$f https://raw.githubusercontent.com/git/git/v2.56.0/$f; done; wc -l 256-setup.c 256-config.c; head -3 256-setup.c
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && sed -n '580,660p' setup.c && echo ---- && sed -n '694,800p' setup.c && echo ---- && sed -n '830,845p' setup.c
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && grep -n "read_repository_format\|check_repository_format_gently\|repository_format_worktree_config\|config.worktree" 256-setup.c | head -30 && echo ==== && grep -n "int git_config_from_file\b\|git_config_from_file_with_options\|static int do_git_config_sequence\|repository_format_worktree_config\|include_depth\|handle_path_include\|respect_includes" 256-config.c | head -60
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && sed -n '1395,1450p' 256-config.c && echo ==== && sed -n '1550,1620p' 256-config.c
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && sed -n '1622,1740p' 256-config.c && echo ==== && sed -n '2900,2935p' 256-config.c
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && sed -n '420,455p' 256-config.c && echo ==== && grep -n "static int do_config_from\b" -A 14 256-config.c
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && curl -sSL -o repository.c https://raw.githubusercontent.com/git/git/v2.56.0/repository.c && curl -sSL -o extensions.adoc https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/extensions.adoc && curl -sSL -o layout.adoc https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitrepository-layout.adoc && grep -n "repo_read_config" -A 40 repository.c | head -70
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && ls -l repository.c extensions.adoc layout.adoc && grep -n "config_set\|read_config\|respect_includes" repository.c | head -20
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && sed -n '1745,1815p' 256-setup.c && echo ==== && sed -n '780,800p' 256-setup.c
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && grep -n "worktreeConfig" -B2 -A8 extensions.adoc; echo ====; grep -n "config.worktree" -B4 -A8 layout.adoc
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && grep -rn "repo_read_config" 256-config.c 256-setup.c repository.c | head; echo ====; head -20 repository.c
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && sed -n '2290,2345p' 256-config.c
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && curl -sSL -o git-2.56.0.tar.gz https://github.com/git/git/archive/refs/tags/v2.56.0.tar.gz && tar xzf git-2.56.0.tar.gz && grep -rn "worktree_config\|worktreeconfig" git-2.56.0 --include=*.c --include=*.h | grep -v "^git-2.56.0/t/" | head -40
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && grep -rn "worktreeConfig" git-2.56.0/t/*.sh | head -40
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && sed -n '88,112p' git-2.56.0/worktree.c && echo ==== && sed -n '1038,1100p' git-2.56.0/worktree.c && echo ==== && sed -n '1367,1396p' 256-config.c && echo ==== && grep -n '"include.path"' 256-config.c
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && grep -rn "is_main_worktree_bare" git-2.56.0 --include=*.c && echo ==== && grep -n "git_configset_add_file" -A 8 256-config.c | head -20
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && sed -n '1,105p' git-2.56.0/t/t2404-worktree-config.sh
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && sed -n '112,150p' git-2.56.0/worktree.c && echo ==== && grep -n "get_worktrees\|get_main_worktree" git-2.56.0/builtin/worktree.c | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '495,556p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "git -C\|GIT_CONFIG_COUNT\|GIT_NO_LAZY_FETCH\|git_config_env\|census_git" tools/souji-census.sh | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '160,220p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '905,1015p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "status_info_file\|guard_bound_filters\|wt=\|for wt\|worktree_config_for" tools/souji-census.sh | sed -n '1,40p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1015,1075p' tools/souji-census.sh
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && grep -n "static int is_current_worktree" -A 30 git-2.56.0/worktree.c
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '760,815p' tools/souji-census.sh
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && grep -n "get_worktree_git_dir" -A 10 git-2.56.0/worktree.c | head -30 && echo ==== && grep -n "struct worktree \*\*get_worktrees" -A 60 git-2.56.0/worktree.c | head -80
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && echo "== setup 750-765"; sed -n '750,765p' 256-setup.c; echo "== setup 783,795"; sed -n '783,795p' 256-setup.c; echo "== setup 864,878"; sed -n '864,878p' 256-setup.c; echo "== setup 585,600"; sed -n '585,600p' 256-setup.c
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && echo "== config 1441-1446"; sed -n '1441,1446p' 256-config.c; echo "== config 1604-1611"; sed -n '1604,1611p' 256-config.c; echo "== config 1630,1640"; sed -n '1630,1640p' 256-config.c; echo "== worktree 95-107"; sed -n '95,107p' git-2.56.0/worktree.c; echo "== worktree 126-136"; sed -n '126,136p' git-2.56.0/worktree.c; echo "== builtin 470,480"; sed -n '470,480p' git-2.56.0/builtin/worktree.c; echo "== list_worktrees"; grep -n "static int list_worktrees" -A 6 git-2.56.0/builtin/worktree.c
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && grep -n "static int list_worktrees\|list_worktrees(" git-2.56.0/builtin/worktree.c | head && echo ==== && grep -n "\"list\"" -B3 -A6 git-2.56.0/builtin/worktree.c | head -30 && echo ==== && grep -n "void get_common_dir" -A 25 256-setup.c
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1150,1180p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "guard_git_pointer\|is_repo_dir\|-e \"\$d/.git\"\|/\.git\"" tools/souji-census.sh | sed -n '1,30p'
cd /tmp && cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && grep -n "do_git_config_sequence" -B5 -A5 git-2.56.0/builtin/worktree.c | head -20; grep -n "static int list(int ac" -A 20 git-2.56.0/builtin/worktree.c | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1280,1310p' tools/souji-census.sh && sed -n '1180,1200p' tools/souji-census.sh
cd /var/tmp/souji-r16-ScoutWorktreeConfigDepth && sed -n '1148,1185p' git-2.56.0/builtin/worktree.c && echo ==== && sed -n '72,82p' git-2.56.0/t/t2404-worktree-config.sh && echo ==== && sed -n '56,66p' git-2.56.0/worktree.c && sed -n '227,238p' git-2.56.0/worktree.c
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "never opened otherwise\|config.worktree is read\|depth\" = 0\|extensions:worktreeconfig\|guard_wt_config()\|inherited\|git takes extensions.worktreeConfig" tools/souji-census.sh && grep -n "for rel in config" tools/souji-census.sh && grep -n "count_worktrees\|worktree list --porcelain" tools/souji-census.sh
mkdir -p /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2 && ls -ld /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2
rm -rf /var/tmp/souji-r16-ScoutWorktreeConfigDepth
```

No tool installs or updates were performed.

STATUS: ok
