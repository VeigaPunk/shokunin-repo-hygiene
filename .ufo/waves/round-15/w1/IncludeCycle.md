# IncludeCycle — round 15 w1 critic (operability, calibration)

**Scope:** an attack on cyclic includes, Git max-depth semantics, and conditional-include applicability for the C1 repair of `tools/souji-census.sh`.

**Status: design-only.** `tools/souji-census.sh` is unchanged at HEAD `cc2168325768d5356a82c039dcdf787377c55784`: `git status --porcelain -- tools tests` shows nothing changed. `tests/fixtures/r15-census-config.py` does not exist yet. All census line numbers below refer to HEAD. Git semantics come from upstream source v2.55.0, which matches the installed `git version 2.55.0`: `config.c`, `path.c` `interpolate_path`, `wrapper.c` `access_error_is_ok` and `odb.c`. I also compared against upstream `master`.

**Axes:**
- **Operability:** benign include/includeIf configurations and mixed fleets keep their rows.
- **Calibration:** a refusal or row reflects what Git would actually open or fail on.

v2.55.0 line anchors (`config.c`): `MAX_INCLUDE_DEPTH` :135; relative base `find_last_dir_sep(kvi->filename)` :170; `access_or_die` then `++inc->depth` :177-178; gitdir realpath / absolute retry :254, :287; `unconditional_remote_url = 1` :343, :388; condition prefixes :402-408; "unknown conditionals are always false" :412; condition gate :437. Upstream master `config.c` :403, :406 add `worktree:` / `worktree/i:`. `odb.c` v2.55.0: dedupe via `odb_is_source_usable` :178; `depth + 1 > 5` ignore :194.

## Git facts the repair must match (source, v2.55.0)

**G1. Depth limit.** `MAX_INCLUDE_DEPTH 10`, in `handle_path_include`:
- The order is `access_or_die(path)`, then `++inc->depth > 10`, then `die("exceeded maximum include depth … circular includes")`.
- The depth counts nested include files. `.git/config` is level 0, and Git reads levels 1–10.
- For a level-11 target, Git still calls `access()` on the path, then dies.
- Missing targets (ENOENT/ENOTDIR) are skipped silently and do not count.
- EACCES, ELOOP and other access errors cause a die: `access_error_is_ok` only tolerates missing-file errors when flag=0.

**G2. Cycles have no detection.** Git terminates a cycle only through the depth die. Any reachable active cycle, including `a` including `a`, makes every Git command in that repo fail. The failure is per repo, not per fleet.

**G3. Relative paths.** A relative `include.path` resolves against the directory of the including file's *opened path string* (`find_last_dir_sep(kvi->filename)`), not its realpath.
- `~/` expands from `$HOME`. `~user/` uses getpwnam. `%(prefix)/` uses `system_path`.
- If `HOME` is unset, the expansion error fails the parse and Git dies.
- A valueless `[include] path` is `config_error_nonbool`, which is also a die.

**G4. A disabled condition never touches its target.** In `git_config_include`, `handle_path_include` runs only if `include_condition_is_true(...)` and the key is `path`. Only `include.path` and `includeif.<cond>.path` are includes. `include.<sub>.path` and `includeif.path` with no condition are inert.

**G5. Condition kinds in 2.55.0:**
- `gitdir:` / `gitdir/i:` use wildmatch with `WM_PATHNAME` against the realpath of the gitdir, then retry against the absolute non-resolved path.
- `./` patterns use a literal prefix taken from the realpath of the config file.
- A pattern that is not absolute gets `**/` prepended. A trailing `/` gets `**` appended.
- `onbranch:` resolves HEAD through the ref store. It is false when HEAD is detached or not under `refs/heads/`.
- `hasconfig:remote.*.url:` is covered by G6.
- Any other prefix is "always false". Upstream **master adds `worktree:` and `worktree/i:`**; v2.55.0 lacks them. The semantics therefore change on a Git upgrade.

**G6. `hasconfig` is effectively unconditional.**
- The first evaluation calls `populate_remote_urls`. That function re-reads the whole configuration with `unconditional_remote_url=1`, which makes **every** reachable `hasconfig` include true, so each one is opened.
- A remote URL inside such a file causes a die.
- A guard that evaluates URL matching and declares a non-matching `hasconfig` include "disabled" is an escape.

