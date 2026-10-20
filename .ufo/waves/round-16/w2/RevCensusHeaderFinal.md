# RevCensusHeaderFinal — header contract (lines 1-135) vs code at HEAD

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` @ `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`.
Target: `tools/souji-census.sh` — bytes sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`, unchanged since `0a70bef`
(`git status --porcelain -- tools/souji-census.sh` empty; `git log -1 -- tools/souji-census.sh` = `0a70bef round-16: integrate wave-1 review fixes…`).
Method: **source review only.** No `ALLOWED-EXEC` in this item, so the census was not run, not on the fleet and not on a copy; no fixture was executed.
The only non-source evidence used is (a) the lane's recorded matrix `census/round-16/c1-matrix-landing.json` (read, not re-run), and
(b) authoritative upstream text for three git/bash semantics questions (`/usr/share/doc/bash/NEWS`, `man git-config`, git `config.c`/`repository.c`/`path.c`).

What it attacks: the header's own promises — CLI/roster, the seven TSV columns, `--compare`/`--selftest`, the protected-boundary and config-outcome contracts,
the "Accepted" list, exit codes — against the code that implements them. Verdicts are about the **header/code match**, not about whether the code is otherwise sound.

## Bottom line

| header lines | contract | code | verdict |
|---|---|---|---|
| 2-5 | r14 pre-access boundary; r16 value/effect-aware config guard | 74-129, 608-732, 821-901 | holds |
| 6-11 | toolchain; never fetch / write outside /var/tmp; mtime walk boundary | 150-164, 1074-1125, 1424, 1527 | **partial** — F3, F8 |
| 14-16 | CLI surface | 1839-1855 | **partial** — F9 |
| 17-21 | default scan roster; `--include-root` main-repo rule | 1257-1306 | **fails** — F1, F7 |
| 24-41 | seven TSV columns | 915-933, 1021-1064, 1174-1255 | **partial** — F5, F10 |
| 42-59 | `mtime_iso` pruning; verdict vocabulary/`wt-dirty` | 1068-1125, 1141-1165, 1224-1250 | **fails** — F3; **partial** — F4 |
| 60-72 | `--compare`; `--selftest` | 1339-1478, 1522-1835 | holds |
| 74-96 | boundary inputs, git metadata, config walk | 200-560, 821-901 | **fails** — F2; **partial** — F6 |
| 97-108 | Refused / error-row / status-skipped split | 574-600, 696-711, 1021-1031, 1174-1181 | partial by F2 |
| 109-121 | "Accepted" set | 150-164, 666-686, 942-1018 | holds |
| 122-129 | env clearing, `.omp` parent, residual | 150-164, 246-313 | holds |
| 131-138 | exit codes; `SHOKUNIN_ROOT` default | 173, 1310-1311, 1864-1882 | holds |

Ten items below: three contract breaches (F1-F3), four under-documented behaviours (F4-F7), three document nits (F8-F10).
Every other sentence in lines 1-135 matched the code at the line level; the explicit checks are in "Claims verified as matching".

## F1 — MEDIUM — `--include-root` emits a row for a linked-worktree / submodule-gitfile root, which the header excludes

Header 19-21:

```
# not emitted as their own row. --include-root also emits a row for the root
# itself when it is a main repo.
```

Code `list_repos:1261-1271`:

```
1261  if [ "$INCLUDE_ROOT" = 1 ] && [ "$ROOT_RAW_IS_SYMLINK" = 0 ] && [ -d "$root" ]; then
1262    g="$root/.git"
1263    if [ -L "$g" ]; then
1264      guard_target git-metadata "$g" >/dev/null
1265    elif [ -f "$g" ]; then
1266      guard_git_surface "$root" || true
1267      REPOS+=("$root")
1268    elif [ -d "$g" ]; then
```

Counterexample: a benign linked worktree `W` (`W/.git` = `gitdir: <owner>/.git/worktrees/W`, nothing protected).
`tools/souji-census.sh --root "$W" --include-root` → 1265 true → `REPOS+=("$W")`. `census_one` passes every filter
(`1183` `.git` is not a symlink, `1187` it exists, `1194` `rev-parse --is-inside-work-tree` is true) and measures `W`,
so stdout carries a row whose `repo` is a linked worktree — contradicting both "not emitted as their own row" (19-20)
and "when it is a main repo" (21). The r14 fixture does not pin the benign case: its `gitfile` case (`tests/fixtures/r14-census-boundary.py:240-242,584-587`)
points `.git` at the protected agent gitdir, so it refuses at 874/1266 before the row decision.

