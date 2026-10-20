# Round 15 w1 · WorktreeCfg (reviewer) — extensions.worktreeConfig and config.worktree

Scope: source inspection only. No tests, probes, census runs, edits, or installs. Tools used: `read`, `grep`, `bash` (`man -P cat` on the installed git 2.55.0 pages; `curl` of git v2.55.0 tag sources from raw.githubusercontent.com). Tool installs/updates this seat: none.

Status of source: the repair is not yet in the tree. The current `tools/souji-census.sh` is the round-14 baseline. Findings marked **[BASELINE]** are verified against that file. Items marked **[DESIGN]** are acceptance requirements for the repair and are not verified against code.

## 1. Baseline behavior (BASELINE)

- `tools/souji-census.sh:505` refuses any local config whose lowercased key list contains `*extensions.worktreeconfig*`. The check is value-blind, so `extensions.worktreeConfig = false` is refused. This is the round-14 harm for this family.
- `:500` reads keys with `git config --file "$cfg" --no-includes --name-only --list`. Only key names are read, never values.
- `:493-522` (`guard_git_config`) reads only `"$dir/config"`. `config.worktree` is never parsed, guarded, or refused. No code path in the tool names `config.worktree`; the grep for `config\.worktree` hits only the header and the round-14 docs.
- `:477` (`guard_git_files`) checks `config HEAD index packed-refs commondir info/exclude objects/info/alternates` for nlink and nonregular status. `config.worktree` is not in the list, so a hardlinked or FIFO `config.worktree` passes this guard.
- `:456-471` (`guard_git_links`) does cover a symlink named `config.worktree` under the gitdir, and refuses it if it resolves outside the gitdir. That coverage is already present.
- `:511-520` checks `core.worktree` from `$dir/config` only. A relative value is resolved as `"$dir/$wt"` (`:518`), which matches git (see §2, source point 4).
- Call sites: `:581` (registrations, linked admin), `:613` and `:650` (gitdir, before commondir), `:628` and `:665` (commondir). At `:647-650` the linked admin's `guard_git_config` runs before `commondir` is guarded at `:651-665`.
- `:831` (`worktree_extra_flags`) calls `guard_git_surface "$cpath"` and then `count_dirty` (`:710`, `git -C ... status`) on each linked worktree. Status in a linked worktree reads that worktree's admin `config.worktree`. So the linked admin's `config.worktree` is an execution-time input to every dirty probe.
- `:710-712` status overrides `core.fsmonitor=false`, `core.hooksPath=/dev/null`, `core.excludesFile=/dev/null`, `core.attributesFile=/dev/null` with `-c`. These overrides beat any `config.worktree` value for status. They do not neutralize `include`, `includeIf`, `filter.*`, `core.worktree`, or any key on non-status commands (`worktree list`, `rev-list`, `for-each-ref`, `rev-parse`).
- Header `:87-91` and SKILL.md `:214-218` describe worktreeConfig as refused. Both must change with the repair.

## 2. Git v2.55.0 semantics (primary source, tag v2.55.0)

1. `setup.c:629-630`: `extensions.worktreeconfig` is parsed with `git_config_bool`. Value `false` disables the extension. Invalid values die. A bare key (no `=`) is true.
2. `setup.c:753-766` (`check_repository_format_gently`) and `setup.c:1735-1736` (discovery): the format, and therefore the extension, is read from `get_common_dir(...)/config`, i.e. `$GIT_COMMON_DIR/config`. A linked admin dir's own `config` is not the source for the extension.
3. `setup.c:787-793`: when the extension is on, git reads `"$gitdir/config.worktree"` for `core.bare` and `core.worktree` during discovery. `setup.c:595-600` handles `core.worktree` there (`read_worktree_config`).
4. `setup.c:1157-1166`: relative `core.worktree` is resolved with `chdir(gitdirenv)`. It is relative to the gitdir (common dir for main, `worktrees/<id>` for linked), not to the worktree directory. The census formula `"$dir/$wt"` matches this.
5. `config.c:1553-1566` and `:1593-1596`: git reads `$git_dir/config.worktree` only when `repository_format_worktree_config` is set and the file is readable (`R_OK`). `config.c:2904` is the write-path analogue.
6. `git-config(1)` FILES wording says `config.worktree` is "only searched when extensions.worktreeConfig is present". The source (point 1) uses the value. Calibration note: use the source behavior, not the doc word "present". Treat `false` as off.
7. `git-worktree(1)`: with the extension off, common `core.bare`/`core.worktree` apply to the main worktree only. With the extension on they are read from `config.worktree`. `git-config(1)` says `$GIT_DIR` equals `$GIT_COMMON_DIR` for the main worktree and `$GIT_COMMON_DIR/worktrees/<id>` for linked ones. `git-gitrepository-layout(5)` lists `worktrees/<id>/config.worktree`.

