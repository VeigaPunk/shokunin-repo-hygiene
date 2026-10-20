# WorktreeFlow — `extensions.worktreeConfig` / `config.worktree`: true safe requirements and access holes

Seat: reviewer, r15 w1. **Source inspection only** — no tests, no probes, no executions
against fixtures. Tool under review: `tools/souji-census.sh`, 1539 lines,
sha256 `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9`.
The r15 value-aware repair is not present at that digest (ConfigRepair owns the file), so
the repair-dependent parts below are labelled **design-only**. Primary docs: local git 2.55
man pages `git-config(1)`, `git-worktree(1)`, `git(1)` (observed, quoted).

## 1. Observed current behaviour (facts at that digest)

1. `guard_git_config` (493–522) reads only `$dir/config`; the key scan at 504–507 refuses
   any key matching `*extensions.worktreeconfig*`. Refusal is **key-presence only**, so
   `extensions.worktreeConfig = false` refuses exactly like `= true`.
2. `config.worktree` appears nowhere in the tool. Grep for `config.worktree`/`worktreeconfig`
   yields only the header (87–88), the key scan (505) and the unrelated `core.worktree`
   value read (511). No per-worktree config file is lstat'ed, parsed, or key-scanned.
3. `guard_git_files` (475–491) covers a fixed set — `config HEAD index packed-refs
   commondir info/exclude objects/info/alternates` — and **not** `config.worktree`.
   Symlink/hardlink/non-regular checks therefore never apply to it.
4. `guard_git_links` (456–472) refuses only symlinks that resolve outside the gitdir; an
   in-gitdir symlink passes.
5. `guard_worktree_registrations` (555–600) already walks `$dir/worktrees/*`, resolves each
   `gitdir` to its admin directory (577) and guards admin `files/links/config` (578–581)
   *before* `git worktree list` (688, 836) and before per-worktree `git status` (831–832).
6. Status neutralizers exist at 710–712: `-c core.fsmonitor=false -c core.hooksPath=/dev/null
   -c core.excludesFile=/dev/null -c core.attributesFile=/dev/null`. `git(1)` on `-c`: the
   value "will override values from configuration files", so these also neutralize values
   placed in `config.worktree`.
7. Guard ordering is already correct for this lane: `census_one` calls `guard_git_surface`
   first (847), before `rev-parse --is-inside-work-tree` (859), `count_worktrees` (866) and
   `count_dirty` (871); `worktree_extra_flags` re-guards each present worktree (831) before
   its status (832). A `config.worktree` check placed inside the guard therefore precedes
   every git read — provided it is not bolted onto `count_dirty`.
8. No committed evidence covers config-family refusal or preservation. `r14-census-boundary.py`
   has 12 namespace cases only (`EXPECTED_IDS` 44–57, `CASES` 629–646); the tool's `--selftest`
   has no config-key case. This is a calibration hole larger than worktreeConfig alone.

## 2. Official semantics (observed, git 2.55)