Verdict: **fails** (contract). Smallest fix — the behaviour (a caller explicitly names a worktree root and asks for its row)
is defensible, so amend the header; this is zero-risk for the 20/20 matrix:

```diff
-# not emitted as their own row. --include-root also emits a row for the root
-# itself when it is a main repo.
+# not emitted as their own row by the default child scan. --include-root also
+# emits a row for the root itself when it is a repository (including a root
+# whose .git is a gitfile, which is emitted only because the caller named it).
```

If the current text is the intended contract instead, delete `1265-1267` (`elif [ -f "$g" ] … REPOS+=`) and a gitfile
root degenerates to a header-only run, which is what "when it is a main repo" says.

## F2 — MEDIUM — `config.worktree` is gated by the linked admin's own `config`, though the header says the common config decides

Header 90-93: relative include targets resolve against the spelled dir "and through `config.worktree` when the
**common config's** extensions.worktreeConfig is true."

Code `guard_git_surface:871-895` (`.git`-file branch) runs `guard_git_config "$dir"` on the *admin* directory before the
commondir is known:

```
871    dir=$(guard_target gitdir "$target") || exit 2
872    guard_git_links "$dir" || exit 2
873    guard_git_files "$dir" || exit 2
874    guard_git_config "$dir" || soft=1
875    first=$dir
876    common="$dir/commondir"
...
892        guard_git_config "$dir" || soft=1
893        guard_wt_config "$first" || soft=1
```

With no `$2`, `guard_git_config:717-726` scans `$dir/config`; `scan_config_file:666-675` sets `CFG_WT_ENABLED=1` from a
depth-0 `extensions.worktreeConfig`, and `guard_git_config:730` then calls `guard_wt_config "$dir"`, which opens
`<admin>/config.worktree` (only a `-L` check precedes it, 699-701).

That admin `config` is **not** repository config: git reads the repo config file from `$GIT_COMMON_DIR/config`
(`repository.c:259-266`, `read_repository_format_from_commondir`, builds `<commondir>/config`; `path.c:119` lists
`config` in `common_list`). So the header's "common config's extensions.worktreeConfig" rule is violated in both directions:
an unread file is scanned, and its flag can force the admin `config.worktree` open.

Counterexample: owner repo `R` with linked worktree `W` (`R/.git/worktrees/W/`), common `R/.git/config` without
`[extensions]`; create `R/.git/worktrees/W/config` = `[extensions]\n\tworktreeConfig = true` and
`R/.git/worktrees/W/config.worktree` = `[include]\n\tpath = ~/.omp/agent/x.gitconfig`. Census of `R`: the owner pass inherits the common value (`guard_worktree_registrations:792` passes it as `$2`, restored at
`guard_git_config:727-729`), so that pass is correct — but `worktree_extra_flags:1156` re-guards `W` and hits 874 with no
inherited value → `scan_config_file:666-675` sets 1 → 730 opens `config.worktree` → 643 `guard_config_path` sees the
protected include → whole run exits 2 with `path-protected: include-protected`,
for a file git never reads. (Same for a crafted `<admin>/config` carrying `include.path` directly.)

Verdict: **fails** (narrow input, whole-run blast radius). Overlaps `RevCensusSurfaceFinal` F2; this item is the header-contract half.
Minimal fix — scan the admin config only when it *is* the common config (no commondir):

```diff
@@ guard_git_surface, .git-file branch
-    guard_git_config "$dir" || soft=1
     first=$dir
     common="$dir/commondir"
+    local has_common=0
     if [ -f "$common" ]; then
       IFS= read -r target < "$common" || target=""
       ...
       if [ -n "$target" ]; then
         ...
         guard_git_config "$dir" || soft=1
         guard_wt_config "$first" || soft=1
+        has_common=1
       fi
     fi
+    if [ "$has_common" = 0 ]; then
+      # No commondir: $GIT_COMMON_DIR falls back to the admin dir, so its
+      # config is git's extension source and config.worktree is read.
+      guard_git_config "$first" || soft=1
+    fi
```