## 3. Access holes in the current design (BASELINE, and what a naive repair would open)

- **H1 config.worktree never guarded.** Once `extensions.worktreeConfig=true` is admitted, git reads `$gitdir/config.worktree` for every census-run status and linked-worktree probe (`:710`, `:831`). Nothing in the baseline scans it. Any key in it runs unchecked. Concrete keys: `include.path`, `includeIf.*.path` (git follows the target file, even under `-c` overrides, so a store path would be read); `filter.*.clean|smudge|process` (status may invoke these); `remote.*.promisor`, `extensions.partialClone`, `core.alternateRefsCommand` (non-status commands). Every one of these is refused in `$dir/config` at `:505` and must be refused in `config.worktree` too.
- **H2 core.worktree in config.worktree unguarded.** The config-file value controls which directory status walks. The baseline checks only common `core.worktree` (`:511-520`). A `config.worktree` value of an absolute path into `~/.omp/agent`, or a relative `../../..` to it, would be honored by status and not checked. `guard_target` (`:422`) would refuse it, but only if it runs on that value. Requirement: run the same `guard_target core-worktree` on the `config.worktree` value, using the gitdir as base.
- **H3 config.worktree hardlink or FIFO.** Not in `guard_git_files` (`:477`). A hardlink to a store file (nlink>1) passes. A FIFO is opened by git's read and can block the census, which the header forbids (`:474`).
- **H4 wrong extension source for linked worktrees (repair hazard).** If the repair reads the extension from `$admin/config` (what `guard_git_config(admin)` reads today), it sees nothing and skips the admin `config.worktree`. Git reads the extension from `commondir/config` (point 2). The repair must resolve and guard `commondir` before deciding. This means reordering `:647-650` against `:651-665`, or reading `$admin/commondir` first.
- **H5 stray config.worktree with the extension off.** Git never reads it (point 5). The census should not open it either. A naive "scan every config.worktree" repair would open it anyway. That is extra read surface but not a hole. The paired fixture should show zero opens.
- **H6 relative core.worktree policy.** The formula is correct (point 4). A relative or absolute value that resolves to a non-protected directory outside the census root is still admitted by the baseline for common config. The repair should keep the same policy for `config.worktree` (no looser path). Decision for SoujiR15: either (a) keep, matching today's common-config behavior, or (b) require the resolved path to be the repo's own worktree or under ROOT. I recommend (b) for `config.worktree` only if the common-config rule is also tightened. Do not split the rule.
- **H7 TOCTOU.** The guard runs before git; git reads `config.worktree` later. This is the existing residual disclosed in the header (`:95-99`). It applies to `config.worktree` as well and must be added to the residual list.
- **H8 core.sparseCheckout in config.worktree.** Not refused, and it makes status read `info/sparse-checkout`, which `guard_git_files` does not cover. Low severity; record as residual or add `info/sparse-checkout` to the nonregular/nlink check.

## 4. Repair acceptance requirements [DESIGN]

A. **Value-aware extension.** `git config --file "$common/config" --no-includes --type=bool --get extensions.worktreeConfig`. Exit 1 (absent) means off. Any other nonzero exit means `protected_fail git-config-unparsed`, exit 2. Let git do the boolean parse, so `1/yes/on/true/bare-key` count as on and `0/no/off/false/empty` as off, with no tool-side reimplementation.
B. **Off → accept without reading config.worktree.** Benign mixed fleets stay admitted. Stray `config.worktree` is not opened.
C. **On → guard each gitdir's config.worktree before git runs.** For main (`$dir == common`) and each linked admin (`$dir/config.worktree`): (i) missing → ok; (ii) symlink → covered by `guard_git_links` (must stay); (iii) regular file with nlink≤1; FIFO/device/socket refused (add to a `guard_git_files`-style check, `git-metadata-hardlink` / `git-metadata-nonregular`); (iv) key scan with `git config --file "$wt" --no-includes --name-only --list`, using the same refusal set as `$dir/config` minus the extension key itself; (v) `core.worktree` read from `config.worktree`, `~` refused, resolved as `$dir/$wt` when relative, then `guard_target core-worktree`.
D. **Ordering.** For linked worktrees, guard `commondir` (and read its extension) before the admin `config.worktree` is scanned (H4).
E. **Non-status commands.** Keys that `-c` does not neutralize (`include`, `filter`, `alternateRefsCommand`, `partialClone`, `promisor`) must be refused in `config.worktree` on every path. The hooksPath/attributes/excludes policy must be the same for `config.worktree` as for common config. Do not create a looser second rule.
F. **Header and SKILL.md.** Replace the refusal list at `:85-91` and SKILL `:214-218` with the value-aware rule. Add the residuals from §3 H7 and H8.

