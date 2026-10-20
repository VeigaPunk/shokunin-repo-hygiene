# RelativePaths — round 15 w1 (config path anchoring, realpath, cwd)

Axes: **operability**, **calibration**. Seat: SoujiR15.RelativePaths (reviewer, leaf).
Scope: source inspection only of `tools/souji-census.sh` (path anchoring for include, attributes, excludes, worktree, cwd, realpath) and the installed git-config(1) manual. No tests, probes, builds, edits, or metadata reads outside the report. No `~/.omp`, no credential file, no `census/operator-sweep-*`, no fleet files opened.

Source state: `tools/souji-census.sh` was clean at HEAD `cc21683` at read time (`git status --short` showed only untracked `.ufo/waves/round-15/`, `census/round-15/`, `census/operator-sweep-20261019/`). The ConfigRepair seat has not landed. Findings below are **design-level acceptance** for that repair, plus defects in the committed round-14 code that the repair touches.

## Method
- Read `souji-census.sh` lines 72–128 (boundary header, env clearing), 165–333 (lexical helpers, protected roots), 333–425 (`resolve_guarded`, `guard_path`, `guard_target`), 456–601 (git link/file/config guards, gitfile, commondir, worktree registrations), 603–672 (`guard_git_surface`), 706–737 (`count_dirty`, `scratch_bytes`), 746–920 (`newest_mtime`, `worktree_extra_flags`, `census_one`).
- git semantics from the installed manual, `zcat /usr/share/man/man1/git-config.1.gz` (roff source lines): include and conditional-include rules at 1074–1124 and 1292–1294; `core.worktree` relative to the `.git` directory at 3654; `config.worktree` locations at 5453–5499.
- Prior round evidence read for context only: `.ufo/waves/round-14/w1/BoundaryAttack.md:41,131–133` (`include.path` made git open a store file on `status`; `filter.x.clean` executed), `BoundaryReviewGit.md:46` (`info/attributes` not nlink-checked), `CensusBoundary.md:102–107,223–229`.

## Verified correct (keep)
1. `core.worktree` relative value anchored to the gitdir (`:511–519`, `$dir/$wt`), matching git-config(1) 3654.
2. Gitfile `gitdir:` relative targets anchored to the owning worktree directory (`:527–541`, `:546–550`).
3. `..` handled physically: `resolve_guarded` pops the already-resolved `acc` (`:369–374`), and symlink targets are folded back into the walk (`:385–403`, 40-hop cap). Consistent with kernel resolution. Only `readlink --` (link text, `:386`) is used; no `readlink -m` or `realpath` binary remains in the file (round-14 A2 is fixed).
4. Environment: all `GIT_*` cleared (`:119`), `GIT_CONFIG_GLOBAL`/`SYSTEM=/dev/null` and `GIT_CONFIG_NOSYSTEM=1` set (`:122–123`). XDG global include files are therefore not read.
5. `count_dirty` neutralizes `core.fsmonitor`, `core.hooksPath`, `core.excludesFile`, `core.attributesFile` on `status` (`:710–712`). `count_worktrees`, `count_unpushed`, and `rev-parse` do not read attributes or excludes.
6. `$PWD` is used only for CLI inputs (`lexical_abs` `:174`, `resolve_guarded` raw input `:348`). Child repos are resolved from `$SHOKUNIN_ROOT`, not cwd.
7. Pre-walk lexical refusal (`:358`, `:382`) means a protected-looking path gets no `lstat` or `readlink` below the store.

## Findings