**G7. Alternates precedent.**
- In `odb.c` (`odb_add_alternate_recursively`), Git de-duplicates sources: `odb_is_source_usable` stops cycles.
- At `depth + 1 > 5` Git only reports `error(... nesting too deep)` and **ignores** the deeper stores.

## Counterexamples against the likely repair, with the smallest correction for each

### IC1 — High (operability, mixed fleet): copying the alternates precedent turns a per-repo Git failure into a fleet-wide exit 2

- **Evidence:**
  - `guard_alternates_file` (`:428-450`) has no visited set. A depth above 5 calls `protected_fail "git-alternates-depth"`, which exits 2.
  - `emit_census` (`:982-988`) exits 2 for the whole fleet on any rc 2, and emits no rows at all.
  - Today a benign include cycle in one child makes `git rev-parse` fail. Through `census_one` (`:859-861`) that child gets an `error` row and the other rows survive.
  - If the repair adds `protected_fail "git-include-depth|cycle"`, one looping repo erases every benign row. That is the same harm class as the r14 rejection.
  - The alternates guard already does this for benign A↔B cycles and for chains deeper than 5, where Git would merely ignore them (G7). Its fan-out is also exponential: k alternates per level means k^6 guard walks.
- **Correction:**
  - Cycle, depth above 10, traversal budget exceeded, nonbool value, or unexpandable `~` → a per-repo `error` row on stdout. Git fails there too (G1–G3).
  - Use `protected_fail` only when a protected target is reachable.
  - Separately (outside the include slice), route alternates cycles and depth above 5 to skip or error instead of exit 2.

### IC2 — High (calibration, namespace): bounding the traversal at depth 10 misses the level-11 `access()`

- **Counterexample:** a chain `.git/inc1` … `.git/inc10`, where `inc10` has `include.path=~/.omp/agent/auth.json`. Git reads levels 1–10, then calls `access()` on the store path (G1) before dying.
  - Under r14's mode-000 synthetic store this is an EACCES. The r14 fixture counts that as forbidden access.
  - The same applies to a cycle that reaches a store path at the 11th step.
- **Correction:** read and scan levels 0–10. Boundary-check every level-11 target **without reading it**. Then emit the per-repo `error` row. Never stop checking at the depth where Git stops reading.

### IC3 — High (calibration): an unbounded or string-memoised recursion either hangs or misses a cycle

- **How it fails:**
  - Without a bound, `a`→`a` recurses forever. With `$(...)` around each level, that is one fork per level until resources run out, and the whole fleet census hangs.
  - Memoising by lexical string never terminates on spellings that grow with each cycle (`sub/../a`, then `sub/../sub/../a`, …).
  - Memoising by realpath is wrong for nested relative includes because of G3. Example: `.git/inc.cfg` is a symlink to `/x/real.cfg` and contains `y.cfg`. Git opens `.git/y.cfg`, not `/x/y.cfg`.
- **Correction:**
  - Use a DFS with a depth bound that mirrors Git (G1, IC2).
  - Memo key: the opened path string after lexically removing only `.` components and `//` (never `..`).
  - Resolve nested relative targets as `dirname(opened string) + value`, then `guard_target`, which already walks `..` physically and bounds symlink hops at 40 (`:396-399`).
  - Add a total visit budget, e.g. 256 files per repo. Exceeding it gives an `error` row, not exit 2.
  - An on-stack revisit of an active include is a definite Git die (G2), so emit an `error` row directly.

### IC4 — High (calibration): treating `hasconfig` as evaluable

G6 means a URL-mismatched `hasconfig` include is still opened.

- **Correction:** always classify `includeIf.hasconfig:remote.*.url:*.path` as active, and boundary-check its closure.
- A benign `hasconfig` include, for example to `~/.gitconfig-work`, stays allowed because only its target's boundary matters. No refusal is based on key presence.

### IC5 — High (calibration): evaluating conditions once per repo instead of once per Git invocation context

- **Evidence:** `count_dirty` runs `git -C "$cpath" status` inside each present linked worktree (`:831-832`). There the gitdir is `<common>/worktrees/<n>` and HEAD is that worktree's own.
- **Counterexamples:**
  - Main HEAD is `main`, and the linked worktree is on `secret`. `[includeIf "onbranch:secret"] path=~/.omp/agent/x` is disabled for main but opened by the worktree status.
  - The same holds for `gitdir:**/worktrees/**`.
  - `guard_git_config` takes only the config directory, not the evaluating context (`:493-495`, called at `:581`, `:613`, `:628`, `:650`, `:665`).