## F3 — LOW-MEDIUM — the mtime walk prunes `.ufo/state`/`.ufo/watchdog.log` only at the work-tree root

Header 10-11 ("`.ufo/state` or `.ufo/watchdog.log` are never traversed by the mtime walk") and 43-45
(".git, .ufo/state, and .ufo/watchdog.log are pruned and never stat'd. census/operator-sweep-* is pruned the same way").

Code `newest_mtime:1074-1078`:

```
1074  raw=$(cd -- "$repo" && find -P . \
1075      \( -name .git -o -path './.ufo/state' -o -path './.ufo/watchdog.log' \
1076         -o -path './census/operator-sweep-*' \
1077         -o -path '*/census/operator-sweep-*' \) -prune \
```

`./.ufo/state` and `./.ufo/watchdog.log` are root-relative only, while the sibling `census/operator-sweep-*` has a
`*/` (any-depth) form. Counterexample: a repo containing `sub/.ufo/state/live.json` (mtime in the future) — find visits it,
`-printf '%T@ %P\0'` (1078) stats it, and `mtime_iso` becomes that future time. The census's own boundary treats any
`.ufo/state` component as protected (`protected_component_reason:329-342`), and the same list already prunes
`*/census/operator-sweep-*`, so the walk is narrower than the contract it documents.

Verdict: **fails** (narrow, but the sentence is unconditional). Minimal fix — add the any-depth forms:

```diff
       \( -name .git -o -path './.ufo/state' -o -path './.ufo/watchdog.log' \
+         -o -path '*/.ufo/state' -o -path '*/.ufo/watchdog.log' \
          -o -path './census/operator-sweep-*' \
          -o -path '*/census/operator-sweep-*' \) -prune \
```

No-behaviour-change alternative: qualify both header sentences to "the repository-root `.ufo/state` and
`.ufo/watchdog.log`". The `count_dirty` pathspecs (1038) have the same root-only shape for `.ufo/state`; if L1 takes the
code fix here, mirror it with `:(exclude,glob)**/.ufo/state` / `**/.ufo/watchdog.log` there for consistency.

## F4 — LOW — `wt-dirty` is set for more than "its own `git status --porcelain` is non-empty"

Header 57-58:

```
#                   wt-dirty: a non-main worktree directory is present and its
#                     own `git status --porcelain` is non-empty.
```

Code `worktree_extra_flags:1141-1165` sets `wt-dirty` without running status when the directory is present but
`cpath/.git` is a symlink (1145-1148), is missing (1150-1154), or the worktree's config cannot be evaluated
(1156-1160); it also sets it when status ran but was `unverifiable` (1162-1165).

Counterexample: a linked worktree with a `filter.<name>.clean` bound to a tracked path → `count_dirty` prints the
`status-skipped: filter-driver-bound` diagnostic and returns `unverifiable` (1027-1031) → `wt-dirty`, though no
`status --porcelain` line exists because status was not run. The same row can also carry `clean` (1239 excludes
`wt-dirty`/`status-unverifiable` at repo level only via the main work tree).

Verdict: **partial** (code is fail-closed; the header is narrower than the behaviour). Smallest fix — header only:

```diff
-#                   wt-dirty: a non-main worktree directory is present and its
-#                     own `git status --porcelain` is non-empty.
+#                   wt-dirty: a non-main worktree directory is present and its
+#                     own status is non-empty, or could not be verified/runs
+#                     unsafely (unverifiable, status-skipped, config-unsupported,
+#                     or a .git that is a symlink/missing).
```

## F5 — LOW — the `dirty` column is a *paths-pec-excluded* status line count, not the documented plain `git status --porcelain` count

Header 35-39 says `dirty` is the "`git status --porcelain` line count", with only `--ignore-submodules=all` noted.
Code `count_dirty:1035-1041` adds four exclusions:

```
1035  if ! st=$(git -C "$1" --no-optional-locks -c core.fsmonitor=false \
1036      -c core.hooksPath=/dev/null -c core.excludesFile="$ex" \
1037      -c core.attributesFile="$at" status --porcelain --ignore-submodules=all -- . \
1038      ':(exclude).ufo/state' ':(exclude).ufo/watchdog.log' \
1039      ':(exclude,glob)census/operator-sweep-*' \
1040      ':(exclude,glob)census/operator-sweep-*/**' \
1041      ':(exclude,glob)**/census/operator-sweep-*' 2>/dev/null); then
```