## 5. Fixture requirements for ConfigFixture and AdmissionChecker (paired red/green) [DESIGN]

Baseline (r14, must show red harm): `extensions.worktreeConfig=false` refused (`:505`). Repaired (green): accepted with unchanged rows.

Accept:
- extension absent, `false`, `no`, `off`, `0`, empty string, with `config.worktree` absent or stray (stray not opened).
- extension `true` (or bare key) with a benign `config.worktree` (for example `user.name`, `core.bare=false`) and a relative `core.worktree` that resolves inside the fixture root.
- Mixed fleet: one repo in each state in one census run, with the other repos' rows unchanged.

Refuse (`git-config-unsupported` or `git-config-unparsed` or `git-metadata-*`, exit 2):
- extension `maybe` (invalid); extension `true` with `include.path` in `config.worktree`; `includeIf` in `config.worktree`; `filter.x.clean` in `config.worktree`; `core.alternateRefsCommand` in `config.worktree`.
- `config.worktree` `core.worktree` absolute into the synthetic credential-store path (use a synthetic `.omp/agent` fixture); relative `../../.omp/agent` form; `~`-prefixed.
- `config.worktree` as a hardlink (nlink>1) and as a FIFO. The FIFO case must refuse without hanging.
- Linked worktree admin `config.worktree` with a refused key (proves the admin scan, not just the main repo's).
- Ordering: linked worktree whose common config holds the extension and whose admin `config.worktree` holds `include.path` → refuse (proves H4).

Forbidden access trace: each refusal case must show zero opens of the include target, the store path, and the FIFO. Each repaired-green case must show zero opens outside the fixture root and zero git reads of stray `config.worktree` when the extension is off.

Paired controls: every refusal case has a same-shape benign twin (same file, benign key). A green-only pass is not enough: the twin must be exercised in the same run.

## 6. Send / handoff

Material findings to SoujiR15: H1-H4 and §4 A-D. No edits made to any file outside this report. Checks for L1 after all seats finish: run the §5 fixtures in the same command for r14 red and repaired green; confirm the forbidden-access traces in both.

## 7. Residuals and unrun checks

- Not run: any census invocation, fixture, `git status` probe, or FIFO test (source-only lane).
- Source-verified only: git behavior in §2 is from v2.55.0 source and man pages. Runtime behavior of `git status` filter invocation under `config.worktree` is **[INFERENCE]**: status may run clean filters on racy entries. Not observed.
- Not checked: `info/sparse-checkout` path reads (H8) and the existing round-14 fixture file contents.
- Operator sweep `census/operator-sweep-20261019/` not opened.
- Not opened: `~/.omp/agent` or any credential/auth file.

## 8. Boundary disclosure (correction to §7)

Earlier calls in this seat broke the no-query boundary. Disclosed here; not repeated.

- `read` of the whole lane root `/home/vgpnk/Projects/shokunin/souji-shokunin` (directory listing). The listing showed the names and mtimes of `census/` children, including `census/operator-sweep-20261019/`. Name-level only; contents were not opened by this call.
- `grep` with pattern `config\.worktree|worktreeconfig|core-worktree|guard_git_config|...` over the whole lane root (recursive, gitignore on). It is unscoped, so it may have read files under `census/operator-sweep-20261019/`. The returned hits came from `census/round-12`, `census/round-3`, `corpus/`, `tools/`, and `.ufo/waves/round-14|15`; none came from the operator sweep. The output does not prove the sweep was untouched.

Consequence: §7 "Operator sweep ... not opened" is qualified by this disclosure. No further whole-root reads or searches were made. Source-only findings in §1-§6 rely on explicit paths (`tools/souji-census.sh`, `.ufo/waves/round-15/*`) and git sources fetched from raw.githubusercontent.com.