### F1 — HIGH (calibration, security): symlinked `commondir` content is never checked
- `:614–616` (main gitdir) and `:582–584` (registered worktree admin): when `commondir` is a **symlink**, the code only calls `guard_target git-common-dir "$common"` on the symlink. It never reads the content, never runs `guard_git_links`, `guard_git_files`, or `guard_git_config` on the resolved common dir, and never updates `dir`.
- The regular-file branch (`:617–629`, `:585–594`) does read the content and re-guards the common dir.
- Exploit shape (hostile child): `$GIT_DIR/commondir -> $GIT_DIR/cd.txt`, where `cd.txt` contains a store path. `guard_git_links` (`:464–470`) passes because the link stays inside gitdir. `guard_target` then checks only the `cd.txt` path, not its content. Git follows symlinks when reading `commondir` [INFERENCE: needs git v2.55.0 source check, `setup.c`/`path.c` reading `commondir` via a symlink-following read]. If so, git reads refs, objects, and **config (including includes)** from the store path, and the config key checks never run.
- The repair makes this decisive: the common config is where safe includes and `core.worktree` would live.
- Acceptance: for a symlinked `commondir`, either refuse outright (`git-metadata-symlink`, exit 2), or read the content with the same bounded read as the regular branch and run `guard_git_links`/`guard_git_files`/`guard_git_config` on the result. Apply the same change to `:582–584`.

### F2 — HIGH (operability/calibration): relative include paths anchor to cwd, and the guard API silently does that
- git-config(1) 1076, 1124, 1292–1294: a relative `include.path` is relative to the directory of the **including config file**. `includeIf` conditions do not change that. `./` in a `gitdir:` pattern also means that directory.
- `guard_path` (`:413–417`) and `guard_target` (`:422–426`) both call `resolve_guarded`, which anchors a relative raw input to `$PWD` (`:344`, `:348`). Calling `guard_target include "$value"` with a relative value would check `$PWD/value` while git opens `$GIT_DIR/value`. Current call sites join the anchor first (`:518`, `:623`, `:645`, `:660`, `:591`), so the committed code is correct. The repair is the risk.
- Logical versus physical anchor: for a nested include reached through a symlink, git joins relative paths onto the **logical** path it opened (e.g. `$GIT_DIR/x.inc`), but a physical resolver anchors on the symlink's target directory. A relative include in a file reached through a symlink can therefore name a different file than the one checked.
- Acceptance:
  1. Anchor every include value to the logical directory of the including file as spelled. Never to `$PWD`, `$repo`, or the target's physical directory.
  2. Refuse symlinked **included files** outright (`include-symlink`, exit 2). This removes the logical/physical split for includes. Symlinks under gitdir are already covered by `guard_git_links`.
  3. Refuse `~user/…` (git expands via `getpwnam`; `passwd_home` `:199–205` covers only the current uid). Accept `~/…` only, which expands via `$HOME` and is already in the protected union (`:216–218`).
  4. Enforce a depth limit and cycle check. git's own depth is about 10 [INFERENCE: source check]. Fail closed past the limit.

### F3 — HIGH (operability/correctness): effective `core.worktree` is last-wins across the include chain
- `:511` reads `core.worktree` with `--no-includes --get` from the direct file only. Because includes are evaluated before later lines in the same file, an included file can set `core.worktree` after the direct file. The guard then checks a value git will not use.
- If safe includes are preserved (repair goal), the effective value must come from a full chain walk: own file, every include (per F2), last value wins. Check each `core.worktree` in the chain with `guard_target`.
- Acceptance: a fixture where the direct file sets a safe `core.worktree` and an included file sets a store path must exit 2.

### F4 — MEDIUM (security/calibration): `config.worktree` is never guarded
- `:475–491` checks `config HEAD index packed-refs commondir info/exclude objects/info/alternates`. It omits `config.worktree`. `guard_git_config` (`:493–522`) reads only `$dir/config`.
- With `extensions.worktreeConfig=true`, git reads per-worktree config from the locations documented at git-config(1) 5453–5499 (`$GIT_DIR/config.worktree`; linked worktrees under `$GIT_COMMON_DIR/worktrees/<id>/`). That file can hold `include`, `core.worktree`, and filter keys.
- The repair spec says preserve `worktreeConfig` where safe. Safe is only defined if `config.worktree` is guarded the same way as `config`. Today the key-only refusal of `extensions.worktreeConfig` (`:505`) is the only thing covering this surface.
- Acceptance: if `worktreeConfig=true` is accepted, `config.worktree` (main and per-linked-worktree) must be opened and checked with the F2/F3 rules. If it is not checked, keep `extensions.worktreeConfig=true` refused.