Counterexample: a tracked file under `census/operator-sweep-x/` (or a tracked `/.ufo/state/live.json`) modified.
`git status --porcelain | wc -l` = 1; the census reports `dirty=0` (and may emit `clean`). Likewise a wholly untracked
`.ufo/state/` is not "one line", it is zero lines. `souji-verify.sh:322` (the "matching souji-verify" reference for
untracked mode) runs `status --porcelain` with no pathspecs, so the two tools differ exactly here.

Verdict: **partial** (deliberate — status must not walk operator surfaces — but undocumented in the dirty definition).
Smallest fix — header after 39:

```diff
#                   not added into this number; see wt-dirty. Submodule
#                   content is not inspected (--ignore-submodules=all).
+#                   The four operator surfaces (.ufo/state, .ufo/watchdog.log,
+#                   census/operator-sweep-* at any depth) are pathspec-excluded,
+#                   so tracked edits there never contribute a line.
```

## F6 — LOW — "any git-metadata symlink must resolve inside its own gitdir" is not the rule for `config`, `config.worktree`, `objects/info/alternates`

Header 84-87: "…objects/info/alternates are boundary-checked before git runs, and any git-metadata symlink must
resolve inside its own gitdir …". `guard_git_links:508-513` implements exactly that (inside-gitdir target admitted).
But three sites refuse a symlink outright, whatever its target:

- `guard_git_config:718-719` (`config`),
- `guard_wt_config:699-701` (`config.worktree`),
- `guard_alternates_file:477-481` (`objects/info/alternates`).

Counterexample: `repo/.git/config -> config.real` (regular file in the same `.git`). `guard_git_links` folds and admits it;
`guard_git_config` then exits 2 with `path-protected: git-metadata-symlink`, and the whole fleet run dies although no
protected root is reached. Same for an in-gitdir `config.worktree`.