- **Also:**
  - Git never reads `worktrees/<n>/config`. With `extensions.worktreeConfig=true` it reads `config.worktree`: `.git/config.worktree` for main and `worktrees/<n>/config.worktree` for a linked worktree.
  - `guard_git_files` (`:477`) does not cover `config.worktree`.
  - If the repair admits `worktreeConfig`, it must scan `config.worktree` with the same include closure and the same key policy.
- **Correction:** `guard_git_config <cfgdir> <context_gitdir> <context_HEAD>`. Evaluate per context (main plus each linked worktree that gets a status run), and take the union.

### IC6 — Medium (calibration): reftable HEAD stub

- With `extensions.refStorage=reftable`, `.git/HEAD` is a stub (`ref: refs/heads/.invalid`). The real HEAD lives in the reftable.
- A textual HEAD read under-evaluates `onbranch:`, which is an escape.
- **Correction:** if `extensions.refstorage` is set and is not `files`, or HEAD is unreadable, treat `onbranch:` as active.

### IC7 — Medium (calibration): bash pattern matching is not wildmatch, and some gaps under-approximate (escape)

1. Inside `[[ == ]]` the right-hand side is matched "as if extglob were enabled", per the bash manual. A gitdir literally containing `@(a)` is true in Git and false in bash. **Use `case` with `shopt -u extglob`, not `[[ ]]`.**
2. In wildmatch, `/**/` matches zero directories. `gitdir:/f/**/r/` matches `/f/r/.git`, but bash `/f/*/r/*` does not. **Also test the pattern with every `/**/` collapsed to `/`, or treat any `**` in the middle of a pattern as active.**
3. For `./` patterns, Git matches the realpath prefix *literally*. A config directory such as `/fleet/a[1]/.git` makes bash treat `[1]` as a character class, which is an escape. **Quote the prefix: `case $text in "$prefix"$rest)`.**
4. `gitdir/i:` → `shopt -s nocasematch` for that test only.
5. Test both the canonical gitdir and the absolute non-resolved gitdir (G5).
6. A bare `*` matching `/` in bash is a safe over-approximation and is acceptable.

**Rule:** errors may only make a condition look true. Any pattern the guard cannot evaluate exactly counts as active.

### IC8 — Medium (calibration): lowercasing and dot-splitting corrupt the condition

- `keys=${keys,,}` (`:503`) lowercases the subsection. That turns a case-sensitive `gitdir:/Fleet/` into `/fleet/`, so it looks disabled: an escape.
- The condition may contain dots (`gitdir:/f/a.b/`). Git splits the key at the **last** dot (`parse_config_key` uses `strrchr`). A first-dot split misreads `.path` and skips the include.
- **Correction:**
  - Read with `git config --file F --no-includes -z --list`, which keeps names and values NUL-separated and newline-safe.
  - Lowercase only the section and the variable name.
  - Use `${name%.*}` / `${name##*.}`.
  - Iterate every value (`include.path` is multi-valued; `--get` returns only the last).

### IC9 — Medium (operability): value-blind glob over a multi-line key list (current `:504-507`)

- `case "$keys"` matches the whole newline-joined list, and `*` crosses newlines.
- `*include.*` refuses `remote.include.url` and `branch.include.merge`. It also refuses inert `include.<sub>.path` and `includeif.path` (G4).
- `*filter.*.clean*` refuses `filter.lfs.required` + `branch.cleanup.remote`.
- **Correction:** loop over each exact key.

### IC10 — Medium (operability): include target types

- **FIFO:** both Git's `fopen` and the guard's own `git config --file` block forever, and the fleet census hangs.
- **Directory or empty value:** `path =` resolves to the config directory. Git opens it and reads EOF, which is harmless and must not be refused.
- **Missing target:** skipped (G1), and the optional `~/.gitconfig.local` pattern is common. It must not be refused, but its path must still be boundary-checked, because `access()` touches it.
- **Correction:**
  - Boundary-check first.
  - Then: missing → skip. Directory → empty. Regular file → scan, with nlink handled as in `guard_git_files`. Anything else (FIFO, socket, device other than `/dev/null`) → per-repo `error`, before any read.