- `git-config(1)` FILES order: system → global → `$GIT_DIR/config` →
  `$GIT_DIR/config.worktree` ("This is optional and is only searched when
  `extensions.worktreeConfig` is present in `$GIT_DIR/config`") → `-c` overrides all files.
- `git-config(1)` `worktreeConfig`: worktrees load `$GIT_DIR/config.worktree` **in addition
  to** `$GIT_COMMON_DIR/config`; its settings override other config files; `$GIT_DIR` equals
  `$GIT_COMMON_DIR` for the main worktree and `$GIT_COMMON_DIR/worktrees/<id>/` for linked
  worktrees. When enabling it, `core.worktree` ("must be moved") and a true `core.bare`
  belong in the main worktree's `config.worktree`.
- `git-config(1)`: "For historical reasons, this extension is respected regardless of the
  `core.repositoryFormatVersion` setting." → **gating on version 1 is wrong** in both
  directions (a v0 repo still reads `config.worktree`; refusing v0 worktreeConfig refuses a
  real configuration).
- `git-config(1)` Values/boolean: true = `yes|on|true|1` or no `=value`; false =
  `no|off|false|0` or the empty string; case-insensitive; `--type=bool` validates and
  canonicalizes (invalid value is an error, not false).
- `git-worktree(1)`: `config.worktree` is read **after** `.git/config`; with the extension
  disabled, common `core.bare`/`core.worktree` apply to the main worktree only.
- `core.worktree` relative base: "relative to the path to the .git directory"
  (`git-config(1)`).

## 3. True safe requirements (design-only)

- **R1 — value, not presence.** Unset or a false-family value (`false/no/off/0/empty`) means
  the extension is inactive: `config.worktree` is inert even if present and hostile, and the
  row must be preserved. A true-family value activates the per-worktree read.
- **R2 — activation source.** Read the flag from the repository config git actually uses
  (`$GIT_COMMON_DIR/config`), never from `config.worktree` itself; a per-worktree file cannot
  enable or disable its own read (FILES doc). A boolean-parse failure is **not** a refusal:
  git cannot use such a repo, so the honest row is `error`, consistent with today's handling
  of unusable repos; guard `config.worktree` defensively in that indeterminate case
  (**design choice, declared**).
- **R3 — guard every file git will read.** For each worktree gitdir that a command will
  initialize — the main gitdir and each registered `$COMMON/worktrees/<id>` — guard
  `$GIT_DIR/config.worktree` before the first command in that worktree.
- **R4 — same metadata treatment as `config`.** Symlink → `git-metadata-symlink`; existing
  non-regular, non-directory → `git-metadata-nonregular`; `nlink > 1` → `git-metadata-hardlink`;
  unparsable (`git config --file … --no-includes --name-only --list` fails) →
  `git-config-unparsed`. Do this in the new per-file helper, not by extending
  `guard_git_files` (which runs at 613 before activation is known).
- **R5 — same key policy, finding names the per-worktree file.** `include/includeIf`,
  `filter.*.clean|smudge|process`, `core.hooksPath`, `core.attributesFile`,
  `core.excludesFile`, `core.alternateRefsCommand`, `remote.*.promisor`,
  `extensions.partialClone` → `git-config-unsupported` with `$cfg` = the `config.worktree`
  path. The four `-c` neutralizers cover `fsmonitor/hooksPath/excludesFile/attributesFile`
  on status, but refusing parity is cheap; if any of those is instead preserved, the header
  must say it rides the `-c` neutralizers.
- **R6 — `core.worktree` inside `config.worktree`.** `~` → `git-config-unsupported`;
  relative → resolve against that worktree's gitdir (`$GIT_DIR`); absolute → as-is; then
  `guard_target core-worktree`, exactly like 508–521. This is the documented home of a
  per-worktree `core.worktree`, so a blanket key refusal would refuse every legitimate
  worktreeConfig repo — the main operability harm this lane must avoid.
- **R7 — include-delegated activation (cross-cuts IncludesSafe/IncludeIfSafe).** If r15
  preserves benign includes, the activation read must traverse the same
  reachable-and-applicable include graph; `--no-includes` detection on the top-level file
  lets a preserved include set `worktreeConfig = true` while the guard never sees it.
- **R8 — commondir divergence.** `guard_git_surface` overwrites `dir` with the resolved
  common dir (630) before `guard_worktree_registrations` (633). Retain the main gitdir
  separately; for a commondir-indirected `.git` directory, the main worktree's
  `config.worktree` is `$MAIN_GITDIR/config.worktree`, not `$COMMON/config.worktree`.
- **R9 — header text.** Replace the key-presence wording (87–89) with an effect statement:
  the extension is honoured; every reachable `config.worktree` is guarded exactly like
  `config`; a per-worktree `core.worktree` that reaches the protected boundary refuses with
  `path-protected`.

## 4. Holes a naive un-refusal would open (what the C2 checker must catch)

- **H1** `include.path` in `config.worktree` is followed during config parse by the first
  repo command (`rev-parse` 859, `worktree list` 688, `status` 710) → arbitrary file read.
- **H2** `filter.*.clean|process` in `config.worktree` may execute a command during status
  content conversion — the same reason the common-config key is refused (header 86–87).
- **H3** `core.worktree` in `config.worktree` re-roots `git status`; the pathspec excludes at
  712–715 are relative to that root, so a protected target causes mass store access and the
  `dirty` column silently describes another tree.
- **H4** a hostile linked-worktree admin `config.worktree` is read by `count_dirty "$cpath"`
  (832) even when the owner row's `.git/config` is clean.
- **H5** a hardlinked or non-regular `config.worktree` is opened by git but never lstat'ed
  (`guard_git_files` list, 479).
- **H6** activation set from a preserved include (R7) while detection uses `--no-includes`.
- **H7** version gating on `repositoryformatversion = 1` leaves v0 repos reading an
  unguarded `config.worktree` (docs: respected regardless).

## 5. Acceptance required (ConfigFixture + AdmissionChecker)

IDs are proposals; ConfigFixture owns finals. All synthetic `/var/tmp` HOME; r14 namespace
controls must stay 12/12. Same command/tool selection must show the r14 baseline red and the
repaired tool green.

Green (preserved; baseline must be red for G2–G5 because r14 refuses on key presence):
- **G1** extension absent → clean row.
- **G2** false-family values `false/no/off/0`, empty `worktreeConfig =` → clean row each.
- **G3** `true` + no `config.worktree` anywhere → clean row.
- **G4** `true` + benign main `config.worktree` with `core.worktree = ..` (resolves to the
  repo) → clean row; no store access in the trace.
- **G5** `true` + benign linked `worktrees/<id>/config.worktree` (`core.sparseCheckout = false`
  or its own worktree path) → row counts and `wt-*` unchanged.

Red (must refuse, exit 2, empty stdout, zero forbidden access):
- **R1** `true` + main `config.worktree` `core.worktree = <store>` → `path-protected`
  (guard order gives this; a `git-config-unsupported` result is a declared alternative, not
  a silent substitution).
- **R2** `true` + `core.worktree = ~/…` → `git-config-unsupported`.
- **R3** `true` + `include.path = <store>/canary` → `git-config-unsupported`; trace shows no
  open below the store.
- **R4** `true` + `filter.x.process = <store-touching command>` → refused, command not
  executed (spy log empty of it).
- **R5** `true` + linked admin `config.worktree` hostile → refused before any
  `git -C <worktree> status`.
- **R6** `repositoryformatversion = 0` + `true` + hostile `config.worktree` → refused
  (discriminates H7).
- **R7** `true` set from a preserved benign include + hostile `config.worktree` → refused, or
  the include is refused — declared either way (discriminates H6).
- **I1** inertness control: `false` + hostile `config.worktree` → clean row. This proves the
  file is not blanket-refused; a checker must label it inertness and **reject** it as
  preservation evidence.

Admission rules for a declared worktreeConfig preservation record: fixture digest and tool
digest bound; G2–G5 present (green-only false-valued evidence rejected); R1–R7 present with
exit/finding/empty-stdout/access assertions; r14 namespace set 12/12. Row caveat: benign
`config.worktree` cases must avoid `core.sparseCheckout = true` (it legitimately changes which
files status sees, hence `dirty`), or pin the resulting row explicitly.

## 6. Remaining unknowns / inference

- **[INFERENCE]** Whether git applies common-config `core.worktree` when the extension is true
  and `config.worktree` sets none. Docs only say the value "must be moved"; no probe was run
  (probe ban). Keep the common-config boundary check (conservative, no hole); do not build
  acceptance on "common value is inert".
- **[INFERENCE]** Exact intra-git read order of worktree config versus repository-format
  detection. The documented FILES order plus "read after `.git/config`" is sufficient for the
  guard-before-any-command rule (R3).
- Overlap boundaries: promisor/partialClone value semantics (PromisorSafe), include
  applicability (IncludeIfSafe), registration relative paths (RelativePaths). R7 and the
  `config.worktree` include bit are the crossing points; duplicated only as activation rules.

## Disclosure — boundary deviation (already occurred; not repeated)

- **Exact call:** the `grep` tool with `path: /home/vgpnk/Projects/shokunin/souji-shokunin`
  and pattern `worktree[Cc]onfig|extensions\.worktreeConfig|worktreeConfig` (first discovery
  batch) — a recursive search of the whole lane root, which can traverse
  `census/operator-sweep-20261019/`. Also a shallow `ls` of the lane root (top-level names
  only, first call).
- **Observed effect:** matches displayed came only from `SKILL.md`,
  `.ufo/waves/round-14/w1/CensusBoundary.md`, `.ufo/waves/round-15/w1-{dispatch,spec}.json`,
  `census/round-3/seat-51.json`, `corpus/lessons/*.md`, `tools/souji-census.sh`. No
  operator-sweep content was displayed, copied into this report, or used.
- **Limitation:** the traversal may have opened files under `census/operator-sweep-20261019/`
  without reporting a match; non-access cannot be proven post hoc. Nothing was edited, moved,
  staged, copied or deleted anywhere. Every later search was scoped to explicit files
  (`tools/souji-census.sh`, `tests/…`, `.ufo/waves/round-14/…`, `tests/fixtures/…`); no
  further whole-root query was made.
- **Scratch artifact:** `/tmp/gitconfig.txt` holds the rendered local `git-config(1)` man
  page (public documentation text) used for the quotes above; it contains no repo or
  credential content.

## Unrun checks

None run: no fixture execution, no `--selftest`, no `git status`/census invocation, no strace.
Every behavioural statement here is from committed source text at the digest above, or from
the quoted git 2.55 man pages. No tool was installed or updated during this seat.