Verdict: **partial** (fail-closed over-refusal; the header's test is not the test the code applies).
Overlap: `RevCensusSurfaceFinal` F1 proposes the code fix (fold the link with `guard_target`, keep reading the spelled path);
this item is the header half. Smallest header-only fix, after "its own gitdir" (86):

```diff
-#   git-metadata symlink must resolve inside its own gitdir (these r14
+#   git-metadata symlink must resolve inside its own gitdir, except that
+#   config, config.worktree and objects/info/alternates are refused when
+#   symlinked at all (these r14
```

## F7 — LOW — the default-scan roster omits the name filters

Header 17-19: "Default scan: every immediate child … whose .git is a directory". Code `list_repos:1274-1282` skips
dot-prefixed children and children containing TAB/CR/LF before the `.git` test:

```
1274  for d in "$root"/*; do
1275    base=${d##*/}
1276    # skip dot-dirs (operator config, .ufo, .scratch) and unrepresentable names
1277    case "$base" in
1278      .*) continue ;;
...
1280    case "$base" in
1281      *$'\n'*|*$'\t'*|*$'\r'*) continue ;;
```

(`*` globbing already omits dot names; the explicit case at 1277-1279 documents the intent.)
Counterexample: `<root>/.archive-repo/.git/` exists and is a main repo; it is silently absent from the census with no
diagnostic and no `error` row, although the header says "every immediate child".

Verdict: **partial** (silent omission; selftest asserts it at 1639-1641, header never says it). Smallest fix — header
after 19:

```diff
# gitfile). Linked work trees are counted on their owner via `worktree list`,
+# Children whose names begin with `.`, or contain TAB/CR/LF, are skipped
+# (operator-shaped and unrepresentable in the TSV).
```

## F8 — NIT — "bash + coreutils + git only" is not the dependency set

Header 7. The script also requires `awk` (`usage:183`, `passwd_home:247`, `newest_mtime:1079`), `find`
(`guard_git_links:502,514`, `newest_mtime:1074`), `grep` (`count_worktrees:917`, `count_unpushed:924`, `count_dirty:1046`),
and optionally `getent` (`passwd_home:246-247`, guarded). `find`/`grep`/`awk` are not coreutils, and `newest_mtime` has
no fallback if `awk` is missing. Minimal fix, header line 7:

```diff
-# One bash tool; bash + coreutils + git only. Never fetches, never writes
+# One bash tool; bash, coreutils, findutils, grep, awk and git only (`getent`
+# is optional and guarded). Never fetches, never writes
```

## F9 — NIT — CLI synopsis omits accepted forms (and `--` silently drops trailing arguments)

Header 14-16 lists `[--root DIR] [--compare PREV.tsv] [--include-root] [--selftest]`. `main:1839-1855` also accepts
`--root=DIR` (1846), `--compare=FILE` (1850), `-h|--help` (1851), and `--` (1852), which `break`s and **ignores** any
following operands. Minimal fix — header 15:

```diff
-#   tools/souji-census.sh [--root DIR] [--compare PREV.tsv]
-#                         [--include-root] [--selftest]
+#   tools/souji-census.sh [--root DIR|--root=DIR]
+#                         [--compare PREV.tsv|--compare=PREV.tsv]
+#                         [--include-root] [--selftest] [-h|--help] [--]
```

## F10 — NIT — `scratch_bytes` zero conditions are narrower than the code

Header 40-41: "0 if absent or a symlink". `scratch_bytes:1050-1053` also returns 0 when `.scratch` exists but is not a
directory (regular file, FIFO, …). One-word header fix: "0 if absent, a symlink, or not a directory".

## Claims verified as matching the code (no finding)

- `worktrees` = `git worktree list` line count (`count_worktrees:915-919`; non-porcelain output quotes odd paths, so one line per entry).
- `unpushed` = `rev-list --count --branches` when zero `refs/remotes/*`, else `… --branches --not --remotes`
  (`count_unpushed:921-933`); `no-remote` + count + `unpushed` all emitted, `clean` suppressed (`census_one:1216-1217,1233-1239`).
- `dirty` on the main work tree only, default untracked mode (whole directory = one line), `--ignore-submodules=all`
  (`count_dirty:1035-1046`) — apart from F5's exclusions.
- `scratch_bytes` uses `du -sb -P` and never follows a symlink (`1049-1064`) — apart from F10.
- `mtime_iso`: newest `-type f` mtime, `%T@` truncated to seconds, `date --iso-8601=seconds` (numeric offset)
  (`1074-1115`); secret-shaped components excluded from the max and flagged (`1081-1103,1118-1121`); contents never opened.
- Verdict vocabulary and order exactly as 51-52 (`census_one:1244`); `clean` only when `unpushed=0`, `dirty=0`, a remote
  tracking ref exists, and no `status-unverifiable`/`error`/`not-a-repo` (`1233-1239`); `no-remote` blocks a false `clean`.
- `--compare`: first line must equal the 7-column header (`load_census:1339-1392`), one row per changed field
  (`emit_compare:1443-1471`), `added`/`removed` rows with `ABSENT`/`PRESENT` (`1449-1460`), exit 0 header-only / 3 drift
  (`1474-1478`, `emit_compare` returns 3 → shell status 3 under `set -e`), fresh census written to `/var/tmp` and removed
  (`1424-1431`), so rows never mix into the diff.
- `--selftest`: fixtures under `mktemp -d /var/tmp` with EXIT cleanup (`1527-1528`), two byte-identical runs
  (`1585-1600`), mutation/compare and malformed-baseline checks (`1745-1797`), protected-boundary checks (`1766-1793`),
  exit 0/1 (`1832-1834`); the header's description is a subset of what it checks.
- Protected inputs: `--root`/`--compare` resolved before any census command (`1864-1865`, `guard_path:457-461`),
  `..` component refused as `ambiguous-path` (384-387), HOME ∪ passwd home plus `PI_CODING_AGENT_DIR` and
  `<home>/${PI_CONFIG_DIR:-.omp}/agent` (`build_protected_roots:257-313`), `.omp/agent` / `census/operator-sweep-*` /
  `.ufo/state|.ufo/watchdog.log` component refusal (`protected_component_reason:318-341`), `path-protected` + exit 2 +
  `<protected>` masking (`protected_fail:200-208`), symlinked roots/children skipped (`1286-1292`, `ROOT_RAW_IS_SYMLINK` 1312-1313).
- git-metadata ordering: gitfile gitdir, commondir, `objects/info/alternates` and worktree registrations are guarded before
  the first `git` measurement (`guard_git_surface:821-901`, `guard_alternates_file:472-494`, `guard_worktree_registrations:766-815`);
  the `commondir` symlink is read through `guard_target` as git does (877-879, 835-837).
- Config walk is per key/value and recursive in file order: `include.path`/`includeIf.*.path` both handled
  (`639-648`), every includeIf target guarded whatever the condition, relative targets based on the spelled including
  file (`expand_config_path:565-574`, `scan_config_file` `$4`), depth/cycle (`610-614`), NUL/unparsable (`615-620`),
  non-regular/hardlinked include or `config.worktree` soft (`guard_config_file_kind:587-596`, `704`), invalid
  `extensions.worktreeConfig` bool soft (`666-676`), config-named path overlap → exit 2 (`guard_config_path:542-559`),
  and a soft finding never stops the scan before a later protected reach (`soft=1; continue`, then `protected_fail`).
- "Accepted" set: `core.hooksPath`/`core.fsmonitor` are never parsed by the scan and every call carries
  `core.fsmonitor=false`/`core.hooksPath=/dev/null` via `GIT_CONFIG_COUNT` (`150-164`, plus `-c` on status `1035-1036`);
  `GIT_NO_LAZY_FETCH=1` (`161`); no census command consumes `core.alternateRefsCommand` (no fetch/receive-pack/
  `--alternate-refs`); unbound filter drivers are inert — `guard_bound_filters:983-1018` skips status only when
  `check-attr` names a configured driver, and the lane's matrix records `R15CFG-13` as an exact `CLEAN` row on bash 5.3.20
  (`c1-matrix-landing.json`); missing include targets are benign (git only includes when `!access_or_die(path, R_OK, 0)`,
  `config.c handle_path_include:144-190`).
- `:(optional)` is stripped for `core.excludesFile`/`core.attributesFile`/`core.worktree` (`status_info_file:947`, `scan_config_file:651-657`)
  and correctly **not** stripped for `include.path` (git strips it only in `git_config_pathname` for pathname variables,
  `config.c:1326-1341`; `handle_path_include` calls `interpolate_path` directly) — the code comment at 529-531 is right.
- Global/system config disabled and every inherited `GIT_*` shell variable unset (`150-155`); `.omp` parent resolution is
  stat/readlink only, with the store name pre-seeded (`300-313`); documented hardlink residual matches the code
  (`load_census:1356-1369`, `guard_git_files:519-535`).
- Exit codes 0/1/2/3 and `SHOKUNIN_ROOT` default = parent of the repo (`173`): usage/malformed baseline 2, protected 2,
  setup (missing git/du, non-directory root, census subcommand failure) 1, compare drift 3.

## Residual risk / verification gaps

- Static review only: no census invocation, so every exit-code path above is control-flow reading, not an observed run.
  The only observed results cited are the lane's recorded matrix rows (read from `census/round-16/c1-matrix-landing.json`).
- "`.ufo/state … never stat'd`" (header 43-44) is platform-dependent even at the root: `-prune` stops descent, but `find`
  must `lstat` the entry itself on filesystems without `d_type`; on this host (btrfs/ext4) it does not. Not counted as a finding.
- `not-a-repo` in the vocabulary (52) is unreachable through `list_repos` (symlinked/missing `.git` are filtered before
  `REPOS`); only a race between `list_repos` and `census_one` can emit it. Defensive, not a contract breach.
- `--` at 1852 silently discards trailing operands (`break`); noted with F9, not separately ranked.
- F2's premise (repo config = `<commondir>/config`) is from git `repository.c:259-266` and `path.c:119`, not from an
  executed `git` in this review.
- Findings F1/F2/F3/F5 were not covered by any peer report at the time of writing (`RevCensusSurfaceFinal` covers F6's code
  half and F2's code half; `RevCensusStatusFinal`/`RevCensusScanFinal` had no report on disk yet).

STATUS: ok

## Commands

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh && wc -l /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
ls /usr/share/doc/bash/ 2>/dev/null; ls /usr/share/doc/bash*/ 2>/dev/null | head -40
grep -n -i -B3 -A6 'process substitution' /usr/share/doc/bash/NEWS | head -80; echo ---; head -12 /usr/share/doc/bash/NEWS
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'include-root|main repo|not emitted|wt-dirty:|never stat|pruned|secret-shaped|status-unverifiable|worktree list|rev-list|scratch_bytes|du -sb|mtime_iso|Linked work|gitfile|symlink|Exit codes|^#   0|^#   1|^#   2|^#   3' tools/souji-census.sh | sed -n '1,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'list_repos|INCLUDE_ROOT|ROOT_RAW_IS_SYMLINK|newest_mtime|worktree_extra_flags|count_dirty|status_info_file|guard_bound_filters|count_worktrees|count_unpushed|scratch_bytes\(\)|guard_config_file_kind|guard_wt_config|scan_config_file' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '' tools/souji-census.sh | sed -n '70,100p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '' tools/souji-census.sh | sed -n '100,140p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '' tools/souji-census.sh | sed -n '1257,1310p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '' tools/souji-census.sh | sed -n '1068,1100p;1127,1170p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '' tools/souji-census.sh | sed -n '500,516p;694,732p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '' tools/souji-census.sh | sed -n '936,1048p'
ls -l /usr/share/man/man5/git-config.5.gz /usr/share/man/man1/git-config.1.gz 2>/dev/null; ls /usr/share/doc/git 2>/dev/null | head
zcat /usr/share/man/man1/git-config.1.gz | col -b 2>/dev/null | grep -n -i -B4 -A10 'optional' | sed -n '1,80p'
zcat /usr/share/man/man1/git-config.1.gz | col -b 2>/dev/null | sed -n '1480,1532p'
zcat /usr/share/man/man1/git-config.1.gz | col -b 2>/dev/null | grep -n -A22 '^ *include\.path' | sed -n '1,60p'
zcat /usr/share/man/man1/git-config.1.gz | col -b 2>/dev/null | grep -n -B2 -A20 'include\.path' | sed -n '1,70p'
zcat /usr/share/man/man1/git-config.1.gz | col -b 2>/dev/null | grep -n -i 'includeif\|conditional include\|include\b' | sed -n '1,40p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -B3 -A12 'GF_REPO *=' tests/fixtures/r14-census-boundary.py | sed -n '1,50p'; echo ---; grep -n -A12 'def refusal_problems' tests/fixtures/r14-census-boundary.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'include-root|wt-dirty|wt-absent|status-unverifiable' tests/fixtures/r14-census-boundary.py | sed -n '1,40p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '' tests/fixtures/r15-census-config.py | sed -n '906,960p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'include-root' tests/fixtures/r14-namespace-census.py tests/fixtures/r15-census-config.py 2>/dev/null | sed -n '1,30p'; echo ---MISSING---; grep -n -i 'missing' tests/fixtures/r15-census-config.py | sed -n '1,30p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'filter|status-unverifiable|unbound' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'optional|include' tests/fixtures/r15-census-config.py | sed -n '1,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E '^CLEAN|def positive_problems|def single_positive|def run_tool' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '' tools/souji-census.sh | sed -n '1180,1256p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git status --porcelain -- tools/souji-census.sh corpus/SOURCES.md 2>/dev/null | sed -n '1,10p'; git log -1 --format='%H %s' -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '' tools/souji-census.sh | sed -n '1,13p;480,496p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '' tools/souji-census.sh | sed -n '866,896p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '' tools/souji-census.sh | sed -n '1832,1862p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'getent|awk .*NR|command -v git|command -v du' tools/souji-census.sh | sed -n '1,12p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E '^ROOT=|GIT_NO_LAZY_FETCH=|GIT_CONFIG_COUNT=|GIT_CONFIG_GLOBAL=|GIT_OPTIONAL_LOCKS=|compgen -v GIT_|export XDG_CONFIG_HOME|mktemp /var/tmp|mktemp -d /var/tmp' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E '^(emit_compare|load_census|field_at|numeric_change|run_selftest|usage|emit_census|count_unpushed|newest_mtime|worktree_extra_flags|census_one|scratch_bytes)\(\)|^while \[ "\$#"|^# --- compare|^# --- selftest|^# --- main' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'rev-list|for-each-ref|refs/remotes|status --porcelain|untracked|no-remote|unpushed' tools/souji-verify.sh | sed -n '1,40p'
```

Non-shell reads (tool-level, for the semantics checks only): `read` of `census/round-16/c1-matrix-landing.json`
(`.arms.changed["r15-config"]`, `.arms["r15-baseline"]`), and `grep` over
`https://raw.githubusercontent.com/git/git/master/{config.c,repository.c,path.c}`.