### F5 — MEDIUM (calibration): a `core.worktree` redirect splits the measured tree
- `:511–521` accepts a `core.worktree` that resolves elsewhere (boundary-checked, not refused). `count_dirty` (`:710`) runs `git -C "$repo" status`, which measures the **effective** worktree (git-config(1) 3654).
- `scratch_bytes` (`:724–725`), `newest_mtime` (`:749`, `cd -- "$repo"; find -P .`), and the secret-shaped scan all measure `$repo`. One row would then carry dirty state from one tree and mtime and scratch from another.
- Acceptance: either (a) accept `core.worktree` only when it resolves to the repo directory itself, or (b) keep the redirect and emit an explicit `worktree-redirected` flag that tells the reader the mtime/scratch columns describe `$repo`, not the dirty tree. Do not silently mix them.
- [INFERENCE, acceptance check]: with `core.worktree` set and cwd outside it, git moves to the worktree top, so the `:(exclude).ufo/state` pathspecs (`:713–716`) bind to the effective worktree. Confirm in the fixture; do not assume.

### F6 — MEDIUM (calibration): `info/attributes` is read but not in the guard list
- `:477` omits `info/attributes`. `status` reads it (`count_dirty`, `:712`), along with in-tree `.gitattributes`. Round-14 BoundaryReviewGit P3 (`:46`) recorded this residual.
- Today `filter.*.clean` is refused (`:505`), so attribute-selected filters cannot run. If safe clean filters are preserved (repair goal), `filter=` attributes become an execution selector that the guard does not inspect. Round-14 BoundaryAttack `:131` showed `filter.x.clean` executing on `status`.
- Acceptance: add `info/attributes` to `guard_git_files`. If clean filters are preserved, either refuse any `filter=` attribute in `info/attributes` and in-tree `.gitattributes` (checked by name only, never content), or keep filter drivers refused. Cross-reference AttributesSafe and FiltersSafe; the execution decision is theirs, not this seat's.

### F7 — MEDIUM (operability): `includeIf` must not change the anchor or the check
- Git-config(1) 1292–1294: relative paths are relative to the including file **whether or not the condition holds**. Conditions do not change the anchor.
- Evaluating conditions would mean reimplementing `wildmatch` for `gitdir:`, reading HEAD for `onbranch:`, and reading remote URLs (which may come through includes) for `hasconfig:`. That is more surface than the repair needs.
- Recommended design: check **every** `include.path` / `includeif.*.path` target, regardless of condition. A protected target is refused even when git would never read it. This is over-refusal only for unsafe targets, never for safe ones.
- No-read property: the lexical pre-check (`:358`, `:382`) refuses protected-looking paths before any `lstat` or `readlink`. Only fleet-side symlink hops are read.
- Acceptance: a fixture with a false `gitdir:` condition pointing at a store path must still exit 2, and must show zero `lstat`/`readlink` under the store.

### F8 — LOW (calibration): check-then-use with the resolved result discarded
- `:571`, `:575`, `:584`, `:593`: `guard_target … >/dev/null`, then the raw string is used (`:576–577`, `:579–581`). The round-14 rule (BoundaryAttack A1: "pass that single resolved path to every later call") is not followed here.
- Not exploitable from the code shown. It is inconsistent with the rule the file claims, and it is what a TOCTOU reviewer will flag.
- Acceptance: use the resolved output for every later read, as `gitfile_admin` already does (`:540`).

### F9 — LOW (operability, adjacent): substring key matching
- `:505` matches `*include.*`, `*core.hookspath*`, and so on against the whole newline-joined key list. That is value-blind and key-substring-blind (for example `foo.include.bar` matches).
- Repair: parse `git config --file "$cfg" --no-includes -z --name-only --list` and match exact anchored keys (`^include\.path$`, `^includeif\..+\.path$`, `^filter\..+\.(clean|smudge|process)$`, and so on).
- The `-z` form also handles includeIf subsections containing newlines or tabs.