### IC11 — Low (calibration, forward compatibility): unknown condition prefixes

- In 2.55.0, `worktree:` is unknown and therefore false. Master makes it true.
- **Correction:** treat `worktree[/i]:` as active now, so it is boundary-checked. Leave other unknown prefixes disabled, which is Git's documented behaviour. Record the bound version (2.55.0) in the header.

**Not refused:** disabled `gitdir`/`onbranch` conditions, missing optional includes, `include.<sub>.path`, and `includeif.path` without a condition. That satisfies "don't refuse harmless disabled conditions".

### IC12 — Low (header accuracy)

The header text at `:85-89` must stop listing `include/includeIf` as refused by presence. It should state:
- the depth/cycle/budget → `error`-row mapping;
- the per-context condition evaluation;
- that `hasconfig` is unconditional;
- the residual risks: TOCTOU, and a Git-version binding.

## Acceptance L1 should require (r15 config fixture, same command, baseline red / installed green)

| id | config | baseline (r14) | repaired |
|---|---|---|---|
| inc-benign-rel | `include.path=../.gitconfig` (tracked file in repo) | refused, exit 2 (red) | row emitted |
| inc-missing-opt | `include.path=~/.gitconfig.local` (absent) | red | row emitted, no refusal |
| inc-home-benign | `~/.gitconfig-work` under synthetic HOME | red | row |
| inc-self-cycle | `.git/a.cfg` includes `a.cfg` | red (exit 2) | that repo `error`, other mixed-fleet rows intact, exit 0 |
| inc-ab-cycle | a→b→a | red | as above |
| inc-depth-10 | 10-file chain | red | row (Git accepts) |
| inc-depth-11-store | 10-file chain, then `~/.omp/agent/auth.json` | refused | protected finding, and **zero EACCES in strace under the mode-000 store** (IC2) |
| inc-fanout | 4 includes per level × depth 10 of distinct spellings | — | bounded wall time; `error` row; no hang |
| incif-disabled-store | `includeIf "gitdir:/nonmatch/"` → store path | red | row, no refusal, zero store syscalls |
| incif-onbranch-wt | `onbranch:secret` → store; main on `main`, linked worktree on `secret` | refused | refused/guarded, zero store syscalls (IC5) |
| incif-hasconfig-nomatch | `hasconfig:remote.*.url:https://nomatch/**` → store | refused | refused/guarded (IC4) |
| incif-starstar | `gitdir:/<fleet>/**/r/` matching `<fleet>/r/.git` → store | refused | refused/guarded (IC7.2) |
| incif-case | `gitdir:/<Fleet-mixedcase>/` → store | refused | refused/guarded (IC8) |
| incif-dotted | `gitdir:<fleet>/a.b/` in a repo `a.b` → store | refused | refused/guarded (IC8) |
| inc-fifo | include → FIFO inside `.git` | — | `error` row, no hang, under a bounded `timeout` |
| key-false-pos | `remote.include.url`, `filter.lfs.required` + `branch.cleanup.remote` | red | row (IC9) |
| reftable-onbranch | reftable repo, `onbranch:main` → store | — | guarded (IC6), or SKIP with a stated nonclaim |

Also required:
- The r14 namespace fixture runs unchanged on the installed tool, with all controls green.
- The legacy `--selftest` passes.

## Process disclosure (boundary reminder received mid-run)

- **Whole-lane grep before the reminder.** My first call was `grep` with pattern `(?i)include(If)?|max_?depth|MAX_INCLUDE|cycle` over the whole lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`. That traversal may have read files under `census/operator-sweep-*`.
  - The displayed results (the first 20 files) came only from `.ufo/waves/round-13`/`round-14`.
  - I did not open, quote or rely on any operator-sweep content.
  - I also ran `glob census/round-14*/**`, which enumerates `census/` entries by name.
  - I will not repeat either query.
- **Other shell calls:**
  - `curl` of upstream Git sources (v2.55.0 and master) into `/var/tmp/souji-r15-includecycle-*.c`.
  - `git --version` and `git -C <lane> status/log`.
  - `grep` over the downloaded upstream files.
- **Not done:** I ran no test, fixture, census or Git-behaviour probe. Every Git semantic above comes from reading the source; none was observed at runtime.

**Tools installed or updated:** none.

**Unrun checks:** everything in the Acceptance section above, for L1.