## Cross-seat notes (not this seat's decision)
- `core.attributesFile` and `core.excludesFile` `-c` overrides neutralize only the global and XDG files. In-tree `.gitignore`/`.gitattributes` and `info/exclude`/`info/attributes` remain. Dirty counts change under `excludesFile=/dev/null` (ExcludesSafe seat).
- Promisor keys and `extensions.partialClone` are outside path anchoring (PromisorSafe seat).

## Residual risk
- F1 and F2 rest on [INFERENCE] about git's `commondir` read and the logical-anchor rule. The source check is not performed here.
- F5's pathspec binding under a redirected `core.worktree` is [INFERENCE].
- The TOCTOU window between guard and git's own open remains documented (CensusBoundary `:98–99`).

## Verification gaps (not run; no probes permitted)
- git v2.55.0 source: `setup.c`/`path.c` handling of `commondir` (symlink follow), include-depth limit, `gitdir:` matching against logical vs physical paths.
- Fixture cases for L1 acceptance (design, not executed):
  - `commondir` symlink to an in-gitdir file containing a store path → exit 2 (F1).
  - Safe relative include `inc/a.inc` in `$GIT_DIR/config` → rows preserved (F2 positive).
  - Included file that is a symlink → exit 2 (F2.2).
  - `~user/x` include and `~/x` include into store → exit 2 and exit 2 respectively, with `~/x` safe elsewhere preserved (F2.3).
  - Included file sets `core.worktree` to a store path after a safe direct value → exit 2 (F3).
  - `extensions.worktreeConfig=true` with `config.worktree` pointing at a store include → exit 2 (F4), and a clean one preserved only if F4 is implemented.
  - `core.worktree` redirect to a sibling fleet worktree → `worktree-redirected` flag or exit 2 (F5).
  - `info/attributes` `filter=` selector → refused or the filter path refused (F6).
  - False `gitdir:` include into store → exit 2 with no `lstat` under store (F7).
- Static checks for L1 after the repair lands: `grep -nE 'readlink -m|realpath' tools/souji-census.sh` → none (expected); `grep -nE 'PWD' tools/souji-census.sh` → only CLI-input call sites.

## Tool installs
None. `zcat` and `awk` were used only to read the installed git-config(1) man page. No package, tool, or binary was installed or upgraded. Per `~/.omp/agent/RULES.md`, no install was needed.

## Query-boundary disclosure (parent reminder)

Whole-lane recursive searches were run before the boundary reminder. They were not scoped to explicit source files:
- `_grep` pattern `realpath|worktree|excludes|attrs|gitattributes|core\.|include` over the whole lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`. Output was truncated at 20 of 242+ files. It returned hits in `census/round-3`, `census/round-6`, `census/round-12`, `census/round-13`, `LOG.md`, `corpus/`, and `.ufo/waves/`.
- `_grep` pattern `value-blind|config refus|refus.*config|includeIf|core\.attributesFile|core\.excludesFile|info/attributes` over the whole lane root. Output was truncated at 44 files. It returned hits in `LOG.md`, `SCORECARD.md`, `census/round-6`, `census/round-3`, `census/round-15`, and `.ufo/waves/`.
- `_bash` `git status --short` and `ls -la` of the lane root. These printed the name `census/operator-sweep-20261019/` as untracked. Its contents were not opened.

Limitation: I cannot confirm that no `census/operator-sweep-20261019/` path appeared in the unseen truncated pages of those two searches. No operator-sweep content was opened, quoted, edited, or relied on. Every finding cites only `tools/souji-census.sh`, the installed git-config(1) man page under `/usr/share/man`, and `.ufo/waves/round-14` and `round-15` files. No further recursive or lane-wide queries were made after the reminder. No runtime probes or tests were run.
